#!/usr/bin/env python3
"""Extract paginated review sheets and a timestamp manifest from a local film.

Requires FFmpeg. Exit 0: extracted, 1: failed, 2: invalid input/unavailable.
Extraction does not establish visual review or playback acceptance.
"""

import argparse
import json
import math
from pathlib import Path
import re
import shutil
import subprocess


def positive(value):
    number = float(value)
    if not math.isfinite(number) or number <= 0:
        raise argparse.ArgumentTypeError("expected positive finite seconds")
    return number


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("media", type=Path)
    parser.add_argument("output", type=Path, help="new review directory; never overwritten")
    parser.add_argument("--every", type=positive, default=1.0, help="minimum seconds between samples")
    args = parser.parse_args()
    try:
        media = args.media.resolve(strict=True)
        if not media.is_file():
            raise ValueError("media must be a local file")
        if not shutil.which("ffmpeg"):
            raise FileNotFoundError("ffmpeg is not installed")
        output = args.output.resolve()
        output.mkdir(parents=True, exist_ok=False)
    except (OSError, ValueError) as error:
        print(json.dumps(dict(status="UNAVAILABLE", error=str(error))))
        return 2

    # Select actual decoded frames, retaining their time relative to the first
    # decoded frame. Unlike fps resampling, this does not invent sample times.
    filters = (
        "setpts=PTS-STARTPTS,"
        f"select='isnan(prev_selected_t)+gte(t-prev_selected_t,{args.every})',"
        "showinfo=checksum=0,scale=360:trunc(360/dar/2)*2,setsar=1,"
        "tile=4x4:padding=4:margin=4"
    )
    command = [
        "ffmpeg", "-hide_banner", "-nostdin", "-nostats", "-n",
        "-xerror", "-protocol_whitelist", "file", "-i", str(media),
        "-map", "0:V:0", "-an", "-sn", "-vf", filters,
        "-fps_mode", "passthrough", str(output / "sheet-%04d.png"),
    ]
    log = output / "ffmpeg.log"
    try:
        with log.open("w") as diagnostic:
            result = subprocess.run(command, stdout=diagnostic, stderr=subprocess.STDOUT,
                                    timeout=600, check=False)
        if result.returncode:
            raise ValueError(f"ffmpeg exited {result.returncode}; inspect {log}")
        samples = []
        with log.open() as diagnostic:
            for line in diagnostic:
                match = re.search(r"\[Parsed_showinfo_\d+[^]]*\].*\bn:\s*(\d+).*\bpts_time:\s*([-+\deE.]+)", line)
                if match:
                    index = int(match[1])
                    samples.append(dict(sheet=f"sheet-{index // 16 + 1:04d}.png",
                                        row=index % 16 // 4 + 1, column=index % 4 + 1,
                                        seconds=float(match[2])))
        pages = sorted(output.glob("sheet-*.png"))
        if not samples or len(pages) != math.ceil(len(samples) / 16):
            raise ValueError("missing samples or incomplete sheet output; inspect ffmpeg.log")
        report = dict(status="EXTRACTED", media=str(media),
                      scope="sampled frames only; visual review and playback unverified",
                      time_origin="first decoded video frame", every_seconds=args.every,
                      thumbnail_width=360, columns=4, rows=4,
                      command=command, samples=samples)
        (output / "manifest.json").write_text(json.dumps(report, indent=2) + "\n")
    except (OSError, ValueError, subprocess.TimeoutExpired) as error:
        print(json.dumps(dict(status="FAIL", error=str(error), log=str(log))))
        return 1
    print(json.dumps(dict(status="EXTRACTED", sheets=len(pages), samples=len(samples),
                          manifest=str(output / "manifest.json"))))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
