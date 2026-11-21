#!/usr/bin/env python3
"""Draft a telemetry data contract from a sample CSV. Units are never guessed.

Exit 0: draft written to stdout. Exit 2: invalid input.
"""
import argparse
import json
import math
import re
import statistics
import sys

from check_contract import (MISSING, TIME_SCALE, InputError, family, load_csv, norm_unit, parse_time,
                            rate, require, rounded, short)

SENTINELS = (65535, 32767, 4095, -999, 9999)


def split_unit(col):
    """Split a header into (name, unit hint): name[bar], name (bar) or name_bar."""
    match = re.fullmatch(r"(.+?)\s*(?:\[([^\]]+)\]|\(([^)]+)\))", col)
    if match:
        return match.group(1), (match.group(2) or match.group(3)).strip()
    base, _, tail = col.rpartition("_")
    if base and family(norm_unit(tail)):
        return base, tail
    return col, None


def infer(args):
    header, rows = load_csv(args.data)
    require(rows, "CSV has no data rows")
    require(args.sensor_time in header, "sensor time column is not in the CSV")
    require(args.ingest_time is None or args.ingest_time in header, "ingest time column is not in the CSV")
    s_idx = header.index(args.sensor_time)
    stamps = [parse_time(r[s_idx], args.time_unit) for r in rows]
    channels, skipped = [], []
    for idx, col in enumerate(header):
        if col in (args.sensor_time, args.ingest_time):
            continue
        values, present, missing, other = [], [], 0, 0
        for row, t in zip(rows, stamps):
            raw = row[idx].strip()
            if raw.lower() in MISSING:
                missing += 1
                continue
            try:
                value = float(raw)
            except ValueError:
                other += 1
                continue
            if math.isfinite(value):
                values.append(value)
                if t is not None:
                    present.append(t)
        if not values:
            skipped.append(short(col))
            continue
        name, hint = split_unit(col)
        repeats = sorted({v for v in (min(values), max(values), *SENTINELS)
                          if values.count(v) > max(2, 0.01 * len(values))})
        channels.append({
            "name": short(name), "column": short(col), "unit": None,
            "unit_note": "Not inferred. Confirm with the owning spec or a person."
                         + (f" Header suffix suggests {short(hint)}; check it." if hint else ""),
            "expected_rate_hz": None, "min": None, "max": None, "saturation": [],
            "max_missing_fraction": None,
            "observed": {"rate_hz": rounded(rate(sorted(set(present)))), "min": min(values),
                         "max": max(values), "median": statistics.median(values),
                         "missing_fraction": round(missing / len(rows), 6),
                         "zero_count": values.count(0), "non_numeric_count": other,
                         "repeated_extremes_or_sentinels": repeats}})
    return {"status": "draft", "source": "inferred from a sample; not confirmed",
            "time": {"sensor": args.sensor_time, "ingest": args.ingest_time, "unit": args.time_unit,
                     "max_lag_s": None, "gap_factor": 3, "rate_tolerance": 0.05},
            "channels": channels, "notes": {"skipped_non_numeric_columns": skipped}}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("data")
    parser.add_argument("--sensor-time", required=True)
    parser.add_argument("--ingest-time")
    parser.add_argument("--time-unit", default="s", choices=[*TIME_SCALE, "iso8601"])
    args = parser.parse_args(argv)
    try:
        result = infer(args)
    except InputError as error:
        print(json.dumps({"error": str(error)}), file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
