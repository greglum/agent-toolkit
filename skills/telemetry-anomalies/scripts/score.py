#!/usr/bin/env python3
"""Score detected events against labeled event ranges at event level, next to a trivial baseline.

A label counts as detected when a detection on its channel (or any channel, for a label
without one) overlaps its range, widened by --tolerance seconds. A detection is a true
positive when it overlaps any label. Point-adjusted metrics are never computed.
The baseline flags |x - median| / (1.4826 * MAD) above a fixed threshold, with the median
and MAD taken once over the whole session (or --baseline-reference) and modes ignored.
"""
import argparse
import json
import math
import statistics
import sys
from pathlib import Path

from telemetry_core import (MAD_TO_SIGMA, InputError, check_params, check_thresholds, emit, events_from_scores, number,
                            read_table, require, session_summary)

EVALUATION = ("event-level range overlap; point-adjusted metrics are not computed because they "
              "let a single hit inside a long label count every point as detected")


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"), parse_constant=reject_constant)


def reject_constant(_):
    raise InputError("nonfinite JSON number")


def read_labels(path, channels):
    labels = load_json(path)
    require(isinstance(labels, list), "labels: expected a JSON list")
    checked = []
    for index, label in enumerate(labels):
        require(isinstance(label, dict) and {"start", "end"} <= set(label) <= {"start", "end", "channel", "kind"},
                f"labels[{index}]: expected start, end and optional channel, kind")
        start, end = number(label["start"], f"labels[{index}].start"), number(label["end"], f"labels[{index}].end")
        require(start <= end, f"labels[{index}]: start is after end")
        channel = label.get("channel")
        require(channel is None or channel in channels, f"labels[{index}]: channel is not a scored channel")
        checked.append({"start": start, "end": end, "channel": channel, "kind": label.get("kind")})
    return checked


def read_events(path):
    report = load_json(path)
    require(isinstance(report, dict) and isinstance(report.get("events"), list), "events: expected detect.py output")
    params = check_params(report.get("params"))
    thresholds = check_thresholds(report.get("thresholds"), params["channels"])
    events = []
    for index, event in enumerate(report["events"]):
        require(isinstance(event, dict) and event.get("channel") in params["channels"], f"events[{index}]: bad channel")
        start, end = number(event.get("start"), f"events[{index}].start"), number(event.get("end"), f"events[{index}].end")
        require(start <= end, f"events[{index}]: start is after end")
        events.append({"channel": event["channel"], "start": start, "end": end})
    return params, thresholds, events


def overlaps(event, label, tolerance):
    same_channel = label["channel"] is None or label["channel"] == event["channel"]
    return same_channel and event["start"] <= label["end"] + tolerance and event["end"] >= label["start"] - tolerance


LONG_ALARM_SHARE = 0.2


def coverage(events, channels, duration):
    """Seconds flagged per channel and as a share of the session.

    Event overlap rewards long detections: one event spanning the session overlaps every
    label. Flagged share exposes that; compare it with the labeled share.
    """
    per_channel = {}
    for channel in channels:
        spans = sorted((e["start"], e["end"]) for e in events if e["channel"] == channel)
        flagged, cursor = 0.0, None
        for start, end in spans:
            start = start if cursor is None else max(start, cursor)
            if end > start:
                flagged += end - start
            cursor = end if cursor is None else max(cursor, end)
        per_channel[channel] = {"flagged_s": round(flagged, 6),
                                "flagged_share": round(flagged / duration, 4) if duration > 0 else None}
    total = sum(c["flagged_s"] for c in per_channel.values())
    overall = round(total / (duration * len(channels)), 4) if duration > 0 else None
    warnings = [f"{channel} is flagged for {c['flagged_share']:.0%} of the session; event precision and "
                "recall reward long detections, so compare this with the labeled share"
                for channel, c in per_channel.items()
                if c["flagged_share"] is not None and c["flagged_share"] > LONG_ALARM_SHARE]
    return {"total_flagged_s": round(total, 6), "flagged_share_overall": overall,
            "per_channel": per_channel, "warnings": warnings}


def evaluate(events, labels, tolerance, hours):
    true_events = [e for e in events if any(overlaps(e, label, tolerance) for label in labels)]
    hits, delays = 0, []
    for label in labels:
        matched = [e for e in events if overlaps(e, label, tolerance)]
        if matched:
            hits += 1
            delays.append(round(min(e["start"] for e in matched) - label["start"], 6))
    false = len(events) - len(true_events)
    precision = len(true_events) / len(events) if events else None
    recall = hits / len(labels) if labels else None
    f1 = (2 * precision * recall / (precision + recall)
          if precision is not None and recall is not None and precision + recall > 0 else None)
    return {"detections": len(events), "true_detections": len(true_events), "false_detections": false,
            "labels_detected": hits, "labels_missed": len(labels) - hits,
            "precision": _round(precision), "recall": _round(recall), "f1": _round(f1),
            "false_alarms_per_hour": round(false / hours, 3) if hours > 0 else None,
            "detection_delay_s": {"per_detected_label": delays,
                                  "median": statistics.median(delays) if delays else None,
                                  "max": max(delays) if delays else None}}


def _round(value):
    return None if value is None else round(value, 4)


def baseline_events(params, thresholds, data, reference):
    times, values, modes = read_table(data, params["time_column"], params["channels"], params["mode_column"])
    if reference:
        _, ref_values, _ = read_table(reference, params["time_column"], params["channels"])
    else:
        ref_values = values
    events = []
    for channel in params["channels"]:
        present = [v for v in ref_values[channel] if v is not None]
        require(len(present) >= 3, f"baseline: too few values for {channel}")
        center = statistics.median(present)
        scale = max(MAD_TO_SIGMA * statistics.median(abs(v - center) for v in present), params["min_scale"])
        scores = [None if v is None else (v - center) / scale for v in values[channel]]
        events += events_from_scores(channel, times, scores, modes, thresholds[channel],
                                     params["min_duration"], params["merge_gap"])
    return times, events


def score(args):
    require(math.isfinite(args.tolerance) and args.tolerance >= 0, "--tolerance must be >= 0")
    params, thresholds, events = read_events(args.events)
    labels = read_labels(args.labels, params["channels"])
    base_thresholds = thresholds
    if args.baseline_threshold is not None:
        require(math.isfinite(args.baseline_threshold) and args.baseline_threshold > 0, "--baseline-threshold must be > 0")
        base_thresholds = {c: args.baseline_threshold for c in params["channels"]}
    times, base = baseline_events(params, base_thresholds, args.data, args.baseline_reference)
    session = session_summary(times)
    require(all(session["start"] - args.tolerance <= e["start"] and e["end"] <= session["end"] + args.tolerance
                for e in events), "events fall outside the data session; score the same session that was detected")
    hours = session["duration_s"] / 3600
    channels = params["channels"]
    expanded_labels = [
        {**label, "channel": ch}
        for label in labels
        for ch in ([label["channel"]] if label["channel"] else channels)
    ]
    labeled = coverage(expanded_labels, channels, session["duration_s"])["flagged_share_overall"]
    channelless = [{**label, "channel": "_all"} for label in labels if label["channel"] is None]
    channelless_s = coverage(channelless, ["_all"], session["duration_s"])["total_flagged_s"] if channelless else 0.0
    notes = ["Single run on the supplied data; if this run was chosen from several, disclose best-of-N.",
             "Counts matter more than ratios at small label counts."]
    if not labels:
        notes.append("No labels: recall is undefined and every detection counts as false.")
    return {"tool": "telemetry-anomalies score", "evaluation": EVALUATION, "point_adjust": False,
            "tolerance_s": args.tolerance, "session": session, "labels": len(labels),
            "labeled_share_overall": labeled, "channelless_labeled_s": channelless_s,
            "detector": {**evaluate(events, labels, args.tolerance, hours),
                         "alarm_time": coverage(events, channels, session["duration_s"])},
            "baseline": {"method": "static robust threshold, whole-session median and MAD, modes ignored",
                         "statistics_from": "baseline-reference" if args.baseline_reference else "scored data",
                         "thresholds": base_thresholds,
                         **evaluate(base, labels, args.tolerance, hours),
                         "alarm_time": coverage(base, channels, session["duration_s"])},
            "notes": notes}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("events", help="JSON written by detect.py")
    parser.add_argument("labels", help="JSON list of {start, end, channel?, kind?} in seconds")
    parser.add_argument("--data", required=True, help="the CSV that detect.py scored")
    parser.add_argument("--tolerance", type=float, default=0.0, help="seconds to widen each label on both sides")
    parser.add_argument("--baseline-threshold", type=float, help="baseline alarm level (default: detector thresholds)")
    parser.add_argument("--baseline-reference", help="known-clean CSV for baseline median and MAD")
    args = parser.parse_args()
    return emit(lambda: score(args))


if __name__ == "__main__":
    sys.exit(main())
