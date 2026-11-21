#!/usr/bin/env python3
"""Name the shared retro state folder for a repository and focus.

Every retro skill carries an identical copy, so all of them compute the same key and the router can
read each focus. Prints the folder; creates nothing.
"""

from __future__ import annotations

import argparse
import hashlib
import re
import subprocess
from pathlib import Path

STATE_ROOT = Path.home() / ".agents" / "state" / "retro"


def _git(repo: Path, *args: str) -> str | None:
    try:
        result = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, check=False)
    except OSError:
        return None
    return result.stdout.strip() if result.returncode == 0 else None


def repo_key(repo: Path) -> str:
    """Key by the origin URL so worktrees and clones share state; fall back to the git common dir."""
    remote = _git(repo, "remote", "get-url", "origin") or ""
    identity = re.sub(r"^(ssh://)?(git@|https?://)", "", remote).replace(":", "/")
    identity = identity.removesuffix(".git").rstrip("/").lower()
    if not identity:
        identity = _git(repo, "rev-parse", "--path-format=absolute", "--git-common-dir") or ""
    if not identity:
        raise SystemExit(f"not a git repository: {repo}")
    return hashlib.sha256(identity.encode()).hexdigest()[:16]


def state_dir(repo: Path, focus: str) -> Path:
    return STATE_ROOT / repo_key(repo) / focus


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--focus", required=True, help="for example guardrails")
    args = parser.parse_args()
    if not re.fullmatch(r"[a-z][a-z-]*", args.focus):
        parser.error("--focus must be lowercase letters and hyphens")
    print(state_dir(args.repo, args.focus))


if __name__ == "__main__":
    main()
