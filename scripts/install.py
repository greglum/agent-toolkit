#!/usr/bin/env python3
"""Link this catalog's skills into the harness skill directories.

~/.agents/skills/<name>  -> <repo>/skills/<name>        (Codex and other agents read here)
~/.claude/skills/<name>  -> ../../.agents/skills/<name>  (Claude Code reads here), except the
                                                         skills harnesses.json keeps Codex-only

An installed real directory whose files match the catalog copy is archived under
~/.agents/skills-archive/pre-catalog-<stamp>/ and replaced by the link. One that differs is
left alone and reported: copy its edits into the catalog first.

A link into this clone's skills/ for a skill no longer in the catalog, or a Claude link for a
Codex-only skill, is reported as stale. Nothing is deleted unless --prune-stale is given,
which removes only those links.
"""

import argparse
import filecmp
import json
import shutil
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKILLS = REPO / "skills"


def same_tree(a: Path, b: Path) -> bool:
    cmp = filecmp.dircmp(a, b, ignore=[".DS_Store"])
    if cmp.left_only or cmp.right_only or cmp.funny_files:
        return False
    _, mismatch, errors = filecmp.cmpfiles(a, b, cmp.common_files, shallow=False)
    if mismatch or errors:
        return False
    return all(same_tree(a / d, b / d) for d in cmp.common_dirs)


def link_agents(name: str, home: Path, archive: Path, dry: bool) -> str:
    source = SKILLS / name
    dest = home / ".agents/skills" / name
    if dest.is_symlink():
        if dest.resolve() == source.resolve():
            return "ok"
        return f"conflict: {dest} links to {dest.readlink()}"
    if dest.exists():
        if not dest.is_dir() or not same_tree(dest, source):
            return f"conflict: {dest} differs from the catalog; copy its edits into {source} first"
        if not dry:
            archive.mkdir(parents=True, exist_ok=True)
            shutil.move(str(dest), str(archive / name))
            try:
                dest.symlink_to(source)
            except OSError:
                # A failed link must not leave a working installed copy missing.
                shutil.move(str(archive / name), str(dest))
                raise
        return f"linked (archived the identical copy to {archive / name})"
    if not dry:
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.symlink_to(source)
    return "linked"


def link_claude(name: str, home: Path, dry: bool, *, shared: bool = True) -> str:
    source = home / ".agents/skills" / name if shared else SKILLS / name
    dest = home / ".claude/skills" / name
    if dest.is_symlink():
        if dest.resolve() == source.resolve():
            return "ok"
        return f"conflict: {dest} links to {dest.readlink()}"
    if dest.exists():
        return f"conflict: {dest} is a real directory"
    if not dry:
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.symlink_to(Path("../../.agents/skills") / name if shared else source)
    return "linked"


def stale_links(home: Path, codex_only: set[str]) -> list[tuple[Path, str]]:
    """Find links into this catalog that it no longer installs. Never other links or folders."""
    found = []
    for root in (".agents/skills", ".claude/skills"):
        directory = home / root
        if not directory.is_dir():
            continue
        for link in sorted(directory.iterdir()):
            if not link.is_symlink():
                continue
            try:
                target = link.resolve()
            except (OSError, RuntimeError):
                continue
            if target.parent != SKILLS:
                continue
            if not (target / "SKILL.md").is_file():
                found.append((link, "no longer in the catalog"))
            elif root == ".claude/skills" and target.name in codex_only:
                found.append((link, "Codex-only in harnesses.json"))
    return found


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true", help="print the plan and change nothing")
    ap.add_argument("--only", help="comma-separated skill names")
    ap.add_argument("--harness", choices=["both", "codex", "claude"], default="both",
                    help="install for both harnesses (default), Codex, or Claude Code")
    ap.add_argument("--prune-stale", action="store_true",
                    help="remove stale links into this catalog; nothing else is removed")
    ap.add_argument("--home", default=str(Path.home()), help=argparse.SUPPRESS)
    a = ap.parse_args()
    home = Path(a.home)
    names = sorted(p.name for p in SKILLS.iterdir() if (p / "SKILL.md").is_file())
    if a.only:
        wanted = set(a.only.split(","))
        unknown = wanted - set(names)
        if unknown:
            print(f"unknown skills: {', '.join(sorted(unknown))}", file=sys.stderr)
            return 2
        names = [n for n in names if n in wanted]
    codex_only = set(json.loads((REPO / "harnesses.json").read_text())["codex_only"])
    archive = home / ".agents/skills-archive" / f"pre-catalog-{time.strftime('%Y%m%dT%H%M%S')}-{time.time_ns()}"
    conflicts = 0
    for name in names:
        # Claude-only installation links directly to the catalog and does not create Codex paths.
        if a.harness == "claude":
            agents = "not selected"
            claude = "codex only" if name in codex_only else link_claude(name, home, a.dry_run, shared=False)
        else:
            agents = link_agents(name, home, archive, a.dry_run)
            if a.harness == "codex":
                claude = "not selected"
            elif agents.startswith("conflict"):
                claude = "skipped"
            elif name in codex_only:
                claude = "codex only"
            else:
                claude = link_claude(name, home, a.dry_run)
        conflicts += agents.startswith("conflict") + claude.startswith("conflict")
        print(f"{name:<26} agents: {agents}; claude: {claude}")
    stale = stale_links(home, codex_only)
    prune = a.prune_stale and not a.dry_run
    for link, reason in stale:
        target = link.readlink()
        if prune:
            link.unlink()
        action = "removed" if prune else "would remove" if a.prune_stale else "kept; --prune-stale removes it"
        print(f"stale: {link} links to {target} ({reason}); {action}")
    print(f"\n{len(names)} skills, {conflicts} conflicts, {len(stale)} stale links"
          f"{' (dry run, nothing changed)' if a.dry_run else ''}")
    return 1 if conflicts else 0


if __name__ == "__main__":
    sys.exit(main())
