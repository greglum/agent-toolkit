#!/usr/bin/env python3
"""Hash, select, and record the files of a skill tree or bundle."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from inspect_skill import check_bundle_entries


class ApplyError(Exception):
    """A safety condition that prevents candidate application."""


def file_hash(path: Path) -> str:
    """Return a SHA-256 digest for one file."""
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def file_state(path: Path) -> dict[str, str | bool]:
    """Return content and Git-relevant executable state for one file."""
    return {
        "sha256": file_hash(path),
        "executable": bool(path.stat().st_mode & 0o111),
    }


def tree_files(root: Path) -> dict[str, dict[str, str | bool]]:
    """Return sorted relative file states for a directory tree."""
    if root.is_symlink() or not root.is_dir():
        raise ApplyError(f"directory does not exist: {root}")
    findings = []
    if not check_bundle_entries(root, findings):
        reason = "symbolic links are not allowed: " if any(
            finding.code == "bundle-symlink" for finding in findings
        ) else "invalid bundle entries: "
        raise ApplyError(reason + "; ".join(
            f"{finding.path}: {finding.message}" for finding in findings
        ))
    paths = sorted(root.rglob("*"))
    return {path.relative_to(root).as_posix(): file_state(path) for path in paths if path.is_file()}


def guard_output_path(
    output: Path, protected_paths: list[Path], protected_files: list[Path]
) -> Path:
    """Keep generated manifests and rollback snapshots outside their inputs."""
    resolved = output.resolve()
    if any(resolved.is_relative_to(path.resolve()) for path in protected_paths):
        raise ApplyError(f"output path overlaps protected input: {output}")
    if resolved.exists() and any(resolved.samefile(path) for path in protected_files):
        raise ApplyError(f"output aliases protected input file: {output}")
    return resolved


def normalize_bundle_paths(paths: list[str]) -> list[str]:
    """Validate and normalize a non-overlapping repo-relative path selection."""
    normalized: list[str] = []
    for raw in paths:
        supplied = Path(raw)
        if (
            supplied.is_absolute()
            or not supplied.parts
            or any(part == ".." for part in supplied.parts)
        ):
            raise ApplyError(f"bundle path must be repo-relative without traversal: {raw}")
        relative = supplied.as_posix().strip("/")
        if not relative or relative == ".":
            raise ApplyError("bundle path must select a file or directory below the root")
        if relative in normalized:
            raise ApplyError(f"duplicate bundle path: {relative}")
        normalized.append(relative)

    normalized.sort()
    for index, relative in enumerate(normalized):
        prefix = relative + "/"
        for other in normalized[index + 1 :]:
            if other.startswith(prefix):
                raise ApplyError(f"overlapping bundle paths are not allowed: {relative}, {other}")
    return normalized


def bundle_path(root: Path, relative: str) -> Path:
    """Resolve one selected path while rejecting symlinks in every path component."""
    selected = root
    for part in Path(relative).parts:
        selected /= part
        if selected.is_symlink():
            raise ApplyError(f"symbolic links are not allowed: {relative}")
    return selected


def bundle_entries(root: Path, paths: list[str]) -> dict[str, dict[str, Any]]:
    """Return kind and file states for selected file, directory, or absent paths."""
    if root.is_symlink() or not root.is_dir():
        raise ApplyError(f"bundle root does not exist: {root}")
    entries: dict[str, dict[str, Any]] = {}
    for relative in normalize_bundle_paths(paths):
        selected = bundle_path(root, relative)
        if not selected.exists():
            entries[relative] = {"kind": "absent", "files": {}}
        elif selected.is_file():
            entries[relative] = {"kind": "file", "files": {relative: file_state(selected)}}
        elif selected.is_dir():
            entries[relative] = {
                "kind": "directory",
                "files": {
                    f"{relative}/{path}": state for path, state in tree_files(selected).items()
                },
            }
        else:
            raise ApplyError(f"unsupported bundle path: {relative}")
    return entries


def validate_file_state(state: object, context: str) -> None:
    """Validate one portable file-state manifest value."""
    if (
        not isinstance(state, dict)
        or set(state) != {"sha256", "executable"}
        or not isinstance(state["sha256"], str)
        or not isinstance(state["executable"], bool)
    ):
        raise ApplyError(f"invalid bundle manifest file state: {context}")


def flatten_bundle_files(entries: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """Flatten validated bundle entry states into one repo-relative mapping."""
    files: dict[str, dict[str, Any]] = {}
    for relative, entry in entries.items():
        kind = entry.get("kind")
        entry_files = entry.get("files")
        if kind not in {"absent", "file", "directory"} or not isinstance(entry_files, dict):
            raise ApplyError(f"invalid bundle manifest entry: {relative}")
        if kind == "absent" and entry_files:
            raise ApplyError(f"absent bundle entry contains files: {relative}")
        if kind == "file" and set(entry_files) != {relative}:
            raise ApplyError(f"file bundle entry has an invalid path: {relative}")
        for path, state in entry_files.items():
            if not isinstance(path, str):
                raise ApplyError(f"invalid bundle manifest file path: {relative}")
            validate_file_state(state, relative)
            supplied = Path(path)
            if (
                supplied.is_absolute()
                or any(part == ".." for part in supplied.parts)
                or supplied.as_posix() != path
            ):
                raise ApplyError(f"invalid bundle file path: {path}")
            if kind == "directory" and not path.startswith(relative + "/"):
                raise ApplyError(f"bundle file escapes selected directory: {path}")
            if path in files:
                raise ApplyError(f"duplicate bundle file path: {path}")
            files[path] = state
    return files


def normalize_deletion_paths(paths: list[str], selected_paths: list[str]) -> list[str]:
    """Validate explicit deletion intents for exact selected bundle paths."""
    normalized = normalize_bundle_paths(paths) if paths else []
    unknown = sorted(set(normalized) - set(selected_paths))
    if unknown:
        raise ApplyError("deletion paths must be selected bundle paths: " + ", ".join(unknown))
    return normalized


def write_bundle_manifest(
    root: Path,
    paths: list[str],
    manifest_path: Path,
    deletion_paths: list[str] | None = None,
) -> None:
    """Write file states for an exact selected-path bundle."""
    normalized = normalize_bundle_paths(paths)
    deletions = normalize_deletion_paths(deletion_paths or [], normalized)
    entries = bundle_entries(root, normalized)
    present_deletions = [path for path in deletions if entries[path]["kind"] != "absent"]
    if present_deletions:
        raise ApplyError(
            "explicit deletion paths must be absent from the bundle: "
            + ", ".join(present_deletions)
        )
    payload = {
        "root": str(root.resolve()),
        "paths": normalized,
        "deletions": deletions,
        "entries": entries,
    }
    manifest_path = guard_output_path(
        manifest_path,
        [bundle_path(root, relative) for relative in normalized],
        [root / relative for relative in flatten_bundle_files(entries)],
    )
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def read_bundle_manifest(manifest_path: Path, root: Path) -> dict[str, Any]:
    """Load and validate one selected-path bundle manifest."""
    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ApplyError(f"cannot read bundle manifest: {manifest_path}") from exc
    if payload.get("root") != str(root.resolve()):
        raise ApplyError("bundle manifest root does not match the selected root")
    raw_paths = payload.get("paths")
    raw_deletions = payload.get("deletions", [])
    entries = payload.get("entries")
    if not isinstance(raw_paths, list) or not all(isinstance(path, str) for path in raw_paths):
        raise ApplyError("bundle manifest paths must be a list of strings")
    paths = normalize_bundle_paths(raw_paths)
    if not isinstance(raw_deletions, list) or not all(
        isinstance(path, str) for path in raw_deletions
    ):
        raise ApplyError("bundle manifest deletions must be a list of strings")
    deletions = normalize_deletion_paths(raw_deletions, paths)
    if raw_paths != paths or not isinstance(entries, dict) or set(entries) != set(paths):
        raise ApplyError("bundle manifest paths and entries do not match")
    flatten_bundle_files(entries)
    present_deletions = [path for path in deletions if entries[path]["kind"] != "absent"]
    if present_deletions:
        raise ApplyError(
            "explicit deletion paths must be absent from the bundle: "
            + ", ".join(present_deletions)
        )
    return {"paths": paths, "deletions": deletions, "entries": entries}


def write_manifest(target: Path, manifest_path: Path) -> None:
    """Write a baseline manifest for the current target tree."""
    files = tree_files(target)
    payload = {"target": str(target.resolve()), "files": files}
    manifest_path = guard_output_path(
        manifest_path, [target], [target / relative for relative in files]
    )
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def read_manifest(manifest_path: Path, target: Path) -> dict[str, dict[str, Any]]:
    """Load and validate a baseline manifest for the selected target."""
    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ApplyError(f"cannot read baseline manifest: {manifest_path}") from exc
    if payload.get("target") != str(target.resolve()):
        raise ApplyError("baseline manifest target does not match the live target")
    files = payload.get("files")
    if not isinstance(files, dict) or not all(isinstance(path, str) for path in files):
        raise ApplyError("baseline manifest files must be a path-to-state mapping")
    for path, state in files.items():
        validate_file_state(state, path)
    return files
