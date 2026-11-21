# 0027: Preserve Unrounded Calibration Thresholds, Strict Upper Bounds, and Nanosecond Duration Rounding

- Status: Accepted
- Date: 2026-11-20

## Context

telemetry-anomalies calibrates alarm thresholds via binary search against a fixed alarm budget and filters events by minimum duration on floating-point timestamps.

## Decision

Include all observed score magnitudes so strict |score| > threshold guarantees the highest candidate yields zero alarms; emit calibrated thresholds unrounded so display rounding down cannot add alarms; and round elapsed durations to 9 decimal places so exact min_duration boundaries (such as 1.2 - 1.0) are not dropped by IEEE-754 representation error.

## Consequences

Replaying calibrated thresholds reproduces the budgeted alarm count deterministically and exact-duration events are never silently lost.

## Code References

- `skills/telemetry-anomalies/scripts/calibrate.py:31`
- `skills/telemetry-anomalies/scripts/calibrate.py:87`
- `skills/telemetry-anomalies/scripts/telemetry_core.py:141`
