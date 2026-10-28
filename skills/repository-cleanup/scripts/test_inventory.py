"""Consequential inventory boundaries, exercised against real disposable Git repos."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from inventory import Inventory


class InventoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.repo = self.root / "source"
        self.repo.mkdir()
        self.git("init", "-b", "main")
        self.git("config", "user.name", "Fixture")
        self.git("config", "user.email", "fixture" + "@" + "example.invalid")
        self.git("config", "core.hooksPath", "/dev/null")
        (self.repo / "tracked").write_text("base\n")
        (self.repo / ".gitignore").write_text("local-data/\n")
        self.git("add", ".")
        self.git("commit", "-m", "base")

    def git(self, *args, repo=None):
        return subprocess.check_output(["git", "-C", str(repo or self.repo), *args],
                                       stderr=subprocess.DEVNULL).decode().strip()

    def test_preserves_unique_detached_dirty_ignored_stashed_and_renamed_work(self):
        self.git("switch", "-c", "unfinished")
        (self.repo / "unique").write_text("valuable\n")
        self.git("add", ".")
        self.git("commit", "-m", "unfinished behavior")
        self.git("switch", "main")
        self.git("branch", "merged")
        stash_path = self.repo / "tracked"
        stash_path.write_text("stashed\n")
        self.git("stash", "push", "-m", "paused")
        detached = self.root / "paused checkout\nwith newline"
        self.git("worktree", "add", "--detach", str(detached), "unfinished")
        self.git("mv", "tracked", "renamed", repo=detached)
        (detached / "untracked\nasset").write_text("draft\n")
        (detached / "local-data").mkdir()
        (detached / "local-data" / "keep").write_text("important ignored bytes\n")
        before_status = self.git("status", "--porcelain=v1", "-z", repo=detached)
        before_refs = self.git("show-ref")
        result = Inventory(str(self.repo)).collect("main")
        self.assertTrue(result["complete"], result["errors"])
        refs = {item["ref"]: item for item in result["refs"]}
        self.assertFalse(refs["refs/heads/unfinished"]["ancestry"]["tip_reachable_from_base"])
        self.assertTrue(refs["refs/heads/merged"]["ancestry"]["tip_reachable_from_base"])
        tree = next(item for item in result["worktrees"] if item["worktree"] == str(detached))
        self.assertIn({"status": "R ", "path": "renamed", "source": "tracked"}, tree["changes"])
        self.assertIn({"status": "??", "path": "untracked\nasset"}, tree["changes"])
        self.assertIn("local-data/", tree["ignored_paths"])
        self.assertEqual(len(result["stashes"]), 1)
        self.assertEqual(before_refs, self.git("show-ref"))
        self.assertEqual(before_status, self.git("status", "--porcelain=v1", "-z", repo=detached))
        self.assertEqual((detached / "local-data" / "keep").read_text(), "important ignored bytes\n")

    def test_squash_merge_remains_unproven_and_missing_worktree_is_incomplete(self):
        self.git("switch", "-c", "feature")
        for number in (1, 2):
            (self.repo / f"feature{number}").write_text("useful\n")
            self.git("add", ".")
            self.git("commit", "-m", f"feature {number}")
        self.git("switch", "main")
        self.git("merge", "--squash", "feature")
        self.git("commit", "-m", "landed squash")
        result = Inventory(str(self.repo)).collect("main")
        feature = next(item for item in result["refs"] if item["ref"] == "refs/heads/feature")
        self.assertFalse(feature["ancestry"]["tip_reachable_from_base"])
        detached = self.root / "missing"
        self.git("worktree", "add", "--detach", str(detached), "main")
        detached.rename(self.root / "moved-away")
        result = Inventory(str(self.repo)).collect("main")
        self.assertFalse(result["complete"])
        self.assertTrue(any(error["error"] == "missing worktree path" for error in result["errors"]))

    def test_shared_clone_lenders_relative_environment_and_unavailable_evidence(self):
        lender = self.root / "lender ü"
        self.repo.rename(lender)
        self.repo = lender
        borrower = self.root / "borrower"
        self.git("clone", "--shared", str(lender), str(borrower))
        relocated = self.root / "lender ü\npaused"
        lender.rename(relocated)
        lender = relocated
        self.repo = lender
        objects = lender / ".git/objects"
        file = borrower / ".git/objects/info/alternates"
        # Use Git's quoted-path syntax to retain the newline in a relative lender path.
        relative = os.path.relpath(objects, borrower / ".git/objects")
        file.write_text(json.dumps(relative, ensure_ascii=False) + "\n")
        before = file.read_bytes()
        refs = self.git("show-ref", repo=borrower)
        result = Inventory(str(borrower)).collect("main")
        self.assertTrue(result["complete"], result["errors"])
        storage = result["object_storage"]
        self.assertEqual(storage["alternate_object_directories"], [str(objects)])
        self.assertEqual(storage["common_alternates_file"], str(file))
        self.assertIn("unknown", storage["outside_borrowers"])
        self.assertEqual(file.read_bytes(), before)
        self.assertEqual(self.git("show-ref", repo=borrower), refs)
        # The same dependency may be injected by the calling environment, not a file.
        file.unlink()
        with patch.dict(os.environ, {"GIT_ALTERNATE_OBJECT_DIRECTORIES": json.dumps(str(objects), ensure_ascii=False)}):
            result = Inventory(str(borrower)).collect("main")
        self.assertTrue(result["complete"], result["errors"])
        self.assertEqual(result["object_storage"]["alternate_object_directories"], [str(objects)])
        self.assertTrue(result["object_storage"]["environment_alternates_present"])
        file.write_bytes(before)
        moved = self.root / "preserved-lender"
        lender.rename(moved)
        result = Inventory(str(borrower)).collect("main")
        self.assertFalse(result["complete"])
        self.assertIsNone(result["object_storage"]["alternate_object_directories"])
        self.assertTrue(any(error["status"] == 0 and "count-objects" in error["args"]
                            for error in result["errors"]))
        # Only independent objects plus a native integrity/functional check remove the dependency.
        moved.rename(lender)
        self.git("repack", "-a", "-d", repo=borrower)
        file.unlink()
        lender.rename(moved)
        self.git("fsck", "--full", repo=borrower)
        self.assertEqual(self.git("show", "main:tracked", repo=borrower), "base")
        result = Inventory(str(borrower)).collect("main")
        self.assertTrue(result["complete"], result["errors"])
        self.assertEqual(result["object_storage"]["alternate_object_directories"], [])

    def test_bare_and_invalid_base_do_not_invent_clean_evidence(self):
        bare = self.root / "bare.git"
        self.git("clone", "--bare", str(self.repo), str(bare))
        result = Inventory(str(bare)).collect("main")
        self.assertTrue(result["complete"], result["errors"])
        self.assertTrue(result["worktrees"][0]["bare"])
        invalid = Inventory(str(self.repo)).collect("missing-base")
        self.assertFalse(invalid["complete"])
        self.assertTrue(invalid["errors"])


if __name__ == "__main__":
    unittest.main()
