"""Read-only Git subprocess execution, safety inspection, and porcelain parsers."""

from __future__ import annotations

import os
from pathlib import Path
import subprocess

ACTIVE_GIT_MARKERS = (
    "MERGE_HEAD",
    "REBASE_HEAD",
    "CHERRY_PICK_HEAD",
    "REVERT_HEAD",
    "BISECT_LOG",
    "rebase-merge",
    "rebase-apply",
    "index.lock",
)


def run_git_bytes(
    repo_path: Path, *args: str, stdin_bytes: bytes | None = None
) -> tuple[int, bytes, str]:
    """Execute Git in strictly read-only mode returning raw stdout bytes."""
    env = {
        **os.environ,
        "GIT_OPTIONAL_LOCKS": "0",
        "GIT_NO_LAZY_FETCH": "1",
        "GIT_ALLOW_PROTOCOL": "",
    }
    proc = subprocess.run(
        ["git", "-c", "core.fsmonitor=false", "--no-pager", "-C", str(repo_path), *args],
        input=stdin_bytes,
        capture_output=True,
        env=env,
        check=False,
    )
    return proc.returncode, proc.stdout, os.fsdecode(proc.stderr).strip()


def run_git(repo_path: Path, *args: str, stdin_bytes: bytes | None = None) -> tuple[int, str, str]:
    """Execute Git in strictly read-only mode with hooks and lazy fetch disabled."""
    rc, out, err = run_git_bytes(repo_path, *args, stdin_bytes=stdin_bytes)
    return rc, os.fsdecode(out), err


def resolve_git_dir(worktree_path: Path) -> Path | None:
    """Resolve the per-worktree git metadata directory."""
    rc, gdir_raw, _ = run_git(worktree_path, "rev-parse", "--path-format=absolute", "--git-dir")
    if rc != 0 or not gdir_raw.strip():
        return None
    return Path(gdir_raw.strip())


def resolve_default_base(repo_path: Path) -> tuple[str | None, str | None]:
    """Resolve the default branch ref and short name without contacting remotes."""
    rc, sym, _ = run_git(repo_path, "symbolic-ref", "--quiet", "--short", "refs/remotes/origin/HEAD")
    if rc == 0 and sym.strip():
        ref = sym.strip()
        short = ref.split("/", 1)[1] if "/" in ref else ref
        return ref, short
    for candidate, short in (
        ("refs/remotes/origin/main", "main"),
        ("refs/remotes/origin/master", "master"),
        ("refs/heads/main", "main"),
        ("refs/heads/master", "master"),
    ):
        rc_ver, _, _ = run_git(repo_path, "rev-parse", "--verify", "--quiet", f"{candidate}^{{commit}}")
        if rc_ver == 0:
            return candidate, short
    return None, None


def _check_attr_drivers(
    worktree_path: Path, tracked: str, attr_name: str, drivers: set[str]
) -> str | None:
    """Check whether any tracked path binds an active custom filter or diff driver."""
    rc_attr, attr_raw, attr_err = run_git(
        worktree_path,
        "check-attr",
        "-z",
        "--stdin",
        attr_name,
        stdin_bytes=os.fsencode(tracked),
    )
    if rc_attr != 0 or attr_err:
        return f"git check-attr failed: {attr_err or 'exit ' + str(rc_attr)}"
    if drivers.intersection(attr_raw.split("\0")[2::3]):
        return f"worktree inspection requires a configured Git {attr_name} driver"
    return None


def check_filter_and_submodule_safety(worktree_path: Path) -> str | None:
    """Verify no filter/diff driver or submodule dirtiness hides state or executes hooks."""
    rc_cfg, cfg_raw, cfg_err = run_git(worktree_path, "config", "--includes", "--name-only", "--null", "--list")
    if rc_cfg != 0:
        return f"git config inspection failed: {cfg_err or 'exit ' + str(rc_cfg)}"
    keys = [k for k in cfg_raw.split("\0") if k]
    if "diff.external" in keys:
        return "worktree diff requires configured diff.external driver"
    if "extensions.partialclone" in keys or any(k.startswith("remote.") and k.endswith(".promisor") for k in keys):
        return "partial clone objects cannot be verified locally"
    filter_drivers = {
        k[len("filter.") : k.rindex(".")]
        for k in keys
        if k.startswith("filter.") and k.endswith((".clean", ".smudge", ".process", ".required"))
    }
    diff_drivers = {
        k[len("diff.") : k.rindex(".")]
        for k in keys
        if k.startswith("diff.") and k.endswith((".command", ".textconv"))
    }
    if filter_drivers or diff_drivers:
        rc_ls, tracked, ls_err = run_git(worktree_path, "ls-files", "-z")
        if rc_ls != 0:
            return f"git ls-files failed: {ls_err or 'exit ' + str(rc_ls)}"
        if tracked:
            if filter_drivers:
                err = _check_attr_drivers(worktree_path, tracked, "filter", filter_drivers)
                if err is not None:
                    return err
            if diff_drivers:
                err = _check_attr_drivers(worktree_path, tracked, "diff", diff_drivers)
                if err is not None:
                    return err
    rc_sub, sub_raw, sub_err = run_git(worktree_path, "submodule", "status")
    if rc_sub != 0:
        return f"git submodule status failed: {sub_err or 'exit ' + str(rc_sub)}"
    sub_lines = [line for line in sub_raw.splitlines() if line]
    if any(not line.startswith("-") for line in sub_lines):
        return "initialized submodule dirtiness requires separate inspection"
    if any(line.startswith("-") for line in sub_lines):
        rc_st, st_raw, st_err = run_git(worktree_path, "ls-files", "--stage", "-z")
        if rc_st != 0:
            return f"git ls-files --stage failed: {st_err or 'exit ' + str(rc_st)}"
        for item in st_raw.split("\0"):
            if item.startswith("160000 ") and "\t" in item:
                sub_dir = worktree_path / item.split("\t", 1)[1]
                try:
                    if sub_dir.is_dir() and any(sub_dir.iterdir()):
                        return "uninitialized submodule directory is populated and requires separate inspection"
                except OSError:
                    return "uninitialized submodule directory could not be inspected"
    return None


def active_git_operations(worktree_path: Path, git_dir: Path | None = None) -> list[str]:
    """Detect active merge/rebase/cherry-pick/bisect markers or index locks."""
    gdir = git_dir if git_dir is not None else resolve_git_dir(worktree_path)
    if gdir is None:
        return ["unknown-git-dir"]
    return [marker for marker in ACTIVE_GIT_MARKERS if (gdir / marker).exists()]


def parse_porcelain_z(status_raw: str) -> dict:
    """Parse git status --porcelain=v1 -z output into change buckets."""
    staged: list[str] = []
    unstaged: list[str] = []
    untracked: list[str] = []
    renamed: list[dict[str, str]] = []
    deleted: list[str] = []
    merge_conflicts: list[str] = []

    fields = iter(status_raw.split("\0"))
    for entry in fields:
        if len(entry) < 4:
            continue
        x_code, y_code = entry[0], entry[1]
        path = entry[3:]
        if "U" in (x_code, y_code) or (x_code, y_code) in (("D", "D"), ("A", "A")):
            merge_conflicts.append(path)
            continue
        if x_code == "?" and y_code == "?":
            untracked.append(path)
            continue
        if x_code == "!" and y_code == "!":
            continue
        if x_code in ("R", "C") or y_code in ("R", "C"):
            orig_path = next(fields, "")
            renamed.append({"from": orig_path, "to": path})
        if x_code == "D" or y_code == "D":
            deleted.append(path)
        if x_code != " ":
            staged.append(path)
        if y_code != " ":
            unstaged.append(path)

    return {
        "staged": staged,
        "unstaged": unstaged,
        "untracked": untracked,
        "renamed": renamed,
        "deleted": deleted,
        "merge_conflicts": merge_conflicts,
    }


def list_worktrees(repo_path: Path) -> tuple[list[dict], str | None]:
    """Parse git worktree list --porcelain -z entries."""
    rc, raw, err = run_git(repo_path, "worktree", "list", "--porcelain", "-z")
    if rc != 0:
        return [], f"worktree list failed: {err or 'exit ' + str(rc)}"
    trees: list[dict] = []
    current: dict = {}
    for token in raw.split("\0"):
        if not token:
            if current:
                trees.append(current)
                current = {}
            continue
        key, _, val = token.partition(" ")
        current[key] = val if val else True
    if current:
        trees.append(current)
    return trees, None
