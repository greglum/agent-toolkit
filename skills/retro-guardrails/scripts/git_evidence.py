"""Read bounded first-parent history with git. Repository text is untrusted data."""

from __future__ import annotations

import os
import re
import subprocess
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

TEXT_LIMIT = 500


PATH_LIMIT = 40


SIDE_COMMIT_LIMIT = 30


SHA = re.compile(r"^[0-9a-f]{40}([0-9a-f]{24})?$")


FIX_SUBJECT = re.compile(r"^(fix|hotfix|bugfix)\b|\b(fix(es|ed)?|regression|hotfix)\b", re.I)


REVERT_SUBJECT = re.compile(r"^revert\b", re.I)


PR_SUBJECT = re.compile(r"\(#\d+\)\s*$")


SCOPE_SUBJECT = re.compile(r"^([a-z]+)(?:\(([^)]+)\))?!?:")


ENV = {**os.environ, "GIT_NO_LAZY_FETCH": "1", "GIT_TERMINAL_PROMPT": "0", "GH_PROMPT_DISABLED": "1"}


def run(command: list[str], timeout: int = 60) -> tuple[int, str, str]:
    result = subprocess.run(command, capture_output=True, timeout=timeout, check=False, env=ENV)
    return (
        result.returncode,
        result.stdout.decode("utf-8", "replace"),
        result.stderr.decode("utf-8", "replace"),
    )


def try_git(repo: Path, *args: str) -> str | None:
    try:
        code, out, _ = run(["git", "-C", str(repo), *args])
    except OSError:
        return None
    return out if code == 0 else None


def git(repo: Path, *args: str) -> str:
    try:
        code, out, err = run(["git", "-C", str(repo), *args])
    except OSError as error:
        raise SystemExit(f"git {' '.join(args)} failed: {error}") from error
    if code != 0:
        raise SystemExit(f"git {' '.join(args)} failed: {err.strip() or 'unknown git error'}")
    return out


def clip(value: str | None) -> tuple[str, bool]:
    text = " ".join((value or "").split())
    return (text, False) if len(text) <= TEXT_LIMIT else (text[:TEXT_LIMIT] + " [clipped]", True)


def short(value: str | None) -> str:
    return clip(value)[0]


def default_ref(repo: Path) -> str:
    symbolic = try_git(repo, "symbolic-ref", "--quiet", "--short", "refs/remotes/origin/HEAD")
    for ref in [(symbolic or "").strip(), "origin/main", "origin/master", "main", "master", "HEAD"]:
        if ref and try_git(repo, "rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}"):
            return ref
    raise SystemExit("no commit found to analyze")


def select_commits(
    repo: Path, ref: str, since_sha: str | None, days: int, limit: int
) -> tuple[list[str], int, dict[str, Any], list[str]]:
    """Return the oldest unprocessed batch, so a long backlog is read across runs."""
    gaps: list[str] = []
    window: dict[str, Any] = {"kind": "days", "days": days}
    selector = [f"--since={days} days ago", ref]
    if since_sha:
        known = (
            ""
            if since_sha.startswith("-")
            else (try_git(repo, "rev-parse", "--verify", "--quiet", f"{since_sha}^{{commit}}") or "").strip()
        )
        ancestor = known and run(["git", "-C", str(repo), "merge-base", "--is-ancestor", known, ref])[0] == 0
        if ancestor:
            selector = [f"{known}..{ref}"]
            window = {"kind": "since_sha", "since_sha": known}
        else:
            window["requested_since_sha"] = since_sha
            gaps.append("marker is missing or not an ancestor; history may be skipped")
    shas = git(repo, "rev-list", "--first-parent", "--reverse", *selector).split()
    return shas[:limit], max(0, len(shas) - limit), window, gaps


def parse_numstat(raw: str) -> tuple[list[tuple[str, int, int]], dict[str, str]]:
    """Parse -z numstat, keeping destination paths and recording renames."""
    rows: list[tuple[str, int, int]] = []
    renames: dict[str, str] = {}
    fields = raw.split("\0")
    index = 0
    while index < len(fields) and fields[index]:
        added, deleted, path = fields[index].split("\t", 2)
        index += 1
        if not path:
            old, path = fields[index], fields[index + 1]
            index += 2
            renames[old] = path
        rows.append((path, int(added) if added != "-" else 0, int(deleted) if deleted != "-" else 0))
    return rows, renames


def commit_diff(repo: Path, sha: str, parents: list[str]) -> str | None:
    flags = ["--numstat", "-z", "-M", "--no-ext-diff", "--no-textconv"]
    if parents:
        return try_git(repo, "diff", *flags, parents[0], sha)
    return try_git(repo, "diff-tree", "--root", "--no-commit-id", "-r", *flags, sha)


def side_commits(repo: Path, parents: list[str], sha: str) -> tuple[list[dict[str, str]], int]:
    if len(parents) < 2:
        return [], 0
    selector = f"{parents[0]}..{sha}"
    total = int((try_git(repo, "rev-list", "--count", "--no-merges", selector) or "0").strip() or 0)
    raw = try_git(
        repo, "log", "--no-merges", f"--max-count={SIDE_COMMIT_LIMIT}", "--format=%H%x00%s%x00", selector
    ) or ""
    fields = raw.split("\0")
    items = [
        {"sha": fields[i].strip()[:12], "subject": short(fields[i + 1])}
        for i in range(0, len(fields) - 1, 2)
        if SHA.match(fields[i].strip())
    ]
    return items, max(0, total - len(items))


def read_commits(repo: Path, shas: list[str]) -> tuple[list[dict[str, Any]], dict[str, str], Counter[str]]:
    commits: list[dict[str, Any]] = []
    renames: dict[str, str] = {}
    issues: Counter[str] = Counter()
    if not shas:
        return commits, renames, issues
    fmt = "tformat:%H%x00%P%x00%cI%x00%s%x00%b%x00"
    fields = git(repo, "log", "--no-walk=unsorted", f"--format={fmt}", *shas).split("\0")
    for index in range(0, len(fields) - 1, 5):
        record = fields[index : index + 5]
        sha = record[0].strip()
        if len(record) < 5 or not SHA.match(sha):
            issues["malformed_records"] += 1
            continue
        parents = record[1].split()
        raw = commit_diff(repo, sha, parents)
        rows: list[tuple[str, int, int]] = []
        if raw is None:
            issues["diffs_unavailable"] += 1
        else:
            try:
                rows, found = parse_numstat(raw)
                renames.update(found)
            except (ValueError, IndexError):
                issues["diffs_unparsed"] += 1
        subject, _ = clip(record[3])
        body, body_clipped = clip(record[4])
        side, side_hidden = side_commits(repo, parents, sha)
        issues["bodies_clipped"] += int(body_clipped)
        issues["path_lists_clipped"] += int(len(rows) > PATH_LIMIT)
        issues["side_commits_clipped"] += side_hidden
        shape = "merge" if len(parents) > 1 else "squash_pr" if PR_SUBJECT.search(subject) else "direct"
        commits.append(
            {
                "sha": sha,
                "date": record[2],
                "subject": subject,
                "body": body,
                "shape": shape,
                "files": len(rows),
                "added": sum(row[1] for row in rows),
                "deleted": sum(row[2] for row in rows),
                "paths": [row[0] for row in rows[:PATH_LIMIT]],
                "side_commits": side,
                "_all_paths": [row[0] for row in rows],
            }
        )
    if len(commits) != len(shas):
        issues["commits_missing"] += len(shas) - len(commits)
    return commits, renames, issues


def canonical(path: str, renames: dict[str, str]) -> str:
    seen = {path}
    while path in renames and renames[path] not in seen:
        path = renames[path]
        seen.add(path)
    return path


def summarize(commits: list[dict[str, Any]], renames: dict[str, str]) -> dict[str, Any]:
    churn: Counter[str] = Counter()
    fixes_by_path: dict[str, list[str]] = defaultdict(list)
    types: Counter[str] = Counter()
    scopes: Counter[str] = Counter()
    fixes: list[str] = []
    reverts: list[str] = []
    for commit in commits:
        subject = commit["subject"]
        match = SCOPE_SUBJECT.match(subject)
        if match:
            types[match.group(1)] += 1
            if match.group(2):
                scopes[match.group(2)] += 1
        side_subjects = [item["subject"] for item in commit["side_commits"]]
        is_fix = any(FIX_SUBJECT.search(text) for text in [subject, *side_subjects])
        if is_fix:
            fixes.append(commit["sha"][:12])
        if any(REVERT_SUBJECT.search(text) for text in [subject, *side_subjects]):
            reverts.append(commit["sha"][:12])
        for path in commit.pop("_all_paths"):
            name = canonical(path, renames)
            churn[name] += 1
            if is_fix:
                fixes_by_path[name].append(commit["sha"][:12])
    return {
        "shapes": dict(Counter(commit["shape"] for commit in commits)),
        "commit_types": dict(types.most_common(15)),
        "commit_scopes": dict(scopes.most_common(20)),
        "empty_bodies": sum(1 for commit in commits if not commit["body"]),
        "fix_like_commits": fixes,
        "reverts": reverts,
        "paths_with_repeated_fixes": {
            path: shas for path, shas in sorted(fixes_by_path.items()) if len(shas) > 1
        },
        "most_changed_paths": dict(churn.most_common(20)),
    }
