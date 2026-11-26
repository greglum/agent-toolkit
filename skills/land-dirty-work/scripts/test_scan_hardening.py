"""Planted-defect regression tests for scanner hardening fixes."""

from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from classify_dirty import compute_dirty_fingerprint
from test_scan_dirty import git_cmd, init_repo, run_cli


def git_dated_commit(repo: Path, iso_date: str, message: str) -> None:
    """Create a commit pinned to a historical timestamp."""
    env = {
        **os.environ,
        "GIT_AUTHOR_NAME": "Test Author",
        "GIT_AUTHOR_EMAIL": "author@example.com",
        "GIT_AUTHOR_DATE": iso_date,
        "GIT_COMMITTER_NAME": "Test Author",
        "GIT_COMMITTER_EMAIL": "author@example.com",
        "GIT_COMMITTER_DATE": iso_date,
    }
    subprocess.run(["git", "-C", str(repo), "commit", "-m", message], check=True, capture_output=True, text=True, env=env)


class ScanHardeningTests(unittest.TestCase):
    def test_same_size_untracked_and_staged_binary_edits_change_fingerprint(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = init_repo(root)
            (repo / "blob.bin").write_bytes(b"\x00\x01\x02")
            git_cmd(repo, "add", "blob.bin")
            git_cmd(repo, "commit", "-m", "Add binary")

            (repo / "note.txt").write_text("aaaa\n", encoding="utf-8")
            _, d1 = run_cli("--repo", str(repo))
            fp1 = d1["repos"][0]["worktrees"][0]["dirty_fingerprint"]

            (repo / "note.txt").write_text("bbbb\n", encoding="utf-8")
            _, d2 = run_cli("--repo", str(repo))
            fp2 = d2["repos"][0]["worktrees"][0]["dirty_fingerprint"]
            self.assertNotEqual(fp1, fp2)

            (repo / "README.md").write_text("stage-v1\n", encoding="utf-8")
            git_cmd(repo, "add", "README.md")
            (repo / "README.md").write_text("work-v3\n", encoding="utf-8")
            _, d3 = run_cli("--repo", str(repo))
            fp3 = d3["repos"][0]["worktrees"][0]["dirty_fingerprint"]

            (repo / "README.md").write_text("stage-v2\n", encoding="utf-8")
            git_cmd(repo, "add", "README.md")
            (repo / "README.md").write_text("work-v3\n", encoding="utf-8")
            _, d4 = run_cli("--repo", str(repo))
            fp4 = d4["repos"][0]["worktrees"][0]["dirty_fingerprint"]
            self.assertNotEqual(fp3, fp4)

            (repo / "blob.bin").write_bytes(b"\x00\x01\x09")
            _, d5 = run_cli("--repo", str(repo))
            fp5 = d5["repos"][0]["worktrees"][0]["dirty_fingerprint"]
            (repo / "blob.bin").write_bytes(b"\x00\x01\x08")
            _, d6 = run_cli("--repo", str(repo))
            fp6 = d6["repos"][0]["worktrees"][0]["dirty_fingerprint"]
            self.assertNotEqual(fp5, fp6)

    def test_diff_external_and_old_repo_safety_gap_return_exit_2(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = init_repo(root, "old-filter")
            sentinel = root / "ext_diff_ran.txt"
            driver = root / "ext.sh"
            driver.write_text(f"#!/bin/sh\necho ran > {sentinel}\n", encoding="utf-8")
            driver.chmod(0o755)
            git_cmd(repo, "config", "diff.external", str(driver))
            (repo / "README.md").write_text("dirty\n", encoding="utf-8")

            rc_ext, d_ext = run_cli("--repo", str(repo))
            self.assertEqual(rc_ext, 2)
            self.assertFalse(sentinel.exists())
            self.assertIn("diff.external", d_ext["repos"][0]["worktrees"][0]["safety_gap"])

            old_repo = root / "stale-filter"
            old_repo.mkdir()
            git_cmd(old_repo, "init", "-b", "main")
            (old_repo / ".gitattributes").write_text("*.bin filter=lfs\n", encoding="utf-8")
            (old_repo / "data.bin").write_text("abc\n", encoding="utf-8")
            git_cmd(old_repo, "add", ".gitattributes", "data.bin")
            git_dated_commit(old_repo, "2020-01-01T00:00:00Z", "Old base commit")
            git_cmd(old_repo, "config", "filter.lfs.clean", str(driver))

            rc_root, d_root = run_cli("--repos-root", str(root), "--active-days", "30")
            self.assertEqual(rc_root, 2)
            self.assertTrue(d_root["incomplete"])
            self.assertNotIn("stale-filter", d_root["skipped_inactive_repos"])

    def test_git_rm_deletion_uses_index_mtime_for_recently_modified(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "rm-repo"
            repo.mkdir()
            git_cmd(repo, "init", "-b", "main")
            (repo / "keep.txt").write_text("old\n", encoding="utf-8")
            git_cmd(repo, "add", "keep.txt")
            git_dated_commit(repo, "2020-01-01T00:00:00Z", "Old commit")
            git_cmd(repo, "rm", "-q", "keep.txt")

            rc, data = run_cli("--repo", str(repo), "--min-stale-minutes", "60")
            self.assertEqual(rc, 0)
            wt = data["repos"][0]["worktrees"][0]
            self.assertTrue(wt["recently_modified"])
            self.assertIsNotNone(wt["stale_minutes"])
            self.assertLess(wt["stale_minutes"], 60.0)

            git_cmd(repo, "reset", "--hard", "HEAD")
            old_untracked = repo / "stale.md"
            old_untracked.write_text("old\n", encoding="utf-8")
            old_ts = time.time() - 7200.0
            os.utime(old_untracked, (old_ts, old_ts))
            _, d_old = run_cli("--repo", str(repo), "--min-stale-minutes", "60")
            self.assertFalse(d_old["repos"][0]["worktrees"][0]["recently_modified"])

    def test_ignored_subdir_renamed_cred_secrets_dir_symlink_and_evidence_doc(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = init_repo(root)
            (repo / ".gitignore").write_text("environments/local/\n", encoding="utf-8")
            (repo / ".env.prod").write_text("ENV=1\n", encoding="utf-8")
            git_cmd(repo, "add", ".gitignore")
            git_cmd(repo, "add", "-f", ".env.prod")
            git_cmd(repo, "commit", "-m", "Add ignore and env")

            git_cmd(repo, "mv", ".env.prod", "cfg.txt")
            (repo / "environments" / "local").mkdir(parents=True)
            (repo / "environments" / "local" / ".env").write_text("TOKEN=x\n", encoding="utf-8")
            (repo / "secrets").mkdir()
            (repo / "secrets" / "prod.json").write_text("{}\n", encoding="utf-8")
            (repo / "docs" / "evidence").mkdir(parents=True)
            (repo / "docs" / "evidence" / "spec.md").write_text("real doc\n", encoding="utf-8")
            outside = root / "outside.txt"
            outside.write_text("host\n", encoding="utf-8")
            (repo / "docs" / "escape").symlink_to(outside)

            rc, data = run_cli("--repo", str(repo))
            self.assertEqual(rc, 0)
            repo_rep = data["repos"][0]
            wt = repo_rep["worktrees"][0]
            self.assertTrue(repo_rep["has_symlink_candidates"])
            self.assertEqual(wt["symlink_candidates"], ["docs/escape"])
            self.assertEqual(wt["ignored_credential_or_env_files"], ["environments/local/.env"])
            self.assertIn(".env.prod", wt["credential_or_env_candidates"])
            self.assertIn("secrets/prod.json", wt["credential_or_env_candidates"])
            self.assertFalse(wt["likely_scratch_only"])

            (repo / "docs" / "escape").unlink()
            git_cmd(repo, "reset", "--hard", "HEAD")
            (repo / "secrets" / "prod.json").unlink()
            (repo / "docs" / "evidence" / "spec.md").write_text("doc only\n", encoding="utf-8")
            _, d_doc = run_cli("--repo", str(repo))
            self.assertFalse(d_doc["repos"][0]["worktrees"][0]["likely_scratch_only"])

    def test_detached_worktree_dedups_to_named_and_skips_root_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target_repo = init_repo(root / "external", "target-repo")
            (root / "link-repo").symlink_to(target_repo)

            repo = init_repo(root, "dup-pref")
            wt_det = root / "wt-detached"
            wt_named = root / "wt-named"
            git_cmd(repo, "worktree", "add", "--detach", str(wt_det), "main")
            git_cmd(repo, "worktree", "add", "-b", "feature/keep", str(wt_named), "main")
            for tree in (wt_det, wt_named):
                (tree / "README.md").write_text("identical\n", encoding="utf-8")

            rc, data = run_cli("--repos-root", str(root))
            self.assertEqual(rc, 0)
            names = [r["name"] for r in data["repos"]]
            self.assertNotIn("target-repo", names)
            wts = {w["path"]: w for w in data["repos"][0]["worktrees"]}
            self.assertIsNone(wts[str(wt_named.resolve())]["duplicate_of_worktree"])
            self.assertEqual(wts[str(wt_det.resolve())]["duplicate_of_worktree"], str(wt_named.resolve()))

            _, d_follow = run_cli("--repos-root", str(root), "--follow-symlinks")
            self.assertIn("target-repo", [r["name"] for r in d_follow["repos"]])

    def test_populated_uninitialized_submodule_triggers_safety_gap(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            sub = init_repo(root, "sub-upstream")
            parent = init_repo(root, "parent")
            subprocess.run(
                ["git", "-c", "protocol.file.allow=always", "-C", str(parent), "submodule", "add", str(sub), "vendor/sub"],
                check=True,
                capture_output=True,
                text=True,
            )
            git_cmd(parent, "commit", "-m", "Add submodule")
            git_cmd(parent, "submodule", "deinit", "-f", "vendor/sub")
            (parent / "vendor" / "sub" / "stray.txt").write_text("untracked inside uninit sub\n", encoding="utf-8")

            rc, data = run_cli("--repo", str(parent))
            self.assertEqual(rc, 2)
            self.assertTrue(data["incomplete"])
            self.assertIn("uninitialized submodule", data["repos"][0]["worktrees"][0]["safety_gap"])

    def test_non_git_repo_and_repos_root_dirty_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            plain = root / "not-a-repo"
            plain.mkdir()
            init_repo(root, "clean-repo")

            rc_single, d_single = run_cli("--repo", str(plain))
            self.assertEqual(rc_single, 1)
            self.assertTrue(d_single["incomplete"])
            self.assertEqual(d_single["repos"][0]["name"], "not-a-repo")
            self.assertFalse(d_single["repos"][0]["has_dirty_work"])
            self.assertEqual(d_single["repos"][0]["worktrees"], [])

            (plain / ".git").mkdir()
            rc_root, d_root = run_cli("--repos-root", str(root), "--dirty-only")
            self.assertEqual(rc_root, 2)
            self.assertTrue(d_root["incomplete"])
            self.assertEqual(d_root["clean_repos_omitted"], 1)
            names = [r["name"] for r in d_root["repos"]]
            self.assertEqual(names, ["not-a-repo"])
            self.assertFalse(d_root["repos"][0]["has_dirty_work"])

    def test_partial_clone_without_filter_driver_and_clean_omitted_count(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = init_repo(root, "partial-clean")
            git_cmd(repo, "config", "extensions.partialclone", "origin")

            rc, data = run_cli("--repos-root", str(root), "--dirty-only")
            self.assertEqual(rc, 2)
            self.assertTrue(data["incomplete"])
            self.assertEqual(data["clean_repos_omitted"], 0)
            self.assertEqual(len(data["repos"]), 1)
            self.assertIn("partial clone", data["repos"][0]["worktrees"][0]["safety_gap"])

    def test_likely_scratch_rejects_ops_conflicts_and_secrets(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = init_repo(root, "scratch-guards")
            (repo / "debug.log").write_text("trace\n", encoding="utf-8")
            (repo / ".git" / "index.lock").write_text("", encoding="utf-8")
            _, d_op = run_cli("--repo", str(repo))
            self.assertFalse(d_op["repos"][0]["worktrees"][0]["likely_scratch_only"])
            (repo / ".git" / "index.lock").unlink()

            (repo / "shared.txt").write_text("base\n", encoding="utf-8")
            git_cmd(repo, "add", "shared.txt")
            git_cmd(repo, "commit", "-m", "Add shared")
            git_cmd(repo, "checkout", "-b", "side")
            (repo / "shared.txt").write_text("side change\n", encoding="utf-8")
            git_cmd(repo, "commit", "-am", "Side edit")
            git_cmd(repo, "checkout", "main")
            (repo / "shared.txt").write_text("main change\n", encoding="utf-8")
            git_cmd(repo, "commit", "-am", "Main edit")
            subprocess.run(["git", "-C", str(repo), "merge", "side"], check=False, capture_output=True, text=True)
            merge_head = repo / ".git" / "MERGE_HEAD"
            if merge_head.exists():
                merge_head.unlink()
            _, d_conf = run_cli("--repo", str(repo))
            wt_conf = d_conf["repos"][0]["worktrees"][0]
            self.assertTrue(wt_conf["merge_conflicts"])
            self.assertFalse(wt_conf["likely_scratch_only"])

            git_cmd(repo, "reset", "--hard", "HEAD")
            (repo / "debug.log").unlink()
            (repo / "secrets").mkdir()
            (repo / "secrets" / "debug.log").write_text("secret=1\n", encoding="utf-8")
            _, d_sec = run_cli("--repo", str(repo))
            wt_sec = d_sec["repos"][0]["worktrees"][0]
            self.assertFalse(wt_sec["likely_scratch_only"])
            self.assertEqual(wt_sec["credential_or_env_candidates"], ["secrets/debug.log"])

    def test_compute_dirty_fingerprint_propagates_git_diff_errors(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fp, errs = compute_dirty_fingerprint(Path(tmp), "deadbeef", b" M a.txt\0", [])
            self.assertIsNone(fp)
            self.assertEqual(len(errs), 2)
            self.assertIn("git diff", errs[0])


if __name__ == "__main__":
    unittest.main()
