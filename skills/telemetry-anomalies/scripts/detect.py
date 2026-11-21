#!/usr/bin/env python3
"""Flag anomaly events in multichannel telemetry with a per-mode trailing robust z-score.

Give either --threshold or --calibration (the JSON written by calibrate.py). A calibration
file fixes every scoring option, so scoring options may not be repeated with it.
"""
import argparse
import json
import sys
from pathlib import Path

from telemetry_core import (InputError, check_params, check_thresholds, common_arguments, emit, events_from_scores,
                            given_scoring_options, params_from, require, score_table, session_summary)


def thresholds_from(args):
    if args.calibration:
        require(args.threshold is None, "give --threshold or --calibration, not both")
        given = given_scoring_options(args)
        require(not given, "--calibration fixes the scoring options; drop: " + ", ".join(given))
        calibration = json.loads(Path(args.calibration).read_text(encoding="utf-8"))
        require(isinstance(calibration, dict), "calibration: expected a JSON object")
        params = check_params(calibration.get("params"))
        return params, check_thresholds(calibration.get("thresholds"), params["channels"])
    require(args.threshold is not None, "give --threshold or --calibration")
    params = params_from(args)
    return params, {channel: args.threshold for channel in params["channels"]}


def detect(args):
    params, thresholds = thresholds_from(args)
    check_thresholds(thresholds, params["channels"])
    times, modes, scored = score_table(args.data, params)
    events, coverage = [], {}
    for channel in params["channels"]:
        scores, counts = scored[channel]
        found = events_from_scores(channel, times, scores, modes, thresholds[channel],
                                   params["min_duration"], params["merge_gap"])
        events.extend(found)
        coverage[channel] = {**counts, "events": len(found)}
    events.sort(key=lambda event: (event["start"], event["channel"]))
    notes = ["Scores compare each sample with earlier samples of the same mode only.",
             "A drift slower than the window is absorbed by the baseline; use a change-point "
             "or physics-residual method for slow drift."]
    if not params["mode_column"]:
        notes.append("No mode column: operating-mode changes are scored and may appear as anomalies.")
    session = session_summary(times)
    hours = session["duration_s"] / 3600
    return {"tool": "telemetry-anomalies detect", "params": params, "thresholds": thresholds,
            "session": session, "total_events": len(events),
            "events_per_hour": round(len(events) / hours, 3) if hours > 0 else None,
            "channels": coverage, "events": events, "notes": notes}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    common_arguments(parser)
    parser.add_argument("--threshold", type=float, help="alarm when |score| exceeds this value")
    parser.add_argument("--calibration", help="JSON from calibrate.py")
    args = parser.parse_args()
    return emit(lambda: detect(args))


if __name__ == "__main__":
    sys.exit(main())
