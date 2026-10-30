#!/usr/bin/env python3
"""Plan dependency waves from an explicit PR snapshot; never access Git or GitHub."""

import argparse
import graphlib
import json
import re
import sys
from datetime import datetime
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def unique_members(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate JSON object member")
        result[key] = value
    return result


def text(value):
    return isinstance(value, str) and bool(value.strip())


def repository(value):
    require(text(value) and re.fullmatch(r"[A-Za-z0-9.-]+/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", value),
            "repository must be host/owner/name, without a URL scheme")
    return value.lower()


def number(value):
    require(type(value) is int and value > 0, "PR numbers must be positive integers")
    return value


def identity(value, label):
    require(isinstance(value, dict) and set(value) == {"repository", "branch", "sha"},
            f"{label} needs repository, branch and sha; use null for unknown values")
    repo = repository(value["repository"]) if value["repository"] is not None else None
    branch, sha = value["branch"], value["sha"]
    require(branch is None or text(branch), f"{label}.branch must be text or null")
    require(sha is None or (isinstance(sha, str) and re.fullmatch(r"[a-fA-F0-9]{40}|[a-fA-F0-9]{64}", sha)),
            f"{label}.sha must be a full 40/64-character hex object ID or null")
    return {"repository": repo, "branch": branch, "sha": sha.lower() if sha else None}


def parse_snapshot(data):
    fields = {"version", "observed_at", "repository", "default_branch", "prs", "orderings"}
    require(isinstance(data, dict) and set(data) == fields, "snapshot fields must match the documented contract")
    require(type(data["version"]) is int and data["version"] == 1, "version must be 1")
    require(text(data["observed_at"]), "observed_at must be an ISO timestamp with timezone")
    observed = datetime.fromisoformat(data["observed_at"].replace("Z", "+00:00"))
    require(observed.tzinfo is not None, "observed_at needs a timezone")
    data["repository"] = repository(data["repository"])
    require(text(data["default_branch"]), "default_branch must be text")
    require(isinstance(data["prs"], list) and data["prs"], "prs must be a nonempty array")
    prs = {}
    for row in data["prs"]:
        require(isinstance(row, dict) and set(row) == {"number", "head", "base", "files", "depends_on"},
                "each PR needs number, head, base, files and depends_on")
        n = number(row["number"])
        require(n not in prs, f"duplicate PR #{n}")
        row["head"] = identity(row["head"], f"#{n}.head")
        row["base"] = identity(row["base"], f"#{n}.base")
        files = row["files"]
        require(files is None or (isinstance(files, list) and all(text(p) for p in files)),
                f"#{n}.files must be a complete path array or null")
        require(isinstance(row["depends_on"], list), f"#{n}.depends_on must be an array")
        for dep in row["depends_on"]:
            require(isinstance(dep, dict) and set(dep) == {"repository", "number", "state", "evidence"},
                    "dependencies need repository, number, state and evidence")
            dep["repository"] = repository(dep["repository"])
            number(dep["number"])
            require(dep["state"] in ("open", "closed", "merged", "unknown"), "invalid dependency state")
            require(text(dep["evidence"]), "dependency evidence must be nonempty")
        prs[n] = row
    require(isinstance(data["orderings"], list), "orderings must be an array")
    for order in data["orderings"]:
        require(isinstance(order, dict) and set(order) == {"before", "after", "reason"},
                "orderings need before, after and reason")
        require(number(order["before"]) in prs and number(order["after"]) in prs,
                "ordering endpoints must be selected PRs")
        require(text(order["reason"]), "ordering reason must be nonempty")
    return prs


def ordered_after(edges, after, before):
    seen, pending = set(), [after]
    while pending:
        current = pending.pop()
        if current in seen:
            continue
        seen.add(current)
        if before in edges[current]:
            return True
        pending.extend(edges[current] - seen)
    return False


def plan(data, prs):
    edges = {n: set() for n in prs}
    reasons, unresolved, unknowns = [], [], []
    heads = {}
    for n, pr in prs.items():
        for side in ("head", "base"):
            missing = [key for key, value in pr[side].items() if value is None]
            if missing:
                unknowns.append({"pr": n, "reason": f"{side} identity unknown: {', '.join(missing)}"})
        if pr["files"] is None:
            unknowns.append({"pr": n, "reason": "changed-file coverage unknown"})
        head = pr["head"]
        if head["repository"] and head["branch"]:
            key = head["repository"], head["branch"]
            require(key not in heads, "multiple selected PRs share a head repository and branch")
            heads[key] = n

    def add(before, after, why):
        edges[after].add(before)
        reasons.append({"before": before, "after": after, "reason": why})

    for n, pr in prs.items():
        base = pr["base"]
        key = base["repository"], base["branch"]
        if key in heads:
            parent = heads[key]
            add(parent, n, "base repository and branch match selected head")
            if base["sha"] and prs[parent]["head"]["sha"] and base["sha"] != prs[parent]["head"]["sha"]:
                unknowns.append({"pr": n, "reason": f"base SHA differs from selected parent #{parent} head"})
        elif key != (data["repository"], data["default_branch"]):
            unresolved.append({"pr": n, "reason": "base branch is unknown or outside the selected set", "base": base})
        for dep in pr["depends_on"]:
            if dep["repository"] == data["repository"] and dep["number"] in prs:
                add(dep["number"], n, dep["evidence"])
                if dep["state"] == "merged":
                    unknowns.append({"pr": n, "reason": "declared merged dependency is also selected; reconcile snapshot"})
            elif dep["state"] != "merged":
                unresolved.append({"pr": n, "reason": "external dependency is not verified merged", "dependency": dep})
    for order in data["orderings"]:
        add(order["before"], order["after"], order["reason"])

    cycle = []
    try:
        graphlib.TopologicalSorter(edges).prepare()
    except graphlib.CycleError as error:
        cycle = error.args[1]

    overlaps = []
    nums = sorted(prs)
    for index, a in enumerate(nums):
        for b in nums[index + 1:]:
            if prs[a]["files"] is None or prs[b]["files"] is None:
                continue
            common = sorted(set(prs[a]["files"]) & set(prs[b]["files"]))
            if common:
                ordered = ordered_after(edges, a, b) or ordered_after(edges, b, a)
                overlaps.append({"prs": [a, b], "files": common, "ordering": "known" if ordered else "unresolved"})

    blocked = {item["pr"] for item in unresolved} | set(cycle)
    for overlap in overlaps:
        if overlap["ordering"] == "unresolved":
            blocked.update(overlap["prs"])
    while True:
        expanded = blocked | {n for n in prs if edges[n] & blocked}
        if expanded == blocked:
            break
        blocked = expanded
    remaining = {n: set(deps) for n, deps in edges.items() if n not in blocked}
    waves = []
    while remaining:
        wave = sorted(n for n, deps in remaining.items() if not deps)
        if not wave:
            blocked.update(remaining)
            break
        waves.append(wave)
        remaining = {n: deps - set(wave) for n, deps in remaining.items() if n not in wave}
    return {
        "version": 1, "observed_at": data["observed_at"], "repository": data["repository"],
        "default_branch": data["default_branch"],
        "scope": "candidate order only, not merge readiness; merge permission is not assessed",
        "status": "incomplete" if blocked or unknowns else "planned",
        "prs": [prs[n] for n in nums], "edges": reasons, "overlaps": overlaps,
        "unresolved": unresolved, "unknowns": unknowns, "cycle": cycle,
        "blocked_prs": sorted(blocked), "candidate_waves": waves,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("snapshot", type=Path)
    args = parser.parse_args()
    try:
        data = json.loads(args.snapshot.read_text(), object_pairs_hook=unique_members)
        result = plan(data, parse_snapshot(data))
    except (OSError, ValueError, TypeError) as error:
        print(f"plan_stack: invalid snapshot: {error}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return 1 if result["status"] == "incomplete" else 0


if __name__ == "__main__":
    sys.exit(main())
