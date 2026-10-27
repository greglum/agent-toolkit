#!/usr/bin/env python3
# ruff: noqa: D102
"""Regression coverage for bundle snapshots, entry guards, and bundle application."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from candidate_fixtures import APPLY, MANIFEST, SCRIPT, CandidateTrees


class ApplyBundleTests(CandidateTrees, unittest.TestCase):
    """Exercise bundle selection, drift, permissions, deletion, and rollback."""

    @unittest.skipUnless(hasattr(os, "mkfifo"), "named pipes are not available")
    def test_special_bundle_entry_blocks_snapshot_before_content_reads(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            os.mkfifo(root / "unrepresented-entry")
            (root / "SKILL.md").write_text("baseline\n", encoding="utf-8")
            with mock.patch.object(MANIFEST, "file_hash", side_effect=AssertionError("content read")):
                with self.assertRaisesRegex(APPLY.ApplyError, "nonregular entry"):
                    APPLY.tree_files(root)

    def test_bundle_dry_run_covers_canonical_wrapper_and_shared_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            target, candidate, baseline_path, candidate_path, _paths = self.make_bundle_trees(root)
            baseline = APPLY.read_bundle_manifest(baseline_path, target)
            candidate_manifest = APPLY.read_bundle_manifest(candidate_path, candidate)

            plan = APPLY.build_bundle_plan(target, candidate, baseline, candidate_manifest)

            self.assertEqual(
                plan["write"],
                [
                    ".agents/skills/demo/SKILL.md",
                    ".agents/skills/demo/added.txt",
                    ".claude/skills/demo/SKILL.md",
                    "setup/repo/skill_evals.json",
                ],
            )
            self.assertEqual(plan["delete"], [".agents/skills/demo/obsolete.txt"])
            self.assertEqual(plan["preserve"], [])

    def test_bundle_shared_file_drift_blocks_before_any_write(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            target, candidate, baseline_path, candidate_path, _paths = self.make_bundle_trees(root)
            baseline = APPLY.read_bundle_manifest(baseline_path, target)
            candidate_manifest = APPLY.read_bundle_manifest(candidate_path, candidate)
            (target / "setup/repo/skill_evals.json").write_text("user edit\n", encoding="utf-8")

            with self.assertRaisesRegex(APPLY.ApplyError, "drifted"):
                APPLY.build_bundle_plan(target, candidate, baseline, candidate_manifest)

            self.assertEqual(
                (target / ".agents/skills/demo/SKILL.md").read_text(encoding="utf-8"),
                "baseline\n",
            )

    @unittest.skipIf(sys.platform == "win32", "POSIX executable modes unavailable")
    def test_bundle_executable_drift_after_snapshot_blocks_plan(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            target, candidate, baseline_path, candidate_path, _paths = self.make_bundle_trees(root)
            baseline = APPLY.read_bundle_manifest(baseline_path, target)
            candidate_manifest = APPLY.read_bundle_manifest(candidate_path, candidate)
            (target / ".agents/skills/demo/SKILL.md").chmod(0o755)

            with self.assertRaisesRegex(APPLY.ApplyError, "drifted"):
                APPLY.build_bundle_plan(target, candidate, baseline, candidate_manifest)

    @unittest.skipIf(sys.platform == "win32", "POSIX executable modes unavailable")
    def test_bundle_candidate_executable_change_after_validation_blocks_plan(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            target, candidate, baseline_path, candidate_path, _paths = self.make_bundle_trees(root)
            baseline = APPLY.read_bundle_manifest(baseline_path, target)
            candidate_manifest = APPLY.read_bundle_manifest(candidate_path, candidate)
            (candidate / ".agents/skills/demo/SKILL.md").chmod(0o755)

            with self.assertRaisesRegex(APPLY.ApplyError, "validated manifest"):
                APPLY.build_bundle_plan(target, candidate, baseline, candidate_manifest)

    @unittest.skipIf(sys.platform == "win32", "POSIX executable modes unavailable")
    def test_bundle_mode_only_candidate_change_is_planned_and_applied(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            target, candidate, baseline_path, candidate_path, paths = self.make_bundle_trees(root)
            target_file = target / "setup/repo/skill_evals.json"
            candidate_file = candidate / "setup/repo/skill_evals.json"
            candidate_file.write_text(target_file.read_text(encoding="utf-8"), encoding="utf-8")
            target_file.chmod(0o644)
            candidate_file.chmod(0o755)
            APPLY.write_bundle_manifest(candidate, paths, candidate_path)
            baseline = APPLY.read_bundle_manifest(baseline_path, target)
            candidate_manifest = APPLY.read_bundle_manifest(candidate_path, candidate)

            plan = APPLY.build_bundle_plan(target, candidate, baseline, candidate_manifest)
            self.assertIn("setup/repo/skill_evals.json", plan["write"])

            APPLY.apply_bundle_plan(target, candidate, plan, root / "rollback")

            self.assertEqual(target_file.read_text(encoding="utf-8"), "baseline\n")
            self.assertTrue(APPLY.file_state(target_file)["executable"])

    @unittest.skipIf(sys.platform == "win32", "POSIX executable modes unavailable")
    def test_bundle_candidate_mode_change_after_plan_blocks_application(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            target, candidate, baseline_path, candidate_path, _paths = self.make_bundle_trees(root)
            baseline = APPLY.read_bundle_manifest(baseline_path, target)
            candidate_manifest = APPLY.read_bundle_manifest(candidate_path, candidate)
            plan = APPLY.build_bundle_plan(target, candidate, baseline, candidate_manifest)
            (candidate / ".agents/skills/demo/SKILL.md").chmod(0o755)

            with self.assertRaisesRegex(APPLY.ApplyError, "candidate bundle changed after"):
                APPLY.apply_bundle_plan(target, candidate, plan, root / "rollback")

    @unittest.skipIf(sys.platform == "win32", "POSIX permission modes unavailable")
    def test_bundle_content_write_preserves_non_executable_permissions(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            target, candidate, baseline_path, candidate_path, _paths = self.make_bundle_trees(root)
            target_file = target / "setup/repo/skill_evals.json"
            target_file.chmod(0o600)
            baseline = APPLY.read_bundle_manifest(baseline_path, target)
            candidate_manifest = APPLY.read_bundle_manifest(candidate_path, candidate)
            plan = APPLY.build_bundle_plan(target, candidate, baseline, candidate_manifest)

            APPLY.apply_bundle_plan(target, candidate, plan, root / "rollback")

            self.assertEqual(target_file.read_text(encoding="utf-8"), "candidate\n")
            self.assertEqual(target_file.stat().st_mode & 0o777, 0o600)

    @unittest.skipIf(sys.platform == "win32", "POSIX permission modes unavailable")
    def test_bundle_content_write_preserves_existing_execute_distribution(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            target, candidate, baseline_path, candidate_path, paths = self.make_bundle_trees(root)
            target_file = target / "setup/repo/skill_evals.json"
            candidate_file = candidate / "setup/repo/skill_evals.json"
            target_file.chmod(0o700)
            candidate_file.chmod(0o755)
            APPLY.write_bundle_manifest(target, paths, baseline_path)
            APPLY.write_bundle_manifest(candidate, paths, candidate_path)
            baseline = APPLY.read_bundle_manifest(baseline_path, target)
            candidate_manifest = APPLY.read_bundle_manifest(candidate_path, candidate)
            plan = APPLY.build_bundle_plan(target, candidate, baseline, candidate_manifest)

            APPLY.apply_bundle_plan(target, candidate, plan, root / "rollback")

            self.assertEqual(target_file.read_text(encoding="utf-8"), "candidate\n")
            self.assertEqual(target_file.stat().st_mode & 0o777, 0o700)

    def test_bundle_absent_selected_path_requires_explicit_deletion(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            target, candidate, baseline_path, candidate_path, paths = self.make_bundle_trees(root)
            shutil_path = candidate / ".agents/skills/demo"
            for path in sorted(shutil_path.rglob("*"), reverse=True):
                path.unlink()
            shutil_path.rmdir()
            APPLY.write_bundle_manifest(candidate, paths, candidate_path)
            baseline = APPLY.read_bundle_manifest(baseline_path, target)
            candidate_manifest = APPLY.read_bundle_manifest(candidate_path, candidate)

            with self.assertRaisesRegex(APPLY.ApplyError, "without an explicit deletion"):
                APPLY.build_bundle_plan(target, candidate, baseline, candidate_manifest)

    def test_bundle_explicit_selected_path_deletion_is_planned(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            target, candidate, baseline_path, candidate_path, paths = self.make_bundle_trees(root)
            candidate_directory = candidate / ".agents/skills/demo"
            for path in sorted(candidate_directory.rglob("*"), reverse=True):
                path.unlink()
            candidate_directory.rmdir()
            APPLY.write_bundle_manifest(
                candidate,
                paths,
                candidate_path,
                deletion_paths=[".agents/skills/demo"],
            )
            baseline = APPLY.read_bundle_manifest(baseline_path, target)
            candidate_manifest = APPLY.read_bundle_manifest(candidate_path, candidate)

            plan = APPLY.build_bundle_plan(target, candidate, baseline, candidate_manifest)

            self.assertIn(".agents/skills/demo/SKILL.md", plan["delete"])
            self.assertIn(".agents/skills/demo/obsolete.txt", plan["delete"])

            APPLY.apply_bundle_plan(target, candidate, plan, root / "rollback")

            self.assertFalse((target / ".agents/skills/demo").exists())

    def test_bundle_apply_failure_restores_every_selected_path(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            target, candidate, baseline_path, candidate_path, _paths = self.make_bundle_trees(root)
            baseline = APPLY.read_bundle_manifest(baseline_path, target)
            candidate_manifest = APPLY.read_bundle_manifest(candidate_path, candidate)
            plan = APPLY.build_bundle_plan(target, candidate, baseline, candidate_manifest)
            original_unlink = Path.unlink
            blocked = target / ".agents/skills/demo/obsolete.txt"

            def fail_one_delete(path: Path, *args: object, **kwargs: object) -> None:
                if path == blocked:
                    raise OSError("forced shared transaction failure")
                original_unlink(path, *args, **kwargs)

            with mock.patch.object(Path, "unlink", fail_one_delete):
                with self.assertRaisesRegex(OSError, "forced shared transaction failure"):
                    APPLY.apply_bundle_plan(target, candidate, plan, root / "rollback")

            self.assertEqual(
                (target / ".agents/skills/demo/SKILL.md").read_text(encoding="utf-8"),
                "baseline\n",
            )
            self.assertEqual(
                (target / ".claude/skills/demo/SKILL.md").read_text(encoding="utf-8"),
                "baseline\n",
            )
            self.assertEqual(
                (target / "setup/repo/skill_evals.json").read_text(encoding="utf-8"),
                "baseline\n",
            )
            self.assertTrue((target / ".agents/skills/demo/obsolete.txt").is_file())
            self.assertFalse((target / ".agents/skills/demo/added.txt").exists())

    def test_bundle_selection_rejects_traversal_and_overlap(self) -> None:
        with self.assertRaisesRegex(APPLY.ApplyError, "repo-relative"):
            APPLY.normalize_bundle_paths(["../outside"])
        with self.assertRaisesRegex(APPLY.ApplyError, "overlapping"):
            APPLY.normalize_bundle_paths([".agents/skills", ".agents/skills/demo"])

    def test_bundle_selection_rejects_symlinked_parent(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            target = root / "target"
            outside = root / "outside"
            target.mkdir()
            outside.mkdir()
            (outside / "SKILL.md").write_text("outside\n", encoding="utf-8")
            (target / ".agents").symlink_to(outside, target_is_directory=True)

            with self.assertRaisesRegex(APPLY.ApplyError, "symbolic links"):
                APPLY.bundle_entries(target, [".agents/SKILL.md"])

    def test_bundle_manifest_rejects_file_outside_selected_directory(self) -> None:
        with self.assertRaisesRegex(APPLY.ApplyError, "escapes selected directory"):
            APPLY.flatten_bundle_files(
                {
                    ".agents/skills/demo": {
                        "kind": "directory",
                        "files": {
                            "setup/repo/skill_evals.json": {
                                "sha256": "digest",
                                "executable": False,
                            }
                        },
                    }
                }
            )

    def test_bundle_cli_dry_run_and_apply_use_both_manifests(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            target, candidate, baseline_path, candidate_path, _paths = self.make_bundle_trees(root)
            command = [
                sys.executable,
                str(SCRIPT),
                "apply-bundle",
                str(target),
                str(candidate),
                str(baseline_path),
                "--candidate-manifest",
                str(candidate_path),
            ]

            dry_run = subprocess.run(command, check=False, capture_output=True, text=True)

            self.assertEqual(dry_run.returncode, 0, dry_run.stderr)
            self.assertEqual(json.loads(dry_run.stdout)["mode"], "dry-run")
            applied = subprocess.run(
                [*command, "--apply", "--rollback-root", str(root / "rollback")],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(applied.returncode, 0, applied.stderr)
            self.assertEqual(json.loads(applied.stdout)["mode"], "applied")
            self.assertEqual(
                (target / "setup/repo/skill_evals.json").read_text(encoding="utf-8"),
                "candidate\n",
            )



if __name__ == "__main__":
    unittest.main()
