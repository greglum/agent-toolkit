#!/usr/bin/env python3
"""Bounded, read-only GitHub PR event notifications. Never a merge gate."""

import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time


FIELDS = "url,state,headRefOid,baseRefOid,baseRefName,isDraft,mergeStateStatus,reviewDecision,autoMergeRequest"
THREADS = """
query($owner:String!, $name:String!, $number:Int!, $endCursor:String) {
  repository(owner:$owner, name:$name) {
    pullRequest(number:$number) {
      reviewThreads(first:100, after:$endCursor) {
        pageInfo { hasNextPage endCursor }
        nodes { id isResolved isOutdated path line }
      }
    }
  }
}
"""


def gh(args, allowed=(0,), empty_checks=False):
    result = subprocess.run(["gh", *args], text=True, capture_output=True, timeout=30)
    if result.returncode not in allowed:
        # Keep response bodies and credential-bearing diagnostics out of event logs.
        raise ValueError(f"GitHub command failed ({result.returncode}): gh {' '.join(args[:2])}")
    if (empty_checks and result.returncode == 1 and not result.stdout.strip()
            and re.fullmatch(r"no checks reported on the '[^\n]+' branch\s*", result.stderr)):
        return []
    data = json.loads(result.stdout)
    if isinstance(data, dict) and data.get("errors"):
        raise ValueError("GitHub returned GraphQL errors; snapshot incomplete")
    return data


def fingerprint(value):
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def metadata(repo, number):
    value = gh(["pr", "view", str(number), "--repo", repo, "--json", FIELDS])
    if not isinstance(value, dict) or any(key not in value for key in FIELDS.split(",")):
        raise ValueError("incomplete PR metadata")
    if not value["headRefOid"] or not value["baseRefOid"]:
        raise ValueError("PR endpoints unavailable")
    auto_merge = value["autoMergeRequest"]
    if auto_merge is not None:
        value["autoMergeRequest"] = {key: auto_merge[key] for key in ("enabledAt", "mergeMethod")}
    return value


def rest_records(repo, number, kind):
    endpoints = {"comments": f"repos/{repo}/issues/{number}/comments",
                 "reviews": f"repos/{repo}/pulls/{number}/reviews",
                 "inline_comments": f"repos/{repo}/pulls/{number}/comments"}
    endpoint = endpoints[kind]
    pages = gh(["api", endpoint + "?per_page=100", "--paginate", "--slurp"])
    records = []
    for page in pages:
        for row in page:
            # Body digests catch edits without persisting comment text.
            records.append({"id": row["id"], "url": row["html_url"],
                            "updated": row.get("updated_at", row.get("submitted_at")),
                            "state": row.get("state"), "commit": row.get("commit_id"),
                            "body_hash": fingerprint(row["body"])})
    return sorted(records, key=lambda row: row["id"])


def threads(repo, number):
    owner, name = repo.split("/")
    pages = gh(["api", "graphql", "--paginate", "--slurp", "-f", f"query={THREADS}",
                "-f", f"owner={owner}", "-f", f"name={name}", "-F", f"number={number}"])
    result = []
    for page in pages:
        if page.get("errors"):
            raise ValueError("GitHub returned thread pagination errors")
        connection = page["data"]["repository"]["pullRequest"]["reviewThreads"]
        result.extend(connection["nodes"])
    if not pages or connection["pageInfo"]["hasNextPage"]:
        raise ValueError("incomplete thread pagination")
    return sorted(result, key=lambda row: row["id"])


def snapshot(repo, number):
    before = metadata(repo, number)
    checks = gh(["pr", "checks", str(number), "--repo", repo, "--json",
                 "name,workflow,bucket,link"], allowed=(0, 1, 8), empty_checks=True)
    if not isinstance(checks, list) or any(row.get("bucket") not in
            {"pass", "fail", "pending", "skipping", "cancel"} for row in checks):
        raise ValueError("unknown check schema")
    value = {"pr": before, "checks": sorted(checks, key=lambda row: json.dumps(row, sort_keys=True)),
             "comments": rest_records(repo, number, "comments"),
             "reviews": rest_records(repo, number, "reviews"),
             "inline_comments": rest_records(repo, number, "inline_comments"),
             "threads": threads(repo, number)}
    after = metadata(repo, number)
    if any(before[key] != after[key] for key in ("headRefOid", "baseRefOid", "baseRefName", "state")):
        raise ValueError("PR endpoints changed during collection; retry after inspection")
    return value


def load_state(path, target):
    if not path.exists():
        return None
    state = json.loads(path.read_text())
    if state.get("schema") != 1 or state.get("target") != target:
        raise ValueError("incompatible watcher state; preserve it and select a new state directory")
    previous = state["snapshot"]
    if not isinstance(previous, dict) or set(previous) != {"pr", "checks", "comments", "reviews", "inline_comments", "threads"}:
        raise ValueError("invalid watcher snapshot")
    if state.get("snapshot_hash") != fingerprint(previous):
        raise ValueError("corrupt watcher snapshot; preserve it and select a new state directory")
    return previous


def save_state(path, target, value):
    pending = path.with_suffix(".tmp")
    with pending.open("w") as handle:
        os.chmod(pending, 0o600)
        json.dump({"schema": 1, "target": target, "snapshot": value,
                   "snapshot_hash": fingerprint(value)}, handle, sort_keys=True)
        handle.flush()
        os.fsync(handle.fileno())
    pending.replace(path)


def observe(previous, current):
    changed = [key for key in current if previous is None or current[key] != previous[key]]
    pr = current["pr"]
    unresolved = sum(not row["isResolved"] for row in current["threads"])
    failed = sum(row["bucket"] in ("fail", "cancel") for row in current["checks"])
    return {"event": "initial" if previous is None else "changed", "changed": changed,
            "url": pr["url"], "head": pr["headRefOid"], "base": pr["baseRefOid"],
            "state": pr["state"], "merge_state": pr["mergeStateStatus"],
            "review_decision": pr["reviewDecision"], "unresolved_threads": unresolved,
            "failed_checks": failed, "check_count": len(current["checks"]),
            "readiness": "not assessed"}


def watch(args, path, target):
    previous = load_state(path, target)
    deadline = time.monotonic() + args.timeout
    while True:
        current = snapshot(args.repo, args.number)
        event = observe(previous, current)
        terminal = current["pr"]["state"] in ("MERGED", "CLOSED")
        if event["changed"] or args.once or terminal:
            print(json.dumps(event, sort_keys=True), flush=True)
        save_state(path, target, current)
        # Initial state is visible, then a normal run waits for a subsequent change.
        if args.once or terminal or (previous is not None and event["changed"]):
            return 0
        previous = current
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            return 3
        time.sleep(min(args.interval, remaining))
        if time.monotonic() >= deadline:
            return 3


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("number", type=int)
    parser.add_argument("--repo", required=True, help="GitHub.com owner/repository")
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--timeout", type=int, default=300, help="polling window in seconds")
    parser.add_argument("--interval", type=int, default=30)
    parser.add_argument("--state-dir", type=Path,
                        default=Path.home() / ".local/state/skills/monitor-pr")
    args = parser.parse_args()
    if (args.number < 1 or not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", args.repo)
            or args.interval < 5 or args.timeout < 1):
        parser.error("positive PR/timeout, interval >= 5, and owner/repository required")
    # gh must use the same host as the identity stored in state.
    os.environ["GH_HOST"] = "github.com"
    target = f"{args.repo.lower()}#{args.number}"
    args.state_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
    path = args.state_dir / (hashlib.sha256(target.encode()).hexdigest() + ".json")
    with path.with_suffix(".lock").open("a") as handle:
        try:
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            print("another watcher owns this target in this state directory", file=sys.stderr)
            return 2
        return watch(args, path, target)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)
    except (OSError, ValueError, KeyError, TypeError, subprocess.TimeoutExpired) as error:
        print(f"monitor-pr unavailable: {error}", file=sys.stderr)
        sys.exit(1)
