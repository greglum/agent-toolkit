"""List the instruction and control files present at the analyzed ref."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from git_evidence import git

INSTRUCTION_NAMES = {"AGENTS.md", "CLAUDE.md", "GEMINI.md", "REVIEW.md", "copilot-instructions.md"}


CONTROL_PATTERNS = tuple(
    re.compile(pattern)
    for pattern in (
        r"(^|/)(Makefile|justfile|package\.json|pyproject\.toml|Package\.swift|pom\.xml)$",
        r"(^|/)(build\.gradle(\.kts)?|Cargo\.toml|go\.mod|lefthook\.ya?ml)$",
        r"(^|/)\.pre-commit-config\.yaml$",
        r"^\.github/workflows/.+\.ya?ml$",
        r"^\.gitlab-ci\.yml$",
        r"(^|/)(check|verify|ci)[^/]*\.(sh|py|mjs|js|ts)$",
        r"(^|/)(check|local_check|validate)_[^/]*\.(sh|py|mjs|js|ts)$",
        r"(^|/)scripts/(check|verify|ci)[^/]*$",
        r"(^|/)(\.?eslint|\.oxlintrc|biome|ruff|\.swiftlint|knip|\.golangci|checkstyle)[^/]*$",
        r"(^|/)[^/]*baseline[^/]*\.json$",
    )
)


def repo_controls(repo: Path, ref: str) -> dict[str, Any]:
    """List instruction and control files as they exist at the analyzed ref."""
    entries: list[tuple[str, str]] = []
    for item in git(repo, "ls-tree", "-r", "-z", "--long", ref).split("\0"):
        if "\t" not in item:
            continue
        meta, path = item.split("\t", 1)
        entries.append((path, meta.split()[-1]))
    instructions = [
        {"path": path, "bytes": int(size) if size.isdigit() else None}
        for path, size in entries
        if Path(path).name in INSTRUCTION_NAMES
    ]
    controls = [path for path, _ in entries if any(p.search(path) for p in CONTROL_PATTERNS)]
    roots = {
        path.split("/skills/")[0] + "/skills"
        for path, _ in entries
        if "/skills/" in path and path.startswith((".agents/", ".claude/", ".gemini/"))
    }
    return {
        "instruction_files": instructions[:40],
        "instruction_files_clipped": len(instructions) > 40,
        "control_files": controls[:120],
        "control_files_clipped": len(controls) > 120,
        "skill_roots": sorted(roots),
        "checkout_has_code_index": (repo / ".codegraph").exists(),
    }
