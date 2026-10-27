#!/usr/bin/env python3
"""Check one local encoded film against an explicit delivery contract using ffprobe.

Metadata checks only. Exit 0: PASS, 1: FAIL, 2: UNAVAILABLE.
"""

import argparse
from fractions import Fraction
import json
import math
from pathlib import Path
import shutil
import subprocess


def positive(value):
    number = float(Fraction(str(value)))
    if not math.isfinite(number) or number <= 0:
        raise ValueError(f"expected a positive finite number, got {value!r}")
    return number


def measure(value):
    try:
        number = float(Fraction(str(value)))
        return number if math.isfinite(number) else None
    except (ValueError, ZeroDivisionError, TypeError):
        return None


def stream_duration(stream):
    duration = measure(stream.get("duration"))
    if duration is not None:
        return duration
    ticks = measure(stream.get("duration_ts"))
    base = measure(stream.get("time_base"))
    return ticks * base if ticks is not None and base is not None else None


def inspect(probe, *, width, height, fps, duration, require_audio=False,
            video_codec=None, pixel_format=None, tolerance=0.1):
    """Return checks without substituting container duration for missing streams."""
    checks = []

    def check(name, actual, expected, matches=None):
        status = "UNAVAILABLE" if actual is None else (
            "PASS" if (actual == expected if matches is None else matches) else "FAIL")
        checks.append(dict(check=name, status=status, actual=actual, expected=expected))

    streams = probe.get("streams", [])
    videos = [s for s in streams if s.get("codec_type") == "video"
              and not s.get("disposition", {}).get("attached_pic")]
    audios = [s for s in streams if s.get("codec_type") == "audio"]
    check("video_stream_count", len(videos), 1)
    if require_audio:
        check("required_audio", bool(audios), True)
    container = probe.get("format", {})
    container_duration = measure(container.get("duration"))
    check("container_duration", container_duration, duration,
          container_duration is not None and abs(container_duration - duration) <= tolerance)
    for index, stream in enumerate(videos + audios):
        label = f"{stream['codec_type']}[{index}]"
        length = stream_duration(stream)
        check(f"{label}.duration", length, duration,
              length is not None and abs(length - duration) <= tolerance)
        start = measure(stream.get("start_time"))
        check(f"{label}.start_time", start, 0,
              start is not None and abs(start) <= tolerance)
        if stream["codec_type"] != "video":
            continue
        check(f"{label}.width", stream.get("width"), width)
        check(f"{label}.height", stream.get("height"), height)
        rate = measure(stream.get("avg_frame_rate"))
        check(f"{label}.average_fps", rate, fps,
              rate is not None and abs(rate - fps) <= 0.001)
        if video_codec:
            check(f"{label}.codec", stream.get("codec_name"), video_codec)
        if pixel_format:
            check(f"{label}.pixel_format", stream.get("pix_fmt"), pixel_format)
    status = "FAIL" if any(c["status"] == "FAIL" for c in checks) else (
        "UNAVAILABLE" if any(c["status"] == "UNAVAILABLE" for c in checks) else "PASS")
    return dict(status=status, scope="metadata only", checks=checks)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("media", type=Path)
    parser.add_argument("--width", type=int, required=True)
    parser.add_argument("--height", type=int, required=True)
    parser.add_argument("--fps", required=True, help="number or rational, e.g. 30000/1001")
    parser.add_argument("--duration", required=True, help="expected seconds")
    parser.add_argument("--require-audio", action="store_true")
    parser.add_argument("--video-codec")
    parser.add_argument("--pixel-format")
    parser.add_argument("--tolerance", default="0.1", help="duration/start tolerance in seconds")
    args = parser.parse_args()
    try:
        fps, duration, tolerance = map(positive, (args.fps, args.duration, args.tolerance))
        if args.width <= 0 or args.height <= 0:
            raise ValueError("dimensions must be positive")
    except (ValueError, ZeroDivisionError) as error:
        parser.error(str(error))
    try:
        media = args.media.resolve(strict=True)
        if not media.is_file():
            raise ValueError("media must be a local file")
        if not shutil.which("ffprobe"):
            raise FileNotFoundError("ffprobe is not installed")
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-protocol_whitelist", "file", "-show_streams",
             "-show_format", "-of", "json", str(media)],
            capture_output=True, text=True, timeout=60, check=False)
        if result.returncode:
            report = dict(status="FAIL", scope="probe", error=result.stderr.strip())
        else:
            report = inspect(json.loads(result.stdout), width=args.width, height=args.height,
                             fps=fps, duration=duration, require_audio=args.require_audio,
                             video_codec=args.video_codec, pixel_format=args.pixel_format,
                             tolerance=tolerance)
        report["media"] = str(media)
    except (OSError, ValueError, subprocess.TimeoutExpired) as error:
        report = dict(status="UNAVAILABLE", scope="probe", error=str(error))
    print(json.dumps(report, indent=2, allow_nan=False))
    return {"PASS": 0, "FAIL": 1, "UNAVAILABLE": 2}[report["status"]]


if __name__ == "__main__":
    raise SystemExit(main())
