#!/usr/bin/env python3
"""Validate a frozen local assessment and calculate conservative quality scores."""

import argparse
import hashlib
import json
import math
from decimal import Decimal
from pathlib import Path
import re
import sys


DIMENSIONS = (
    "functional", "reliability", "security", "maintainability", "tests",
    "accessibility", "performance", "reproducibility",
)
STATES = {"PASS", "FAIL", "UNAVAILABLE", "NOT RUN"}
HEX = re.compile(r"[0-9a-f]{64}")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, f"duplicate JSON key: {key}")
        result[key] = value
    return result


def read_json(path):
    def invalid_constant(value):
        raise ValueError(f"nonfinite JSON number: {value}")
    return json.loads(path.read_text(), object_pairs_hook=unique_object,
                      parse_constant=invalid_constant)


def digest(value):
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"),
                         ensure_ascii=False, allow_nan=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def evidence_files(entries, root, required):
    root = root.resolve()
    require(isinstance(entries, list), "evidence must be a list")
    require(not required or entries, "verified claim needs evidence files")
    for entry in entries:
        require(isinstance(entry, dict), "evidence entry must be an object")
        path, expected = entry.get("path"), entry.get("sha256")
        require(nonempty(path) and not Path(path).is_absolute(),
                "evidence path must be relative to evidence root")
        resolved = (root / path).resolve()
        require(resolved.is_relative_to(root), "evidence escapes evidence root")
        require(resolved.is_file(), f"evidence file not found: {path}")
        require(isinstance(expected, str) and HEX.fullmatch(expected),
                f"invalid evidence sha256: {path}")
        require(hashlib.sha256(resolved.read_bytes()).hexdigest() == expected,
                f"evidence hash mismatch: {path}")


def validate_plan(plan, root):
    require(isinstance(plan, dict) and type(plan.get("schema_version")) is int
            and plan["schema_version"] == 1,
            "plan needs schema_version 1")
    require(nonempty(plan.get("assessment_id")), "assessment_id is required")
    require(nonempty(plan.get("frozen_at")), "frozen_at is required")
    require(isinstance(plan.get("scope"), dict) and plan["scope"],
            "scope must be a nonempty object")
    target = plan.get("target")
    require(type(target) in (int, float) and math.isfinite(target)
            and 0 <= target <= 10, "target must be a finite number in [0, 10]")
    dimensions = plan.get("dimensions")
    require(isinstance(dimensions, list) and len(dimensions) == len(DIMENSIONS),
            "plan must contain all eight dimensions exactly once")
    ids, dimension_ids = set(), set()
    for dimension in dimensions:
        require(isinstance(dimension, dict), "dimension must be an object")
        dimension_id = dimension.get("id")
        require(dimension_id in DIMENSIONS and dimension_id not in dimension_ids,
                f"invalid or duplicate dimension: {dimension_id}")
        dimension_ids.add(dimension_id)
        applicable = dimension.get("applicable")
        require(type(applicable) is bool, "applicable must be boolean")
        criteria = dimension.get("criteria")
        require(isinstance(criteria, list), "criteria must be a list")
        if not applicable:
            require(not criteria and nonempty(dimension.get("reason")),
                    "N/A needs empty criteria and a reason")
            evidence_files(dimension.get("evidence"), root, required=True)
            continue
        require(criteria, "applicable dimension needs positive total weight")
        for criterion in criteria:
            require(isinstance(criterion, dict), "criterion must be an object")
            criterion_id = criterion.get("id")
            require(nonempty(criterion_id) and criterion_id not in ids,
                    "criterion IDs must be nonempty and globally unique")
            ids.add(criterion_id)
            require(type(criterion.get("weight")) is int and criterion["weight"] > 0,
                    f"{criterion_id}: weight must be a positive integer")
            require(type(criterion.get("critical")) is bool,
                    f"{criterion_id}: critical must be boolean")
            for field in ("pass_condition", "evidence_level", "raw_measure"):
                require(nonempty(criterion.get(field)),
                        f"{criterion_id}: {field} is required")
    require(ids, "assessment needs at least one applicable dimension")
    return ids


def score(plan, observations, root):
    expected_ids = validate_plan(plan, root)
    require(isinstance(observations, dict)
            and type(observations.get("schema_version")) is int
            and observations["schema_version"] == 1,
            "observations need schema_version 1")
    for field, expected in (
        ("assessment_id", plan["assessment_id"]),
        ("plan_sha256", digest(plan)),
        ("scope_sha256", digest(plan["scope"])),
    ):
        require(observations.get(field) == expected, f"{field} mismatch")
    source = observations.get("source")
    require(isinstance(source, dict) and nonempty(source.get("revision")),
            "source revision is required")
    require(isinstance(source.get("diff_sha256"), str)
            and HEX.fullmatch(source["diff_sha256"]), "source diff_sha256 is required")
    require(nonempty(observations.get("observed_at")), "observed_at is required")
    entries = observations.get("criteria")
    require(isinstance(entries, list), "observed criteria must be a list")
    by_id = {}
    for entry in entries:
        require(isinstance(entry, dict), "observation must be an object")
        criterion_id = entry.get("id")
        require(isinstance(criterion_id, str) and criterion_id in expected_ids
                and criterion_id not in by_id, "unknown or duplicate observed ID")
        status = entry.get("status")
        require(status in STATES, f"{criterion_id}: invalid status")
        require(nonempty(entry.get("reason")), f"{criterion_id}: reason is required")
        require(isinstance(entry.get("raw"), dict) and entry["raw"],
                f"{criterion_id}: raw measures or missing-data reasons are required")
        evidence_files(entry.get("evidence"), root, status in {"PASS", "FAIL"})
        by_id[criterion_id] = entry
    require(set(by_id) == expected_ids,
            f"missing observed IDs: {sorted(expected_ids - set(by_id))}")
    target = Decimal(str(plan["target"]))
    rows = []
    for dimension in plan["dimensions"]:
        if not dimension["applicable"]:
            rows.append({"id": dimension["id"], "status": "N/A",
                         "reason": dimension["reason"], "score": None,
                         "target_met": None})
            continue
        total = passed = unknown = 0
        blockers, states = [], {state: 0 for state in sorted(STATES)}
        for criterion in dimension["criteria"]:
            weight = criterion["weight"]
            status = by_id[criterion["id"]]["status"]
            states[status] += weight
            total += weight
            passed += weight if status == "PASS" else 0
            unknown += weight if status in {"UNAVAILABLE", "NOT RUN"} else 0
            if criterion["critical"] and status != "PASS":
                blockers.append({"id": criterion["id"], "status": status})
        lower = Decimal(10) * passed / total
        upper = Decimal(10) * (passed + unknown) / total
        met = not blockers and Decimal(10) * passed >= target * total
        rows.append({"id": dimension["id"], "status": "MET" if met else "UNMET",
                     "score": float(lower), "possible_interval": [float(lower), float(upper)],
                     "total_weight": total, "pass_weight": passed,
                     "unknown_weight": unknown, "status_weights": states,
                     "critical_blockers": blockers, "target_met": met})
    return {"schema_version": 1, "assessment_id": plan["assessment_id"],
            "plan_sha256": digest(plan), "scope_sha256": digest(plan["scope"]),
            "observed_at": observations["observed_at"], "source": source,
            "target": plan["target"], "dimensions": rows,
            "all_applicable_dimensions_met": all(row["target_met"] is not False for row in rows),
            "evidence_limit": "File presence and hashes checked; evidence sufficiency requires review."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("freeze", "score"))
    parser.add_argument("plan", type=Path)
    parser.add_argument("observations", type=Path, nargs="?")
    parser.add_argument("--evidence-root", type=Path, required=True)
    args = parser.parse_args()
    try:
        root = args.evidence_root.resolve(strict=True)
        require(root.is_dir(), "evidence root must be a directory")
        plan = read_json(args.plan)
        validate_plan(plan, root)
        if args.mode == "freeze":
            require(args.observations is None, "freeze does not accept observations")
            output = {"assessment_id": plan["assessment_id"],
                      "plan_sha256": digest(plan), "scope_sha256": digest(plan["scope"])}
        else:
            require(args.observations is not None, "score requires observations")
            output = score(plan, read_json(args.observations), root)
        print(json.dumps(output, indent=2, allow_nan=False))
        return 0 if args.mode == "freeze" or output["all_applicable_dimensions_met"] else 1
    except (ValueError, OSError, TypeError, KeyError) as error:
        print(json.dumps({"error": str(error)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
