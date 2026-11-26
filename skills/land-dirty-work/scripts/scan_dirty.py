#!/usr/bin/env python3
"""Read-only scanner for uncommitted dirty work across repositories and worktrees."""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys

SCRIPT_DIR = str(Path(__file__).resolve().parent)
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from classify_dirty import (
    cap_list,
    classify_binary_and_oversized,
    compute_dirty_fingerprint,
    compute_mtime_and_clusters,
    count_omitted,
    find_ignored_credentials,
    find_symlink_paths,
    is_credential_candidate,
    is_likely_scratch_path,
)
from scan_git import (
    active_git_operations,
    check_filter_and_submodule_safety,
    list_worktrees,
    parse_porcelain_z,
    resolve_default_base,
    resolve_git_dir,
    run_git,
    run_git_bytes,
)


def inspect_worktree(
    entry: dict,
    default_base: str | None,
    default_short: str | None,
    oversized_bytes: int,
    now_ts: float,
    max_paths: int,
    min_stale_minutes: int,
) -> tuple[dict, list[str], float | None]:
    """Inspect a single worktree entry without modifying working tree or index."""
    wt_path = Path(entry["worktree"])
    errors: list[str] = []
    if entry.get("bare"):
        return {"path": str(wt_path), "bare": True, "dirty": False}, errors, None
    if not wt_path.is_dir():
        msg = f"missing worktree directory: {wt_path}"
        errors.append(msg)
        return {"path": str(wt_path), "inspection_error": msg, "dirty": False}, errors, None

    branch_ref = entry.get("branch")
    branch_short = branch_ref.removeprefix("refs/heads/") if isinstance(branch_ref, str) else None
    detached = bool(entry.get("detached")) or branch_short is None
    head_sha = entry.get("HEAD") if isinstance(entry.get("HEAD"), str) else None

    wt_head_age_days = None
    rc_h, h_ts_raw, _ = run_git(wt_path, "log", "-1", "--format=%ct")
    if rc_h == 0 and h_ts_raw.strip().isdigit():
        wt_head_age_days = round(max(0.0, (now_ts - int(h_ts_raw.strip())) / 86400.0), 2)

    ahead_behind = None
    if default_base and head_sha:
        rc_ab, ab_raw, _ = run_git(wt_path, "rev-list", "--left-right", "--count", f"{default_base}...HEAD")
        if rc_ab == 0 and len(ab_raw.split()) == 2:
            behind_s, ahead_s = ab_raw.split()
            ahead_behind = {"behind": int(behind_s), "ahead": int(ahead_s)}

    git_dir = resolve_git_dir(wt_path)
    ops = active_git_operations(wt_path, git_dir)
    gap = check_filter_and_submodule_safety(wt_path)
    if gap is not None:
        errors.append(f"{wt_path}: {gap}")
        return {
            "path": str(wt_path),
            "branch": branch_short,
            "detached": detached,
            "head_sha": head_sha,
            "on_default_branch": (not detached) and branch_short in {"main", "master", default_short},
            "ahead_behind": ahead_behind,
            "heavily_behind": bool(ahead_behind is not None and ahead_behind["behind"] >= 50),
            "active_git_op": ops,
            "safety_gap": gap,
            "dirty": False,
        }, errors, wt_head_age_days

    rc_st, st_bytes, st_err = run_git_bytes(
        wt_path, "status", "--ignore-submodules=dirty", "--porcelain=v1", "-z", "--untracked-files=all"
    )
    if rc_st != 0:
        msg = f"git status failed in {wt_path}: {st_err or 'exit ' + str(rc_st)}"
        errors.append(msg)
        return {"path": str(wt_path), "branch": branch_short, "inspection_error": msg, "dirty": False}, errors, wt_head_age_days

    parsed = parse_porcelain_z(os.fsdecode(st_bytes))
    renamed_from = [r["from"] for r in parsed["renamed"] if r.get("from")]
    unique_paths = sorted(
        set([*parsed["staged"], *parsed["unstaged"], *parsed["untracked"], *parsed["merge_conflicts"], *(r["to"] for r in parsed["renamed"])])
    )
    dirty = bool(unique_paths or ops)
    creds = [p for p in sorted(set([*unique_paths, *renamed_from])) if is_credential_candidate(p)]
    symlinks = find_symlink_paths(wt_path, unique_paths)
    ignored_creds = find_ignored_credentials(wt_path) if dirty else []
    bin_big, bin_capped = classify_binary_and_oversized(wt_path, parsed["untracked"], oversized_bytes)
    clusters, cluster_counts, newest_iso, stale_days, stale_minutes = compute_mtime_and_clusters(
        wt_path, unique_paths, now_ts, git_dir=git_dir
    )
    if dirty:
        fingerprint, diff_errs = compute_dirty_fingerprint(wt_path, head_sha, st_bytes, parsed["untracked"])
        errors.extend(diff_errs)
    else:
        fingerprint = None
    recently_modified = bool(min_stale_minutes > 0 and stale_minutes is not None and stale_minutes < min_stale_minutes)
    heavily_behind = bool(ahead_behind is not None and ahead_behind["behind"] >= 50)
    likely_scratch = bool(
        dirty
        and not parsed["staged"]
        and not parsed["unstaged"]
        and not parsed["deleted"]
        and not parsed["renamed"]
        and not parsed["merge_conflicts"]
        and not ops
        and not creds
        and not symlinks
        and parsed["untracked"]
        and all(is_likely_scratch_path(p) for p in parsed["untracked"])
    )

    return {
        "path": str(wt_path),
        "branch": branch_short,
        "detached": detached,
        "head_sha": head_sha,
        "on_default_branch": (not detached) and branch_short in {"main", "master", default_short},
        "ahead_behind": ahead_behind,
        "heavily_behind": heavily_behind,
        "staged": cap_list(parsed["staged"], max_paths),
        "staged_count": len(parsed["staged"]),
        "unstaged": cap_list(parsed["unstaged"], max_paths),
        "unstaged_count": len(parsed["unstaged"]),
        "untracked": cap_list(parsed["untracked"], max_paths),
        "untracked_count": len(parsed["untracked"]),
        "renamed": cap_list(parsed["renamed"], max_paths),
        "renamed_count": len(parsed["renamed"]),
        "deleted": cap_list(parsed["deleted"], max_paths),
        "deleted_count": len(parsed["deleted"]),
        "merge_conflicts": parsed["merge_conflicts"],
        "active_git_op": ops,
        "credential_or_env_candidates": creds,
        "ignored_credential_or_env_files": ignored_creds,
        "symlink_candidates": symlinks,
        "binary_or_oversized_untracked": cap_list(bin_big, max_paths),
        "binary_or_oversized_count": len(bin_big),
        "binary_scan_capped": bin_capped,
        "omitted_paths_count": count_omitted(parsed, bin_big, max_paths),
        "cluster_counts": cluster_counts,
        "logical_clusters": {} if (max_paths > 0 and len(unique_paths) > max_paths) else clusters,
        "dirty_path_count": len(unique_paths),
        "newest_dirty_mtime_utc": newest_iso,
        "stale_days": stale_days,
        "stale_minutes": stale_minutes,
        "recently_modified": recently_modified,
        "likely_scratch_only": likely_scratch,
        "dirty_fingerprint": fingerprint,
        "duplicate_of_worktree": None,
        "dirty": dirty,
    }, errors, wt_head_age_days


def inspect_repo(
    repo_path: Path,
    oversized_bytes: int,
    now_ts: float,
    max_paths: int = 0,
    min_stale_minutes: int = 0,
    dirty_only: bool = False,
) -> tuple[dict, bool]:
    """Scan one Git repository and all of its registered worktrees."""
    resolved = repo_path.resolve()
    rc_common, common_raw, common_err = run_git(resolved, "rev-parse", "--path-format=absolute", "--git-common-dir")
    if rc_common != 0 or not common_raw.strip():
        err = common_err or "not a git repository"
        return {
            "name": resolved.name,
            "repo": str(resolved),
            "default_base_ref": None,
            "head_age_days": None,
            "has_dirty_work": False,
            "has_dirty_on_default_branch": False,
            "has_credential_candidates": False,
            "has_ignored_credential_files": False,
            "has_symlink_candidates": False,
            "has_merge_conflicts": False,
            "clean_worktrees_omitted": 0,
            "worktrees": [],
            "errors": [err],
            "complete": False,
        }, True
    default_base, default_short = resolve_default_base(resolved)
    head_ages: list[float] = []
    rc_head, head_ts_raw, _ = run_git(resolved, "log", "-1", "--format=%ct")
    if rc_head == 0 and head_ts_raw.strip().isdigit():
        head_ages.append(round(max(0.0, (now_ts - int(head_ts_raw.strip())) / 86400.0), 2))

    entries, wt_err = list_worktrees(resolved)
    errors: list[str] = [wt_err] if wt_err else []
    worktrees: list[dict] = []
    for entry in entries:
        wt_info, wt_errs, wt_age = inspect_worktree(
            entry, default_base, default_short, oversized_bytes, now_ts, max_paths, min_stale_minutes
        )
        worktrees.append(wt_info)
        errors.extend(wt_errs)
        if wt_age is not None:
            head_ages.append(wt_age)

    ordered_fps = sorted(
        [(idx, wt) for idx, wt in enumerate(worktrees) if wt.get("dirty_fingerprint")],
        key=lambda item: (0 if item[1].get("on_default_branch") else 1, 0 if item[1].get("branch") else 1, item[0]),
    )
    seen_fp: dict[str, str] = {}
    for _, wt in ordered_fps:
        fp = wt["dirty_fingerprint"]
        if fp in seen_fp:
            wt["duplicate_of_worktree"] = seen_fp[fp]
        else:
            seen_fp[fp] = wt["path"]

    any_dirty = any(w.get("dirty") for w in worktrees)
    any_secrets = any(w.get("credential_or_env_candidates") for w in worktrees)
    any_ignored_secrets = any(w.get("ignored_credential_or_env_files") for w in worktrees)
    any_symlinks = any(w.get("symlink_candidates") for w in worktrees)
    any_conflicts = any(w.get("merge_conflicts") for w in worktrees)
    any_on_default = any(w.get("dirty") and w.get("on_default_branch") for w in worktrees)

    clean_wt_omitted = 0
    if dirty_only:
        filtered: list[dict] = []
        for wt in worktrees:
            if wt.get("dirty") or wt.get("safety_gap") or wt.get("inspection_error"):
                filtered.append(wt)
            else:
                clean_wt_omitted += 1
        worktrees = filtered

    return {
        "name": resolved.name,
        "repo": str(resolved),
        "default_base_ref": default_base,
        "head_age_days": min(head_ages) if head_ages else None,
        "has_dirty_work": any_dirty,
        "has_dirty_on_default_branch": any_on_default,
        "has_credential_candidates": any_secrets,
        "has_ignored_credential_files": any_ignored_secrets,
        "has_symlink_candidates": any_symlinks,
        "has_merge_conflicts": any_conflicts,
        "clean_worktrees_omitted": clean_wt_omitted,
        "worktrees": worktrees,
        "errors": errors,
        "complete": not errors,
    }, bool(errors)


def is_repo_active(report: dict, active_days: int) -> bool:
    """Return True if latest commit or newest dirty file is within active_days."""
    head_age = report.get("head_age_days")
    if head_age is not None and head_age <= active_days:
        return True
    return any(wt.get("stale_days") is not None and wt["stale_days"] <= active_days for wt in report.get("worktrees", []))


def discover_targets(repos_root: Path, excluded: set[str], follow_symlinks: bool) -> list[Path]:
    """Discover unique repositories under --repos-root while skipping symlinks unless opted in."""
    by_common: dict[str, Path] = {}
    for child in sorted(repos_root.iterdir()):
        if child.name in excluded or (child.is_symlink() and not follow_symlinks) or not child.is_dir():
            continue
        if (child / ".git").exists():
            rc_c, c_raw, _ = run_git(child, "rev-parse", "--path-format=absolute", "--git-common-dir")
            key = c_raw.strip() if rc_c == 0 and c_raw.strip() else str(child.resolve())
            if key not in by_common or (child / ".git").is_dir():
                by_common[key] = child
    return sorted(by_common.values(), key=lambda p: p.name)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(description="Read-only inventory of uncommitted dirty work across repos and worktrees.")
    scope = parser.add_mutually_exclusive_group(required=True)
    scope.add_argument("--repo", type=Path, help="Single Git repository or worktree path to inspect.")
    scope.add_argument("--repos-root", type=Path, help="Parent directory containing Git repositories.")
    parser.add_argument("--active-days", type=int, default=None, help="With --repos-root, skip clean or inactive repos older than N days.")
    parser.add_argument("--exclude", type=str, default="", help="Comma-separated directory names to skip under --repos-root.")
    parser.add_argument("--dirty-only", action="store_true", help="Omit clean repositories and clean worktrees from output.")
    parser.add_argument("--oversized-bytes", type=int, default=524288, help="Byte threshold for flagging oversized untracked files.")
    parser.add_argument("--max-paths", type=int, default=None, help="Cap path arrays per category (0 for unlimited; default 50 for --repos-root, 0 for --repo).")
    parser.add_argument("--min-stale-minutes", type=int, default=0, help="Mark worktrees modified fewer than N minutes ago as recently_modified.")
    parser.add_argument("--follow-symlinks", action="store_true", help="Follow symlinked top-level entries under --repos-root.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""
    args = parse_args(argv)
    if (args.active_days is not None and args.active_days < 0) or args.oversized_bytes <= 0 or (args.max_paths is not None and args.max_paths < 0) or args.min_stale_minutes < 0:
        print("error: invalid numeric argument", file=sys.stderr)
        return 1
    max_paths = args.max_paths if args.max_paths is not None else (50 if args.repos_root is not None else 0)
    now_ts = datetime.now(tz=timezone.utc).timestamp()
    excluded = {item.strip() for item in args.exclude.split(",") if item.strip()}
    if args.repo is not None:
        if not args.repo.exists():
            print(f"error: repository path does not exist: {args.repo}", file=sys.stderr)
            return 1
        targets = [args.repo]
    else:
        if not args.repos_root.is_dir():
            print(f"error: --repos-root is not a directory: {args.repos_root}", file=sys.stderr)
            return 1
        targets = discover_targets(args.repos_root, excluded, args.follow_symlinks)

    if len(targets) > 1:
        workers = min(16, max(4, (os.cpu_count() or 4) * 2), len(targets))
        with ThreadPoolExecutor(max_workers=workers) as pool:
            results = list(
                pool.map(
                    lambda t: inspect_repo(t, args.oversized_bytes, now_ts, max_paths, args.min_stale_minutes, args.dirty_only),
                    targets,
                )
            )
    else:
        results = [inspect_repo(t, args.oversized_bytes, now_ts, max_paths, args.min_stale_minutes, args.dirty_only) for t in targets]

    repos: list[dict] = []
    skipped_inactive: list[str] = []
    clean_count = 0
    incomplete = False
    for report, has_err in results:
        if has_err:
            incomplete = True
        elif args.repos_root is not None and args.active_days is not None and not is_repo_active(report, args.active_days):
            skipped_inactive.append(report["name"])
            continue
        if not report["has_dirty_work"] and args.dirty_only and not has_err:
            clean_count += 1
            continue
        repos.append(report)

    if args.repo is not None and repos and not repos[0]["worktrees"] and not repos[0]["complete"]:
        print(json.dumps({"observed_at": datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "repos": repos, "incomplete": True}, indent=2))
        return 1 if "not a git repository" in " ".join(repos[0]["errors"]) else 2

    payload = {
        "observed_at": datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "scanned_targets": len(targets),
        "clean_repos_omitted": clean_count if args.dirty_only else 0,
        "skipped_inactive_repos": skipped_inactive,
        "dirty_repos_count": sum(1 for r in repos if r.get("has_dirty_work")),
        "incomplete": incomplete,
        "repos": repos,
    }
    print(json.dumps(payload, indent=2))
    return 2 if incomplete else 0


if __name__ == "__main__":
    sys.exit(main())
