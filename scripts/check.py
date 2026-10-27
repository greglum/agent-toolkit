#!/usr/bin/env python3
"""Validate every skill in this catalog. Exit 1 on any error.

Checks, per skills/<name>/SKILL.md:
- frontmatter opens the file and has `name` and `description`;
- Claude boolean fields such as `disable-model-invocation` are a bare `true` or `false`;
- `name` matches the folder and is lowercase hyphen-case, at most 64 characters;
- `description` is at most 1024 characters, the Agent Skills limit, and within the
  catalog budget: 360 for a model-invoked skill, 600 for an explicit-only one;
- no em dash in Markdown prose outside fenced code (authoring rule 10);
- every relative Markdown link resolves inside its skill bundle, and a `#fragment` on a
  Markdown target matches a heading anchor there (GitHub slugs, fenced code ignored);
- no machine-specific home path (/Users/<name>/), email address, or /private/tmp path;
  write `~` instead. The same scan covers README.md, THIRD_PARTY_NOTICES.md, and docs/.
Explicit-only skills must carry both Claude and Codex invocation controls.
Reader guides in the repository root, docs/, and docs/examples/ must also have
working local links and heading anchors. Dated internal research is not a reader guide.
And across the catalog: no skill name also appears in vendor.json (when present), and every harnesses.json
entry names a catalog skill.

Private names: when ~/.config/skills/private-names.txt exists (one name per line, `#` for
comments), every text file in the repository is scanned for those names as whole words,
ignoring case. Hits name the file, line, and pattern number, never the name. When the file is
missing, the check is skipped with a notice. Keep that file outside the repository.
"""

import json
import re
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import unquote

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "skills/harden-skill/scripts"))
from inspect_skill import (  # Reuse the catalog's existing dependency-free YAML reader.
    LINK_RE,
    Field,
    check_booleans,
    check_bundle_entries,
    link_target,
    openai_policy,
    parse_frontmatter,
    split_frontmatter,
)

NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
AUTO_BUDGET, EXPLICIT_BUDGET = 360, 600
EM_DASH = "\u2014"
HEADING_RE = re.compile(r"^ {0,3}#{1,6}[ \t]+(.*?)(?:[ \t]+#+)?[ \t]*$")
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}")
TEMP_RE = re.compile(r"/private/tmp\b")
LEAK_ROOTS = ("README.md", "THIRD_PARTY_NOTICES.md", "docs")
TEXT_SUFFIXES = {".md", ".mjs", ".js", ".py", ".sh", ".yaml", ".yml", ".json", ".txt", ".toml", ".ini", ""}
PRIVATE_NAMES = Path.home() / ".config/skills/private-names.txt"
HOME_RE = re.compile(r"(?<![A-Za-z0-9._~:/-])(?:/(?:Users|home)/[A-Za-z0-9._-]+/|[A-Za-z]:[\\/]+Users[\\/]+[^\\/\s]+[\\/])")


def leak_errors(path: Path, line: str, n: int) -> list[str]:
    """Machine-specific or personal details that must not ship."""
    found = []
    if HOME_RE.search(line):
        found.append(f"{path}:{n}: machine-specific home path; use ~")
    if EMAIL_RE.search(line):
        found.append(f"{path}:{n}: email address")
    if TEMP_RE.search(line):
        found.append(f"{path}:{n}: local temporary path")
    return found


def text_files(root: Path):
    """Text files under root (a file or folder), skipping Git data, caches, and hidden tool folders."""
    paths = [root] if root.is_file() else sorted(root.rglob("*"))
    for path in paths:
        parts = path.relative_to(REPO).parts if path.is_relative_to(REPO) else path.parts
        hidden = any(p.startswith(".") and p not in (".github", ".githooks") for p in parts[:-1])
        if hidden or ".git" in parts or "__pycache__" in parts or not path.is_file() or path.is_symlink():
            continue
        if path.suffix in TEXT_SUFFIXES:
            yield path


def check_private_names(names_file: Path = PRIVATE_NAMES, root: Path = REPO) -> tuple[list[str], str | None]:
    """Scan every text file for locally listed private names. Returns (errors, skip notice)."""
    if not names_file.is_file():
        return [], "private-name check skipped: no ~/.config/skills/private-names.txt"
    names = [s.strip() for s in names_file.read_text().splitlines() if s.strip() and not s.lstrip().startswith("#")]
    patterns = [re.compile(rf"(?<![A-Za-z0-9]){re.escape(name)}(?![A-Za-z0-9])", re.I) for name in names]
    errors = []
    for path in text_files(root):
        for n, line in enumerate(path.read_text(errors="replace").splitlines(), 1):
            errors += [f"{path}:{n}: private name pattern {i}" for i, p in enumerate(patterns, 1) if p.search(line)]
    return errors, None


def heading_anchors(path: Path) -> set[str]:
    """GitHub heading slugs in a Markdown file; fenced code is skipped, repeats get -1, -2."""
    anchors, seen, fenced = set(), Counter(), False
    for line in path.read_text(errors="replace").splitlines():
        if line.lstrip().startswith(("```", "~~~")):
            fenced = not fenced
        elif not fenced and (heading := HEADING_RE.match(line)):
            slug = re.sub(r"[^\w\- ]", "", heading[1].lower()).replace(" ", "-")
            anchors.add(f"{slug}-{seen[slug]}" if seen[slug] else slug)
            seen[slug] += 1
    return anchors


def frontmatter(text: str) -> dict[str, Field] | None:
    findings = []
    path = Path("SKILL.md")
    raw, _ = split_frontmatter(text, path, findings)
    fields = parse_frontmatter(raw, path, findings)
    if any(f.severity == "error" for f in findings):
        return None
    return fields


def check_skill(skill: Path) -> list[str]:
    errors = []
    findings = []
    if not check_bundle_entries(skill, findings):
        return [f"{f.path}: {f.message}" for f in findings]
    md = skill / "SKILL.md"
    text = md.read_text()
    fields = frontmatter(text)
    if fields is None:
        return [f"{md}: invalid frontmatter; inspect with harden-skill/scripts/inspect_skill.py"]
    findings = []
    check_booleans(fields, md, findings)
    errors += [f"{f.path}: {f.message}" for f in findings]
    fm = {key: field.value for key, field in fields.items()}
    name, desc = fm.get("name", ""), fm.get("description", "")
    if name != skill.name:
        errors.append(f"{md}: name '{name}' does not match folder '{skill.name}'")
    if not NAME_RE.match(name) or len(name) > 64:
        errors.append(f"{md}: name must be lowercase hyphen-case, at most 64 characters")
    if not desc:
        errors.append(f"{md}: description is empty")
    elif len(desc) > 1024:
        errors.append(f"{md}: description is {len(desc)} characters; the limit is 1024")
    claude_explicit = fm.get("disable-model-invocation", "").lower() == "true"
    budget = EXPLICIT_BUDGET if claude_explicit else AUTO_BUDGET
    if len(desc) > budget and len(desc) <= 1024:
        errors.append(f"{md}: description is {len(desc)} characters; the catalog budget is {budget}")
    if len(fm.get("compatibility", "")) > 500:
        errors.append(f"{md}: compatibility exceeds the 500-character limit")
    findings = []
    policy = skill / "agents/openai.yaml"
    implicit = openai_policy(policy, findings, required=claude_explicit)
    if claude_explicit and implicit is not False:
        errors.append(f"{policy}: explicit-only skill needs policy.allow_implicit_invocation: false")
    elif implicit is False and not claude_explicit:
        errors.append(f"{md}: Codex explicit-only skill needs disable-model-invocation: true")
    errors += [f"{f.path}: {f.message}" for f in findings if f.severity == "error"]
    for f in skill.rglob("*"):
        if not f.is_file() or f.suffix not in (".md", ".mjs", ".js", ".py", ".sh", ".yaml", ".yml"):
            continue
        body = f.read_text(errors="replace")
        for n, line in enumerate(body.splitlines(), 1):
            errors += leak_errors(f, line, n)
        if f.suffix == ".md":
            fenced = False
            for n, line in enumerate(body.splitlines(), 1):
                if line.lstrip().startswith(("```", "~~~")):
                    fenced = not fenced
                elif not fenced and EM_DASH in line:
                    errors.append(f"{f}:{n}: em dash in prose; use plain punctuation")
            for raw_target in LINK_RE.findall(body):
                target, _, fragment = unquote(link_target(raw_target)).partition("#")
                if re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", target) or target.startswith("~"):
                    continue
                resolved = (f.parent / target if target else f).resolve()
                if not resolved.is_relative_to(skill.resolve()):
                    errors.append(f"{f}: link leaves its skill bundle '{target}'")
                elif not resolved.exists():
                    errors.append(f"{f}: broken relative link '{target}'")
                elif fragment and resolved.suffix == ".md" and resolved.is_file() and fragment not in heading_anchors(resolved):
                    errors.append(f"{f}: broken heading anchor '{target}#{fragment}'")
    return errors


def check_reader_links(root: Path = REPO) -> list[str]:
    """Check the public entry points, including in an extracted source archive."""
    paths = sorted(root.glob("*.md")) + sorted((root / "docs").glob("*.md"))
    paths += sorted((root / "docs/examples").rglob("*.md"))
    errors = []
    for path in paths:
        for raw_target in LINK_RE.findall(path.read_text()):
            target, _, fragment = unquote(link_target(raw_target)).partition("#")
            if re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", target) or target.startswith("~"):
                continue
            resolved = (path.parent / target if target else path).resolve()
            if not resolved.is_relative_to(root.resolve()):
                errors.append(f"{path}: link leaves the repository '{target}'")
            elif not resolved.exists():
                errors.append(f"{path}: broken relative link '{target}'")
            elif fragment and resolved.suffix == ".md" and resolved.is_file() and fragment not in heading_anchors(resolved):
                errors.append(f"{path}: broken heading anchor '{target}#{fragment}'")
    return errors


def main() -> int:
    skills = sorted(p for p in (REPO / "skills").iterdir() if p.is_dir())
    errors = check_reader_links()
    for skill in skills:
        if not (skill / "SKILL.md").is_file():
            errors.append(f"{skill}: no SKILL.md")
            continue
        errors += check_skill(skill)
    for root in LEAK_ROOTS:
        if (REPO / root).exists():
            for f in text_files(REPO / root):
                for n, line in enumerate(f.read_text(errors="replace").splitlines(), 1):
                    errors += leak_errors(f, line, n)
    private, notice = check_private_names()
    errors += private
    if notice:
        print(notice)
    if (REPO / "vendor.json").is_file():  # Optional local list of third-party skills used alongside.
        vendor = json.loads((REPO / "vendor.json").read_text())
        clash = {s["name"] for s in vendor["skills"]} & {p.name for p in skills}
        errors += [f"vendor.json: '{n}' is also a catalog skill" for n in sorted(clash)]
    codex_only = set(json.loads((REPO / "harnesses.json").read_text())["codex_only"])
    errors += [f"harnesses.json: '{n}' is not a catalog skill" for n in sorted(codex_only - {p.name for p in skills})]
    for e in errors:
        print(e)
    print(f"{len(skills)} skills checked, {len(errors)} errors")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
