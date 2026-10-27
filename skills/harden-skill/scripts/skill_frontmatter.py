#!/usr/bin/env python3
"""Parse Agent Skill frontmatter and record structural findings."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

TOP_LEVEL_RE = re.compile(r"^([A-Za-z0-9_-]+):(?:[ \t]*(.*))?$")


@dataclass(frozen=True)
class Finding:
    """One structural result."""

    severity: str
    code: str
    message: str
    path: str
    line: int | None = None


@dataclass(frozen=True)
class Field:
    """A minimally parsed top-level frontmatter field."""

    value: str
    style: str
    line: int


def add(
    findings: list[Finding],
    severity: str,
    code: str,
    message: str,
    path: Path,
    line: int | None = None,
) -> None:
    """Append a finding with a stable path representation."""
    findings.append(Finding(severity, code, message, str(path), line))




def strip_inline_comment(value: str) -> str:
    """Strip a YAML comment outside simple single or double quotes."""
    quote: str | None = None
    escaped = False
    for index, char in enumerate(value):
        if quote == '"' and char == "\\" and not escaped:
            escaped = True
            continue
        if char in {'"', "'"} and not escaped:
            if quote is None:
                quote = char
            elif quote == char:
                quote = None
        if char == "#" and quote is None and (index == 0 or value[index - 1].isspace()):
            return value[:index].rstrip()
        escaped = False
    return value.rstrip()


def unquote_scalar(value: str) -> tuple[str, str]:
    """Resolve the small quoted-scalar subset needed for metadata checks."""
    value = strip_inline_comment(value.strip())
    if len(value) >= 2 and value[0] == value[-1] == "'":
        return value[1:-1].replace("''", "'"), "quoted"
    if len(value) >= 2 and value[0] == value[-1] == '"':
        try:
            resolved = json.loads(value)
        except json.JSONDecodeError:
            return value, "invalid-quoted"
        return str(resolved), "quoted"
    return value, "plain"


def split_frontmatter(text: str, path: Path, findings: list[Finding]) -> tuple[str, str]:
    """Return raw frontmatter and body, reporting delimiter failures."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        add(findings, "error", "frontmatter-missing", "SKILL.md must start with ---", path, 1)
        return "", text
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            return "\n".join(lines[1:index]), "\n".join(lines[index + 1 :])
    add(findings, "error", "frontmatter-unclosed", "frontmatter has no closing ---", path, 1)
    return "\n".join(lines[1:]), ""


def parse_frontmatter(raw: str, path: Path, findings: list[Finding]) -> dict[str, Field]:
    """Parse top-level YAML scalars and block scalars without accepting silent drift."""
    lines = raw.splitlines()
    fields: dict[str, Field] = {}
    index = 0
    while index < len(lines):
        line = lines[index]
        line_number = index + 2
        if not line.strip() or line.lstrip().startswith("#"):
            index += 1
            continue
        if line[0].isspace():
            add(
                findings,
                "error",
                "frontmatter-indent",
                "unexpected indented content outside a top-level field",
                path,
                line_number,
            )
            index += 1
            continue
        match = TOP_LEVEL_RE.match(line)
        if not match:
            add(
                findings,
                "error",
                "frontmatter-syntax",
                "invalid top-level YAML field",
                path,
                line_number,
            )
            index += 1
            continue
        key, raw_value = match.group(1), (match.group(2) or "")
        if key in fields:
            add(
                findings,
                "error",
                "frontmatter-duplicate",
                f"duplicate field {key!r}",
                path,
                line_number,
            )
        if raw_value in {">", ">-", ">+", "|", "|-", "|+"}:
            style = "folded" if raw_value.startswith(">") else "literal"
            block: list[str] = []
            index += 1
            while index < len(lines) and (not lines[index].strip() or lines[index][0].isspace()):
                current = lines[index]
                block.append(current[2:] if current.startswith("  ") else current.lstrip())
                index += 1
            if style == "folded":
                paragraphs = "\n".join(block).split("\n\n")
                value = "\n\n".join(
                    " ".join(part.splitlines()).strip() for part in paragraphs
                ).strip()
            else:
                value = "\n".join(block).strip()
            fields[key] = Field(value, style, line_number)
            continue
        if raw_value == "":
            nested: list[str] = []
            index += 1
            while index < len(lines) and (not lines[index].strip() or lines[index][0].isspace()):
                nested.append(lines[index])
                index += 1
            fields[key] = Field("\n".join(nested).strip(), "mapping", line_number)
            continue
        value, style = unquote_scalar(raw_value)
        if style == "invalid-quoted":
            add(
                findings,
                "error",
                "frontmatter-quote",
                f"invalid quoted value for {key!r}",
                path,
                line_number,
            )
        if style == "plain" and ": " in value:
            add(
                findings,
                "error",
                "frontmatter-colon",
                f"plain scalar for {key!r} contains ': '; quote it or use a block scalar",
                path,
                line_number,
            )
        fields[key] = Field(value, style, line_number)
        index += 1
    return fields
