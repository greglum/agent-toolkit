"""Planted-defect and safety tests for scan_dirty.py."""

from __future__ import annotations

import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import scan_dirty


def git_cmd(repo: Path, *args: str) -> str:
    """Run a deterministic git command inside a test fixture repository."""
    env = {
        **os.environ,
        "GIT_AUTHOR_NAME": "Test Author",
        "GIT_AUTHOR_EMAIL": "author@example.com",
        "GIT_COMMITTER_NAME": "Test Author",
        "GIT_COMMITTER_EMAIL": "author@example.com",
    }
    res = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        capture_output=True,
        text=True,
        env=env,
    )
    return res.stdout.strip()


def init_repo(root: Path, name: str = "demo") -> Path:
    """Create a committed git repository on branch main."""
    repo = root / name
    repo.mkdir(parents=True)
    git_cmd(repo, "init", "-b", "main")
    (repo / "README.md").write_text("# Demo\n", encoding="utf-8")
    (repo / "keep.txt").write_text("base\n", encoding="utf-8")
    git_cmd(repo, "add", "README.md", "keep.txt")
    git_cmd(repo, "commit", "-m", "Initial commit")
    return repo


def run_cli(*args: str) -> tuple[int, dict]:
    """Execute scan_dirty.main in-process and decode JSON stdout."""
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = scan_dirty.main(list(args))
    return rc, json.loads(buf.getvalue())


class ScanDirtyTests(unittest.TestCase):
    def test_detects_dirty_categories_secrets_locks_and_binary_on_main(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = init_repo(Path(tmp))
            (repo / ".gitignore").write_text(".env.local\n*.pem\n", encoding="utf-8")
            git_cmd(repo, "add", ".gitignore")
            git_cmd(repo, "commit", "-m", "Add local ignore rules")
            (repo / "old_name.txt").write_text("rename me\n", encoding="utf-8")
            git_cmd(repo, "add", "old_name.txt")
            git_cmd(repo, "commit", "-m", "Add rename fixture")
            git_cmd(repo, "mv", "old_name.txt", "new_name.txt")
            (repo / "staged.txt").write_text("staged\n", encoding="utf-8")
            git_cmd(repo, "add", "staged.txt")
            (repo / "README.md").write_text("# Modified\n", encoding="utf-8")
            (repo / "src").mkdir()
            (repo / "src" / "notes.md").write_text("untracked\n", encoding="utf-8")
            (repo / "secrets.json").write_text("{\"token\": \"example\"}\n", encoding="utf-8")
            (repo / "id_ed25519").write_text("private-key-placeholder\n", encoding="utf-8")
            (repo / ".env.local").write_text("TOKEN=example\n", encoding="utf-8")
            (repo / "service-key.pem").write_text("key-material\n", encoding="utf-8")
            (repo / "blob.bin").write_bytes(b"\x00\x01\x02\x03")
            (repo / "big.txt").write_bytes(b"a" * 2048)
            git_cmd(repo, "rm", "-q", "keep.txt")
            (repo / ".git" / "index.lock").write_text("lock\n", encoding="utf-8")

            before_hash = hashlib.sha256((repo / "README.md").read_bytes()).hexdigest()
            before_index = git_cmd(repo, "ls-files", "-s")

            rc, data = run_cli("--repo", str(repo), "--oversized-bytes", "1024")
            self.assertEqual(rc, 0)
            self.assertFalse(data["incomplete"])
            wt = data["repos"][0]["worktrees"][0]
            self.assertTrue(wt["on_default_branch"])
            self.assertIn("staged.txt", wt["staged"])
            self.assertIn({"from": "old_name.txt", "to": "new_name.txt"}, wt["renamed"])
            self.assertIn("README.md", wt["unstaged"])
            self.assertIn("src/notes.md", wt["untracked"])
            self.assertIn("keep.txt", wt["deleted"])
            self.assertEqual(wt["active_git_op"], ["index.lock"])
            self.assertEqual(sorted(wt["credential_or_env_candidates"]), ["id_ed25519", "secrets.json"])
            self.assertEqual(sorted(wt["ignored_credential_or_env_files"]), [".env.local", "service-key.pem"])
            self.assertEqual(sorted(wt["binary_or_oversized_untracked"]), ["big.txt", "blob.bin"])
            self.assertIsNotNone(wt["dirty_fingerprint"])
            self.assertEqual(wt["omitted_paths_count"], 0)
            self.assertEqual(before_hash, hashlib.sha256((repo / "README.md").read_bytes()).hexdigest())
            self.assertEqual(before_index, git_cmd(repo, "ls-files", "-s"))

    def test_detects_merge_conflict_and_linked_worktree_under_repos_root(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = init_repo(root, "active-repo")
            wt_dir = root / "active-repo-wt"
            wt_clean = root / "active-repo-clean-wt"
            git_cmd(repo, "branch", "feature/a")
            git_cmd(repo, "branch", "feature/b")
            git_cmd(repo, "checkout", "-q", "feature/a")
            (repo / "README.md").write_text("branch a\n", encoding="utf-8")
            git_cmd(repo, "commit", "-am", "Change A")
            git_cmd(repo, "checkout", "-q", "feature/b")
            (repo / "README.md").write_text("branch b\n", encoding="utf-8")
            git_cmd(repo, "commit", "-am", "Change B")
            subprocess.run(["git", "-C", str(repo), "merge", "feature/a"], capture_output=True, check=False)

            git_cmd(repo, "worktree", "add", "-b", "feature/wt", str(wt_dir), "main")
            (wt_dir / "wt_dirty.log").write_text("worktree log\n", encoding="utf-8")
            git_cmd(repo, "worktree", "add", "-b", "feature/clean", str(wt_clean), "main")

            clean_repo = init_repo(root, "clean-repo")
            self.assertTrue((clean_repo / ".git").is_dir())
            excluded_repo = init_repo(root, "ignored-mirror")
            (excluded_repo / "dirty.txt").write_text("skip me\n", encoding="utf-8")

            rc, data = run_cli(
                "--repos-root",
                str(root),
                "--active-days",
                "7",
                "--exclude",
                "ignored-mirror",
                "--dirty-only",
            )
            self.assertEqual(rc, 0)
            self.assertEqual(data["clean_repos_omitted"], 1)
            names = [r["name"] for r in data["repos"]]
            self.assertEqual(names, ["active-repo"])
            self.assertEqual(data["repos"][0]["clean_worktrees_omitted"], 1)
            wts = data["repos"][0]["worktrees"]
            self.assertEqual(len(wts), 2)
            self.assertIn("README.md", wts[0]["merge_conflicts"])
            self.assertIn("MERGE_HEAD", wts[0]["active_git_op"])
            self.assertIn("wt_dirty.log", wts[1]["untracked"])
            self.assertFalse(wts[1]["on_default_branch"])
            self.assertTrue(wts[1]["likely_scratch_only"])

    def test_caps_paths_flags_recent_and_deduplicates_identical_worktree_diffs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = init_repo(root, "dup-repo")
            wt_dup = root / "dup-repo-wt"
            git_cmd(repo, "worktree", "add", "-b", "feature/dup", str(wt_dup), "main")

            for tree in (repo, wt_dup):
                (tree / "README.md").write_text("same change\n", encoding="utf-8")
                (tree / "a.txt").write_text("1\n", encoding="utf-8")
                (tree / "b.txt").write_text("2\n", encoding="utf-8")
                (tree / "c.txt").write_text("3\n", encoding="utf-8")
                (tree / "d.txt").write_text("4\n", encoding="utf-8")
            (repo / "secrets.json").write_text('{"secret": "placeholder"}\n', encoding="utf-8")

            rc, data = run_cli("--repo", str(repo), "--max-paths", "2", "--min-stale-minutes", "60")
            self.assertEqual(rc, 0)
            wt_main, wt_copy = data["repos"][0]["worktrees"]
            self.assertEqual(len(wt_main["untracked"]), 2)
            self.assertEqual(wt_main["untracked_count"], 5)
            self.assertEqual(wt_main["omitted_paths_count"], 3)
            self.assertEqual(wt_main["cluster_counts"], {"(root)": 6})
            self.assertEqual(wt_main["logical_clusters"], {})
            self.assertEqual(wt_main["credential_or_env_candidates"], ["secrets.json"])
            self.assertTrue(wt_main["recently_modified"])
            self.assertIsNotNone(wt_main["dirty_fingerprint"])

            (repo / "secrets.json").unlink()
            rc_same, data_same = run_cli("--repo", str(repo), "--max-paths", "2")
            self.assertEqual(rc_same, 0)
            w0, w1 = data_same["repos"][0]["worktrees"]
            self.assertEqual(w0["dirty_fingerprint"], w1["dirty_fingerprint"])
            self.assertIsNone(w0["duplicate_of_worktree"])
            self.assertEqual(w1["duplicate_of_worktree"], w0["path"])

    def test_clean_filter_returns_exit_2_without_executing_filter_script(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = init_repo(root)
            sentinel = root / "filter_ran.txt"
            driver = root / "evil_filter.sh"
            driver.write_text(f"#!/bin/sh\necho ran > {sentinel}\ncat\n", encoding="utf-8")
            driver.chmod(0o755)
            (repo / ".gitattributes").write_text("*.txt filter=demo\n", encoding="utf-8")
            git_cmd(repo, "add", ".gitattributes")
            git_cmd(repo, "commit", "-m", "Add filter attribute")
            git_cmd(repo, "config", "filter.demo.clean", str(driver))

            rc, data = run_cli("--repo", str(repo))
            self.assertEqual(rc, 2)
            self.assertTrue(data["incomplete"])
            self.assertFalse(sentinel.exists())
            self.assertIn("filter", data["repos"][0]["worktrees"][0]["safety_gap"].lower())


if __name__ == "__main__":
    unittest.main()
