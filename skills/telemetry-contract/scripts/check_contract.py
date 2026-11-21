#!/usr/bin/env python3
"""Check a telemetry CSV against a JSON data contract. Draft a contract with infer_contract.py.

Exit 0: no findings. Exit 1: findings. Exit 2: invalid input. Output is JSON on stdout.
"""
import argparse
import csv
import json
import math
import re
import statistics
import sys
from datetime import datetime, timezone
from pathlib import Path

MISSING = ("", "na", "nan", "null", "none", "-")
TIME_SCALE = {"s": 1.0, "ms": 1e-3, "us": 1e-6, "ns": 1e-9}
CAP = 20
UNITS = {
    "pressure": {"pa": (1, 0), "kpa": (1e3, 0), "mpa": (1e6, 0), "bar": (1e5, 0),
                 "mbar": (100, 0), "psi": (6894.757, 0)},
    "temperature": {"k": (1, 0), "degc": (1, 273.15), "degf": (5 / 9, 273.15 - 32 * 5 / 9)},
    "speed": {"m/s": (1, 0), "km/h": (1 / 3.6, 0), "mph": (0.44704, 0)},
    "length": {"m": (1, 0), "mm": (1e-3, 0), "km": (1e3, 0)},
    "acceleration": {"m/s2": (1, 0), "g": (9.80665, 0)},
}
ALIASES = {"c": "degc", "°c": "degc", "deg_c": "degc", "celsius": "degc", "kelvin": "k",
           "f": "degf", "°f": "degf", "deg_f": "degf", "mps": "m/s", "m_s": "m/s",
           "kph": "km/h", "kmh": "km/h", "km_h": "km/h", "m/s^2": "m/s2"}
GENERIC = [(1000, 0), (1e-3, 0), (100, 0), (0.01, 0), (3.6, 0), (1 / 3.6, 0),
           (14.5038, 0), (1 / 14.5038, 0), (1, 273.15), (1, -273.15)]
CONTRACT_KEYS = {"status", "source", "notes", "missing_tokens", "time", "channels"}
TIME_KEYS = {"sensor", "ingest", "unit", "max_lag_s", "min_lag_s", "gap_factor", "rate_tolerance"}
CHANNEL_KEYS = {"name", "column", "unit", "unit_note", "expected_rate_hz", "min", "max", "typical_min",
                "typical_max", "saturation", "max_missing_fraction", "note", "observed"}
NUMERIC_KEYS = ("expected_rate_hz", "min", "max", "typical_min", "typical_max", "max_missing_fraction")


class InputError(ValueError):
    pass


def require(ok, message):
    if not ok:
        raise InputError(message)


def short(value):
    text = str(value)
    return text if len(text) <= 80 else text[:77] + "..."


def norm_unit(unit):
    u = unit.strip().lower().replace(" ", "")
    return ALIASES.get(u, u)


def family(unit):
    return next((f for f, members in UNITS.items() if unit in members), None)


def num(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def reject_constant(_):
    raise InputError("nonfinite JSON number")


def load_json(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"), parse_constant=reject_constant)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise InputError(f"cannot read JSON {Path(path).name}: {short(error)}")


def load_csv(path):
    try:
        with open(path, newline="", encoding="utf-8-sig") as handle:
            reader = csv.reader(handle)
            header = next(reader, None)
            rows = list(reader)
    except (OSError, UnicodeDecodeError, csv.Error) as error:
        raise InputError(f"cannot read CSV {Path(path).name}: {short(error)}")
    require(header and all(h.strip() for h in header), "CSV needs a header with nonempty names")
    header = [h.strip() for h in header]
    require(len(set(header)) == len(header), "CSV header has duplicate column names")
    require(all(len(r) == len(header) for r in rows), "CSV rows must match the header width")
    return header, rows


def parse_time(raw, unit):
    raw = raw.strip()
    if unit == "iso8601":
        try:
            stamp = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        except ValueError:
            return None
        if stamp.tzinfo is None:
            stamp = stamp.replace(tzinfo=timezone.utc)
        return stamp.timestamp()
    try:
        value = float(raw)
    except ValueError:
        return None
    return value * TIME_SCALE[unit] if math.isfinite(value) else None


def unknown(obj, allowed, label):
    extra = sorted(set(obj) - allowed)
    require(not extra, f"{label}: unknown keys {[short(k) for k in extra]}")


def validate(contract):
    require(isinstance(contract, dict), "contract must be a JSON object")
    unknown(contract, CONTRACT_KEYS, "contract")
    require(contract.get("status") in ("draft", "confirmed"), "contract: status must be draft or confirmed")
    time = contract.get("time")
    require(isinstance(time, dict) and isinstance(time.get("sensor"), str), "contract: time.sensor is required")
    unknown(time, TIME_KEYS, "time")
    require(time.get("unit", "s") in [*TIME_SCALE, "iso8601"], "time.unit must be s, ms, us, ns or iso8601")
    for key in TIME_KEYS - {"sensor", "ingest", "unit"}:
        require(time.get(key) is None or num(time[key]), f"time.{key} must be a number or null")
    if time.get("gap_factor") is not None:
        require(time["gap_factor"] > 0, "time.gap_factor must be positive")
    if time.get("rate_tolerance") is not None:
        require(time["rate_tolerance"] >= 0, "time.rate_tolerance must be nonnegative")
    channels = contract.get("channels")
    require(isinstance(channels, list) and channels, "contract: channels must be a nonempty list")
    names = set()
    for index, ch in enumerate(channels, 1):
        label = f"channel {index}"
        require(isinstance(ch, dict) and isinstance(ch.get("name"), str) and ch["name"], label + ": name required")
        require(ch["name"] not in names, label + ": duplicate channel name")
        names.add(ch["name"])
        unknown(ch, CHANNEL_KEYS, label)
        rate_hz = ch.get("expected_rate_hz")
        require(rate_hz is None or (num(rate_hz) and rate_hz > 0), label + ": expected_rate_hz must be positive")
        require(ch.get("unit") is None or isinstance(ch["unit"], str), label + ": unit must be text or null")
        for key in NUMERIC_KEYS:
            require(ch.get(key) is None or num(ch[key]), f"{label}: {key} must be a number or null")
        frac = ch.get("max_missing_fraction")
        if frac is not None:
            require(0 <= frac <= 1, f"{label}: max_missing_fraction must be between 0 and 1")
        sat = ch.get("saturation") or []
        require(isinstance(sat, list) and all(num(v) for v in sat), label + ": saturation must list numbers")
    tokens = contract.get("missing_tokens", list(MISSING))
    require(isinstance(tokens, list) and all(isinstance(t, str) for t in tokens), "missing_tokens must be text")
    return contract


def header_unit(col, name):
    """Unit written after the channel name in a header: name[bar], name (bar) or name_bar."""
    if not col.startswith(name) or col == name:
        return None
    rest = col[len(name):].strip()
    match = re.fullmatch(r"\[(.+)\]|\((.+)\)", rest)
    if match:
        return (match.group(1) or match.group(2)).strip()
    if rest.startswith("_") and family(norm_unit(rest[1:])):
        return rest[1:]
    return None


def find_column(header, ch):
    if ch.get("column"):
        col = ch["column"]
        return (col, header_unit(col, ch["name"])) if col in header else (None, None)
    if ch["name"] in header:
        return ch["name"], None
    for col in header:
        unit = header_unit(col, ch["name"])
        if unit:
            return col, unit
    return None, None


def scale_candidates(median, declared, low, high):
    found = []
    fam = family(declared) if declared else None
    if fam:
        a_to, b_to = UNITS[fam][declared]
        for source, (a, b) in UNITS[fam].items():
            converted = (a * median + b - b_to) / a_to
            if source != declared and low <= converted <= high:
                found.append({"recorded_as": source, "declared": declared, "converted_median": round(converted, 4)})
        return found
    for factor, offset in GENERIC:
        converted = median * factor + offset
        if low <= converted <= high:
            found.append({"factor": round(factor, 6), "offset": offset, "converted_median": round(converted, 4)})
    return found


def rate(stamps):
    deltas = [b - a for a, b in zip(stamps, stamps[1:]) if b > a]
    return 1 / statistics.median(deltas) if deltas else None


def rounded(value, places=4):
    return round(value, places) if value is not None else None


def check_time(contract, header, rows, findings, period):
    time = contract["time"]
    unit = time.get("unit", "s")
    require(time["sensor"] in header, f"sensor time column {short(time['sensor'])} is not in the CSV")
    ingest = time.get("ingest")
    require(ingest is None or ingest in header, f"ingest time column {short(ingest)} is not in the CSV")
    s_idx = header.index(time["sensor"])
    stamps, bad, regressions, latest = [], [], [], None
    for line, row in enumerate(rows, 2):
        t = parse_time(row[s_idx], unit)
        stamps.append(t)
        if t is None:
            bad.append(line)
            continue
        if latest is not None and t < latest:
            regressions.append({"line": line, "time": t, "latest_before": latest})
        latest = t if latest is None else max(latest, t)
    good = [t for t in stamps if t is not None]
    unique = sorted(set(good))
    dupes = len(good) - len(unique)
    observed = rate(unique)
    summary = {"rows": len(rows), "unparseable_sensor_time": len(bad), "regressions": len(regressions),
               "duplicate_timestamps": dupes, "observed_rate_hz": rounded(observed)}
    if bad:
        findings.append({"check": "time_unparseable", "severity": "high", "count": len(bad), "lines": bad[:CAP]})
    if regressions:
        findings.append({"check": "time_non_monotonic", "severity": "high", "count": len(regressions),
                         "examples": regressions[:CAP]})
    if dupes:
        findings.append({"check": "time_duplicate", "severity": "medium", "count": dupes})
    step = period or (1 / observed if observed else None)
    if step:
        gap_factor = 3 if time.get("gap_factor") is None else time["gap_factor"]
        threshold = round(gap_factor * step, 6)
        gaps = [{"start": a, "end": b, "seconds": round(b - a, 6)}
                for a, b in zip(unique, unique[1:]) if b - a > threshold]
        summary["gap_threshold_s"] = threshold
        if gaps:
            findings.append({"check": "time_gap", "severity": "medium", "count": len(gaps),
                             "threshold_s": threshold, "gaps": gaps[:CAP]})
    if ingest:
        i_idx = header.index(ingest)
        lags, unparsed = [], 0
        for t, row in zip(stamps, rows):
            i = parse_time(row[i_idx], unit)
            if i is None:
                unparsed += 1
            elif t is not None:
                lags.append(i - t)
        summary["lag_s"] = ({"min": round(min(lags), 6), "median": round(statistics.median(lags), 6),
                             "max": round(max(lags), 6)} if lags else None)
        if unparsed:
            findings.append({"check": "ingest_time_unparseable", "severity": "medium", "count": unparsed})
        min_lag = 0 if time.get("min_lag_s") is None else time["min_lag_s"]
        max_lag = time.get("max_lag_s")
        early = [lag for lag in lags if lag < min_lag]
        late = [lag for lag in lags if max_lag is not None and lag > max_lag]
        if early:
            findings.append({"check": "lag_negative", "severity": "high", "count": len(early),
                             "min_lag_s": round(min(early), 6),
                             "meaning": "ingest before sensor time: clock skew or a time zone error"})
        if late:
            findings.append({"check": "lag_late", "severity": "medium", "count": len(late),
                             "max_lag_s": round(max(late), 6), "meaning": "late-arriving or backfilled rows"})
    return stamps, summary


def check_channel(ch, header, rows, stamps, tokens, metadata, tolerance, findings):
    name = ch["name"]

    def add(check, severity, **extra):
        findings.append({"channel": name, "check": check, "severity": severity, **extra})

    col, head_unit = find_column(header, ch)
    out = {"column": short(col) if col else None, "declared_unit": ch.get("unit")}
    if col is None:
        add("channel_absent", "high", detail="no CSV column matches this channel")
        return out
    declared = norm_unit(ch["unit"]) if ch.get("unit") else None
    source_unit = metadata.get(col) or head_unit
    out["source_unit"] = short(source_unit) if source_unit else None
    if declared is None:
        add("unit_undeclared", "high", detail="contract has no unit; confirm it with the owner")
    elif source_unit and norm_unit(source_unit) != declared:
        fam = family(declared)
        add("unit_mismatch", "high", source_unit=short(source_unit), declared_unit=ch["unit"],
            same_family=fam is not None and family(norm_unit(source_unit)) == fam)
    idx = header.index(col)
    sat = set(ch.get("saturation") or [])
    low, high = ch.get("min"), ch.get("max")
    counts = {"missing": 0, "unparseable": 0, "saturated": 0, "zero": 0, "out_of_range": 0, "valid_nonzero": 0}
    present, values, range_lines = [], [], []
    for line, (row, t) in enumerate(zip(rows, stamps), 2):
        raw = row[idx].strip()
        if raw.lower() in tokens:
            counts["missing"] += 1
            continue
        try:
            value = float(raw)
        except ValueError:
            value = math.nan
        if not math.isfinite(value):
            counts["unparseable"] += 1
            continue
        if t is not None:
            present.append(t)
        if value in sat:
            counts["saturated"] += 1
        elif value == 0:
            counts["zero"] += 1
        elif (low is not None and value < low) or (high is not None and value > high):
            counts["out_of_range"] += 1
            range_lines.append(line)
        else:
            counts["valid_nonzero"] += 1
            values.append(value)
    out["counts"] = counts
    if counts["valid_nonzero"] + counts["zero"] == 0:
        add("no_valid_samples", "high", detail="no in-range readings; nothing to analyze")
    allowed = ch.get("max_missing_fraction")
    fraction = counts["missing"] / (len(rows) or 1)
    if allowed is not None and fraction > allowed:
        add("missing_over_allowed", "medium", fraction=round(fraction, 6), allowed=allowed)
    if counts["unparseable"]:
        add("unparseable_values", "medium", count=counts["unparseable"])
    if counts["saturated"]:
        add("saturated", "medium", count=counts["saturated"], sentinels=sorted(sat))
    if counts["zero"] and ((low is not None and low > 0) or (high is not None and high < 0)):
        add("zero_outside_range", "medium", count=counts["zero"], detail="zero is outside min/max; maybe a dropout code")
    if counts["out_of_range"]:
        add("out_of_range", "medium", count=counts["out_of_range"], lines=range_lines[:CAP])
    if values:
        median = statistics.median(values)
        out["median_valid_nonzero"] = round(median, 6)
        t_low = ch["typical_min"] if ch.get("typical_min") is not None else low
        t_high = ch["typical_max"] if ch.get("typical_max") is not None else high
        if t_low is not None and t_high is not None and not t_low <= median <= t_high:
            add("unit_scale_suspicion", "high", median=round(median, 6), plausible=[t_low, t_high],
                candidates=scale_candidates(median, declared, t_low, t_high),
                detail="median of in-range nonzero values is outside the plausible range; a suspicion, not proof")
    present = sorted(set(present))
    expected, observed = ch.get("expected_rate_hz"), rate(present)
    out["observed_rate_hz"] = rounded(observed)
    if expected and observed:
        half = len(present) // 2
        halves = [rate(present[:half + 1]), rate(present[half:])]
        out["observed_rate_by_half_hz"] = [rounded(h) for h in halves]
        worst = max(abs(r - expected) / expected for r in [observed, *halves] if r)
        if worst > tolerance:
            add("rate_mismatch", "medium", expected_hz=expected, observed_hz=out["observed_rate_hz"],
                by_half_hz=out["observed_rate_by_half_hz"], tolerance=tolerance)
    return out


def check(args):
    contract = validate(load_json(args.contract))
    header, rows = load_csv(args.data)
    metadata = load_json(args.units) if args.units else {}
    require(isinstance(metadata, dict) and all(isinstance(v, str) for v in metadata.values()),
            "units metadata must map column names to unit text")
    tokens = {t.strip().lower() for t in contract.get("missing_tokens", list(MISSING))}
    findings = []
    if contract["status"] != "confirmed":
        findings.append({"check": "contract_not_confirmed", "severity": "high",
                         "detail": "draft contract; an owner must confirm units and limits"})
    if not rows:
        findings.append({"check": "no_data_rows", "severity": "high", "detail": "CSV has a header only"})
    rates = [c["expected_rate_hz"] for c in contract["channels"] if c.get("expected_rate_hz")]
    stamps, time_summary = check_time(contract, header, rows, findings, 1 / max(rates) if rates else None)
    tolerance = 0.05 if contract["time"].get("rate_tolerance") is None else contract["time"]["rate_tolerance"]
    channels = {c["name"]: check_channel(c, header, rows, stamps, tokens, metadata, tolerance, findings)
                for c in contract["channels"]}
    used = {contract["time"]["sensor"], contract["time"].get("ingest")}
    used |= {find_column(header, c)[0] for c in contract["channels"]}
    return {"contract_status": contract["status"], "time": time_summary, "channels": channels,
            "undeclared_columns": [short(h) for h in header if h not in used], "findings": findings,
            "limits": ["Unit-scale and rate checks are heuristics; confirm units with the owner.",
                       "Counts are per row; mixed-rate wide files inflate missing counts.",
                       "Naive ISO 8601 times are read as UTC."]}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("contract")
    parser.add_argument("data")
    parser.add_argument("--units", help="JSON mapping column name to the unit recorded at the source")
    args = parser.parse_args(argv)
    try:
        result = check(args)
    except InputError as error:
        print(json.dumps({"error": str(error)}), file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2))
    return 1 if result["findings"] else 0


if __name__ == "__main__":
    sys.exit(main())
