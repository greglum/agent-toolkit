#!/usr/bin/env python3
"""Compare two local still captures as decoded 8-bit RGBA pixels using FFmpeg.

Exit 0: pixel contract PASS, 1: FAIL, 2: invalid input or UNAVAILABLE.
This does not capture frames or establish visual quality, timing or playback.
"""

import argparse
import json
from pathlib import Path
import shutil
import subprocess


def decode(path):
    path = path.resolve(strict=True)
    if not path.is_file():
        raise ValueError(f"expected a local image file: {path}")
    if path.suffix.lower() not in {".png", ".jpg", ".jpeg", ".bmp", ".ppm", ".pam"}:
        raise ValueError("use a PNG, JPEG, BMP, PPM or PAM still capture")
    command = [
        "ffmpeg", "-v", "error", "-nostdin", "-xerror",
        "-protocol_whitelist", "file", "-f", "image2", "-pattern_type", "none",
        "-i", str(path), "-map", "0:v:0", "-frames:v", "1",
        "-pix_fmt", "rgba", "-c:v", "pam", "-f", "image2pipe", "pipe:1",
    ]
    result = subprocess.run(command, capture_output=True, timeout=60, check=False)
    if result.returncode:
        raise ValueError(f"cannot decode {path}: {result.stderr.decode(errors='replace')[-1200:]}")
    header, separator, pixels = result.stdout.partition(b"ENDHDR\n")
    if not separator or not header.startswith(b"P7\n"):
        raise ValueError(f"no decoded RGBA image from {path}")
    fields = dict(line.split(maxsplit=1) for line in header.splitlines()[1:]
                  if line and not line.startswith(b"#"))
    width, height = int(fields[b"WIDTH"]), int(fields[b"HEIGHT"])
    if (width <= 0 or height <= 0 or fields.get(b"DEPTH") != b"4"
            or fields.get(b"MAXVAL") != b"255" or len(pixels) != width * height * 4):
        raise ValueError(f"incomplete or unsupported decoded image from {path}")
    return width, height, pixels


def compare(expected, actual, *, max_channel_delta=0, max_different_pixels=0):
    width, height, left = expected
    other_width, other_height, right = actual
    if (width, height) != (other_width, other_height):
        return dict(status="FAIL", reason="dimensions differ",
                    expected_dimensions=[width, height], actual_dimensions=[other_width, other_height])
    different = 0
    largest_delta = 0
    for offset in range(0, len(left), 4):
        delta = max(abs(a - b) for a, b in zip(left[offset:offset + 4], right[offset:offset + 4]))
        largest_delta = max(largest_delta, delta)
        different += delta > max_channel_delta
    return dict(status="PASS" if different <= max_different_pixels else "FAIL",
                dimensions=[width, height], different_pixels=different,
                total_pixels=width * height, largest_channel_delta=largest_delta,
                max_channel_delta=max_channel_delta, max_different_pixels=max_different_pixels)


def nonnegative(value):
    number = int(value)
    if number < 0:
        raise argparse.ArgumentTypeError("expected a nonnegative integer")
    return number


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("expected", type=Path)
    parser.add_argument("actual", type=Path)
    parser.add_argument("--max-channel-delta", type=nonnegative, default=0,
                        help="allowed per-channel difference, 0 to 255; default exact")
    parser.add_argument("--max-different-pixels", type=nonnegative, default=0,
                        help="allowed count of pixels beyond the channel limit; default zero")
    args = parser.parse_args()
    if args.max_channel_delta > 255:
        parser.error("--max-channel-delta must be 0 to 255")
    try:
        if not shutil.which("ffmpeg"):
            raise FileNotFoundError("ffmpeg is not installed")
        expected, actual = decode(args.expected), decode(args.actual)
        report = compare(expected, actual, max_channel_delta=args.max_channel_delta,
                         max_different_pixels=args.max_different_pixels)
    except (OSError, ValueError, KeyError, subprocess.TimeoutExpired) as error:
        print(json.dumps(dict(status="UNAVAILABLE", error=str(error))))
        return 2
    report.update(scope="decoded 8-bit RGBA pixels only",
                  expected=str(args.expected.resolve()), actual=str(args.actual.resolve()))
    print(json.dumps(report))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
