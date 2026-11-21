"""Shared reading, robust scoring and event extraction for the telemetry-anomalies tools."""
import bisect
import csv
import json
import math
import sys
from pathlib import Path

MAD_TO_SIGMA = 1.4826


class InputError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise InputError(message)


def number(text, label):
    try:
        value = float(text)
    except (TypeError, ValueError):
        raise InputError(f"{label}: not a number") from None
    require(math.isfinite(value), f"{label}: not a finite number")
    return value


def split_list(text):
    return [part.strip() for part in (text or "").split(",") if part.strip()]


def read_table(path, time_column, channels, mode_column=None):
    """Return times, {channel: [value or None]}, modes. Blank channel cells are missing samples."""
    require(channels, "at least one channel is required")
    require(len(set(channels)) == len(channels), "channels repeat")
    with Path(path).open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        header = reader.fieldnames or []
        require(len(set(header)) == len(header), f"{path}: duplicate column names")
        for name in [time_column, *channels] + ([mode_column] if mode_column else []):
            require(name in header, f"{path}: missing column '{name}'")
        times, modes = [], []
        values = {channel: [] for channel in channels}
        for line, row in enumerate(reader, start=2):
            require(None not in row and None not in row.values(), f"{path}:{line}: wrong field count")
            stamp = number(row[time_column], f"{path}:{line} {time_column}")
            require(not times or stamp > times[-1], f"{path}:{line}: timestamps must strictly increase")
            times.append(stamp)
            for channel in channels:
                cell = row[channel].strip()
                values[channel].append(number(cell, f"{path}:{line} {channel}") if cell else None)
            if mode_column:
                mode = row[mode_column].strip()
                require(mode, f"{path}:{line}: empty mode")
                modes.append(mode)
    require(len(times) >= 2, f"{path}: needs at least two rows")
    return times, values, modes or ["all"] * len(times)


def _median_sorted(window):
    n = len(window)
    middle = n // 2
    return window[middle] if n % 2 else (window[middle - 1] + window[middle]) / 2


def _mad_sorted(window, center):
    """Median absolute deviation of a sorted window, merging both sides outward in O(n)."""
    n = len(window)
    split = bisect.bisect_left(window, center)
    low, high = split - 1, split
    deviations = []
    need = n // 2 + 1
    while len(deviations) < need:
        below = center - window[low] if low >= 0 else math.inf
        above = window[high] - center if high < n else math.inf
        if below <= above:
            deviations.append(below)
            low -= 1
        else:
            deviations.append(above)
            high += 1
    return deviations[n // 2] if n % 2 else (deviations[n // 2 - 1] + deviations[n // 2]) / 2


def robust_scores(values, modes, window, min_history, min_scale, excluded):
    """Score each sample against the trailing `window` earlier samples of the same mode.

    Score = (x - median) / max(1.4826 * MAD, min_scale). The current sample is not in its own
    baseline. A sample is unscored (None) when missing, in an excluded mode, or when its mode
    has fewer than `min_history` earlier samples. Returns scores and coverage counts.
    """
    history, ordered = {}, {}
    scores = []
    counts = {"scored": 0, "warmup": 0, "missing": 0, "excluded": 0}
    for value, mode in zip(values, modes):
        if mode in excluded:
            counts["excluded"] += 1
            scores.append(None)
            continue
        if value is None:
            counts["missing"] += 1
            scores.append(None)
            continue
        recent = history.setdefault(mode, [])
        window_sorted = ordered.setdefault(mode, [])
        if len(recent) >= min_history:
            center = _median_sorted(window_sorted)
            scale = max(MAD_TO_SIGMA * _mad_sorted(window_sorted, center), min_scale)
            scores.append((value - center) / scale)
            counts["scored"] += 1
        else:
            scores.append(None)
            counts["warmup"] += 1
        recent.append(value)
        bisect.insort(window_sorted, value)
        if len(recent) > window:
            old = recent.pop(0)
            del window_sorted[bisect.bisect_left(window_sorted, old)]
    return scores, counts


def events_from_scores(channel, times, scores, modes, threshold, min_duration, merge_gap):
    """Group samples with |score| > threshold into events.

    Runs closer than `merge_gap` seconds merge; events shorter than `min_duration` seconds
    are dropped. Unscored samples never alarm.
    """
    runs = []
    for index, score in enumerate(scores):
        if score is None or abs(score) <= threshold:
            continue
        if runs and (index == runs[-1][1] + 1 or (merge_gap > 0 and round(times[index] - times[runs[-1][1]], 9) <= merge_gap)):
            runs[-1][1] = index
        else:
            runs.append([index, index])
    events = []
    for first, last in runs:
        if round(times[last] - times[first], 9) < min_duration:
            continue
        peak = max(range(first, last + 1), key=lambda i: abs(scores[i]) if scores[i] is not None else -1)
        events.append({
            "channel": channel,
            "start": times[first],
            "end": times[last],
            "peak_score": round(scores[peak], 3),
            "mode": modes[peak],
            "alarm_samples": sum(1 for i in range(first, last + 1)
                                 if scores[i] is not None and abs(scores[i]) > threshold),
        })
    return events


def session_summary(times):
    return {"start": times[0], "end": times[-1], "duration_s": times[-1] - times[0], "rows": len(times)}


DEFAULTS = {"time_column": "t", "mode_column": None, "exclude_modes": "", "window": 50,
            "min_history": None, "min_scale": 1e-6, "min_duration": 0.0, "merge_gap": 0.0}
SCORING_OPTIONS = ("time_column", "channels", "mode_column", "exclude_modes", "window",
                   "min_history", "min_scale", "min_duration", "merge_gap")


def common_arguments(parser):
    """Scoring options default to None so a caller can tell which were given."""
    parser.add_argument("data", help="CSV with a timestamp column in seconds and channel columns")
    parser.add_argument("--time-column", help="timestamp column in seconds (default t)")
    parser.add_argument("--channels", help="comma-separated channel columns")
    parser.add_argument("--mode-column", help="operating-mode column; baselines are kept per mode")
    parser.add_argument("--exclude-modes", help="comma-separated modes that are not scored")
    parser.add_argument("--window", type=int, help="trailing samples per mode baseline (default 50)")
    parser.add_argument("--min-history", type=int, help="samples a mode needs before scoring (default window)")
    parser.add_argument("--min-scale", type=float, help="floor for 1.4826*MAD; use the sensor resolution")
    parser.add_argument("--min-duration", type=float, help="seconds an event must last (default 0)")
    parser.add_argument("--merge-gap", type=float, help="seconds between alarm runs that still merge (default 0)")


def given_scoring_options(args):
    return [name for name in SCORING_OPTIONS if getattr(args, name) is not None]


def params_from(args):
    raw = {name: (DEFAULTS.get(name) if getattr(args, name) is None else getattr(args, name))
           for name in SCORING_OPTIONS}
    require(raw["channels"], "--channels is required")
    window = raw["window"]
    min_history = window if raw["min_history"] is None else raw["min_history"]
    require(window >= 3, "--window must be at least 3")
    require(3 <= min_history <= window, "--min-history must be between 3 and --window")
    for name in ("min_scale", "min_duration", "merge_gap"):
        value = raw[name]
        require(math.isfinite(value) and value >= 0, f"--{name.replace('_', '-')} must be finite and >= 0")
    require(raw["min_scale"] > 0, "--min-scale must be > 0")
    excluded = split_list(raw["exclude_modes"])
    require(not excluded or raw["mode_column"], "--exclude-modes needs --mode-column")
    return {"time_column": raw["time_column"], "channels": split_list(raw["channels"]),
            "mode_column": raw["mode_column"], "exclude_modes": excluded, "window": window,
            "min_history": min_history, "min_scale": raw["min_scale"],
            "min_duration": raw["min_duration"], "merge_gap": raw["merge_gap"]}


def check_params(params):
    """Validate a params object read back from a calibration or detection file."""
    require(isinstance(params, dict) and set(params) == {"time_column", "channels", "mode_column",
            "exclude_modes", "window", "min_history", "min_scale", "min_duration", "merge_gap"},
            "params: expected the fields written by calibrate or detect")
    require(isinstance(params["channels"], list) and params["channels"]
            and all(isinstance(c, str) and c for c in params["channels"]), "params: bad channels")
    require(isinstance(params["time_column"], str) and params["time_column"], "params: bad time_column")
    require(params["mode_column"] is None or (isinstance(params["mode_column"], str) and params["mode_column"]),
            "params: bad mode_column")
    require(isinstance(params["exclude_modes"], list) and all(isinstance(m, str) for m in params["exclude_modes"]),
            "params: exclude_modes must be a list of strings")
    require(not params["exclude_modes"] or params["mode_column"], "params: exclude_modes needs mode_column")
    for name in ("window", "min_history"):
        value = params[name]
        require(isinstance(value, int) and not isinstance(value, bool) and value >= 3, f"params: bad {name}")
    require(params["min_history"] <= params["window"], "params: min_history exceeds window")
    for name in ("min_scale", "min_duration", "merge_gap"):
        value = params[name]
        require(isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)
                and value >= 0, f"params: bad {name}")
    require(params["min_scale"] > 0, "params: min_scale must be > 0")
    return params


def check_thresholds(thresholds, channels):
    """Thresholds must be positive finite numbers for exactly the given channels."""
    require(isinstance(thresholds, dict) and set(thresholds) == set(channels),
            "thresholds must cover exactly the scored channels")
    for channel, value in thresholds.items():
        require(isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)
                and value > 0, f"threshold for {channel} must be a positive number")
    return thresholds


def score_table(path, params):
    times, values, modes = read_table(path, params["time_column"], params["channels"], params["mode_column"])
    scored = {}
    for channel in params["channels"]:
        scored[channel] = robust_scores(values[channel], modes, params["window"], params["min_history"],
                                        params["min_scale"], set(params["exclude_modes"]))
    return times, modes, scored


def emit(run):
    """Run a main body; print JSON to stdout, or a JSON error to stderr with exit 2."""
    try:
        output = run()
        print(json.dumps(output, indent=2, allow_nan=False))
        return 0
    except (InputError, OSError, UnicodeError, json.JSONDecodeError, csv.Error) as error:
        message = str(error) if isinstance(error, InputError) else f"cannot read input: {type(error).__name__}"
        print(json.dumps({"error": message}), file=sys.stderr)
        return 2
