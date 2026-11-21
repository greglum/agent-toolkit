#!/usr/bin/env python3
"""Plan rolling-origin folds by group and audit fold assignments for temporal leakage.

plan:  rows CSV -> fold assignments CSV (--out) and a JSON summary on stdout. Exit 0 or 2.
audit: assignments CSV + contract JSON -> JSON findings on stdout.
       Exit 0 when no findings, 1 on findings, 2 on invalid input.
"""
import argparse
import csv
import json
import math
from datetime import datetime, timezone
from pathlib import Path
import sys

SPLITS = ("train", "test", "purged", "embargo", "future")
AVAILABLE = "__available_at"
CONTRACT_FIELDS = {"schema_version", "unit", "hierarchy", "prediction_time", "label_horizon", "label_horizon_time",
                   "group_key", "forward_only", "embargo_time", "features", "regime_breaks"}
EXAMPLES = 5
MIN_RUNS_SIDE = 5


class InputError(ValueError):
    pass


class Parser(argparse.ArgumentParser):
    def error(self, message):
        self.exit(2, json.dumps({"error": "invalid arguments: " + message}) + "\n")


def require(condition, message):
    if not condition:
        raise InputError(message)


class Clock:
    """Parse every time in one run with one representation: numbers, or ISO 8601 all aware or all naive."""

    def __init__(self):
        self.kind = None

    def parse(self, value, label):
        require(isinstance(value, (str, int, float)) and not isinstance(value, bool) and str(value).strip(),
                label + ": missing time")
        text = str(value).strip()
        try:
            number, kind = float(text), "number"
        except ValueError:
            try:
                moment = datetime.fromisoformat(text[:-1] + "+00:00" if text.endswith("Z") else text)
            except ValueError:
                raise InputError(label + ": not a number or ISO 8601 time") from None
            kind = "naive" if moment.tzinfo is None else "aware"
            number = (moment.replace(tzinfo=timezone.utc) if kind == "naive" else moment).timestamp()
        require(math.isfinite(number), label + ": nonfinite time")
        require(self.kind in (None, kind), label + ": mixes numeric, naive and timezone-aware times")
        self.kind = kind
        return number

    def format(self, number):
        if self.kind == "number":
            return repr(number)
        moment = datetime.fromtimestamp(number, timezone.utc)
        return moment.replace(tzinfo=None).isoformat() if self.kind == "naive" else \
            moment.isoformat().replace("+00:00", "Z")


def read_rows(path, required):
    try:
        with open(path, newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            columns = reader.fieldnames or []
            rows = list(reader)
    except (OSError, UnicodeError, csv.Error):
        raise InputError("cannot read a valid UTF-8 CSV file: " + Path(path).name) from None
    require(len(columns) == len(set(columns)), "duplicate CSV column names")
    missing = [c for c in required if c not in columns]
    require(not missing, "missing required columns: " + ", ".join(missing))
    require(rows, "no data rows")
    for number, row in enumerate(rows, 2):
        require(None not in row and all(v is not None for v in row.values()),
                "line %d: wrong number of fields" % number)
    return columns, rows


def times(rows, clock, horizon=None):
    """Attach parsed prediction and label-end times. An empty label_end_time is an error
    unless a horizon is given, which then sets label_end_time = prediction_time + horizon."""
    for row in rows:
        rid = row["row_id"]
        require(rid.strip() and row["group"].strip(), "empty row_id or group")
        row["_pt"] = clock.parse(row["prediction_time"], "row %s prediction_time" % rid)
        end = (row.get("label_end_time") or "").strip()
        if end:
            row["_le"] = clock.parse(end, "row %s label_end_time" % rid)
        else:
            require(horizon is not None, "row %s: empty label_end_time; supply it or pass --label-horizon" % rid)
            row["_le"] = row["_pt"] + horizon
            row["label_end_time"] = clock.format(row["_le"])
        require(row["_le"] >= row["_pt"], "row %s: label_end_time precedes prediction_time" % rid)


def overlaps(row, start, end):
    """Label window (pt, le] meets test period [start, end): the one predicate for purge and audit."""
    return row["_le"] > start and row["_pt"] < end


def test_period(test_rows):
    return min(r["_pt"] for r in test_rows), max(r["_le"] for r in test_rows)


def plan(args):
    clock = Clock()
    columns, rows = read_rows(args.rows, ("row_id", "group", "prediction_time"))
    require(not {"fold", "split"} & set(columns), "input already has fold or split columns")
    require(len({r["row_id"] for r in rows}) == len(rows), "duplicate row_id")
    require(args.label_horizon is None or (math.isfinite(args.label_horizon) and args.label_horizon >= 0),
            "label-horizon must be finite and nonnegative")
    times(rows, clock, args.label_horizon)
    require(args.folds >= 1 and args.test_groups >= 1 and args.embargo_groups >= 0,
            "folds and test-groups must be positive; embargo-groups nonnegative")
    require(args.embargo_time >= 0 and math.isfinite(args.embargo_time), "embargo-time must be finite and nonnegative")
    require(args.window == "expanding" or (args.max_train_groups or 0) >= 1,
            "a sliding window needs --max-train-groups")
    by_group = {}
    for row in rows:
        by_group.setdefault(row["group"], []).append(row)
    order = sorted(by_group, key=lambda g: (min(r["_pt"] for r in by_group[g]), g))
    needed = args.folds * args.test_groups + args.embargo_groups + 1
    require(len(order) >= needed, "need at least %d groups, found %d" % (needed, len(order)))

    out_columns = [c for c in columns if c != "label_end_time"] + ["label_end_time", "fold", "split"]
    output, folds = [], []
    for fold in range(args.folds):
        first = len(order) - (args.folds - fold) * args.test_groups
        test_groups = order[first:first + args.test_groups]
        embargo_groups = order[max(0, first - args.embargo_groups):first]
        train_groups = order[:first - args.embargo_groups]
        if args.window == "sliding":
            train_groups = train_groups[-args.max_train_groups:]
        test_rows = [r for g in test_groups for r in by_group[g]]
        start, end = test_period(test_rows)
        counts = dict.fromkeys(SPLITS, 0)

        def emit(row, split):
            counts[split] += 1
            record = {c: row.get(c, "") for c in columns}
            record["label_end_time"] = row["label_end_time"]
            output.append({**record, "fold": str(fold), "split": split})

        for group in train_groups:
            for row in by_group[group]:
                if row["_pt"] >= start:
                    emit(row, "future")
                elif args.purge and overlaps(row, start, end):
                    emit(row, "purged")
                elif args.embargo_time and row["_pt"] >= start - args.embargo_time:
                    emit(row, "embargo")
                else:
                    emit(row, "train")
        for group in embargo_groups:
            for row in by_group[group]:
                emit(row, "embargo")
        for row in test_rows:
            emit(row, "test")
        require(counts["train"] > 0, "fold %d has no train rows after purge and embargo" % fold)
        folds.append({"fold": fold, "train_groups": train_groups, "embargo_groups": embargo_groups,
                      "test_groups": test_groups, "rows": counts})

    try:
        with open(args.out, "w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=out_columns)
            writer.writeheader()
            writer.writerows(output)
    except OSError:
        raise InputError("cannot write --out file") from None
    return {
        "command": "plan",
        "settings": {"folds": args.folds, "test_groups": args.test_groups, "window": args.window,
                     "max_train_groups": args.max_train_groups, "purge": args.purge,
                     "embargo_groups": args.embargo_groups, "embargo_time": args.embargo_time},
        "groups": len(order), "rows": len(rows), "time_kind": clock.kind, "folds": folds,
        "notes": ["Folds are forward only: train groups precede test groups in time order.",
                  "Embargo excludes train rows within embargo-time before the test start "
                  "and the embargo-groups immediately before the test groups.",
                  "Rows not assigned to train or test are kept with their split label for audit."],
    }


def load_contract(path, clock):
    def unique(pairs):
        keys = [k for k, _ in pairs]
        require(len(keys) == len(set(keys)), "contract: duplicate key")
        return dict(pairs)

    def reject(_):
        raise InputError("contract: nonfinite number")

    try:
        contract = json.loads(Path(path).read_text(encoding="utf-8"), object_pairs_hook=unique,
                              parse_constant=reject)
    except (OSError, UnicodeError, json.JSONDecodeError):
        raise InputError("cannot read a valid UTF-8 JSON contract") from None
    require(isinstance(contract, dict), "contract: expected an object")
    extra, missing = set(contract) - CONTRACT_FIELDS - {"notes"}, CONTRACT_FIELDS - set(contract)
    require(not extra and not missing, "contract: missing %s; unknown %s" % (sorted(missing), sorted(extra)))
    require(contract["schema_version"] == 1 and type(contract["schema_version"]) is int,
            "contract: unsupported schema_version")
    for key in ("unit", "prediction_time", "label_horizon", "group_key"):
        require(isinstance(contract[key], str) and contract[key].strip(), "contract: empty " + key)
    require(isinstance(contract["hierarchy"], list) and contract["hierarchy"]
            and all(isinstance(h, str) and h.strip() for h in contract["hierarchy"]),
            "contract: hierarchy must list levels")
    require(type(contract["forward_only"]) is bool, "contract: forward_only must be true or false")
    for key in ("embargo_time", "label_horizon_time"):
        value = contract[key]
        require(type(value) in (int, float) and math.isfinite(value) and value >= 0,
                "contract: %s must be a nonnegative number" % key)
    features = contract["features"]
    require(isinstance(features, dict) and all(isinstance(k, str) and k.strip() and isinstance(v, str)
                                               and v.strip() for k, v in features.items()),
            "contract: features must map each feature to its availability rule")
    breaks = contract["regime_breaks"]
    require(isinstance(breaks, list), "contract: regime_breaks must be a list")
    for item in breaks:
        require(isinstance(item, dict) and set(item) == {"time", "note"} and isinstance(item["note"], str),
                "contract: each regime break has exactly time and note")
        item["_t"] = clock.parse(item["time"], "contract regime break")
    return contract


def finding(check, fold, rows, detail, heuristic=False):
    ids = sorted({r["row_id"] for r in rows})
    item = {"check": check, "fold": fold, "rows": len(ids), "examples": ids[:EXAMPLES], "detail": detail}
    if heuristic:
        item["heuristic"] = True
    return item


def runs_z(ordered):
    """Wald-Wolfowitz runs z-score of train/test labels in time order. Near 0 looks random."""
    n1 = sum(1 for s in ordered if s == "train")
    n2 = len(ordered) - n1
    if min(n1, n2) < MIN_RUNS_SIDE:
        return None
    runs = 1 + sum(1 for a, b in zip(ordered, ordered[1:]) if a != b)
    n = n1 + n2
    mean = 1 + 2 * n1 * n2 / n
    variance = 2 * n1 * n2 * (2 * n1 * n2 - n) / (n * n * (n - 1))
    return (runs - mean) / math.sqrt(variance) if variance > 0 else None


def audit(args):
    clock = Clock()
    columns, rows = read_rows(args.assignments,
                              ("row_id", "group", "prediction_time", "label_end_time", "fold", "split"))
    times(rows, clock)
    contract = load_contract(args.contract, clock)
    seen = set()
    for row in rows:
        require(row["split"] in SPLITS, "row %s: split must be one of %s" % (row["row_id"], ", ".join(SPLITS)))
        require(row["fold"].strip(), "row %s: empty fold" % row["row_id"])
        key = (row["row_id"], row["fold"])
        require(key not in seen, "duplicate row_id %s in fold %s" % key)
        seen.add(key)
    available = [c for c in columns if c.endswith(AVAILABLE) and len(c) > len(AVAILABLE)]
    for row in rows:
        for column in available:
            value = row[column].strip()
            row[column] = clock.parse(value, "row %s %s" % (row["row_id"], column)) if value else None

    findings = []
    for feature in sorted(contract["features"]):
        if feature + AVAILABLE not in columns:
            findings.append(finding("availability_missing", None, [],
                                    "declared feature %s has no %s%s column" % (feature, feature, AVAILABLE)))
    for column in available:
        feature = column[:-len(AVAILABLE)]
        late = [r for r in rows if r[column] is not None and r[column] > r["_pt"]]
        empty = [r for r in rows if r[column] is None]
        if late:
            findings.append(finding("lookahead", None, late,
                                    "%s becomes available after prediction_time" % feature))
        if empty:
            findings.append(finding("availability_missing", None, empty,
                                    "%s has empty availability cells" % feature))

    horizon = contract["label_horizon_time"]
    short = [r for r in rows if r["_le"] - r["_pt"] < horizon - 1e-9]
    if short:
        findings.append(finding("label_window_short", None, short,
                                "label_end_time is less than label_horizon_time after prediction_time; "
                                "purge cannot see the full label window"))

    folds = sorted({r["fold"] for r in rows}, key=lambda f: (len(f), f))
    split_counts, regime_notes = {}, []
    embargo = contract["embargo_time"]
    for fold in folds:
        members = [r for r in rows if r["fold"] == fold]
        train = [r for r in members if r["split"] == "train"]
        test = [r for r in members if r["split"] == "test"]
        split_counts[fold] = {s: sum(1 for r in members if r["split"] == s) for s in SPLITS}
        if not train or not test:
            findings.append(finding("fold_incomplete", fold, members, "fold needs both train and test rows"))
            continue
        start, end = test_period(test)
        both = {r["group"] for r in test} & {r["group"] for r in train}
        shared = [r for r in train + test if r["group"] in both]
        if shared:
            findings.append(finding("group_leak", fold, shared, "groups appear in both train and test: "
                                    + ", ".join(sorted({r["group"] for r in shared})[:EXAMPLES])))
        overlap = [r for r in train if overlaps(r, start, end)]
        if overlap:
            findings.append(finding("label_overlap", fold, overlap,
                                    "train label windows overlap the test period; purge them"))
        if contract["forward_only"]:
            later = [r for r in train if r["_pt"] >= start]
            if later:
                findings.append(finding("forward_order", fold, later,
                                        "train rows at or after the test start in a forward-only contract"))
        near = [r for r in train if start - embargo <= r["_pt"] <= end + embargo] if embargo > 0 else []
        if near:
            findings.append(finding("embargo", fold, near,
                                    "train rows inside the test period widened by embargo_time"))
        ordered = [r["split"] for r in sorted(train + test, key=lambda r: (r["_pt"], r["split"], r["row_id"]))]
        z = runs_z(ordered)
        if z is not None and z > -2:
            findings.append(finding("shuffle_suspect", fold, test,
                                    "train/test labels in time order have runs z=%.2f (> -2), "
                                    "consistent with a random split" % z, heuristic=True))
        span_start = min(r["_pt"] for r in train)
        crossed = [b["note"] for b in contract["regime_breaks"] if span_start < b["_t"] <= end]
        if crossed:
            regime_notes.append({"fold": fold, "breaks_in_span": crossed})

    return {
        "command": "audit",
        "status": "findings" if findings else "pass",
        "rows": len(rows), "folds": len(folds), "time_kind": clock.kind, "split_counts": split_counts,
        "checks": ["availability_missing", "lookahead", "label_window_short", "fold_incomplete", "group_leak", "label_overlap",
                   "forward_order" if contract["forward_only"] else "forward_order (off)", "embargo",
                   "shuffle_suspect (heuristic)"],
        "findings": findings,
        "regime_notes": regime_notes,
        "limits": ["Checks use the supplied availability times; they cannot prove those times are true.",
                   "A feature with no __available_at column and no contract entry is not checked.",
                   "A row can appear under several checks.",
                   "shuffle_suspect is a heuristic; it skips folds with fewer than %d train or test rows."
                   % MIN_RUNS_SIDE],
    }


def main():
    parser = Parser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True, parser_class=Parser)
    p = sub.add_parser("plan")
    p.add_argument("rows")
    p.add_argument("--out", required=True)
    p.add_argument("--folds", type=int, default=3)
    p.add_argument("--test-groups", type=int, default=1)
    p.add_argument("--window", choices=("expanding", "sliding"), default="expanding")
    p.add_argument("--max-train-groups", type=int)
    p.add_argument("--embargo-groups", type=int, default=0)
    p.add_argument("--embargo-time", type=float, default=0.0)
    p.add_argument("--label-horizon", type=float)
    p.add_argument("--no-purge", dest="purge", action="store_false")
    a = sub.add_parser("audit")
    a.add_argument("assignments")
    a.add_argument("contract")
    args = parser.parse_args()
    try:
        result = plan(args) if args.command == "plan" else audit(args)
    except (InputError, OverflowError) as error:
        message = str(error) if isinstance(error, InputError) else "a number is too large"
        print(json.dumps({"error": message}), file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, allow_nan=False))
    return 1 if result.get("status") == "findings" else 0


if __name__ == "__main__":
    sys.exit(main())
