#!/usr/bin/env python3
"""Link this catalog's skills into the harness skill directories.

~/.agents/skills/<name>        -> <repo>/skills/<name>             (Codex and other agents read here)
~/.claude/skills/<name>        -> ../../.agents/skills/<name>      (Claude Code reads here), except the
                                                                    skills harnesses.json keeps Codex-only
~/.gemini/config/skills/<name> -> ../../../.agents/skills/<name>   (Antigravity, with --harness all;
                                                                    --harness antigravity links directly),
                                                                    except the same Codex-only skills

An installed real directory whose files match the catalog copy is archived under
~/.agents/skills-archive/pre-catalog-<stamp>/ and replaced by the link. One that differs is
left alone and reported: copy its edits into the catalog first.

A link into this clone's skills/ for a skill no longer in the catalog, or a Claude or Antigravity
link for a Codex-only skill, is reported as stale. Nothing is deleted unless --prune-stale or --prune-only
is given, which remove only those links; --prune-only also installs nothing.

--pack names groups from packs.json and combines with --only; --list-packs shows them. When a
selected skill has companions (packs.json) that are neither selected nor installed, the run
warns and names them. It never installs a companion on its own.
"""

import argparse
import filecmp
import json
import os
import shutil
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKILLS = REPO / "skills"
PACKS = REPO / "packs.json"


def load_packs() -> dict:
    """packs.json as a dict; an empty one when the file is absent. Raises ValueError when unreadable."""
    if not PACKS.is_file():
        return {}
    try:
        data = json.loads(PACKS.read_text())
    except json.JSONDecodeError as error:
        raise ValueError(f"packs.json is not valid JSON: {error}") from error
    if not isinstance(data, dict) or not all(isinstance(data.get(k, {}), dict) for k in ("packs", "companions")):
        raise ValueError("packs.json needs 'packs' and 'companions' objects; run scripts/check.py")
    return data


def split_names(value: str) -> list[str] | None:
    """Comma-separated names, trimmed; None when any is empty."""
    names = [name.strip() for name in value.split(",")]
    return names if all(names) else None


def list_packs(packs: dict) -> int:
    if not packs.get("packs"):
        print("No packs: packs.json is missing or empty.", file=sys.stderr)
        return 2
    for name, skills in packs["packs"].items():
        print(f"{name:<20} {len(skills):>3} skills  {', '.join(skills)}")
    return 0


def missing_companions(names: list[str], packs: dict, home: Path, harness: str, codex_only: set[str]) -> dict:
    """Companions of the selected skills that this run neither installs nor finds installed."""
    roots = []
    if harness in ("both", "codex", "all"):
        roots.append(".agents/skills")
    if harness in ("both", "claude", "all"):
        roots.append(".claude/skills")
    if harness in ("antigravity", "all"):
        roots.append(".gemini/config/skills")
    selected, missing = set(names), {}
    for name in names:
        needed = [
            c for c in packs.get("companions", {}).get(name, [])
            if c not in selected and any(
                not os.path.lexists(home / root / c)
                for root in roots
                if not (root != ".agents/skills" and (name in codex_only or c in codex_only))
            )
        ]
        if needed:
            missing[name] = needed
    return missing


def same_tree(a: Path, b: Path) -> bool:
    cmp = filecmp.dircmp(a, b, ignore=[".DS_Store", "__pycache__"])
    if cmp.left_only or cmp.right_only or cmp.common_funny or cmp.funny_files:
        return False
    _, mismatch, errors = filecmp.cmpfiles(a, b, cmp.common_files, shallow=False)
    if mismatch or errors:
        return False
    return all(same_tree(a / d, b / d) for d in cmp.common_dirs)


def same_link(dest: Path, source: Path) -> bool:
    try:
        return dest.resolve() == source.resolve()
    except (OSError, RuntimeError):
        return False


def link_agents(name: str, home: Path, archive: Path, dry: bool) -> str:
    source = SKILLS / name
    dest = home / ".agents/skills" / name
    if dest.is_symlink():
        if same_link(dest, source):
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
                shutil.move(str(archive / name), str(dest))
                raise
        return f"linked (archived the identical copy to {archive / name})"
    if not dry:
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.symlink_to(source)
    return "linked"


def link_mirror(name: str, home: Path, root: str, rel_agents: str, dry: bool, *, shared: bool = True) -> str:
    source = home / ".agents/skills" / name if shared else SKILLS / name
    dest = home / root / name
    if dest.is_symlink():
        if same_link(dest, source) or (dry and shared and same_link(dest, SKILLS / name)):
            return "ok"
        return f"conflict: {dest} links to {dest.readlink()}"
    if dest.exists():
        return f"conflict: {dest} is a real file or directory"
    if not dry:
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.symlink_to(Path(rel_agents) / name if shared else source)
    return "linked"


def link_claude(name: str, home: Path, dry: bool, *, shared: bool = True) -> str:
    return link_mirror(name, home, ".claude/skills", "../../.agents/skills", dry, shared=shared)


def link_antigravity(name: str, home: Path, dry: bool, *, shared: bool = True) -> str:
    return link_mirror(name, home, ".gemini/config/skills", "../../../.agents/skills", dry, shared=shared)


def stale_links(home: Path, codex_only: set[str]) -> list[tuple[Path, str]]:
    """Find links into this catalog that it no longer installs. Never other links or folders."""
    found, seen = [], set()
    for root in (".agents/skills", ".claude/skills", ".gemini/config/skills"):
        directory = home / root
        if not directory.is_dir() or directory.resolve() in seen:
            continue
        seen.add(directory.resolve())
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
            elif root != ".agents/skills" and target.name in codex_only:
                found.append((link, "Codex-only in harnesses.json"))
    return found


def report_unknown(unknown: list[str], stale: list[tuple[Path, str]]) -> int:
    """Refuse the selection and change nothing, but still show the links a pull left stale."""
    for link, reason in stale:
        print(f"stale: {link} links to {link.readlink()} ({reason}); kept")
    sys.stdout.flush()
    removed = sorted({link.name for link, _ in stale} & set(unknown))
    print(f"unknown skills: {', '.join(unknown)}. docs/catalog.md lists every current name.", file=sys.stderr)
    if removed:
        print(f"{', '.join(removed)} left the catalog: drop it from --only. To remove only the stale "
              "links above and install nothing, run this with --prune-only.", file=sys.stderr)
    return 2


def blocked_path(home: Path, harness: str, names: list[str], codex_only: set[str]):
    """Something other than a folder where these names need one, which a dry run would otherwise miss."""
    roots = []
    if harness in ("both", "codex", "all"):
        roots.append(".agents/skills")
    if harness in ("both", "claude", "all") and set(names) - codex_only:
        roots.append(".claude/skills")
    if harness in ("antigravity", "all") and set(names) - codex_only:
        roots.append(".gemini/config/skills")
    for root in roots:
        path = home / root
        while path != home:
            if os.path.lexists(path) and not path.is_dir():
                return path
            path = path.parent
    return None


def run(a: argparse.Namespace) -> int:
    home = Path(a.home)
    names = sorted(p.name for p in SKILLS.iterdir() if (p / "SKILL.md").is_file())
    codex_only = set(json.loads((REPO / "harnesses.json").read_text())["codex_only"])
    try:
        packs = load_packs()
    except ValueError as error:
        if a.pack is not None or a.list_packs:
            print(f"Stopped: {error}", file=sys.stderr)
            return 2
        packs = {}
    if a.list_packs:
        return list_packs(packs)
    if a.prune_only:
        names = []
    elif a.only is not None or a.pack is not None:
        wanted = []
        if a.only is not None:
            wanted = split_names(a.only)
            if wanted is None:
                print("--only needs comma-separated skill names, with none empty; leave it out for the whole catalog.",
                      file=sys.stderr)
                return 2
        if a.pack is not None:
            chosen, valid = split_names(a.pack), packs.get("packs", {})
            if chosen is None:
                print("--pack needs comma-separated pack names, with none empty.", file=sys.stderr)
                return 2
            bad = sorted(set(chosen) - set(valid))
            if bad:
                print(f"unknown packs: {', '.join(bad)}. Valid packs: {', '.join(valid) or 'none (no packs.json)'}. "
                      "--list-packs shows them.", file=sys.stderr)
                return 2
            wanted += [skill for pack in chosen for skill in valid[pack]]
        unknown = sorted(set(wanted) - set(names))
        if unknown:
            return report_unknown(unknown, stale_links(home, codex_only))
        names = [n for n in names if n in wanted]
    blocked = blocked_path(home, a.harness, names, codex_only) if names else None
    if blocked:
        print(f"Stopped: {blocked} is not a folder, and a skills folder belongs there. Move it and rerun; nothing changed.",
              file=sys.stderr)
        return 2
    archive = home / ".agents/skills-archive" / f"pre-catalog-{time.strftime('%Y%m%dT%H%M%S')}-{time.time_ns()}"
    conflicts = 0
    for name in names:
        if a.harness == "claude":
            agents = "not selected"
            claude = "codex only" if name in codex_only else link_claude(name, home, a.dry_run, shared=False)
            antigravity = "not selected"
        elif a.harness == "antigravity":
            agents = "not selected"
            claude = "not selected"
            antigravity = "codex only" if name in codex_only else link_antigravity(name, home, a.dry_run, shared=False)
        else:
            agents = link_agents(name, home, archive, a.dry_run)
            if a.harness == "codex":
                claude = "not selected"
                antigravity = "not selected"
            else:
                if agents.startswith("conflict"):
                    claude = "skipped"
                elif name in codex_only:
                    claude = "codex only"
                else:
                    claude = link_claude(name, home, a.dry_run)
                if a.harness == "all":
                    if agents.startswith("conflict"):
                        antigravity = "skipped"
                    elif name in codex_only:
                        antigravity = "codex only"
                    else:
                        antigravity = link_antigravity(name, home, a.dry_run)
                else:
                    antigravity = "not selected"
        conflicts += agents.startswith("conflict") + claude.startswith("conflict") + antigravity.startswith("conflict")
        if a.harness in ("antigravity", "all"):
            print(f"{name:<26} agents: {agents}; claude: {claude}; antigravity: {antigravity}")
        else:
            print(f"{name:<26} agents: {agents}; claude: {claude}")
    stale = stale_links(home, codex_only)
    pruning = a.prune_stale or a.prune_only
    prune = pruning and not a.dry_run
    for link, reason in stale:
        target = link.readlink()
        if prune:
            link.unlink()
        action = "removed" if prune else "would remove" if pruning else "kept; --prune-stale removes it"
        print(f"stale: {link} links to {target} ({reason}); {action}")
    print(f"\n{len(names)} skills, {conflicts} conflicts, {len(stale)} stale links"
          f"{' (dry run, nothing changed)' if a.dry_run else ''}")
    missing = missing_companions(names, packs, home, a.harness, codex_only)
    for name, needed in missing.items():
        print(f"warning: {name} works with {', '.join(needed)}; not selected and not installed.")
    if missing:
        extra = sorted({c for needed in missing.values() for c in needed})
        harness = f" --harness {a.harness}" if a.harness != "both" else ""
        print(f"To add them: python3 scripts/install.py{harness} --only {','.join(extra)}")
    return 1 if conflicts else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dry-run", action="store_true", help="print the plan and change nothing")
    ap.add_argument("--only", help="comma-separated skill names")
    ap.add_argument("--pack", help="comma-separated pack names from packs.json; combines with --only")
    ap.add_argument("--list-packs", action="store_true", help="print each pack and its skills, then exit")
    ap.add_argument("--harness", choices=["both", "codex", "claude", "antigravity", "all"], default="both",
                    help="install for Codex and Claude Code (both, default), Codex, Claude Code, Antigravity, or all three")
    ap.add_argument("--prune-stale", action="store_true",
                    help="after installing, remove stale links into this catalog; nothing else is removed")
    ap.add_argument("--prune-only", action="store_true",
                    help="remove stale links into this catalog and install nothing")
    ap.add_argument("--home", default=str(Path.home()), help=argparse.SUPPRESS)
    a = ap.parse_args()
    if a.prune_only and (a.only is not None or a.pack is not None or a.prune_stale):
        ap.error("--prune-only takes no --only, --pack or --prune-stale")
    try:
        return run(a)
    except OSError as error:
        print(f"Stopped: {error.strerror or error}: {error.filename2 or error.filename}. Fix that path and rerun; "
              "any links already made stay in place.", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
