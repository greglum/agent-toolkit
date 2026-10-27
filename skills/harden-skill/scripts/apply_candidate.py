#!/usr/bin/env python3
"""Snapshot and safely apply a staged Agent Skill candidate."""

from __future__ import annotations

import argparse
import json
import shutil
import stat
import sys
import tempfile
from pathlib import Path
from typing import Any

from bundle_manifest import (  # noqa: F401  Re-exported for callers and tests.
    ApplyError,
    file_hash,
    file_state,
    tree_files,
    guard_output_path,
    normalize_bundle_paths,
    bundle_path,
    bundle_entries,
    validate_file_state,
    flatten_bundle_files,
    normalize_deletion_paths,
    write_bundle_manifest,
    read_bundle_manifest,
    write_manifest,
    read_manifest,
)


def build_plan(
    target: Path, candidate: Path, baseline: dict[str, dict[str, Any]]
) -> dict[str, Any]:
    """Validate live drift and return the exact candidate synchronization plan."""
    current = tree_files(target)
    staged = tree_files(candidate)

    drifted = sorted(path for path, state in baseline.items() if current.get(path) != state)
    if drifted:
        raise ApplyError(f"live target drifted after snapshot: {', '.join(drifted)}")

    post_snapshot = sorted(set(current) - set(baseline))
    collisions = sorted(path for path in post_snapshot if path in staged)
    if collisions:
        raise ApplyError("candidate would overwrite post-snapshot files: " + ", ".join(collisions))

    return {
        "write": sorted(path for path, state in staged.items() if baseline.get(path) != state),
        "delete": sorted(set(baseline) - set(staged)),
        "preserve": post_snapshot,
        "_target_files": current,
        "_candidate_files": staged,
    }


def build_bundle_plan(
    target_root: Path,
    candidate_root: Path,
    baseline: dict[str, Any],
    candidate_manifest: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Validate a selected live bundle and return one synchronization plan."""
    paths = baseline["paths"]
    baseline_entries = baseline["entries"]
    current_entries = bundle_entries(target_root, paths)
    staged_entries = bundle_entries(candidate_root, paths)
    candidate_deletions: set[str] = set()
    if candidate_manifest is not None:
        if candidate_manifest["paths"] != paths:
            raise ApplyError("candidate bundle selects different paths from the baseline")
        if candidate_manifest["entries"] != staged_entries:
            raise ApplyError("candidate bundle differs from its validated manifest")
        candidate_deletions = set(candidate_manifest["deletions"])

    for relative in paths:
        baseline_kind = baseline_entries[relative]["kind"]
        current_kind = current_entries[relative]["kind"]
        staged_kind = staged_entries[relative]["kind"]
        if baseline_kind != "absent" and current_kind != baseline_kind:
            raise ApplyError(f"live bundle path drifted after snapshot: {relative}")
        if baseline_kind != "absent" and staged_kind not in {baseline_kind, "absent"}:
            raise ApplyError(f"candidate changes bundle path kind: {relative}")
        if baseline_kind != "absent" and staged_kind == "absent":
            if relative not in candidate_deletions:
                raise ApplyError(
                    "candidate bundle path is absent without an explicit deletion: " + relative
                )
        elif relative in candidate_deletions:
            raise ApplyError(f"candidate deletion path was absent at baseline: {relative}")
        if baseline_kind == "absent" and current_kind != "absent" and staged_kind != "absent":
            raise ApplyError(f"candidate would overwrite post-snapshot path: {relative}")

    baseline_files = flatten_bundle_files(baseline_entries)
    current_files = flatten_bundle_files(current_entries)
    staged_files = flatten_bundle_files(staged_entries)
    drifted = sorted(
        path for path, state in baseline_files.items() if current_files.get(path) != state
    )
    if drifted:
        raise ApplyError(f"live bundle drifted after snapshot: {', '.join(drifted)}")
    post_snapshot = sorted(set(current_files) - set(baseline_files))
    collisions = sorted(path for path in post_snapshot if path in staged_files)
    if collisions:
        raise ApplyError(
            "candidate would overwrite post-snapshot bundle files: " + ", ".join(collisions)
        )

    return {
        "write": sorted(
            path for path, state in staged_files.items() if baseline_files.get(path) != state
        ),
        "delete": sorted(set(baseline_files) - set(staged_files)),
        "preserve": post_snapshot,
        "_paths": paths,
        "_target_entries": current_entries,
        "_candidate_entries": staged_entries,
    }


def public_plan(plan: dict[str, object]) -> dict[str, object]:
    """Return the stable user-facing portion of an internal synchronization plan."""
    return {key: plan[key] for key in ("write", "delete", "preserve")}


def restore_tree(target: Path, snapshot: Path) -> None:
    """Restore the exact pre-apply target tree after an application failure."""
    shutil.rmtree(target)
    shutil.copytree(snapshot, target)


def remove_path(path: Path) -> None:
    """Remove one existing non-symlink file or directory."""
    if path.is_symlink():
        raise ApplyError(f"refusing to remove symbolic link: {path}")
    if path.is_dir():
        shutil.rmtree(path)
    elif path.exists():
        path.unlink()


def copy_candidate_file(source: Path, destination: Path, candidate_state: dict[str, Any]) -> None:
    """Copy content while changing only the Git-relevant executable mode."""
    shutil.copyfile(source, destination)
    current_mode = stat.S_IMODE(destination.stat().st_mode)
    current_executable = bool(current_mode & 0o111)
    if current_executable == candidate_state["executable"]:
        executable_mode = current_mode
    elif candidate_state["executable"]:
        executable_mode = current_mode | stat.S_IXUSR
    else:
        executable_mode = current_mode & ~0o111
    destination.chmod(executable_mode)


def snapshot_bundle_paths(root: Path, paths: list[str], snapshot: Path) -> None:
    """Copy the selected live state, including post-snapshot additions, for rollback."""
    snapshot.mkdir(parents=True, exist_ok=False)
    for relative in paths:
        source = bundle_path(root, relative)
        destination = snapshot / relative
        if source.is_dir():
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(source, destination)
        elif source.is_file():
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)


def restore_bundle_paths(root: Path, paths: list[str], snapshot: Path) -> None:
    """Restore every selected path to its pre-apply state."""
    for relative in sorted(paths, key=lambda value: len(Path(value).parts), reverse=True):
        remove_path(bundle_path(root, relative))
    for relative in paths:
        source = snapshot / relative
        destination = root / relative
        if source.is_dir():
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(source, destination)
        elif source.is_file():
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)


def apply_plan(
    target: Path,
    candidate: Path,
    plan: dict[str, object],
    rollback_root: Path | None,
) -> Path:
    """Apply a validated plan and return the retained rollback snapshot path."""
    expected_target = plan.get("_target_files")
    expected_candidate = plan.get("_candidate_files")
    if tree_files(target) != expected_target:
        raise ApplyError("live target changed after the synchronization plan was built")
    if tree_files(candidate) != expected_candidate:
        raise ApplyError("candidate changed after the synchronization plan was built")

    protected_paths = [target, candidate]
    protected_files = [target / relative for relative in expected_target] + [
        candidate / relative for relative in expected_candidate
    ]
    if rollback_root is None:
        temporary_parent = guard_output_path(Path(tempfile.gettempdir()), protected_paths, [])
        root = Path(tempfile.mkdtemp(prefix="harden-skill-rollback-", dir=temporary_parent))
    else:
        root = rollback_root
    snapshot = guard_output_path(root / target.name, protected_paths, protected_files)
    snapshot.parent.mkdir(parents=True, exist_ok=True)
    if snapshot.exists():
        raise ApplyError(f"rollback snapshot already exists: {snapshot}")
    shutil.copytree(target, snapshot)
    if tree_files(target) != expected_target:
        raise ApplyError("live target changed while the rollback snapshot was created")
    if tree_files(candidate) != expected_candidate:
        raise ApplyError("candidate changed while the rollback snapshot was created")
    try:
        for relative in plan["write"]:  # type: ignore[union-attr]
            source = candidate / relative
            destination = target / relative
            expected_state = expected_target.get(relative)  # type: ignore[union-attr]
            candidate_state = expected_candidate[relative]  # type: ignore[index]
            if file_state(source) != candidate_state:
                raise ApplyError(f"candidate changed before write: {relative}")
            if destination.is_symlink():
                raise ApplyError(f"live target changed before write: {relative}")
            if destination.exists():
                if file_state(destination) != expected_state:
                    raise ApplyError(f"live target changed before write: {relative}")
            elif expected_state is not None:
                raise ApplyError(f"live target file disappeared before write: {relative}")
            destination.parent.mkdir(parents=True, exist_ok=True)
            copy_candidate_file(source, destination, candidate_state)
            if file_state(destination) != candidate_state:
                raise ApplyError(f"candidate state was not preserved while writing: {relative}")
        for relative in plan["delete"]:  # type: ignore[union-attr]
            path = target / relative
            if path.is_symlink() or file_state(path) != expected_target[relative]:  # type: ignore[index]
                raise ApplyError(f"live target changed before delete: {relative}")
            path.unlink()
            parent = path.parent
            while parent != target and not any(parent.iterdir()):
                parent.rmdir()
                parent = parent.parent
    except Exception:
        restore_tree(target, snapshot)
        raise
    return snapshot


def apply_bundle_plan(
    target_root: Path,
    candidate_root: Path,
    plan: dict[str, Any],
    rollback_root: Path | None,
) -> Path:
    """Apply one selected-path transaction and roll back every path on failure."""
    paths = plan["_paths"]
    expected_target = plan["_target_entries"]
    expected_candidate = plan["_candidate_entries"]
    if bundle_entries(target_root, paths) != expected_target:
        raise ApplyError("live bundle changed after the synchronization plan was built")
    if bundle_entries(candidate_root, paths) != expected_candidate:
        raise ApplyError("candidate bundle changed after the synchronization plan was built")

    protected_paths = [
        bundle_path(protected_root, relative)
        for protected_root in (target_root, candidate_root)
        for relative in paths
    ]
    protected_files = [target_root / relative for relative in flatten_bundle_files(expected_target)] + [
        candidate_root / relative for relative in flatten_bundle_files(expected_candidate)
    ]
    if rollback_root is None:
        temporary_parent = guard_output_path(Path(tempfile.gettempdir()), protected_paths, [])
        root = Path(tempfile.mkdtemp(prefix="harden-skill-bundle-rollback-", dir=temporary_parent))
    else:
        root = rollback_root
    snapshot = guard_output_path(root / "bundle", protected_paths, protected_files)
    snapshot.parent.mkdir(parents=True, exist_ok=True)
    if snapshot.exists():
        raise ApplyError(f"rollback snapshot already exists: {snapshot}")
    snapshot_bundle_paths(target_root, paths, snapshot)
    if bundle_entries(target_root, paths) != expected_target:
        raise ApplyError("live bundle changed while the rollback snapshot was created")
    if bundle_entries(candidate_root, paths) != expected_candidate:
        raise ApplyError("candidate bundle changed while the rollback snapshot was created")

    target_files = flatten_bundle_files(expected_target)
    candidate_files = flatten_bundle_files(expected_candidate)
    try:
        for relative in plan["write"]:
            source = bundle_path(candidate_root, relative)
            destination = bundle_path(target_root, relative)
            expected_state = target_files.get(relative)
            candidate_state = candidate_files[relative]
            if file_state(source) != candidate_state:
                raise ApplyError(f"candidate bundle changed before write: {relative}")
            if destination.exists():
                if file_state(destination) != expected_state:
                    raise ApplyError(f"live bundle changed before write: {relative}")
            elif expected_state is not None:
                raise ApplyError(f"live bundle file disappeared before write: {relative}")
            destination.parent.mkdir(parents=True, exist_ok=True)
            copy_candidate_file(source, destination, candidate_state)
            if file_state(destination) != candidate_state:
                raise ApplyError(f"candidate state was not preserved while writing: {relative}")
        for relative in plan["delete"]:
            path = bundle_path(target_root, relative)
            if file_state(path) != target_files[relative]:
                raise ApplyError(f"live bundle changed before delete: {relative}")
            path.unlink()
            parent = path.parent
            while parent != target_root and not any(parent.iterdir()):
                parent.rmdir()
                parent = parent.parent
    except Exception:
        restore_bundle_paths(target_root, paths, snapshot)
        raise
    return snapshot


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line interface."""
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    snapshot = subparsers.add_parser("snapshot", help="Record baseline hashes for a target.")
    snapshot.add_argument("target", type=Path)
    snapshot.add_argument("manifest", type=Path)

    snapshot_bundle = subparsers.add_parser(
        "snapshot-bundle", help="Record file states for selected paths below a root."
    )
    snapshot_bundle.add_argument("root", type=Path)
    snapshot_bundle.add_argument("manifest", type=Path)
    snapshot_bundle.add_argument("--path", action="append", required=True, dest="paths")
    snapshot_bundle.add_argument(
        "--delete-path",
        action="append",
        default=[],
        dest="deletion_paths",
        help="Declare one selected path intentionally absent from a candidate bundle.",
    )

    apply = subparsers.add_parser("apply", help="Preview or apply a staged candidate.")
    apply.add_argument("target", type=Path)
    apply.add_argument("candidate", type=Path)
    apply.add_argument("manifest", type=Path)
    apply.add_argument(
        "--candidate-manifest",
        type=Path,
        help="Manifest created from the validated candidate; required with --apply.",
    )
    apply.add_argument(
        "--apply",
        action="store_true",
        help="Perform the synchronization; without this flag the command is a dry run.",
    )
    apply.add_argument("--rollback-root", type=Path)

    apply_bundle = subparsers.add_parser(
        "apply-bundle", help="Preview or atomically apply a selected-path candidate bundle."
    )
    apply_bundle.add_argument("target_root", type=Path)
    apply_bundle.add_argument("candidate_root", type=Path)
    apply_bundle.add_argument("manifest", type=Path)
    apply_bundle.add_argument("--candidate-manifest", type=Path)
    apply_bundle.add_argument("--apply", action="store_true")
    apply_bundle.add_argument("--rollback-root", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the snapshot or application command."""
    args = build_parser().parse_args(argv)
    try:
        if args.command == "snapshot":
            write_manifest(args.target, args.manifest)
            print(f"baseline manifest: {args.manifest}")
            return 0

        if args.command == "snapshot-bundle":
            write_bundle_manifest(args.root, args.paths, args.manifest, args.deletion_paths)
            print(f"bundle manifest: {args.manifest}")
            return 0

        if args.command == "apply-bundle":
            baseline_bundle = read_bundle_manifest(args.manifest, args.target_root)
            if args.apply and args.candidate_manifest is None:
                raise ApplyError("--candidate-manifest is required with --apply")
            candidate_bundle = (
                read_bundle_manifest(args.candidate_manifest, args.candidate_root)
                if args.candidate_manifest is not None
                else None
            )
            bundle_plan = build_bundle_plan(
                args.target_root,
                args.candidate_root,
                baseline_bundle,
                candidate_bundle,
            )
            if not args.apply:
                print(json.dumps({"mode": "dry-run", **public_plan(bundle_plan)}, indent=2))
                return 0
            rollback = apply_bundle_plan(
                args.target_root, args.candidate_root, bundle_plan, args.rollback_root
            )
            print(
                json.dumps(
                    {
                        "mode": "applied",
                        "rollback": str(rollback),
                        **public_plan(bundle_plan),
                    },
                    indent=2,
                )
            )
            return 0

        baseline = read_manifest(args.manifest, args.target)
        if args.apply and args.candidate_manifest is None:
            raise ApplyError("--candidate-manifest is required with --apply")
        if args.candidate_manifest is not None:
            expected_candidate = read_manifest(args.candidate_manifest, args.candidate)
            if tree_files(args.candidate) != expected_candidate:
                raise ApplyError("candidate differs from its validated manifest")
        plan = build_plan(args.target, args.candidate, baseline)
        if not args.apply:
            print(json.dumps({"mode": "dry-run", **public_plan(plan)}, indent=2))
            return 0
        rollback = apply_plan(args.target, args.candidate, plan, args.rollback_root)
        print(
            json.dumps(
                {"mode": "applied", "rollback": str(rollback), **public_plan(plan)}, indent=2
            )
        )
        return 0
    except (ApplyError, OSError) as exc:
        print(f"[apply-candidate] error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
