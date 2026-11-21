#!/usr/bin/env python3
"""Ban non-directive comments across repository code files using a per-file ratchet."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys

if sys.version_info < (3, 10):
    sys.exit(f"Python 3.10 or later is required; this python3 is {sys.version.split()[0]}.")

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from comment_scanners import CommentFinding, file_kind, scan_text

REPO = SCRIPT_DIR.parent
DEFAULT_RATCHET = SCRIPT_DIR / "comment-ratchet.json"
SKIP_DIRS = {"__pycache__", "node_modules"}


def _is_skipped_dir_part(part: str) -> bool:
    if part in SKIP_DIRS:
        return True
    return part.startswith(".") and part not in (".github", ".githooks")


def discover_code_files(root: Path) -> list[str]:
    """List tracked and unignored untracked code files, or walk root without .git."""
    candidates: list[str] = []
    if (root / ".git").exists():
        raw = subprocess.check_output(
            ["git", "-C", str(root), "ls-files", "-z", "--cached", "--others", "--exclude-standard"]
        )
        for entry in raw.split(b"\0"):
            if not entry:
                continue
            rel = entry.decode("utf-8", errors="surrogateescape")
            path = root / rel
            if file_kind(rel) is not None and path.is_file() and not path.is_symlink():
                candidates.append(rel)
    else:
        for path in root.rglob("*"):
            if not path.is_file() or path.is_symlink():
                continue
            rel = path.relative_to(root).as_posix()
            if any(_is_skipped_dir_part(part) for part in Path(rel).parts[:-1]):
                continue
            if file_kind(rel) is not None:
                candidates.append(rel)
    return sorted(set(candidates))


def scan_repo(root: Path) -> dict[str, list[CommentFinding]]:
    """Scan all discovered code files under root."""
    results: dict[str, list[CommentFinding]] = {}
    for rel in discover_code_files(root):
        kind = file_kind(rel)
        if kind is None:
            continue
        text = (root / rel).read_text(encoding="utf-8", errors="replace")
        results[rel] = scan_text(text, kind)
    return results


def load_ratchet(path: Path) -> dict[str, int]:
    """Load per-file comment ceilings from a ratchet JSON file."""
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("files"), dict):
        raise ValueError(f"{path}: expected JSON object with a 'files' map")
    ceilings: dict[str, int] = {}
    for rel, limit in data["files"].items():
        if not isinstance(rel, str) or isinstance(limit, bool) or not isinstance(limit, int) or limit < 0:
            raise ValueError(f"{path}: invalid ceiling entry for {rel!r}: {limit!r}")
        ceilings[rel] = limit
    return ceilings


def save_ratchet(path: Path, files: dict[str, int]) -> None:
    """Write sorted non-zero per-file ceilings to the ratchet JSON file."""
    cleaned = {rel: count for rel, count in sorted(files.items()) if count > 0}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"files": cleaned}, indent=2) + "\n", encoding="utf-8")


def format_comment_preview(text: str) -> str:
    """Format a comment for single-line diagnostic output."""
    first = text.splitlines()[0].strip()
    if len(text.splitlines()) > 1:
        first = f"{first} ..."
    if len(first) > 120:
        return first[:117] + "..."
    return first


def run_estimate(results: dict[str, list[CommentFinding]]) -> int:
    """Print comment totals across all scanned files."""
    total_non_directive = 0
    standalone_lines = 0
    inline_comments = 0
    exempt_directives = 0
    files_with_comments = 0

    for findings in results.values():
        file_non_directive = [f for f in findings if not f.exempt]
        if file_non_directive:
            files_with_comments += 1
        total_non_directive += len(file_non_directive)
        standalone_lines += sum(f.standalone_lines for f in file_non_directive)
        inline_comments += sum(1 for f in file_non_directive if f.is_inline)
        exempt_directives += sum(1 for f in findings if f.exempt)

    print(f"Files scanned: {len(results)}")
    print(f"Files with non-directive comments: {files_with_comments}")
    print(f"Total non-directive comments: {total_non_directive}")
    print(f"Standalone comment lines that will be shed: {standalone_lines}")
    print(f"Inline comments: {inline_comments}")
    print(f"Exempted directives and shebangs: {exempt_directives}")
    return 0


def run_update_ratchet(
    results: dict[str, list[CommentFinding]],
    ratchet_path: Path,
    allow_increase: bool,
) -> int:
    """Create or tighten the ratchet baseline without raising ceilings unless allowed."""
    initializing = not ratchet_path.is_file()
    existing = {} if initializing else load_ratchet(ratchet_path)
    updated: dict[str, int] = {}
    blocked: list[tuple[str, int, int]] = []

    for rel, findings in sorted(results.items()):
        count = sum(1 for f in findings if not f.exempt)
        if initializing or allow_increase:
            if count > 0:
                updated[rel] = count
            continue
        ceiling = existing.get(rel, 0)
        if count > ceiling:
            blocked.append((rel, count, ceiling))
            if ceiling > 0:
                updated[rel] = ceiling
        elif count > 0:
            updated[rel] = count

    save_ratchet(ratchet_path, updated)
    if blocked:
        for rel, count, ceiling in blocked:
            print(
                f"{rel}: {count} non-directive comments exceed ceiling {ceiling}; "
                "pass --allow-increase to raise ceilings",
                file=sys.stderr,
            )
        return 1
    action = "Initialized" if initializing else "Updated"
    print(f"{action} {ratchet_path} with {len(updated)} files ({sum(updated.values())} comments).")
    return 0


def run_check(
    results: dict[str, list[CommentFinding]],
    ratchet_path: Path,
    strict_ratchet: bool,
) -> int:
    """Verify no file exceeds its ratchet ceiling and report tightenable entries."""
    if not ratchet_path.is_file():
        print(
            f"Missing ratchet baseline at {ratchet_path}. "
            "Run: python3 scripts/check_comments.py --update-ratchet",
            file=sys.stderr,
        )
        return 1

    ceilings = load_ratchet(ratchet_path)
    violations: list[str] = []
    tightenable: list[tuple[str, int, int]] = []

    for rel, findings in sorted(results.items()):
        non_exempt = [f for f in findings if not f.exempt]
        count = len(non_exempt)
        ceiling = ceilings.get(rel, 0)
        if count > ceiling:
            violations.append(f"{rel}: {count} non-directive comments (ceiling {ceiling})")
            for finding in non_exempt:
                violations.append(f"  {rel}:{finding.line}: {format_comment_preview(finding.text)}")
        elif count < ceiling:
            tightenable.append((rel, count, ceiling))

    for rel, ceiling in sorted(ceilings.items()):
        if rel not in results and ceiling > 0:
            tightenable.append((rel, 0, ceiling))

    for line in violations:
        print(line)

    if tightenable:
        for rel, count, ceiling in tightenable:
            print(f"Notice: {rel} dropped from {ceiling} to {count} non-directive comments.")
        print("Notice: ratchet can be tightened; run: python3 scripts/check_comments.py --update-ratchet")

    if violations:
        return 1
    if strict_ratchet and tightenable:
        print("Strict ratchet check failed: tighten with --update-ratchet.")
        return 1

    total = sum(1 for findings in results.values() for f in findings if not f.exempt)
    print(f"Comment check passed: {len(results)} files scanned, {total} baseline comments allowed.")
    return 0


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Enforce a zero-new-comment ratchet across repository code files.")
    parser.add_argument("--root", type=Path, default=REPO, help="Repository root to scan.")
    parser.add_argument("--ratchet", type=Path, default=None, help="Path to comment-ratchet.json.")
    parser.add_argument("--update-ratchet", action="store_true", help="Initialize or tighten the ratchet baseline.")
    parser.add_argument("--allow-increase", action="store_true", help="Allow --update-ratchet to raise ceilings.")
    parser.add_argument("--strict-ratchet", action="store_true", help="Fail if any file is below its ratchet ceiling.")
    parser.add_argument("--estimate", action="store_true", help="Print comment counts and line-shedding estimates.")
    args = parser.parse_args(argv)

    root = args.root.resolve()
    ratchet_path = args.ratchet if args.ratchet is not None else (root / "scripts" / "comment-ratchet.json")
    results = scan_repo(root)

    if args.estimate:
        return run_estimate(results)
    if args.update_ratchet:
        return run_update_ratchet(results, ratchet_path, args.allow_increase)
    return run_check(results, ratchet_path, args.strict_ratchet)


if __name__ == "__main__":
    sys.exit(main())
