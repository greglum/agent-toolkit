#!/usr/bin/env python3
"""Reconcile a local extraction manifest with the explicitly requested inputs.

Exit 0: reconciled, including declared failed/unsupported inputs; 1: mismatch;
2: unreadable/invalid manifest. This checks files and declarations, not content fidelity.
"""

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path


STATUSES = {"verified", "partial", "failed", "unsupported"}


def digest(path):
    checksum = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            checksum.update(chunk)
    return checksum.hexdigest()


def local_path(value, root, label):
    if not isinstance(value, str) or not value or "://" in value:
        raise ValueError(f"{label}: expected a local file path")
    path = (root / value).resolve()
    if not path.is_relative_to(root):
        raise ValueError(f"{label}: path leaves the declared bundle root")
    return path


def strings(value):
    return isinstance(value, list) and all(isinstance(item, str) and item.strip() for item in value)


def reconcile(manifest, inputs, root):
    entries = manifest.get("sources") if isinstance(manifest, dict) else manifest
    if not isinstance(entries, list):
        raise ValueError("manifest: expected a list or an object with a sources list")
    requested = [local_path(str(path), root, "input") for path in inputs]
    if len(requested) != len(set(requested)):
        raise ValueError("input: duplicate paths in the requested corpus")
    expected = set(requested)
    original_identities = set()
    for source in expected:
        try:
            info = source.stat()
        except OSError:
            # Failed/unsupported sources may be unreadable; their status is checked below.
            continue
        original_identities.add((info.st_dev, info.st_ino))
    seen_paths, seen_ids, errors, counts = set(), set(), [], Counter()
    for ordinal, entry in enumerate(entries, 1):
        label = f"source {ordinal}"
        if not isinstance(entry, dict):
            errors.append(f"{label}: expected an object")
            continue
        identity = entry.get("source_id")
        if not isinstance(identity, str) or not identity.strip() or identity in seen_ids:
            errors.append(f"{label}: missing or duplicate source_id")
        elif identity:
            seen_ids.add(identity)
        try:
            source = local_path(entry.get("source"), root, label)
        except (ValueError, OSError) as error:
            errors.append(str(error))
            continue
        if source in seen_paths:
            errors.append(f"{label}: duplicate source path")
        seen_paths.add(source)
        if source not in expected:
            errors.append(f"{label}: source was not requested")
            continue
        status = entry.get("status")
        if status not in STATUSES:
            errors.append(f"{label}: invalid status")
            continue
        counts[status] += 1
        for field in ("known_loss", "errors"):
            if not strings(entry.get(field)):
                errors.append(f"{label}: {field} must be a list of nonempty strings")
        if status == "partial" and not entry.get("known_loss"):
            errors.append(f"{label}: partial extraction needs its known loss or uncertainty")
        if status in {"failed", "unsupported"} and not entry.get("errors"):
            errors.append(f"{label}: failed or unsupported input needs a reason")
        try:
            source_hash = digest(source)
        except OSError:
            source_hash = None
            if status not in {"failed", "unsupported"}:
                errors.append(f"{label}: source is unreadable")
        if entry.get("source_sha256") != source_hash:
            errors.append(f"{label}: source hash is missing or no longer matches")
        tool = entry.get("tool")
        if (tool is not None or status in {"verified", "partial"}) and (
                not isinstance(tool, dict) or not isinstance(tool.get("name"), str)
                or not tool["name"].strip() or "version" not in tool
                or (tool["version"] is not None and not isinstance(tool["version"], str))):
            errors.append(f"{label}: record the converter name and version (null if unknown)")
        verification = entry.get("verification")
        if not isinstance(verification, dict):
            errors.append(f"{label}: missing verification record")
            continue
        coverage = verification.get("coverage")
        if coverage not in {"full", "sampled", "none"}:
            errors.append(f"{label}: invalid verification coverage")
        if status == "verified" and coverage == "none":
            errors.append(f"{label}: verified status has no verification coverage")
        locators = verification.get("locators")
        if not isinstance(locators, list) or any(
                not isinstance(item, dict) or not isinstance(item.get("source"), str)
                or not item["source"].strip() or not isinstance(item.get("output"), str)
                or not item["output"].strip() for item in locators):
            errors.append(f"{label}: locators must map nonempty source/output descriptions")
        output = entry.get("output")
        if output is None:
            if status in {"verified", "partial"}:
                errors.append(f"{label}: successful or partial extraction has no output")
            continue
        if not isinstance(output, dict):
            errors.append(f"{label}: output must be null or a path/hash object")
            continue
        try:
            output_path = local_path(output.get("path"), root, label + " output")
            if not output_path.is_file():
                raise ValueError(f"{label}: output is not a readable file")
            output_info = output_path.stat()
            if output_path in expected or (output_info.st_dev, output_info.st_ino) in original_identities:
                errors.append(f"{label}: output aliases a requested original")
            if output_info.st_size == 0 and status == "verified":
                errors.append(f"{label}: empty output cannot establish verified extraction")
            if output.get("sha256") != digest(output_path):
                errors.append(f"{label}: output hash is missing or no longer matches")
        except (ValueError, OSError) as error:
            errors.append(str(error))
    missing = len(expected - seen_paths)
    if missing:
        errors.append(f"manifest omits {missing} requested input(s)")
    return {"status": "MISMATCH" if errors else "RECONCILED",
            "scope": "local file identity, declared coverage and manifest accounting only",
            "requested_inputs": len(expected), "manifest_entries": len(entries),
            "source_statuses": dict(counts), "errors": errors,
            "content_fidelity": "not established by this checker"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--root", type=Path, help="bundle root; default: manifest parent")
    parser.add_argument("--input", action="append", required=True,
                        help="one explicitly requested local source; repeat for each input")
    args = parser.parse_args()
    try:
        manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
        report = reconcile(manifest, args.input, (args.root or args.manifest.parent).resolve())
    except (OSError, ValueError, TypeError) as error:
        print(json.dumps({"status": "UNAVAILABLE", "error": str(error)}))
        return 2
    print(json.dumps(report, indent=2))
    return 0 if report["status"] == "RECONCILED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
