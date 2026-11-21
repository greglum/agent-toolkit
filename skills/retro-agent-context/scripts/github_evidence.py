"""Fetch the pull requests that commits name, with their reviews, through gh."""

from __future__ import annotations

import json
import re
import subprocess
from typing import Any

from git_evidence import run, short

PR_FIELDS = """
number title body additions deletions changedFiles createdAt mergedAt
author { __typename login }
commits { totalCount }
reviews(first: 30) { totalCount nodes { author { __typename login } state body } }
comments(first: 30) { totalCount nodes { author { __typename login } body } }
reviewThreads(first: 40) {
  totalCount
  nodes { isResolved path line comments(first: 3) { nodes { author { __typename login } body } } }
}
"""


PR_BATCH = 20


PR_REFERENCE = re.compile(r"\(#(\d+)\)\s*$|^Merge pull request #(\d+)\b")


def github_slug(remote: str | None) -> str | None:
    match = re.search(r"github\.com[:/]([^/\s]+/[^/\s]+?)(?:\.git)?/?$", remote or "")
    return match.group(1) if match else None


def author(node: dict[str, Any] | None) -> dict[str, Any]:
    node = node or {}
    return {"login": node.get("login"), "bot": node.get("__typename") == "Bot"}


def human_review(pr: dict[str, Any]) -> bool:
    """A review, comment or thread comment by a person other than the pull request's author."""
    owner = (pr.get("author") or {}).get("login")
    nodes = [*pr["reviews"]["nodes"], *pr["comments"]["nodes"]]
    nodes += [c for t in pr["reviewThreads"]["nodes"] for c in t["comments"]["nodes"]]
    for node in nodes:
        who = author(node.get("author"))
        if not who["bot"] and who["login"] and who["login"] != owner:
            return True
    return False


def pr_item(pr: dict[str, Any]) -> dict[str, Any]:
    threads = pr["reviewThreads"]
    return {
        "human_review": human_review(pr),
        "number": pr["number"],
        "title": short(pr["title"]),
        "body": short(pr["body"]),
        "author": author(pr["author"]),
        "created_at": pr["createdAt"],
        "merged_at": pr["mergedAt"],
        "added": pr["additions"],
        "deleted": pr["deletions"],
        "files": pr["changedFiles"],
        "commits": pr["commits"]["totalCount"],
        "review_count": pr["reviews"]["totalCount"],
        "comment_count": pr["comments"]["totalCount"],
        "thread_count": threads["totalCount"],
        "reviews": [
            {"author": author(r["author"]), "state": r["state"], "body": short(r["body"])}
            for r in pr["reviews"]["nodes"]
            if r["body"].strip()
        ],
        "comments": [
            {"author": author(c["author"]), "body": short(c["body"])} for c in pr["comments"]["nodes"]
        ],
        "threads": [
            {
                "path": t["path"],
                "line": t["line"],
                "resolved": t["isResolved"],
                "comments": [
                    {"author": author(c["author"]), "body": short(c["body"])}
                    for c in t["comments"]["nodes"]
                ],
            }
            for t in threads["nodes"]
        ],
    }


def pr_numbers(commits: list[dict[str, Any]]) -> tuple[list[int], int]:
    numbers: set[int] = set()
    unreferenced = 0
    for commit in commits:
        match = PR_REFERENCE.search(commit["subject"])
        if match:
            numbers.add(int(match.group(1) or match.group(2)))
        else:
            unreferenced += 1
    return sorted(numbers), unreferenced


def read_prs(slug: str, numbers: list[int]) -> dict[str, Any]:
    """Fetch the pull requests that commits name, in small batches, so busy windows stay complete."""
    owner, name = slug.split("/", 1)
    items: list[dict[str, Any]] = []
    missing: list[int] = []
    graphql_errors: list[str] = []
    for start in range(0, len(numbers), PR_BATCH):
        batch = numbers[start : start + PR_BATCH]
        fields = " ".join(f"p{n}: pullRequest(number: {n}) {{ {PR_FIELDS} }}" for n in batch)
        query = f"query($o: String!, $r: String!) {{ repository(owner: $o, name: $r) {{ {fields} }} }}"
        command = ["gh", "api", "graphql", "-f", f"query={query}", "-f", f"o={owner}", "-f", f"r={name}"]
        code = 0
        err = ""
        try:
            code, out, err = run(command, timeout=120)
            payload = json.loads(out) if out.strip() else {}
            if not isinstance(payload, dict):
                return {"status": "unavailable", "reason": short(err or out) or "invalid JSON", "items": items}
            errors = payload.get("errors")
            if isinstance(errors, list):
                for entry in errors:
                    msg = entry.get("message") if isinstance(entry, dict) else str(entry)
                    if msg:
                        graphql_errors.append(short(str(msg)))
            data = payload.get("data")
            found = data.get("repository") if isinstance(data, dict) else None
            if (code != 0 and not isinstance(found, dict)) or (not isinstance(found, dict) and graphql_errors):
                reason = "; ".join(graphql_errors[:5]) if graphql_errors else short(err)
                result: dict[str, Any] = {"status": "unavailable", "reason": reason, "items": items}
                if graphql_errors:
                    result["errors"] = graphql_errors
                return result
            found = found if isinstance(found, dict) else {}
            for number in batch:
                pr = found.get(f"p{number}")
                if pr:
                    items.append(pr_item(pr))
                else:
                    missing.append(number)
        except (OSError, subprocess.TimeoutExpired, ValueError, KeyError, TypeError, AttributeError) as error:
            reason = short(err) if isinstance(error, ValueError) and code != 0 and err.strip() else type(error).__name__
            return {"status": "unavailable", "reason": reason, "items": items}
    result = {"status": "ok", "matched": len(items), "missing": missing, "items": items}
    if graphql_errors:
        result["errors"] = graphql_errors
    return result
