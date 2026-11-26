#!/usr/bin/env python3
"""Static contract, palette, ID-scope, and motion-safety linter for SVG illustrations.

Exit 0: PASS, 1: FAIL (contract violations), 2: invalid invocation or parse error.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET

HEX_RE = re.compile(r"#(?:[0-9a-fA-F]{8}|[0-9a-fA-F]{6}|[0-9a-fA-F]{4}|[0-9a-fA-F]{3})\b")
URL_RE = re.compile(r"url\([^)]*\)", re.IGNORECASE)
CSS_COMMENT_RE = re.compile(r"/\*.*?\*/", re.DOTALL)
REDUCED_MOTION_RULE_RE = re.compile(
    r"@media[^{]*prefers-reduced-motion\s*:\s*reduce[^{]*\{[^{}]*(?:\{[^{}]*\}[^{}]*)+\}",
    re.IGNORECASE | re.DOTALL,
)
SMIL_TAGS = {"animate", "animatetransform", "animatemotion", "set"}
COLOR_ATTRS = {"fill", "stroke", "stop-color", "flood-color", "lighting-color"}
ALLOWED_COLOR_KEYWORDS = {"none", "transparent", "currentcolor", "inherit", "context-fill", "context-stroke"}


def local_name(tag: str) -> str:
    if "}" in tag:
        return tag.rsplit("}", 1)[1].lower()
    return tag.lower()


def normalize_hex(token: str) -> str:
    raw = token.lower()
    if len(raw) == 4:
        return "#" + "".join(ch * 2 for ch in raw[1:])
    if len(raw) == 5:
        return "#" + "".join(ch * 2 for ch in raw[1:4])
    if len(raw) == 9:
        return raw[:7]
    return raw


def parse_viewbox(value: str | None) -> tuple[bool, str]:
    if not value or not value.strip():
        return False, "missing viewBox attribute on root <svg>"
    parts = re.split(r"[\s,]+", value.strip())
    if len(parts) != 4:
        return False, f"viewBox must have 4 numeric values, got {value!r}"
    try:
        nums = [float(p) for p in parts]
    except ValueError:
        return False, f"viewBox contains non-numeric values: {value!r}"
    if nums[2] <= 0 or nums[3] <= 0:
        return False, f"viewBox width and height must be positive, got {value!r}"
    return True, ""


def extract_color_values(elem: ET.Element) -> list[str]:
    raw_values: list[str] = []
    for attr in COLOR_ATTRS:
        val = elem.attrib.get(attr)
        if val:
            raw_values.append(val)
    style = elem.attrib.get("style", "")
    if style:
        for decl in style.split(";"):
            prop, sep, val = decl.partition(":")
            if sep and prop.strip().lower() in COLOR_ATTRS:
                raw_values.append(val)
    cleaned_values: list[str] = []
    for raw in raw_values:
        val = URL_RE.sub("", raw).strip()
        if not val:
            continue
        lower = val.lower()
        if lower in ALLOWED_COLOR_KEYWORDS or lower.startswith("var("):
            continue
        cleaned_values.append(val)
    return cleaned_values


def lint_svg_text(
    text: str,
    *,
    id_prefix: str | None = None,
    palette: set[str] | None = None,
    allow_style: bool = False,
    allow_image: bool = False,
    max_octaves: int = 2,
) -> dict:
    findings: list[dict] = []
    try:
        root = ET.fromstring(text)
    except ET.ParseError as exc:
        return {"status": "ERROR", "error": f"XML parse error: {exc}", "findings": []}

    if local_name(root.tag) != "svg":
        findings.append({"rule": "root-svg", "severity": "FAIL", "message": f"root element is <{local_name(root.tag)}>, expected <svg>"})

    ok_vb, vb_msg = parse_viewbox(root.attrib.get("viewBox"))
    if not ok_vb:
        findings.append({"rule": "viewbox", "severity": "FAIL", "message": vb_msg})

    seen_ids: set[str] = set()
    has_smil = False
    has_keyframes = False
    has_reduced_motion_css = False

    for elem in root.iter():
        tag = local_name(elem.tag)
        elem_id = elem.attrib.get("id")
        if elem_id is not None:
            if elem_id in seen_ids:
                findings.append({"rule": "duplicate-id", "severity": "FAIL", "message": f"duplicate id '{elem_id}'"})
            seen_ids.add(elem_id)
            if id_prefix and not elem_id.startswith(id_prefix):
                findings.append({"rule": "id-prefix", "severity": "FAIL", "message": f"id '{elem_id}' does not start with required prefix '{id_prefix}'"})

        if tag == "image" and not allow_image:
            findings.append({"rule": "no-raster-image", "severity": "FAIL", "message": "embedded <image> element violates pure-vector contract"})

        if tag == "style":
            css_text = CSS_COMMENT_RE.sub("", "".join(elem.itertext()))
            if "@keyframes" in css_text.lower():
                has_keyframes = True
            if REDUCED_MOTION_RULE_RE.search(css_text):
                has_reduced_motion_css = True
            if not allow_style:
                findings.append({"rule": "no-inline-style-tag", "severity": "FAIL", "message": "embedded <style> block can leak globally into host DOM"})

        if tag in SMIL_TAGS:
            has_smil = True

        if tag == "feturbulence":
            oct_raw = elem.attrib.get("numOctaves")
            if oct_raw is not None:
                try:
                    octaves = int(oct_raw.strip())
                    if octaves < 1 or octaves > max_octaves:
                        findings.append({"rule": "turbulence-octaves", "severity": "FAIL", "message": f"<feTurbulence numOctaves='{oct_raw}'> must be between 1 and {max_octaves}"})
                except ValueError:
                    findings.append({"rule": "turbulence-octaves", "severity": "FAIL", "message": f"invalid integer numOctaves value '{oct_raw}'"})

        if palette is not None:
            for color_val in extract_color_values(elem):
                if HEX_RE.fullmatch(color_val):
                    norm = normalize_hex(color_val)
                    if norm not in palette:
                        findings.append({"rule": "off-palette", "severity": "FAIL", "message": f"color '{color_val}' ({norm}) on <{tag}> is outside declared palette"})
                else:
                    findings.append({"rule": "off-palette", "severity": "FAIL", "message": f"non-hex color '{color_val}' on <{tag}> cannot be verified against declared hex palette"})

    if has_smil:
        findings.append({
            "rule": "reduced-motion",
            "severity": "FAIL",
            "message": "SMIL animation elements cannot be paused by CSS prefers-reduced-motion; drive animation via CSS or deterministic JS clock",
        })
    if has_keyframes and not has_reduced_motion_css:
        findings.append({
            "rule": "reduced-motion",
            "severity": "FAIL",
            "message": "animated SVG uses CSS @keyframes without a prefers-reduced-motion: reduce rule",
        })

    status = "FAIL" if any(f["severity"] == "FAIL" for f in findings) else "PASS"
    return {"status": status, "id_count": len(seen_ids), "findings": findings}


def parse_palette(raw: str | None) -> set[str] | None:
    if not raw:
        return None
    colors: set[str] = set()
    for part in raw.split(","):
        token = part.strip()
        if not token:
            continue
        if not HEX_RE.fullmatch(token):
            raise ValueError(f"invalid hex color in --palette: {token!r}")
        colors.add(normalize_hex(token))
    if not colors:
        raise ValueError("--palette must contain at least one hex color")
    return colors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("svg", type=Path, help="Path to local SVG file")
    parser.add_argument("--id-prefix", help="Required prefix for every id attribute")
    parser.add_argument("--palette", help="Comma-separated allowed hex colors, e.g. '#faf6ef,#1c1b18'")
    parser.add_argument("--allow-style", action="store_true", help="Permit <style> blocks inside the SVG")
    parser.add_argument("--allow-image", action="store_true", help="Permit embedded <image> tags")
    parser.add_argument("--max-octaves", type=int, default=2, help="Maximum allowed feTurbulence numOctaves (default 2)")
    args = parser.parse_args(argv)

    try:
        palette = parse_palette(args.palette)
        target = args.svg.resolve(strict=True)
        if not target.is_file():
            raise ValueError(f"target is not a file: {target}")
        text = target.read_text(encoding="utf-8")
    except (OSError, ValueError) as exc:
        print(json.dumps({"status": "ERROR", "error": str(exc)}, indent=2))
        return 2

    report = lint_svg_text(
        text,
        id_prefix=args.id_prefix,
        palette=palette,
        allow_style=args.allow_style,
        allow_image=args.allow_image,
        max_octaves=args.max_octaves,
    )
    report["file"] = str(target)
    print(json.dumps(report, indent=2))
    return {"PASS": 0, "FAIL": 1, "ERROR": 2}[report["status"]]


if __name__ == "__main__":
    raise SystemExit(main())
