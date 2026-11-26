#!/usr/bin/env python3
"""Check an encoded local film for unintended freezes, loop-seam duplication, and post-encode audio true peak.

Uses installed ffmpeg/ffprobe without modifying media.
Exit 0: PASS, 1: FAIL, 2: invalid invocation or UNAVAILABLE.
"""

from __future__ import annotations

import argparse
import io
import json
import math
from pathlib import Path
import re
import shutil
import subprocess

FREEZE_START_RE = re.compile(r"freeze_start:\s*([0-9]+(?:\.[0-9]+)?)")
FREEZE_END_RE = re.compile(r"freeze_end:\s*([0-9]+(?:\.[0-9]+)?)")
FREEZE_DUR_RE = re.compile(r"freeze_duration:\s*([0-9]+(?:\.[0-9]+)?)")
INTEGRATED_RE = re.compile(r"I:\s*(-?[0-9]+(?:\.[0-9]+)?|-inf)\s*LUFS", re.IGNORECASE)
TRUE_PEAK_RE = re.compile(r"Peak:\s*(-?[0-9]+(?:\.[0-9]+)?|-inf)\s*dBFS", re.IGNORECASE)
NOISE_RE = re.compile(r"^-?[0-9]+(?:\.[0-9]+)?(?:dB)?$")


def parse_hold_windows(raw_windows: list[str]) -> list[tuple[float, float]]:
    windows: list[tuple[float, float]] = []
    for item in raw_windows:
        if ":" not in item:
            raise ValueError(f"invalid --allow-hold value {item!r}; use START:END in seconds")
        left, right = item.split(":", 1)
        start, end = float(left), float(right)
        if start < 0 or end <= start:
            raise ValueError(f"--allow-hold requires 0 <= START < END, got {item!r}")
        windows.append((start, end))
    return windows


def parse_freezedetect(stderr: str) -> list[dict]:
    intervals: list[dict] = []
    current_start: float | None = None
    pending_dur: float | None = None
    for line in stderr.splitlines():
        m_start = FREEZE_START_RE.search(line)
        if m_start:
            current_start = float(m_start.group(1))
            pending_dur = None
            continue
        m_dur = FREEZE_DUR_RE.search(line)
        if m_dur:
            pending_dur = float(m_dur.group(1))
        m_end = FREEZE_END_RE.search(line)
        if m_end:
            end_val = float(m_end.group(1))
            dur_val = pending_dur if pending_dur is not None else (
                round(end_val - current_start, 6) if current_start is not None else None
            )
            intervals.append({
                "start": current_start,
                "end": end_val,
                "duration": dur_val,
            })
            current_start = None
            pending_dur = None
    if current_start is not None:
        intervals.append({"start": current_start, "end": None, "duration": pending_dur})
    return intervals


def is_allowed_hold(
    interval: dict,
    allowed: list[tuple[float, float]],
    tolerance: float = 0.05,
    media_duration: float | None = None,
) -> bool:
    start = interval.get("start")
    end = interval.get("end")
    if start is None:
        return False
    effective_end = end if end is not None else media_duration
    if effective_end is None:
        return False
    return any(
        a_start - tolerance <= start and effective_end <= a_end + tolerance
        for a_start, a_end in allowed
    )


def parse_ebur128(stderr: str) -> dict:
    summary_idx = stderr.rfind("Summary:")
    section = stderr[summary_idx:] if summary_idx != -1 else stderr
    integrated_matches = INTEGRATED_RE.findall(section)
    peak_matches = TRUE_PEAK_RE.findall(section)
    integrated_raw = integrated_matches[-1].lower() if integrated_matches else None
    peak_raw = peak_matches[-1].lower() if peak_matches else None
    integrated = None if (integrated_raw is None or integrated_raw == "-inf") else float(integrated_raw)
    silent = peak_raw == "-inf"
    true_peak = None if (peak_raw is None or silent) else float(peak_raw)
    return {
        "integrated_lufs": integrated,
        "true_peak_dbtp": true_peak,
        "silent_track": silent,
    }


def read_exact(stream: io.BufferedIOBase, size: int) -> bytes:
    chunks: list[bytes] = []
    remaining = size
    while remaining > 0:
        chunk = stream.read(remaining)
        if not chunk:
            raise ValueError(f"truncated PAM pixel payload: expected {size} bytes")
        chunks.append(chunk)
        remaining -= len(chunk)
    return b"".join(chunks)


def read_pam_frame_from_stream(stream: io.BufferedIOBase) -> tuple[int, int, bytes] | None:
    magic = stream.readline()
    if not magic:
        return None
    if magic != b"P7\n":
        raise ValueError(f"unexpected PAM header magic: {magic!r}")
    fields: dict[bytes, bytes] = {}
    while True:
        line = stream.readline()
        if not line:
            raise ValueError("truncated PAM header before ENDHDR")
        if line == b"ENDHDR\n":
            break
        if line.startswith(b"#") or not line.strip():
            continue
        parts = line.split(maxsplit=1)
        if len(parts) == 2:
            fields[parts[0]] = parts[1].strip()
    try:
        width = int(fields[b"WIDTH"])
        height = int(fields[b"HEIGHT"])
        depth = int(fields[b"DEPTH"])
    except (KeyError, ValueError) as exc:
        raise ValueError("missing or invalid PAM header dimensions") from exc
    if width <= 0 or height <= 0 or depth != 3:
        raise ValueError("unexpected decoded RGB24 PAM frame dimensions")
    pixels = read_exact(stream, width * height * depth)
    return width, height, pixels


def parse_last_pam_frame(raw: bytes) -> tuple[int, int, bytes]:
    buf = io.BytesIO(raw)
    last_frame: tuple[int, int, bytes] | None = None
    while True:
        frame = read_pam_frame_from_stream(buf)
        if frame is None:
            break
        last_frame = frame
    if last_frame is None:
        raise ValueError("no decoded frame returned by ffmpeg")
    return last_frame


def compare_rgb_frames(
    first: tuple[int, int, bytes],
    last: tuple[int, int, bytes],
    max_mean_delta: float = 2.0,
) -> dict:
    w1, h1, p1 = first
    w2, h2, p2 = last
    if (w1, h1) != (w2, h2):
        raise ValueError("first and last frame dimensions differ")
    total_channels = len(p1)
    diff_sum = sum(abs(a - b) for a, b in zip(p1, p2))
    max_delta = max((abs(a - b) for a, b in zip(p1, p2)), default=0)
    mean_delta = diff_sum / total_channels if total_channels else 0.0
    duplicate = max_delta == 0 or mean_delta <= max_mean_delta
    return {
        "dimensions": [w1, h1],
        "mean_channel_delta": round(mean_delta, 4),
        "max_channel_delta": max_delta,
        "max_mean_delta_threshold": max_mean_delta,
        "identical_endpoints": max_delta == 0,
        "duplicate_endpoints": duplicate,
    }


def probe_duration(media: Path) -> float | None:
    if not shutil.which("ffprobe"):
        return None
    cmd = [
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", str(media),
    ]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=30, check=False)
    except (OSError, subprocess.TimeoutExpired):
        return None
    if res.returncode != 0:
        return None
    try:
        val = float(res.stdout.strip())
        return val if math.isfinite(val) and val > 0 else None
    except ValueError:
        return None


def extract_boundary_frame(media: Path, *, last: bool) -> tuple[int, int, bytes]:
    cmd = ["ffmpeg", "-v", "error", "-nostdin", "-protocol_whitelist", "file"]
    if last:
        cmd += ["-sseof", "-1"]
    cmd += ["-i", str(media), "-map", "0:v:0"]
    if not last:
        cmd += ["-frames:v", "1"]
    cmd += ["-pix_fmt", "rgb24", "-c:v", "pam", "-f", "image2pipe", "pipe:1"]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    assert proc.stdout is not None and proc.stderr is not None
    selected: tuple[int, int, bytes] | None = None
    try:
        while True:
            frame = read_pam_frame_from_stream(proc.stdout)
            if frame is None:
                break
            selected = frame
            if not last:
                break
        proc.stdout.close()
        stderr_text = proc.stderr.read().decode(errors="replace")
        rc = proc.wait(timeout=60)
    except (OSError, ValueError, subprocess.TimeoutExpired) as exc:
        proc.kill()
        proc.wait()
        raise ValueError(f"ffmpeg boundary decode failed: {exc}") from exc
    if rc != 0:
        raise ValueError(f"ffmpeg boundary decode failed: {stderr_text[-600:]}")
    if selected is None:
        raise ValueError("no decoded frame returned by ffmpeg")
    return selected


def run_freezes(media: Path, noise: str, min_duration: float, allowed_holds: list[tuple[float, float]]) -> dict:
    cmd = [
        "ffmpeg", "-v", "info", "-nostdin", "-protocol_whitelist", "file",
        "-i", str(media), "-map", "0:v:0",
        "-vf", f"freezedetect=n={noise}:d={min_duration}",
        "-f", "null", "-",
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=180, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"status": "UNAVAILABLE", "error": f"freezedetect timed out or failed: {exc}"}
    if result.returncode != 0:
        return {"status": "UNAVAILABLE", "error": result.stderr[-600:].strip()}
    intervals = parse_freezedetect(result.stderr)
    media_duration = probe_duration(media) if any(iv["end"] is None for iv in intervals) else None
    if media_duration is not None:
        for iv in intervals:
            if iv["end"] is None and iv["start"] is not None:
                iv["end"] = round(media_duration, 6)
                iv["duration"] = round(media_duration - iv["start"], 6)
    unplanned = [
        iv for iv in intervals
        if not is_allowed_hold(iv, allowed_holds, media_duration=media_duration)
    ]
    return {
        "status": "FAIL" if unplanned else "PASS",
        "noise": noise,
        "min_duration": min_duration,
        "detected_freezes": intervals,
        "unplanned_freezes": unplanned,
    }


def run_audio_peak(media: Path, max_true_peak: float) -> dict:
    cmd = [
        "ffmpeg", "-v", "info", "-nostdin", "-protocol_whitelist", "file",
        "-i", str(media), "-map", "0:a:0",
        "-af", "ebur128=peak=true",
        "-f", "null", "-",
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=180, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"status": "UNAVAILABLE", "error": f"ebur128 timed out or failed: {exc}"}
    if result.returncode != 0:
        return {"status": "UNAVAILABLE", "error": result.stderr[-600:].strip()}
    metrics = parse_ebur128(result.stderr)
    if metrics["silent_track"]:
        return {
            "status": "PASS",
            "max_true_peak_dbtp": max_true_peak,
            **metrics,
        }
    peak = metrics["true_peak_dbtp"]
    if peak is None:
        return {"status": "UNAVAILABLE", "error": "could not parse ebur128 true peak from ffmpeg output", **metrics}
    return {
        "status": "PASS" if peak <= max_true_peak else "FAIL",
        "max_true_peak_dbtp": max_true_peak,
        **metrics,
    }


def run_loop_seam(media: Path, max_mean_delta: float = 2.0) -> dict:
    try:
        first = extract_boundary_frame(media, last=False)
        last = extract_boundary_frame(media, last=True)
        stats = compare_rgb_frames(first, last, max_mean_delta=max_mean_delta)
    except ValueError as exc:
        return {"status": "UNAVAILABLE", "error": str(exc)}
    if stats["identical_endpoints"]:
        reason = "last frame identically duplicates frame 0 (frame-N loop stutter)"
    elif stats["duplicate_endpoints"]:
        reason = (
            f"last frame near-duplicates frame 0 within lossy tolerance "
            f"(mean_channel_delta={stats['mean_channel_delta']} <= {max_mean_delta})"
        )
    else:
        reason = "endpoints distinct; review motion continuity visually"
    return {
        "status": "FAIL" if stats["duplicate_endpoints"] else "PASS",
        "reason": reason,
        **stats,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("media", type=Path, help="Local encoded video file")
    parser.add_argument("--noise", default="-60dB", help="freezedetect noise floor (default -60dB)")
    parser.add_argument("--min-freeze", type=float, default=0.5, help="minimum freeze seconds (default 0.5)")
    parser.add_argument("--allow-hold", action="append", default=[], help="planned hold window START:END in seconds")
    parser.add_argument("--skip-freezes", action="store_true", help="skip video freeze detection")
    parser.add_argument("--check-loop-seam", action="store_true", help="check frame 0 vs last frame for duplicate-frame stutter")
    parser.add_argument("--loop-max-mean-delta", type=float, default=2.0, help="mean RGB delta threshold treating lossy endpoints as duplicate (default 2.0)")
    parser.add_argument("--check-audio-peak", action="store_true", help="measure post-encode integrated loudness and true peak via ebur128")
    parser.add_argument("--max-true-peak", type=float, default=-1.0, help="maximum allowed true peak in dBTP (default -1.0)")
    args = parser.parse_args(argv)

    try:
        if not NOISE_RE.fullmatch(args.noise):
            raise ValueError(f"invalid --noise value {args.noise!r}; expected number with optional dB suffix")
        if args.min_freeze <= 0:
            raise ValueError("--min-freeze must be positive")
        if args.loop_max_mean_delta < 0:
            raise ValueError("--loop-max-mean-delta must be non-negative")
        allowed_holds = parse_hold_windows(args.allow_hold)
        media = args.media.resolve(strict=True)
        if not media.is_file():
            raise ValueError("media must be a local file")
        if not shutil.which("ffmpeg"):
            raise FileNotFoundError("ffmpeg is not installed")
    except (OSError, ValueError) as exc:
        print(json.dumps({"status": "UNAVAILABLE", "error": str(exc)}, indent=2))
        return 2

    checks: dict[str, dict] = {}
    if not args.skip_freezes:
        checks["freezes"] = run_freezes(media, args.noise, args.min_freeze, allowed_holds)
    if args.check_loop_seam:
        checks["loop_seam"] = run_loop_seam(media, max_mean_delta=args.loop_max_mean_delta)
    if args.check_audio_peak:
        checks["audio_peak"] = run_audio_peak(media, args.max_true_peak)

    if not checks:
        print(json.dumps({"status": "UNAVAILABLE", "error": "no checks selected"}, indent=2))
        return 2

    statuses = {c["status"] for c in checks.values()}
    overall = "FAIL" if "FAIL" in statuses else ("UNAVAILABLE" if "UNAVAILABLE" in statuses else "PASS")
    report = {
        "status": overall,
        "scope": "automated motion, seam, and post-encode audio checks; does not replace human playback review",
        "media": str(media),
        "checks": checks,
    }
    print(json.dumps(report, indent=2))
    return {"PASS": 0, "FAIL": 1, "UNAVAILABLE": 2}[overall]


if __name__ == "__main__":
    raise SystemExit(main())
