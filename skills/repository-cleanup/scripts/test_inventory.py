"""Consequential inventory boundaries, exercised against real disposable Git repos."""
from pathlib import Path
import subprocess
import tempfile
import unittest

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
