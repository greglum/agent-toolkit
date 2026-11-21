#!/usr/bin/env python3
"""Choose alarm thresholds on known-clean reference telemetry under a total false-alarm budget.

The budget counts events across all channels for the reference session. Every alarm on clean
data is a false alarm. The chosen threshold fits the budget and the next lower candidate does
not, re-counted with the same event rules detect.py uses. Counts are not strictly monotone in
the threshold (raising it can split one event into two), so a still lower threshold may also fit;
the search does not scan every candidate. With --per-channel, each channel
gets an equal share of the budget and its own threshold.
"""
import argparse
import math
import sys

from telemetry_core import (common_arguments, emit, events_from_scores, params_from, require,
                            score_table, session_summary)


def count_events(channels, times, modes, scored, thresholds, params):
    return {channel: len(events_from_scores(channel, times, scored[channel][0], modes, thresholds[channel],
                                            params["min_duration"], params["merge_gap"]))
            for channel in channels}


def lowest_fitting(channels, times, modes, scored, params, budget, floor):
    """Bisect for a threshold >= floor that fits the budget while the next lower candidate does not.

    Not guaranteed to be the global lowest fitting threshold, because counts are not monotone.
    """
    magnitudes = sorted({abs(s) for c in channels for s in scored[c][0] if s is not None and abs(s) >= floor})
    candidates = [floor] + magnitudes

    def total(threshold):
        return sum(count_events(channels, times, modes, scored, {c: threshold for c in channels}, params).values())

    low, high = 0, len(candidates) - 1
    if total(candidates[low]) <= budget:
        return candidates[low]
    while high - low > 1:
        middle = (low + high) // 2
        if total(candidates[middle]) <= budget:
            high = middle
        else:
            low = middle
    return candidates[high]


def calibrate(args):
    params = params_from(args)
    require(args.min_threshold is not None and math.isfinite(args.min_threshold) and args.min_threshold > 0,
            "--min-threshold must be a positive number")
    times, modes, scored = score_table(args.data, params)
    session = session_summary(times)
    hours = session["duration_s"] / 3600
    if args.alarms_per_hour is not None:
        require(args.budget is None, "give --budget or --alarms-per-hour, not both")
        require(math.isfinite(args.alarms_per_hour) and args.alarms_per_hour >= 0, "--alarms-per-hour must be >= 0")
        budget = math.floor(args.alarms_per_hour * hours)
        require(budget > 0, f"--alarms-per-hour {args.alarms_per_hour} over a {hours:.3f} h reference rounds "
                            "down to a budget of 0 alarms; use a longer reference or an explicit --budget")
    else:
        require(args.budget is not None and args.budget >= 0, "give --budget (>= 0) or --alarms-per-hour")
        budget = args.budget
    channels = params["channels"]
    if args.per_channel:
        share = budget // len(channels)
        thresholds = {c: lowest_fitting([c], times, modes, scored, params, share, args.min_threshold)
                      for c in channels}
    else:
        share = None
        shared = lowest_fitting(channels, times, modes, scored, params, budget, args.min_threshold)
        thresholds = {c: shared for c in channels}
    alarms = count_events(channels, times, modes, scored, thresholds, params)
    total = sum(alarms.values())
    require(total <= budget, "internal check failed: calibrated alarms exceed the budget")
    coverage = {c: {**scored[c][1], "alarms": alarms[c]} for c in channels}
    notes = ["All alarms on the reference are counted as false alarms; the reference must be known clean.",
             "A single reference session gives a noisy estimate of the false-alarm rate; confirm on a "
             "second clean session before relying on the threshold.",
             "Thresholds are only valid with the same params; pass this file to detect.py --calibration."]
    if budget == 0:
        notes.append("Budget 0: no alarm is allowed on the reference, so budget_used is undefined.")
    if any(t == args.min_threshold for t in thresholds.values()):
        notes.append("At least one threshold sits at --min-threshold; the budget was not the binding limit.")
    return {"tool": "telemetry-anomalies calibrate", "params": params,
            "thresholds": thresholds,
            "mode": "per-channel" if args.per_channel else "shared",
            "reference": session, "budget": {"total_alarms": budget, "per_channel_share": share,
                                             "source": "alarms_per_hour" if args.alarms_per_hour is not None else "count",
                                             "alarms_per_hour": args.alarms_per_hour,
                                             "reference_hours": round(hours, 6)},
            "alarms_total": total, "budget_used": round(total / budget, 3) if budget else None,
            "channels": coverage, "notes": notes}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    common_arguments(parser)
    parser.add_argument("--budget", type=int, help="total false alarms allowed on the reference across all channels")
    parser.add_argument("--alarms-per-hour", type=float, help="budget as alarms per hour across all channels")
    parser.add_argument("--per-channel", action="store_true", help="equal budget share and a threshold per channel")
    parser.add_argument("--min-threshold", type=float, default=3.0, help="never choose a threshold below this")
    args = parser.parse_args()
    return emit(lambda: calibrate(args))


if __name__ == "__main__":
    sys.exit(main())
