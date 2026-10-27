#!/usr/bin/env python3
"""Inspect an Agent Skill without third-party dependencies."""

from __future__ import annotations

import argparse
import json
import os
import re
import stat
from dataclasses import asdict
from pathlib import Path
from urllib.parse import unquote

from skill_frontmatter import (
    Field,
    Finding,
    add,
    parse_frontmatter,
    split_frontmatter,
    strip_inline_comment,
    unquote_scalar,
)

NAME_RE = re.compile(r"^(?!-)(?!.*--)[a-z0-9-]{1,64}(?<!-)$")
LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
SCHEME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")
XML_TAG_RE = re.compile(r"<[^>]+>")

STANDARD_FIELDS = {
    "name",
    "description",
    "license",
    "compatibility",
    "metadata",
    "allowed-tools",
}
CLAUDE_FIELDS = {
    "disable-model-invocation",
    "user-invocable",
    "arguments",
    "argument-hint",
    "model",
    "context",
    "agent",
    "hooks",
    "when_to_use",
    "disallowed-tools",
    "effort",
    "paths",
    "shell",
    "background",
}
BOOLEAN_FIELDS = {"disable-model-invocation", "user-invocable", "background"}
CLAUDE_FIELD_NOTES = {
    "when_to_use": "Codex and the standard ignore it; keep trigger text in description",
    "effort": "it overrides the user's effort setting; omit it in a global skill",
    "model": "it overrides the user's model setting; omit it in a global skill",
}


def check_bundle_entries(directory: Path, findings: list[Finding]) -> bool:
    """Reject internal links and special files before reading bundle contents.

    An explicitly selected root may be a harness installation symlink.
    """
    valid = True

    def inventory_error(error: OSError) -> None:
        nonlocal valid
        add(
            findings, "error", "bundle-inventory",
            f"cannot inventory bundle entry: {error.strerror}",
            Path(error.filename) if error.filename else directory,
        )
        valid = False

    for root, directories, files in os.walk(directory, followlinks=False, onerror=inventory_error):
        for name in sorted(directories + files):
            path = Path(root) / name
            try:
                mode = path.lstat().st_mode
            except OSError as error:
                inventory_error(error)
                if name in directories:
                    directories.remove(name)
                continue
            if stat.S_ISLNK(mode):
                add(findings, "error", "bundle-symlink", "bundle contains a symbolic link", path)
                valid = False
                if name in directories:
                    directories.remove(name)
            elif not (stat.S_ISREG(mode) or stat.S_ISDIR(mode)):
                add(findings, "error", "bundle-special-file", "bundle contains a nonregular entry", path)
                valid = False
    return valid



def validate_fields(
    fields: dict[str, Field],
    directory: Path,
    skill_path: Path,
    profile: str,
    findings: list[Finding],
) -> None:
    """Validate specification fields and identify portable harness extensions."""
    for required in ("name", "description"):
        if required not in fields:
            add(
                findings,
                "error",
                "field-missing",
                f"missing required field {required!r}",
                skill_path,
            )

    for key, field in fields.items():
        if key in CLAUDE_FIELDS:
            note = CLAUDE_FIELD_NOTES.get(key, "it is not portable Agent Skills metadata")
            add(
                findings,
                "warning",
                "harness-extension",
                f"{key!r} is a Claude Code extension; {note}",
                skill_path,
                field.line,
            )
        elif key not in STANDARD_FIELDS:
            add(
                findings,
                "error",
                "field-unknown",
                f"unknown frontmatter field {key!r} for profile {profile}",
                skill_path,
                field.line,
            )

    name = fields.get("name")
    if name:
        if not NAME_RE.fullmatch(name.value):
            add(
                findings,
                "error",
                "name-invalid",
                "name must be 1-64 lowercase letters, digits, or hyphens with no edge "
                "or consecutive hyphens",
                skill_path,
                name.line,
            )
        if name.value != directory.name:
            add(
                findings,
                "error",
                "directory-parity",
                f"name {name.value!r} does not match directory {directory.name!r}",
                skill_path,
                name.line,
            )

    description = fields.get("description")
    if description:
        if not description.value.strip():
            add(
                findings,
                "error",
                "description-empty",
                "description must not be empty",
                skill_path,
                description.line,
            )
        if len(description.value) > 1024:
            add(
                findings,
                "error",
                "description-long",
                f"description is {len(description.value)} characters; maximum is 1024",
                skill_path,
                description.line,
            )
        if XML_TAG_RE.search(description.value):
            add(
                findings,
                "error",
                "description-tag",
                "description must not contain XML/HTML tags",
                skill_path,
                description.line,
            )

    compatibility = fields.get("compatibility")
    if compatibility and len(compatibility.value) > 500:
        add(
            findings,
            "error",
            "compatibility-long",
            f"compatibility is {len(compatibility.value)} characters; maximum is 500",
            skill_path,
            compatibility.line,
        )

    check_booleans(fields, skill_path, findings)


def check_booleans(fields: dict[str, Field], skill_path: Path, findings: list[Finding]) -> None:
    """Require bare true/false; harnesses disagree on yes, on, 1, and quoted values."""
    for key in sorted(BOOLEAN_FIELDS & fields.keys()):
        field = fields[key]
        if field.style != "plain" or field.value not in {"true", "false"}:
            add(
                findings,
                "error",
                "extension-boolean",
                f"{key!r} must be a bare true or false; write true or false unquoted",
                skill_path,
                field.line,
            )


def link_target(raw_target: str) -> str:
    """Extract the destination from a Markdown inline-link target."""
    target = raw_target.strip()
    if target.startswith("<") and ">" in target:
        return target[1 : target.index(">")]
    if " " in target:
        target = target.split(" ", 1)[0]
    return target


def check_links(directory: Path, findings: list[Finding]) -> None:
    """Report broken relative Markdown links throughout the skill."""
    for source in sorted(directory.rglob("*.md")):
        if not source.is_file():
            continue
        try:
            text = source.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            add(findings, "error", "encoding", "Markdown file is not valid UTF-8", source)
            continue
        for line_number, line in enumerate(text.splitlines(), 1):
            for match in LINK_RE.finditer(line):
                target = unquote(link_target(match.group(1)))
                path_part = target.split("#", 1)[0]
                if (
                    not path_part
                    or path_part.startswith(("/", "~", "$"))
                    or SCHEME_RE.match(path_part)
                ):
                    continue
                resolved = source.parent / path_part
                if not resolved.exists():
                    add(
                        findings,
                        "error",
                        "link-broken",
                        f"relative link target does not exist: {target}",
                        source,
                        line_number,
                    )


def read_frontmatter(path: Path) -> str | None:
    """Read raw frontmatter for parity comparison without emitting duplicate findings."""
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError):
        return None
    if not lines or lines[0].strip() != "---":
        return None
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            return "\n".join(lines[1:index])
    return None


def harness_location(directory: Path) -> tuple[Path, str, str] | None:
    """Return repo root, harness tree, and skill name for known project locations."""
    parts = directory.absolute().parts
    for index in range(len(parts) - 2):
        if parts[index] in {".agents", ".claude"} and parts[index + 1] == "skills":
            root = Path(*parts[:index])
            return root, parts[index], parts[index + 2]
    return None


def check_wrapper_parity(directory: Path, raw_frontmatter: str, findings: list[Finding]) -> None:
    """Compare canonical and referral-wrapper frontmatter when both are present."""
    location = harness_location(directory)
    if not location:
        return
    root, tree, name = location
    other_tree = ".claude" if tree == ".agents" else ".agents"
    counterpart = root / other_tree / "skills" / name / "SKILL.md"
    if not counterpart.is_file():
        return
    other_frontmatter = read_frontmatter(counterpart)
    if other_frontmatter is not None and other_frontmatter != raw_frontmatter:
        add(
            findings,
            "error",
            "wrapper-drift",
            f"frontmatter differs from {counterpart}",
            directory / "SKILL.md",
        )


def openai_policy(path: Path, findings: list[Finding], *, required: bool = False) -> bool | None:
    """Read Codex invocation policy from the supported sidecar shape."""
    if not path.is_file():
        return None
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        add(findings, "error", "encoding", "agents/openai.yaml is not valid UTF-8", path)
        return None
    value: str | None = None
    in_policy = False
    for line in text.splitlines():
        content = line.split("#", 1)[0].rstrip()
        if line and not line[0].isspace():
            in_policy = content == "policy:"
            continue
        if in_policy:
            match = re.match(r"^  allow_implicit_invocation:\s*([^#\s]+)", line)
            if match:
                value = match.group(1).lower()

    if value is None:
        add(
            findings,
            "error" if required else "warning",
            "codex-policy-missing",
            "agents/openai.yaml has no policy.allow_implicit_invocation value",
            path,
        )
        return None
    if value not in {"true", "false"}:
        add(
            findings,
            "error",
            "codex-policy-boolean",
            "policy.allow_implicit_invocation must be a bare true or false",
            path,
        )
        return None
    return value == "true"


def check_invocation_extensions(
    directory: Path,
    fields: dict[str, Field],
    profile: str,
    findings: list[Finding],
) -> None:
    """Detect contradictory or incomplete cross-harness invocation wiring."""
    sidecar = directory / "agents" / "openai.yaml"
    disable_field = fields.get("disable-model-invocation")
    claude_disabled = bool(disable_field and disable_field.value.lower() == "true")
    implicit = openai_policy(
        sidecar,
        findings,
        required=claude_disabled and profile == "codex",
    )
    if claude_disabled and implicit is True:
        add(
            findings,
            "error",
            "invocation-conflict",
            "Claude disables model invocation but Codex explicitly allows implicit invocation",
            sidecar,
        )
    if claude_disabled and not sidecar.is_file():
        severity = "error" if profile == "codex" else "warning"
        add(
            findings,
            severity,
            "codex-policy-absent",
            "Claude explicit-only metadata has no Codex agents/openai.yaml counterpart",
            sidecar,
        )
    if implicit is False and not claude_disabled:
        add(
            findings,
            "warning",
            "invocation-asymmetry",
            "Codex is explicit-only while Claude Code metadata does not suppress model invocation",
            sidecar,
        )


def inspect(directory: Path, profile: str = "auto") -> dict[str, object]:
    """Inspect one skill directory and return a serializable report."""
    findings: list[Finding] = []
    if not check_bundle_entries(directory, findings):
        return {
            "skill_directory": str(directory),
            "profile": profile,
            "summary": {"errors": len(findings), "warnings": 0},
            "findings": [asdict(item) for item in findings],
        }
    skill_path = directory / "SKILL.md"
    try:
        text = skill_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        add(findings, "error", "encoding", "SKILL.md is not valid UTF-8", skill_path)
        text = ""
    raw_frontmatter, body = split_frontmatter(text, skill_path, findings)
    fields = parse_frontmatter(raw_frontmatter, skill_path, findings) if raw_frontmatter else {}
    validate_fields(fields, directory, skill_path, profile, findings)
    if not body.strip():
        add(findings, "error", "body-empty", "SKILL.md body must not be empty", skill_path)
    line_count = len(text.splitlines())
    if line_count > 500:
        add(
            findings,
            "warning",
            "skill-size",
            f"SKILL.md has {line_count} lines; move detail into linked references",
            skill_path,
        )
    check_links(directory, findings)
    check_wrapper_parity(directory, raw_frontmatter, findings)
    check_invocation_extensions(directory, fields, profile, findings)
    findings.sort(key=lambda item: (item.severity != "error", item.path, item.line or 0, item.code))
    errors = sum(item.severity == "error" for item in findings)
    warnings = sum(item.severity == "warning" for item in findings)
    return {
        "skill_directory": str(directory),
        "profile": profile,
        "summary": {"errors": errors, "warnings": warnings},
        "findings": [asdict(item) for item in findings],
    }


def text_report(report: dict[str, object]) -> str:
    """Render the report for humans."""
    summary = report["summary"]
    assert isinstance(summary, dict)
    lines = [
        f"Skill: {report['skill_directory']}",
        f"Profile: {report['profile']}",
        f"Errors: {summary['errors']}  Warnings: {summary['warnings']}",
    ]
    findings = report["findings"]
    assert isinstance(findings, list)
    if not findings:
        lines.append("OK — no structural findings.")
    for item in findings:
        assert isinstance(item, dict)
        location = str(item["path"])
        if item.get("line"):
            location += f":{item['line']}"
        lines.append(
            f"{str(item['severity']).upper()} [{item['code']}] {location} — {item['message']}"
        )
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("skill_directory", help="skill directory or its SKILL.md")
    parser.add_argument(
        "--profile",
        choices=("auto", "agent-skills", "codex", "claude"),
        default="auto",
    )
    parser.add_argument("--format", choices=("text", "json"), default="text")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the inspector. Argparse and invalid targets exit 2."""
    parser = build_parser()
    args = parser.parse_args(argv)
    supplied = Path(args.skill_directory).expanduser().absolute()
    if supplied.name == "SKILL.md":
        supplied = supplied.parent
    if not supplied.is_dir():
        parser.error(f"skill directory does not exist: {supplied}")
    if not (supplied / "SKILL.md").is_file():
        parser.error(f"no SKILL.md in skill directory: {supplied}")
    report = inspect(supplied, args.profile)
    if args.format == "json":
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(text_report(report))
    summary = report["summary"]
    assert isinstance(summary, dict)
    return 1 if summary["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
