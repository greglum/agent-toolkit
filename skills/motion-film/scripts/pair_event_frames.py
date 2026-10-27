#!/usr/bin/env python3
"""Extract event-matched reference | draft images from two local videos.

Needs FFmpeg. Exit 0 means EXTRACTED, 1 failed, 2 invalid input/unavailable.
Images support human review; they do not establish fidelity, pacing or audio.
"""

import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import shutil
import subprocess


def identity(path):
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return dict(path=str(path), sha256=digest.hexdigest())


def read_pairs(path):
    pairs = json.loads(path.read_text())
    if not isinstance(pairs, list) or not 1 <= len(pairs) <= 64:
        raise ValueError("pairs must be a list of 1 to 64 events")
    for pair in pairs:
        if not isinstance(pair, dict) or not isinstance(pair.get("event"), str) or not pair["event"].strip():
            raise ValueError("each pair needs a nonempty event name")
        for key in ("reference_seconds", "draft_seconds"):
            value = pair.get(key)
            if type(value) not in (int, float) or not math.isfinite(value) or value < 0:
                raise ValueError(f"{key} must be finite, nonnegative seconds")
    return pairs


def run(command, log):
    with log.open("w") as diagnostic:
        result = subprocess.run(command, stdout=diagnostic, stderr=subprocess.STDOUT,
                                timeout=600, check=False)
    if result.returncode:
        raise ValueError(f"ffmpeg exited {result.returncode}; inspect {log.name}")
    return log.read_text(errors="replace")


def extract(media, seconds, output):
    filters = (
        "setpts=PTS-STARTPTS,"
        f"select='gte(t,{seconds})',trim=end_frame=1,showinfo=checksum=0,"
        "scale=w='max(2,trunc(min(360,360*dar)/2)*2)':"
        "h='max(2,trunc(min(360,360/dar)/2)*2)',"
        "setsar=1,pad=360:360:(ow-iw)/2:(oh-ih)/2"
    )
    command = [
        "ffmpeg", "-hide_banner", "-nostdin", "-nostats", "-n", "-xerror",
        "-protocol_whitelist", "file", "-i", str(media), "-map", "0:V:0",
        "-an", "-sn", "-vf", filters, "-frames:v", "1", "-update", "1", str(output),
    ]
    log = output.with_suffix(".log")
    diagnostic = run(command, log)
    match = re.search(r"\[Parsed_showinfo_\d+[^]]*\].*\bpts_time:\s*([-+\deE.]+)", diagnostic)
    if not output.is_file() or not match:
        raise ValueError(f"no frame at or after {seconds}s; inspect {log.name}")
    actual = float(match[1])
    if not math.isfinite(actual) or actual + 0.000001 < seconds:
        raise ValueError(f"invalid decoded timestamp; inspect {log.name}")
    return dict(requested_seconds=seconds, decoded_seconds=actual,
                image=output.name, command=command)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("reference", type=Path)
    parser.add_argument("draft", type=Path)
    parser.add_argument("pairs", type=Path, help="JSON event and timestamp pairs")
    parser.add_argument("output", type=Path, help="new directory; never overwritten")
    args = parser.parse_args()
    try:
        media = [args.reference.resolve(strict=True), args.draft.resolve(strict=True)]
        if not all(path.is_file() for path in media):
            raise ValueError("reference and draft must be local files")
        pairs = read_pairs(args.pairs)
        if not shutil.which("ffmpeg"):
            raise FileNotFoundError("ffmpeg is not installed")
        inputs = [identity(path) for path in media]
        output = args.output.resolve()
        output.mkdir(parents=True, exist_ok=False)
    except (OSError, ValueError, OverflowError) as error:
        print(json.dumps(dict(status="UNAVAILABLE", error=str(error))))
        return 2

    try:
        samples = []
        for index, pair in enumerate(pairs, 1):
            stem = f"pair-{index:03d}"
            reference = extract(media[0], pair["reference_seconds"], output / f"{stem}-reference.png")
            draft = extract(media[1], pair["draft_seconds"], output / f"{stem}-draft.png")
            image = output / f"{stem}.png"
            command = ["ffmpeg", "-hide_banner", "-nostdin", "-nostats", "-n", "-xerror",
                       "-protocol_whitelist", "file", "-i", str(output / reference["image"]),
                       "-protocol_whitelist", "file", "-i", str(output / draft["image"]),
                       "-filter_complex", "hstack=inputs=2", "-frames:v", "1", "-update", "1", str(image)]
            run(command, output / f"{stem}.log")
            if not image.is_file():
                raise ValueError(f"missing comparison image {image.name}")
            samples.append(dict(event=pair["event"], image=image.name,
                                reference=reference, draft=draft, command=command))
        if inputs != [identity(path) for path in media]:
            raise ValueError("input media changed during extraction; retry into a new directory")
        version = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True,
                                 timeout=10, check=True).stdout.splitlines()[0]
        manifest = dict(status="EXTRACTED", scope="paired stills only; visual review, pacing and audio unverified",
                        layout="reference left, draft right; each fitted inside 360x360 without cropping",
                        time_origin="first decoded video frame in each input", ffmpeg=version,
                        inputs=dict(reference=inputs[0], draft=inputs[1]), samples=samples)
        (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        print(json.dumps(dict(status="FAIL", error=str(error), diagnostics=str(output))))
        return 1
    print(json.dumps(dict(status="EXTRACTED", pairs=len(samples), manifest=str(output / "manifest.json"))))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
