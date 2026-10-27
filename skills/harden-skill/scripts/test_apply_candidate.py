#!/usr/bin/env python3
# ruff: noqa: D102
"""Regression coverage for drift-safe candidate application."""

from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from candidate_fixtures import APPLY, CandidateTrees


class ApplyCandidateTests(CandidateTrees, unittest.TestCase):
    """Exercise snapshot, drift, synchronization, and preservation behavior."""

    def test_dry_run_reports_changes_without_writing(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            target, candidate, manifest = self.make_trees(Path(temp))
            baseline = APPLY.read_manifest(manifest, target)

            plan = APPLY.build_plan(target, candidate, baseline)

            self.assertEqual(plan["write"], ["SKILL.md", "added.txt"])
            self.assertEqual(plan["delete"], ["obsolete.txt"])
            self.assertEqual((target / "SKILL.md").read_text(encoding="utf-8"), "baseline\n")

    def test_apply_syncs_candidate_and_preserves_post_snapshot_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            target, candidate, manifest = self.make_trees(root)
            (target / "user-note.txt").write_text("keep\n", encoding="utf-8")
            plan = APPLY.build_plan(target, candidate, APPLY.read_manifest(manifest, target))

            rollback = APPLY.apply_plan(target, candidate, plan, root / "rollback")

            self.assertEqual((target / "SKILL.md").read_text(encoding="utf-8"), "candidate\n")
            self.assertTrue((target / "added.txt").is_file())
            self.assertFalse((target / "obsolete.txt").exists())
            self.assertEqual((target / "user-note.txt").read_text(encoding="utf-8"), "keep\n")
            self.assertEqual((rollback / "SKILL.md").read_text(encoding="utf-8"), "baseline\n")

    def test_modified_baseline_file_blocks_application(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            target, candidate, manifest = self.make_trees(Path(temp))
            (target / "SKILL.md").write_text("user edit\n", encoding="utf-8")

            with self.assertRaisesRegex(APPLY.ApplyError, "drifted"):
                APPLY.build_plan(target, candidate, APPLY.read_manifest(manifest, target))

    def test_candidate_collision_with_post_snapshot_file_blocks_application(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            target, candidate, manifest = self.make_trees(Path(temp))
            (target / "new.txt").write_text("user\n", encoding="utf-8")
            (candidate / "new.txt").write_text("candidate\n", encoding="utf-8")

            with self.assertRaisesRegex(APPLY.ApplyError, "post-snapshot"):
                APPLY.build_plan(target, candidate, APPLY.read_manifest(manifest, target))

    def test_target_change_after_plan_blocks_application(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            target, candidate, manifest = self.make_trees(root)
            plan = APPLY.build_plan(target, candidate, APPLY.read_manifest(manifest, target))
            (target / "SKILL.md").write_text("late edit\n", encoding="utf-8")

            with self.assertRaisesRegex(APPLY.ApplyError, "changed after"):
                APPLY.apply_plan(target, candidate, plan, root / "rollback")

    def test_candidate_change_after_plan_blocks_application(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            target, candidate, manifest = self.make_trees(root)
            plan = APPLY.build_plan(target, candidate, APPLY.read_manifest(manifest, target))
            (candidate / "SKILL.md").write_text("late candidate\n", encoding="utf-8")

            with self.assertRaisesRegex(APPLY.ApplyError, "candidate changed"):
                APPLY.apply_plan(target, candidate, plan, root / "rollback")

    def test_symlink_in_tree_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            target, _candidate, _manifest = self.make_trees(root)
            (target / "link.txt").symlink_to(target / "SKILL.md")

            with self.assertRaisesRegex(APPLY.ApplyError, "symbolic links"):
                APPLY.tree_files(target)

    def test_manifest_is_bound_to_target(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            target, _candidate, manifest = self.make_trees(root)
            payload = json.loads(manifest.read_text(encoding="utf-8"))
            payload["target"] = str(root / "other")
            manifest.write_text(json.dumps(payload), encoding="utf-8")

            with self.assertRaisesRegex(APPLY.ApplyError, "does not match"):
                APPLY.read_manifest(manifest, target)

    def test_snapshot_outputs_cannot_replace_or_enter_selected_inputs(self) -> None:
        for api in ("single", "bundle"):
            for alias in (
                "direct", "nested", "absent", "symlink-parent", "symlink-file", "hardlink",
                "resolved-hardlink",
            ):
                with self.subTest(api=api, alias=alias), tempfile.TemporaryDirectory() as temp:
                    root = Path(temp)
                    target = root / "skill"
                    target.mkdir()
                    source = target / "SKILL.md"
                    source.write_bytes(b"preserve this skill\n")
                    source.chmod(0o750)
                    before = APPLY.tree_files(target)
                    selected = ["skill"]
                    if alias == "direct":
                        output = source
                        selected = ["skill/SKILL.md"]
                    elif alias == "nested":
                        output = target / "new-parent/manifest.json"
                    elif alias == "absent":
                        output = (
                            target / "future/manifest.json"
                            if api == "single"
                            else root / "future/manifest.json"
                        )
                        selected.append("future")
                    elif alias == "symlink-parent":
                        linked = root / "linked"
                        linked.symlink_to(target, target_is_directory=True)
                        output = linked / "new-parent/manifest.json"
                    elif alias == "symlink-file":
                        output = root / "linked.json"
                        output.symlink_to(source)
                    else:
                        output = root / "linked.json"
                        os.link(source, output)
                        if alias == "resolved-hardlink":
                            output = root / "uncreated/../linked.json"
                    parent_existed = output.parent.exists()

                    with self.assertRaisesRegex(APPLY.ApplyError, "protected input"):
                        if api == "single":
                            APPLY.write_manifest(target, output)
                        else:
                            APPLY.write_bundle_manifest(root, selected, output)

                    self.assertEqual(source.read_bytes(), b"preserve this skill\n")
                    self.assertEqual(source.stat().st_mode & 0o777, 0o750)
                    self.assertEqual(APPLY.tree_files(target), before)
                    if not parent_existed:
                        self.assertFalse(output.parent.exists())

    def test_manifest_outputs_use_resolved_safe_paths(self) -> None:
        for api in ("single", "bundle"):
            with self.subTest(api=api), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                target = root / "skill"
                target.mkdir()
                source = target / "SKILL.md"
                source.write_bytes(b"preserve this skill\n")
                source.chmod(0o750)
                before = APPLY.tree_files(target)
                if api == "single":
                    intermediate = target / "new-parent"
                    output = intermediate / "../../manifest.json"
                    APPLY.write_manifest(target, output)
                    manifest = APPLY.read_manifest(output.resolve(), target)
                    self.assertEqual(manifest, before)
                else:
                    intermediate = root / "future"
                    output = intermediate / "../bundle.json"
                    paths = ["skill", "future"]
                    entries = APPLY.bundle_entries(root, paths)
                    APPLY.write_bundle_manifest(root, paths, output)
                    manifest = APPLY.read_bundle_manifest(output.resolve(), root)
                    self.assertEqual(manifest["entries"], entries)
                self.assertTrue(output.resolve().is_file())
                self.assertFalse(intermediate.exists())
                self.assertEqual(source.read_bytes(), b"preserve this skill\n")
                self.assertEqual(source.stat().st_mode & 0o777, 0o750)
                self.assertEqual(APPLY.tree_files(target), before)

    def test_rollback_outputs_use_resolved_safe_paths(self) -> None:
        for api in ("single", "bundle"):
            for mode in ("explicit", "default"):
                with self.subTest(api=api, mode=mode), tempfile.TemporaryDirectory() as temp:
                    root = Path(temp)
                    if api == "single":
                        target, candidate, baseline = self.make_trees(root)
                        plan = APPLY.build_plan(target, candidate, APPLY.read_manifest(baseline, target))
                        before = APPLY.tree_files(target)
                        intermediate = target / "new-parent"
                        rollback = intermediate / "../../rollbacks"
                    else:
                        target, candidate, baseline, staged, paths = self.make_bundle_trees(root)
                        paths.append("future")
                        APPLY.write_bundle_manifest(target, paths, baseline)
                        APPLY.write_bundle_manifest(candidate, paths, staged)
                        plan = APPLY.build_bundle_plan(
                            target,
                            candidate,
                            APPLY.read_bundle_manifest(baseline, target),
                            APPLY.read_bundle_manifest(staged, candidate),
                        )
                        before = APPLY.bundle_entries(target, paths)
                        intermediate = target / "future"
                        rollback = intermediate / "../rollbacks"
                    canonical = rollback.resolve()
                    if mode == "default":
                        canonical.mkdir()
                    with mock.patch.object(APPLY.tempfile, "gettempdir", return_value=str(rollback)):
                        destination = None if mode == "default" else rollback
                        if api == "single":
                            snapshot = APPLY.apply_plan(target, candidate, plan, destination)
                            self.assertEqual(APPLY.tree_files(snapshot), before)
                            self.assertEqual(APPLY.tree_files(target), APPLY.tree_files(candidate))
                        else:
                            snapshot = APPLY.apply_bundle_plan(target, candidate, plan, destination)
                            self.assertEqual(APPLY.bundle_entries(snapshot, paths), before)
                            self.assertEqual(
                                APPLY.bundle_entries(target, paths), APPLY.bundle_entries(candidate, paths)
                            )
                    self.assertFalse(intermediate.exists())
                    self.assertTrue(snapshot.is_relative_to(canonical))

    def test_bundle_outputs_can_use_unselected_repository_paths(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            target, candidate, _baseline, staged, paths = self.make_bundle_trees(root)
            before = APPLY.bundle_entries(target, paths)
            output = target / "reports/bundle.json"

            APPLY.write_bundle_manifest(target, paths, output)

            self.assertEqual(APPLY.bundle_entries(target, paths), before)
            baseline = APPLY.read_bundle_manifest(output, target)
            self.assertEqual(baseline["paths"], paths)
            plan = APPLY.build_bundle_plan(
                target, candidate, baseline, APPLY.read_bundle_manifest(staged, candidate)
            )
            temporary_parent = target / "unselected-temp"
            temporary_parent.mkdir()
            with mock.patch.object(APPLY.tempfile, "gettempdir", return_value=str(temporary_parent)):
                snapshot = APPLY.apply_bundle_plan(target, candidate, plan, None)

            self.assertTrue(snapshot.is_relative_to(temporary_parent.resolve()))
            self.assertEqual(APPLY.bundle_entries(snapshot, paths), before)
            self.assertEqual(
                APPLY.bundle_entries(target, paths), APPLY.bundle_entries(candidate, paths)
            )

    def test_rollback_outputs_cannot_enter_live_or_candidate_inputs(self) -> None:
        for api in ("single", "bundle"):
            for role in ("target", "candidate"):
                for alias in ("nested", "symlink-parent", "default"):
                    with self.subTest(api=api, role=role, alias=alias), tempfile.TemporaryDirectory() as temp:
                        root = Path(temp)
                        if api == "single":
                            target, candidate, manifest = self.make_trees(root)
                            plan = APPLY.build_plan(target, candidate, APPLY.read_manifest(manifest, target))
                            protected = target if role == "target" else candidate
                        else:
                            target, candidate, baseline, staged, _paths = self.make_bundle_trees(root)
                            plan = APPLY.build_bundle_plan(
                                target,
                                candidate,
                                APPLY.read_bundle_manifest(baseline, target),
                                APPLY.read_bundle_manifest(staged, candidate),
                            )
                            protected = (target if role == "target" else candidate) / ".agents/skills/demo"
                        if alias == "symlink-parent":
                            linked = root / "linked"
                            linked.symlink_to(protected, target_is_directory=True)
                            protected = linked
                        rollback = protected / "uncreated-rollback"
                        before_target = APPLY.tree_files(target)
                        before_candidate = APPLY.tree_files(candidate)

                        with (
                            mock.patch.object(APPLY.shutil, "copytree") as copy,
                            mock.patch.object(APPLY.tempfile, "gettempdir", return_value=str(protected)),
                            mock.patch.object(
                                APPLY.tempfile, "mkdtemp",
                                side_effect=AssertionError("unsafe temporary directory creation"),
                            ) as temporary,
                        ):
                            with self.assertRaisesRegex(APPLY.ApplyError, "protected input"):
                                if api == "single":
                                    APPLY.apply_plan(target, candidate, plan, None if alias == "default" else rollback)
                                else:
                                    APPLY.apply_bundle_plan(target, candidate, plan, None if alias == "default" else rollback)
                            copy.assert_not_called()
                            temporary.assert_not_called()

                        self.assertFalse(rollback.exists())
                        self.assertEqual(APPLY.tree_files(target), before_target)
                        self.assertEqual(APPLY.tree_files(candidate), before_candidate)



if __name__ == "__main__":
    unittest.main()
