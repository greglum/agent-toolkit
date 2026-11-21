#!/usr/bin/env python3
"""Scan repositories for non-directive code comments and enforce comment ratchets."""

from __future__ import annotations

import argparse
import fnmatch
import json
import os
import subprocess
import sys
from dataclasses import asdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from scanners import CommentHit, ScanError, detect_language, scan_file

SKIP_DIRS = {
    ".git",
    "node_modules",
    ".venv",
    "venv",
    "__pycache__",
    "dist",
    "build",
    "target",
    ".next",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
}


def resolve_root(targets: list[str]) -> Path:
    """Resolve the git repository root or fall back to the target or working directory."""
    probe = Path(targets[0]).resolve() if targets else Path.cwd().resolve()
    probe_dir = probe if probe.is_dir() else probe.parent
    try:
        proc = subprocess.run(
            ["git", "-C", str(probe_dir), "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=False,
        )
        if proc.returncode == 0 and proc.stdout.strip():
            return Path(proc.stdout.strip()).resolve()
    except OSError:
        pass
    return probe_dir if targets else Path.cwd().resolve()


def _should_skip_dir(name: str) -> bool:
    if name in SKIP_DIRS:
        return True
    return name.startswith(".") and name not in (".github", ".githooks")


def discover_files(root: Path, targets: list[str], excludes: list[str]) -> list[tuple[Path, str]]:
    """List candidate files under root, using git ls-files when inside a git repo."""
    rel_paths: list[str] = []
    used_git = False
    git_args = [
        "git",
        "-C",
        str(root),
        "ls-files",
        "-z",
        "--cached",
        "--others",
        "--exclude-standard",
    ]
    if targets:
        git_args.append("--")
        for target in targets:
            resolved = Path(target).resolve()
            try:
                rel_arg = resolved.relative_to(root).as_posix()
            except ValueError:
                rel_arg = target
            git_args.append(rel_arg)
    try:
        proc = subprocess.run(git_args, capture_output=True, check=False)
        if proc.returncode == 0:
            used_git = True
            seen: set[str] = set()
            for entry in proc.stdout.decode("utf-8", errors="replace").split("\x00"):
                if entry and entry not in seen:
                    seen.add(entry)
                    rel_paths.append(entry)
    except OSError:
        used_git = False

    if not used_git:
        search_roots = [Path(t).resolve() for t in targets] if targets else [root]
        collected: set[str] = set()
        for item in search_roots:
            if item.is_file():
                try:
                    collected.add(item.relative_to(root).as_posix())
                except ValueError:
                    collected.add(item.as_posix())
            elif item.is_dir():
                for walk_root, dirs, files in os.walk(item, followlinks=False):
                    dirs[:] = sorted(d for d in dirs if not _should_skip_dir(d))
                    for fname in sorted(files):
                        fpath = Path(walk_root) / fname
                        if fpath.is_symlink():
                            continue
                        try:
                            collected.add(fpath.relative_to(root).as_posix())
                        except ValueError:
                            collected.add(fpath.as_posix())
        rel_paths = sorted(collected)

    results: list[tuple[Path, str]] = []
    for rel in sorted(rel_paths):
        if any(fnmatch.fnmatch(rel, pat) for pat in excludes):
            continue
        full = (root / rel) if not Path(rel).is_absolute() else Path(rel)
        if not full.is_file() or full.is_symlink():
            continue
        results.append((full, rel))
    return results


def count_comment_blocks(hits: list[CommentHit]) -> int:
    """Count contiguous runs of non-directive standalone comments."""
    blocks = 0
    prev_file = None
    prev_end = -2
    for hit in hits:
        if hit.exempted:
            continue
        if hit.inline or hit.file != prev_file or hit.line > prev_end + 1:
            blocks += 1
        prev_file = hit.file
        prev_end = -2 if hit.inline else hit.end_line
    return blocks


def validate_targets(targets: list[str]) -> None:
    """Ensure every explicit target path exists before scanning."""
    for target in targets:
        if not Path(target).exists():
            raise ScanError(f"Target path not found: {target}")


def run_scan(
    root: Path, targets: list[str], excludes: list[str]
) -> tuple[list[str], list[CommentHit]]:
    validate_targets(targets)
    files = discover_files(root, targets, excludes)
    all_hits: list[CommentHit] = []
    scanned_rels: list[str] = []
    for full, rel in files:
        first_line = ""
        try:
            with full.open("rb") as handle:
                first_line = handle.readline().decode("utf-8", errors="replace")
        except OSError as exc:
            raise ScanError(f"{rel}: {exc}") from exc
        if detect_language(full, first_line) is None:
            continue
        scanned_rels.append(rel)
        all_hits.extend(scan_file(full, rel))
    return scanned_rels, all_hits


def cmd_estimate(args: argparse.Namespace) -> int:
    root = resolve_root(args.paths)
    scanned_rels, hits = run_scan(root, args.paths, args.exclude)
    scanned = len(scanned_rels)
    active = [h for h in hits if not h.exempted]
    exempted = [h for h in hits if h.exempted]
    per_file: dict[str, int] = {}
    for hit in active:
        per_file[hit.file] = per_file.get(hit.file, 0) + 1
    top_files = sorted(per_file.items(), key=lambda kv: (-kv[1], kv[0]))[:10]
    summary = {
        "files_scanned": scanned,
        "files_with_comments": len(per_file),
        "comments": len(active),
        "comment_blocks": count_comment_blocks(hits),
        "standalone_lines_shed": sum(h.standalone_lines for h in active),
        "inline_comments": sum(1 for h in active if h.inline),
        "exempted_directives": len(exempted),
        "top_files": [{"file": f, "comments": c} for f, c in top_files],
    }
    if args.json:
        print(json.dumps(summary, indent=2))
        return 0
    print(f"Files scanned: {summary['files_scanned']}")
    print(f"Files with non-directive comments: {summary['files_with_comments']}")
    print(f"Non-directive comments: {summary['comments']} (in {summary['comment_blocks']} blocks)")
    print(f"Standalone lines shed on delete: {summary['standalone_lines_shed']}")
    print(f"Inline comments: {summary['inline_comments']}")
    print(f"Exempted directives/shebangs: {summary['exempted_directives']}")
    if top_files:
        print("Top files:")
        for fname, count in top_files:
            print(f"  {count:4d}  {fname}")
    return 0


def cmd_inventory(args: argparse.Namespace) -> int:
    validate_targets(args.paths)
    root = resolve_root(args.paths)
    _, hits = run_scan(root, args.paths, args.exclude)
    selected = hits if args.include_exempted else [h for h in hits if not h.exempted]
    file_cache: dict[str, list[str]] = {}

    def get_context(rel: str, start_line: int, end_line: int) -> dict[str, list[str]]:
        if rel not in file_cache:
            try:
                file_cache[rel] = (root / rel).read_text(encoding="utf-8", errors="replace").splitlines()
            except OSError as exc:
                raise ScanError(f"{rel}: {exc}") from exc
        lines = file_cache[rel]
        ctx = max(0, args.context)
        before_start = max(1, start_line - ctx)
        after_end = min(len(lines), end_line + ctx)
        return {
            "before": lines[before_start - 1 : start_line - 1],
            "after": lines[end_line:after_end],
        }

    if args.format == "json":
        records = []
        for idx, hit in enumerate(selected):
            rec = asdict(hit)
            rec["index"] = idx
            rec["context"] = get_context(hit.file, hit.line, hit.end_line)
            records.append(rec)
        print(json.dumps(records, indent=2))
        return 0

    for idx, hit in enumerate(selected):
        mode = "inline" if hit.inline else "standalone"
        status = ", exempted" if hit.exempted else ""
        print(f"[{idx}] {hit.file}:{hit.line} ({hit.kind}, {mode}{status}): {hit.text}")
        if args.context > 0:
            ctx = get_context(hit.file, hit.line, hit.end_line)
            for line_text in ctx["before"]:
                print(f"    | {line_text}")
            for line_text in ctx["after"]:
                print(f"    > {line_text}")
    return 0


def load_ratchet(path: Path) -> dict[str, int]:
    """Load and validate per-file comment ceilings from a ratchet JSON file."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"{path}: invalid JSON: {exc}") from exc
    if not isinstance(data, dict) or "files" not in data or not isinstance(data["files"], dict):
        raise ValueError(f"{path}: expected JSON object with a 'files' map")
    ceilings: dict[str, int] = {}
    for rel, limit in data["files"].items():
        if (
            not isinstance(rel, str)
            or not rel
            or isinstance(limit, bool)
            or not isinstance(limit, int)
            or limit < 0
        ):
            raise ValueError(f"{path}: invalid ceiling entry for {rel!r}: {limit!r}")
        ceilings[rel] = limit
    return ceilings


def cmd_check(args: argparse.Namespace) -> int:
    validate_targets(args.paths)
    root = resolve_root(args.paths)
    ratchet_path = Path(args.ratchet)
    if not ratchet_path.is_file():
        print(f"Ratchet file not found: {ratchet_path}", file=sys.stderr)
        return 1
    ceilings = load_ratchet(ratchet_path)
    scanned_rels, hits = run_scan(root, args.paths, args.exclude)
    scanned_set = set(scanned_rels)
    active = [h for h in hits if not h.exempted]
    by_file: dict[str, list[CommentHit]] = {}
    for hit in active:
        by_file.setdefault(hit.file, []).append(hit)

    violations: list[str] = []
    tighten_count = 0
    for rel, file_hits in sorted(by_file.items()):
        ceiling = ceilings.get(rel, 0)
        if len(file_hits) > ceiling:
            violations.append(f"{rel}: {len(file_hits)} non-directive comments (ceiling {ceiling})")
            for hit in file_hits:
                violations.append(f"  {hit.file}:{hit.line}: {hit.text}")
        elif len(file_hits) < ceiling:
            tighten_count += 1
    for rel, ceiling in sorted(ceilings.items()):
        if rel not in by_file and ceiling > 0 and (not (args.paths or args.exclude) or rel in scanned_set):
            tighten_count += 1

    if violations:
        for line_msg in violations:
            print(line_msg)
        return 1
    if tighten_count:
        print(
            f"Ratchet check passed; {tighten_count} file(s) are below ceiling. "
            f"Run update-ratchet --ratchet {ratchet_path} to tighten."
        )
    else:
        print("Ratchet check passed.")
    return 0


def cmd_update_ratchet(args: argparse.Namespace) -> int:
    validate_targets(args.paths)
    root = resolve_root(args.paths)
    ratchet_path = Path(args.ratchet)
    if ratchet_path.exists() and not ratchet_path.is_file():
        raise ValueError(f"Ratchet path is not a file: {ratchet_path}")
    has_existing = ratchet_path.is_file() and not args.init
    existing = load_ratchet(ratchet_path) if has_existing else {}
    scanned_rels, hits = run_scan(root, args.paths, args.exclude)
    scanned_set = set(scanned_rels)
    counts: dict[str, int] = {}
    for hit in hits:
        if not hit.exempted:
            counts[hit.file] = counts.get(hit.file, 0) + 1

    if has_existing:
        regressions = [
            f"{rel}: {count} exceeds existing ceiling {existing.get(rel, 0)}"
            for rel, count in sorted(counts.items())
            if count > existing.get(rel, 0)
        ]
        if regressions:
            for msg in regressions:
                print(msg, file=sys.stderr)
            return 1

    merged = dict(existing) if (has_existing and (args.paths or args.exclude)) else {}
    for rel in scanned_set:
        merged.pop(rel, None)
    for rel, count in counts.items():
        if count > 0:
            merged[rel] = count
    new_files = {rel: count for rel, count in sorted(merged.items()) if count > 0}
    ratchet_path.parent.mkdir(parents=True, exist_ok=True)
    ratchet_path.write_text(json.dumps({"files": new_files}, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {ratchet_path} ({len(new_files)} file(s), {sum(new_files.values())} comment(s)).")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Audit and ratchet non-directive code comments.")
    sub = parser.add_subparsers(dest="command", required=True)

    for name in ("estimate", "inventory", "check", "update-ratchet"):
        p = sub.add_parser(name)
        p.add_argument("paths", nargs="*", help="Optional files or directories to scan.")
        p.add_argument("--exclude", action="append", default=[], help="Glob pattern to skip.")
        if name == "estimate":
            p.add_argument("--json", action="store_true", help="Emit JSON output.")
        elif name == "inventory":
            p.add_argument("--format", choices=("text", "json"), default="text")
            p.add_argument("--context", type=int, default=2)
            p.add_argument(
                "--include-exempted",
                action="store_true",
                help="Include exempted directives and shebangs.",
            )
        elif name == "check":
            p.add_argument("--ratchet", required=True, help="Path to ratchet JSON file.")
        elif name == "update-ratchet":
            p.add_argument("--ratchet", required=True, help="Path to ratchet JSON file.")
            p.add_argument("--init", action="store_true", help="Initialize or reset ceilings.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "estimate":
            return cmd_estimate(args)
        if args.command == "inventory":
            return cmd_inventory(args)
        if args.command == "check":
            return cmd_check(args)
        if args.command == "update-ratchet":
            return cmd_update_ratchet(args)
    except (ScanError, ValueError, OSError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 1


if __name__ == "__main__":
    sys.exit(main())
