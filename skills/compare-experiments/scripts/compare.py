#!/usr/bin/env python3
"""Describe supplied paired observations against a content-bound experiment plan."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import statistics
import sys


class PrivateArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        self.exit(2, 'Invalid arguments. Use --help for the accepted form.\n')


class InputError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise InputError(message)


def object_pairs(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate JSON object key")
        result[key] = value
    return result


def reject_constant(_):
    raise InputError("nonfinite JSON number")


def load(path):
    return json.loads(Path(path).read_text(), object_pairs_hook=object_pairs,
                      parse_constant=reject_constant)


def digest(value):
    body = json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(body.encode()).hexdigest()


def fields(value, names, label):
    require(isinstance(value, dict) and set(value) == set(names.split()),
            label + ": expected the documented fields exactly")


def text(value):
    return isinstance(value, str) and bool(value.strip())


def number(value):
    if type(value) not in (int, float):
        return False
    try:
        return math.isfinite(value)
    except OverflowError:
        return False


def plan_from(path):
    plan = load(path)
    fields(plan, "schema_version experiment metric unit direction workload profile control unchanged "
           "arms rounds minimum_pairs minimum_improvement maximum_unchanged_delta guard_contract", "plan")
    require(type(plan["schema_version"]) is int and plan["schema_version"] == 1,
            "plan: unsupported schema_version")
    for key in ("experiment", "metric", "unit", "workload", "profile", "control", "unchanged", "guard_contract"):
        require(text(plan[key]), "plan: empty or nontext " + key)
    require(plan["direction"] in ("lower", "higher"), "plan: direction must be lower or higher")
    arms = plan["arms"]
    require(isinstance(arms, dict) and len(arms) >= 3 and all(text(k) and text(v) for k, v in arms.items()),
            "plan: arms must map at least three names to revision identities")
    control, unchanged = plan["control"], plan["unchanged"]
    require(control != unchanged and control in arms and unchanged in arms,
            "plan: distinct control and unchanged arms must exist")
    require(arms[control] == arms[unchanged], "plan: unchanged control must use the control revision")
    for arm, revision in arms.items():
        if arm not in (control, unchanged):
            require(revision != arms[control], "plan: treatment revision must differ from control")
    require(type(plan["minimum_pairs"]) is int and plan["minimum_pairs"] >= 2,
            "plan: minimum_pairs must be an integer of at least two")
    for key in ("minimum_improvement", "maximum_unchanged_delta"):
        require(number(plan[key]) and plan[key] >= 0, "plan: invalid " + key)
    require(plan["minimum_improvement"] > 0, "plan: minimum_improvement must be positive")
    rounds = plan["rounds"]
    fields(rounds, "unchanged discovery confirmation", "plan rounds")
    all_rounds = []
    for values in rounds.values():
        require(isinstance(values, list) and len(values) >= plan["minimum_pairs"]
                and all(text(v) for v in values), "plan: each phase needs minimum_pairs named rounds")
        all_rounds.extend(values)
    require(len(set(all_rounds)) == len(all_rounds), "plan: round identities must be unique across phases")
    return plan


def observations(plan, path):
    rows = load(path)
    require(isinstance(rows, list), "samples: expected a JSON array")
    samples, run_ids = {}, set()
    round_phase = {r: phase for phase, rounds in plan["rounds"].items() for r in rounds}
    for index, row in enumerate(rows, 1):
        label = "sample " + str(index)
        fields(row, "round arm run_id revision metric unit direction workload profile status value guards guard_contract", label)
        require(text(row["run_id"]) and row["run_id"] not in run_ids,
                label + ": empty or reused run_id")
        run_ids.add(row["run_id"])
        require(text(row["arm"]) and row["arm"] in plan["arms"], label + ": unknown arm")
        require(text(row["round"]) and row["round"] in round_phase, label + ": unplanned round")
        for key in ("metric", "unit", "direction", "workload", "profile", "guard_contract"):
            require(row[key] == plan[key], label + ": mismatched " + key)
        require(row["revision"] == plan["arms"][row["arm"]], label + ": mismatched revision")
        require(row["status"] in ("success", "failure", "skipped", "timeout"), label + ": invalid status")
        require(row["guards"] in ("pass", "fail", "unknown"), label + ": invalid guards")
        if row["status"] == "success":
            require(number(row["value"]), label + ": success needs a finite numeric value")
        else:
            require(row["value"] is None, label + ": unsuccessful sample must have null value")
        phase = round_phase[row["round"]]
        allowed = (plan["control"], plan["unchanged"]) if phase == "unchanged" else tuple(
            arm for arm in plan["arms"] if arm != plan["unchanged"])
        require(row["arm"] in allowed, label + ": arm not allowed in this phase")
        key = (row["round"], row["arm"])
        require(key not in samples, label + ": duplicate arm/round observation")
        samples[key] = row
    return samples


def summarize(plan, samples, phase, arm):
    deltas, issues = [], []
    counts = {"missing": 0, "failure": 0, "skipped": 0, "timeout": 0, "guard_fail": 0, "guard_unknown": 0}
    for round_id in plan["rounds"][phase]:
        pair = [samples.get((round_id, name)) for name in (plan["control"], arm)]
        good = True
        for row in pair:
            if row is None:
                counts["missing"] += 1
                good = False
                continue
            if row["status"] != "success":
                counts[row["status"]] += 1
                good = False
            if row["guards"] != "pass":
                counts["guard_" + row["guards"]] += 1
                good = False
        if good:
            control, treatment = pair
            delta = control["value"] - treatment["value"]
            if plan["direction"] == "higher":
                delta = -delta
            require(number(delta), "computed difference exceeds finite numeric range")
            deltas.append(delta)
    if any(counts.values()):
        issues.append("missing, unsuccessful or unverified-guard observations remain")
    if len(deltas) < plan["minimum_pairs"]:
        issues.append("fewer complete pairs than the frozen minimum")
    median = statistics.median(deltas) if deltas else None
    require(median is None or number(median), "computed median exceeds finite numeric range")
    return {"complete_pairs": len(deltas), "planned_pairs": len(plan["rounds"][phase]),
            "counts": counts, "deltas": deltas, "median_improvement": median,
            "minimum_improvement_observed": min(deltas) if deltas else None,
            "maximum_improvement_observed": max(deltas) if deltas else None,
            "positive_pairs": sum(v > 0 for v in deltas), "issues": issues}


def discovery_rows(plan, samples):
    rounds = set(plan["rounds"]["unchanged"] + plan["rounds"]["discovery"])
    return [row for key, row in sorted(samples.items()) if key[0] in rounds]


def analyze(plan, samples, selection=None):
    aa = summarize(plan, samples, "unchanged", plan["unchanged"])
    noise = max((abs(v) for v in aa["deltas"]), default=None)
    if noise is not None and noise > plan["maximum_unchanged_delta"]:
        aa["issues"].append("unchanged-control variation exceeds the frozen limit")
    result = {"plan_sha256": digest(plan), "discovery_sha256": digest(discovery_rows(plan, samples)),
              "metric": plan["metric"], "unit": plan["unit"], "direction": plan["direction"],
              "unchanged_control": aa, "observed_unchanged_spread": noise, "arms": {},
              "evidence": "descriptive paired observations; no significance or causal claim"}
    treatments = [a for a in plan["arms"] if a not in (plan["control"], plan["unchanged"])]
    for arm in treatments:
        summary = summarize(plan, samples, "discovery", arm)
        if aa["issues"] or summary["issues"]:
            verdict = "INCONCLUSIVE"
        elif summary["median_improvement"] < plan["minimum_improvement"] or summary["median_improvement"] <= noise:
            verdict = "DOES_NOT_MEET_BAR"
        elif summary["positive_pairs"] != summary["complete_pairs"]:
            verdict = "INCONCLUSIVE"
        else:
            verdict = "NEEDS_CONFIRMATION"
        summary["verdict"] = verdict
        result["arms"][arm] = summary
    confirm_rounds = set(plan["rounds"]["confirmation"])
    confirmation = [row for key, row in samples.items() if key[0] in confirm_rounds]
    if selection is None:
        require(not confirmation, "confirmation samples require a recorded discovery selection")
    else:
        fields(selection, "plan_sha256 discovery_sha256 arm", "selection")
        require(selection["plan_sha256"] == result["plan_sha256"] and
                selection["discovery_sha256"] == result["discovery_sha256"],
                "selection does not match this plan and discovery content")
        arm = selection["arm"]
        require(text(arm) and arm in result["arms"], "selection: unknown treatment")
        require(result["arms"][arm]["verdict"] == "NEEDS_CONFIRMATION",
                "selection: discovery does not meet the frozen rule")
        require(all(row["arm"] in (arm, plan["control"]) for row in confirmation),
                "confirmation contains an unselected treatment")
        check = summarize(plan, samples, "confirmation", arm)
        if check["issues"]:
            check["verdict"] = "INCONCLUSIVE"
        elif check["median_improvement"] >= plan["minimum_improvement"] and check["median_improvement"] > noise and check["positive_pairs"] == check["complete_pairs"]:
            check["verdict"] = "CONFIRMED_OBSERVATION"
        else:
            check["verdict"] = "DOES_NOT_MEET_BAR"
        result["confirmation"] = {"arm": arm, **check}
    return result


def main():
    parser = PrivateArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("freeze", "analyze", "select"))
    parser.add_argument("plan")
    parser.add_argument("samples", nargs="?")
    parser.add_argument("--plan-sha")
    parser.add_argument("--arm")
    parser.add_argument("--selection")
    args = parser.parse_args()
    try:
        plan = plan_from(args.plan)
        if args.command == "freeze":
            require(not any((args.samples, args.plan_sha, args.arm, args.selection)), "freeze only takes a plan")
            output = {"plan_sha256": digest(plan)}
        else:
            require(args.samples is not None, "samples file is required")
            require(args.plan_sha == digest(plan), "plan digest differs from the retained frozen digest")
            samples = observations(plan, args.samples)
            if args.command == "select":
                require(args.selection is None, "select does not take --selection")
                report = analyze(plan, samples)
                require(text(args.arm) and args.arm in report["arms"], "select requires a treatment --arm")
                require(report["arms"][args.arm]["verdict"] == "NEEDS_CONFIRMATION",
                        "selected treatment does not meet the discovery rule")
                output = {"plan_sha256": digest(plan), "discovery_sha256": report["discovery_sha256"], "arm": args.arm}
            else:
                require(args.arm is None, "analyze does not take --arm")
                selection = load(args.selection) if args.selection else None
                output = analyze(plan, samples, selection)
        print(json.dumps(output, indent=2, allow_nan=False))
        return 0
    except (InputError, OSError, UnicodeError, json.JSONDecodeError) as error:
        message = str(error) if isinstance(error, InputError) else "cannot read a valid UTF-8 JSON input file"
        print(json.dumps({"error": message}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
