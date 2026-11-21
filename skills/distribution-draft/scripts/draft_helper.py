#!/usr/bin/env python3
"""Deterministic character-counting and used-source ledger helper for distribution-draft."""

from __future__ import annotations

import argparse
from datetime import datetime
import json
import os
from pathlib import Path
import re
import stat
import sys
import unicodedata
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

URL_RE = re.compile(r"https?://[^\s<>\"'\)\]]+")
PLATFORMS = {"linkedin", "x"}
DECISIONS = {"accepted", "edited", "dropped"}


def is_wide_char(ch: str) -> bool:
    """Return True for codepoints outside standard single-weight Latin ranges."""
    code = ord(ch)
    if code <= 0x10FF:
        return False
    if 0x2000 <= code <= 0x200D or 0x2010 <= code <= 0x201F or 0x2032 <= code <= 0x2037:
        return False
    return True


def count_draft(
    text: str,
    platform: str,
    url_weight: int | None = None,
    wide_weight: int = 1,
    limit: int | None = None,
) -> dict[str, object]:
    """Measure normalized draft length with configurable URL and wide-character weights."""
    if platform not in PLATFORMS:
        raise ValueError("platform must be linkedin or x")
    if url_weight is not None and url_weight < 0:
        raise ValueError("--url-weight must be nonnegative")
    if wide_weight < 1:
        raise ValueError("--wide-weight must be at least 1")
    if limit is not None and limit < 1:
        raise ValueError("--limit must be at least 1")
    normalized = unicodedata.normalize("NFC", text)
    if not normalized.strip():
        raise ValueError("draft text must not be empty")

    urls = list(URL_RE.finditer(normalized))
    if url_weight is None:
        weighted = sum(wide_weight if is_wide_char(ch) else 1 for ch in normalized)
        url_rule = "raw (fixed URL length unconfirmed)"
    else:
        pieces = []
        cursor = 0
        for match in urls:
            pieces.append(normalized[cursor : match.start()])
            cursor = match.end()
        pieces.append(normalized[cursor:])
        non_url = "".join(pieces)
        weighted = sum(wide_weight if is_wide_char(ch) else 1 for ch in non_url) + len(urls) * url_weight
        url_rule = f"fixed:{url_weight}"

    within_limit = None if limit is None else weighted <= limit
    remaining = None if limit is None else limit - weighted
    rule_status = "configured" if (limit is not None and (url_weight is not None or not urls)) else "unconfirmed"
    return {
        "platform": platform,
        "normalized_chars": len(normalized),
        "weighted_chars": weighted,
        "urls_detected": len(urls),
        "url_rule": url_rule,
        "wide_weight": wide_weight,
        "limit": limit,
        "remaining": remaining,
        "within_limit": within_limit,
        "rule_status": rule_status,
    }


def normalize_source_key(key: str) -> str:
    """Normalize a source key; canonicalize HTTP/HTTPS URLs and trim tracking tags."""
    cleaned = key.strip()
    if not cleaned:
        raise ValueError("source key must not be empty")
    if cleaned.lower().startswith(("http://", "https://")):
        parsed = urlsplit(cleaned)
        if not parsed.hostname:
            raise ValueError("URL source key must include a hostname")
        scheme = parsed.scheme.lower()
        host = parsed.hostname.lower()
        port = parsed.port
        netloc = host if port in (None, 80 if scheme == "http" else 443) else f"{host}:{port}"
        path = parsed.path.rstrip("/") or "/"
        params = [(k, v) for k, v in parse_qsl(parsed.query, keep_blank_values=True) if not k.lower().startswith("utm_")]
        return urlunsplit((scheme, netloc, path, urlencode(params), ""))
    return cleaned


def assert_regular_or_missing(path: Path) -> None:
    """Reject symlinks and non-regular files to prevent unsafe writes or reads."""
    try:
        info = path.lstat()
    except FileNotFoundError:
        return
    if stat.S_ISLNK(info.st_mode):
        raise ValueError(f"refusing symlink path: {path}")
    if not stat.S_ISREG(info.st_mode):
        raise ValueError(f"expected a regular file: {path}")


def read_ledger(path: Path) -> list[dict[str, object]]:
    """Read and validate JSONL rows from an existing ledger file."""
    assert_regular_or_missing(path)
    if not path.exists():
        return []
    rows = []
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"ledger line {lineno}: invalid JSON: {exc}") from exc
        if not isinstance(obj, dict):
            raise ValueError(f"ledger line {lineno}: expected JSON object")
        rows.append(obj)
    return rows


def find_matches(rows: list[dict[str, object]], source_key: str, platform: str) -> list[dict[str, object]]:
    """Return ledger rows matching (normalized_source_key, platform)."""
    if platform not in PLATFORMS:
        raise ValueError("platform must be linkedin or x")
    target = normalize_source_key(source_key)
    matches = []
    for row in rows:
        src = row.get("source")
        row_key = src.get("key") if isinstance(src, dict) else None
        if row.get("platform") == platform and isinstance(row_key, str) and row_key.strip():
            if normalize_source_key(row_key) == target:
                matches.append(row)
    return matches


def validate_record(record: dict[str, object]) -> tuple[str, str]:
    """Validate a ledger row against the record contract before appending."""
    if not isinstance(record, dict):
        raise ValueError("record must be a JSON object")
    src = record.get("source")
    if not isinstance(src, dict) or not isinstance(src.get("key"), str) or not src["key"].strip():
        raise ValueError("record.source.key must be a nonempty string")
    if src.get("owner_confirmed") is not True:
        raise ValueError("record.source.owner_confirmed must be true")
    platform = record.get("platform")
    if platform not in PLATFORMS:
        raise ValueError("record.platform must be linkedin or x")
    decision = record.get("decision")
    if decision not in DECISIONS:
        raise ValueError("record.decision must be accepted, edited, or dropped")
    flags = record.get("flags")
    if flags != []:
        raise ValueError("record.flags must be empty ([]) before recording")
    decided_at = record.get("decided_at")
    if not isinstance(decided_at, str) or not decided_at.strip():
        raise ValueError("record.decided_at must be an ISO-8601 timestamp")
    try:
        parsed = datetime.fromisoformat(decided_at.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("record.decided_at must be a valid ISO-8601 timestamp") from exc
    if parsed.tzinfo is None:
        raise ValueError("record.decided_at must include a timezone")
    if decision == "dropped":
        if "text" in record and record["text"] is not None:
            raise ValueError("dropped drafts must omit text")
    elif not isinstance(record.get("text"), str) or not record["text"].strip():
        raise ValueError("accepted or edited drafts require nonempty text")
    return normalize_source_key(src["key"]), platform


def append_ledger(ledger_path: Path, record: dict[str, object], allow_new_angle: bool = False) -> dict[str, object]:
    """Validate and append one row to the JSONL ledger."""
    norm_key, platform = validate_record(record)
    rows = read_ledger(ledger_path)
    matches = find_matches(rows, norm_key, platform)
    if matches and not allow_new_angle:
        raise ValueError(f"source '{norm_key}' for {platform} already exists in ledger (pass --allow-new-angle to add)")
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(record, ensure_ascii=False) + "\n"
    with ledger_path.open("a", encoding="utf-8") as handle:
        handle.write(line)
    return {"status": "appended", "ledger": str(ledger_path), "normalized_key": norm_key, "platform": platform}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_count = sub.add_parser("count", help="Count normalized and weighted draft characters")
    p_count.add_argument("--platform", required=True, choices=sorted(PLATFORMS))
    src_group = p_count.add_mutually_exclusive_group(required=True)
    src_group.add_argument("--file", type=Path, help="Draft file path, or '-' for stdin")
    src_group.add_argument("--text", help="Draft text directly")
    p_count.add_argument("--url-weight", type=int, help="Fixed character weight per http/https URL")
    p_count.add_argument("--wide-weight", type=int, default=1, help="Weight for non-ASCII/emoji/CJK ranges (default 1)")
    p_count.add_argument("--limit", type=int, help="Confirmed platform character limit")

    p_check = sub.add_parser("ledger-check", help="Check whether (source_key, platform) is in the ledger")
    p_check.add_argument("--ledger", type=Path, required=True)
    p_check.add_argument("--source-key", required=True)
    p_check.add_argument("--platform", required=True, choices=sorted(PLATFORMS))

    p_append = sub.add_parser("ledger-append", help="Validate and append a decided row to the JSONL ledger")
    p_append.add_argument("--ledger", type=Path, required=True)
    p_append.add_argument("--record", type=Path, required=True, help="JSON file or '-' for stdin")
    p_append.add_argument("--allow-new-angle", action="store_true")

    args = parser.parse_args(argv)
    try:
        if args.cmd == "count":
            if args.text is not None:
                raw_text = args.text
            elif str(args.file) == "-":
                raw_text = sys.stdin.read()
            else:
                assert_regular_or_missing(args.file)
                raw_text = args.file.read_text(encoding="utf-8")
            result = count_draft(raw_text, args.platform, args.url_weight, args.wide_weight, args.limit)
            print(json.dumps(result, indent=2))
            return 1 if result["within_limit"] is False else 0

        if args.cmd == "ledger-check":
            rows = read_ledger(args.ledger)
            matches = find_matches(rows, args.source_key, args.platform)
            payload = {
                "matched": bool(matches),
                "match_count": len(matches),
                "normalized_key": normalize_source_key(args.source_key),
                "matches": matches,
            }
            print(json.dumps(payload, indent=2))
            return 1 if matches else 0

        if args.cmd == "ledger-append":
            if str(args.record) == "-":
                raw_json = sys.stdin.read()
            else:
                assert_regular_or_missing(args.record)
                raw_json = args.record.read_text(encoding="utf-8")
            record = json.loads(raw_json)
            try:
                out = append_ledger(args.ledger, record, allow_new_angle=args.allow_new_angle)
            except ValueError as exc:
                if "already exists in ledger" in str(exc):
                    print(json.dumps({"status": "duplicate", "error": str(exc)}), file=sys.stderr)
                    return 1
                raise
            print(json.dumps(out, indent=2))
            return 0
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "error", "error": str(exc)}), file=sys.stderr)
        return 2
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
