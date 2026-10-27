#!/usr/bin/env python3
"""Score each post against the same account's other posts in a matched cohort.

Reads a CSV of public post metrics (see references/input.md) and writes lift.json and
lift.md into a new directory. Offline, standard library only. Lift is descriptive: it
says a post did unusually well for that account, not why, and never ranks accounts.
"""

import argparse
import csv
import hashlib
import io
import json
import math
import re
import sys
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from statistics import median

COLUMNS = ["account", "platform", "format", "post_id", "url", "published_at", "observed_at", "age_window", "metric",
           "value", "status", "source"]
COHORT = ("platform", "account", "format", "metric", "age_window")
MIN_PEERS = 3
WINDOW_RE = re.compile(r"^([1-9][0-9]*)([hd])$")
TIME_RE = re.compile(r"^([0-9]{4})-([0-9]{2})-([0-9]{2})(?:T([0-9]{2}):([0-9]{2})(?::([0-9]{2}))?)?Z?$")
SOURCES = ("export", "api", "page")


def safe(text):
    """Neutralize spreadsheet formulas and Markdown table breaks in untrusted text."""
    text = " ".join(str(text).split())
    if text[:1] in ("=", "+", "-", "@"):
        text = "'" + text
    return text


def parse_time(text):
    """Parse YYYY-MM-DD[THH:MM[:SS]][Z] as UTC, the same on every Python version."""
    match = TIME_RE.match(text)
    if not match:
        raise ValueError("not YYYY-MM-DD[THH:MM[:SS]][Z]")
    return datetime(*(int(part or 0) for part in match.groups()))


def md(text):
    return re.sub(r"([|\[\]`<>*_\\])", r"\\\1", safe(text))


def parse_row(n, raw):
    label = f"row {n}"
    row = {key: (raw[key] or "").strip() for key in COLUMNS}
    for key in COLUMNS:
        if key != "value" and not row[key]:
            raise ValueError(f"{label}: {key} is empty")
    for key in ("platform", "format"):
        if row[key] != row[key].lower():
            raise ValueError(f"{label}: {key} must be lowercase")
    if not row["url"].startswith("https://"):
        raise ValueError(f"{label}: url must be a public https locator")
    times = {}
    for key in ("published_at", "observed_at"):
        try:
            times[key] = parse_time(row[key])
        except ValueError:
            raise ValueError(f"{label}: {key} must be YYYY-MM-DD[THH:MM[:SS]][Z]") from None
    if times["observed_at"] < times["published_at"]:
        raise ValueError(f"{label}: observed_at precedes published_at")
    window = WINDOW_RE.match(row["age_window"])
    if not window:
        raise ValueError(f"{label}: age_window must be a fixed window like 48h or 7d, not lifetime")
    hours = int(window[1]) * (24 if window[2] == "d" else 1)
    row["age_window"] = f"{hours}h"
    if row["status"] not in ("complete", "partial", "unavailable"):
        raise ValueError(f"{label}: status must be complete, partial or unavailable")
    if row["source"] not in SOURCES:
        raise ValueError(f"{label}: source must be export, api or page")
    if row["status"] == "complete":
        try:
            # A date-only publication time could be as late as the end of that day.
            late = timedelta(days=0 if "T" in row["published_at"] else 1)
            end = times["published_at"] + late + timedelta(hours=hours)
        except OverflowError:
            raise ValueError(f"{label}: age_window exceeds the date range") from None
        if times["observed_at"] < end:
            raise ValueError(f"{label}: the age window had not elapsed at observed_at; mark the row partial")
    if row["status"] == "unavailable":
        if row["value"]:
            raise ValueError(f"{label}: unavailable rows leave value empty")
        row["value"] = None
    else:
        try:
            value = float(row["value"])
        except ValueError:
            raise ValueError(f"{label}: value must be a number") from None
        if not math.isfinite(value) or value < 0:
            raise ValueError(f"{label}: value must be a finite nonnegative number")
        row["value"] = int(value) if value.is_integer() else value
    row["row"] = n
    return row


def read_rows(raw_text):
    reader = csv.DictReader(io.StringIO(raw_text, newline=""))
    if reader.fieldnames is None or sorted(reader.fieldnames) != sorted(COLUMNS):
        raise ValueError("header must be exactly: " + ",".join(COLUMNS))
    rows, seen = [], set()
    for n, raw in enumerate(reader, start=2):
        if None in raw or None in raw.values():
            raise ValueError(f"row {n}: wrong number of cells")
        row = parse_row(n, raw)
        key = tuple(row[k] for k in COHORT) + (row["post_id"],)
        if key in seen:
            raise ValueError(f"row {n}: duplicate post in the same cohort")
        seen.add(key)
        rows.append(row)
    return rows


def score(rows):
    groups = defaultdict(list)
    for row in rows:
        groups[tuple(row[k] for k in COHORT)].append(row)
    cohorts = []
    for key in sorted(groups):
        members = groups[key]
        complete = [r for r in members if r["status"] == "complete"]
        for row in members:
            peers = [r["value"] for r in complete if r is not row]
            base = median(peers) if len(peers) >= MIN_PEERS else None
            reason = None
            if row["status"] != "complete":
                reason = f"status {row['status']}"
            elif base is None:
                reason = f"fewer than {MIN_PEERS} comparable peers"
            elif base == 0:
                reason = "zero peer median"
            row.update(peer_count=len(peers), peer_median=base,
                       lift=round(row["value"] / base, 4) if reason is None else None, excluded=reason)
        members.sort(key=lambda r: (r["lift"] is None, -(r["lift"] or 0), r["row"]))
        counts = {s: sum(r["status"] == s for r in members) for s in ("complete", "partial", "unavailable")}
        cohorts.append({"cohort": dict(zip(COHORT, key)), "total": len(members), **counts,
                        "scored": sum(r["lift"] is not None for r in members), "rows": members})
    return cohorts


def render(cohorts, total, top, digest):
    lines = ["# Lift by account cohort", "",
             f"Input rows: {total}. Input SHA-256: {digest}.",
             "Lift = value / median of the same account's other complete posts in the same platform, "
             "format, metric and age window. Descriptive only; never compare lift or raw values across accounts.", ""]
    for c in cohorts:
        head = ", ".join(f"{k}={md(v)}" for k, v in c["cohort"].items())
        scored = [r for r in c["rows"] if r["lift"] is not None]
        shown = scored if top is None else scored[:top]
        lines += [f"## {head}", "",
                  f"Rows: {c['total']} (complete {c['complete']}, partial {c['partial']}, "
                  f"unavailable {c['unavailable']}); scored {c['scored']}; showing {len(shown)} of {len(scored)} scored.", ""]
        if shown:
            lines += ["| post_id | value | peer median | peers | lift | source | url |",
                      "| --- | --- | --- | --- | --- | --- | --- |"]
            lines += [f"| {md(r['post_id'])} | {r['value']} | {r['peer_median']} | {r['peer_count']} | {r['lift']:.2f}x "
                      f"| {md(r['source'])} | {md(r['url'])} |" for r in shown]
            lines.append("")
        excluded = [r for r in c["rows"] if r["lift"] is None]
        if excluded:
            lines += ["Not scored (kept visible):", ""]
            lines += [f"- {md(r['post_id'])}: value {r['value'] if r['value'] is not None else 'none'}; "
                      f"{r['excluded']}; peers {r['peer_count']}; {md(r['source'])}; {md(r['url'])}" for r in excluded]
            lines.append("")
    if not cohorts:
        lines += ["No rows. Insufficient evidence.", ""]
    return "\n".join(lines)


def build(input_path, out, top=None):
    raw = input_path.read_bytes()
    rows = read_rows(raw.decode("utf-8-sig"))
    cohorts = score(rows)
    digest = hashlib.sha256(raw).hexdigest()
    report = {"input_sha256": digest, "input_rows": len(rows), "min_peers": MIN_PEERS, "cohorts": cohorts}
    text_json = json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
    text_md = render(cohorts, len(rows), top, digest)
    out.mkdir(parents=True, exist_ok=False)
    (out / "lift.json").write_text(text_json, encoding="utf-8")
    (out / "lift.md").write_text(text_md, encoding="utf-8")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="CSV in the documented column contract")
    parser.add_argument("--out", type=Path, required=True, help="new directory; an existing path is refused")
    parser.add_argument("--top", type=int, help="scored rows to show per cohort in lift.md; totals and JSON keep all")
    args = parser.parse_args()
    if args.top is not None and args.top < 1:
        parser.error("--top must be at least 1")
    try:
        report = build(args.input, args.out, args.top)
    except (ValueError, OSError, csv.Error, UnicodeDecodeError) as exc:
        print(f"Not scored: {exc}", file=sys.stderr)
        return 1
    scored = sum(c["scored"] for c in report["cohorts"])
    print(f"Wrote {args.out}: {report['input_rows']} rows, {len(report['cohorts'])} cohorts, {scored} scored.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
