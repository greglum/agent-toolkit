"""Regression and contract tests for the five shared retro-guardrails scripts."""

from __future__ import annotations

import json
import os
import stat
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

SCRIPTS_DIR = Path(os.environ.get("RETRO_SCRIPTS_DIR", Path(__file__).resolve().parent))
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import git_evidence  # noqa: E402
import github_evidence  # noqa: E402
import repo_controls  # noqa: E402
import retro_state  # noqa: E402

BASE_ENV = {
    **os.environ,
    "GIT_CONFIG_GLOBAL": os.devnull,
    "GIT_CONFIG_NOSYSTEM": "1",
    "GIT_AUTHOR_NAME": "fixture",
    "GIT_AUTHOR_EMAIL": "fixture@localhost",
    "GIT_COMMITTER_NAME": "fixture",
    "GIT_COMMITTER_EMAIL": "fixture@localhost",
}


class TempGitRepo:
    def __init__(self, root: Path, remote: str | None = "https://github.com/org/demo.git") -> None:
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)
        self.git("init", "-q", "-b", "main")
        if remote:
            self.git("remote", "add", "origin", remote)

    def git(self, *args: str, days_ago: int | None = None) -> str:
        env = dict(BASE_ENV)
        if days_ago is not None:
            stamp = (datetime.now(timezone.utc) - timedelta(days=days_ago)).isoformat()
            env.update(GIT_AUTHOR_DATE=stamp, GIT_COMMITTER_DATE=stamp)
        proc = subprocess.run(
            ["git", "-C", str(self.root), *args],
            capture_output=True,
            text=True,
            env=env,
            check=True,
        )
        return proc.stdout.strip()

    def write(self, rel: str, text: str) -> None:
        target = self.root / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")

    def commit(self, subject: str, days_ago: int = 1) -> str:
        self.git("add", "-A")
        self.git("commit", "-q", "-m", subject, days_ago=days_ago)
        return self.git("rev-parse", "HEAD")


def make_fake_gh(bin_dir: Path, exit_code: int, stdout_json: dict, stderr_text: str = "") -> dict[str, str]:
    gh_path = bin_dir / "gh"
    payload = json.dumps(stdout_json)
    gh_path.write_text(
        f"#!/bin/sh\n"
        f"printf '%s' {json.dumps(payload)}\n"
        f"printf '%s' {json.dumps(stderr_text)} >&2\n"
        f"exit {exit_code}\n",
        encoding="utf-8",
    )
    gh_path.chmod(gh_path.stat().st_mode | stat.S_IXUSR)
    env = dict(BASE_ENV)
    env["PATH"] = f"{bin_dir}:{BASE_ENV.get('PATH', '/usr/bin:/bin')}"
    return env


def pr_node(number: int, author_login: str = "alice", reviewer_login: str = "bob", review_count: int = 1) -> dict:
    return {
        "number": number,
        "title": f"PR {number}",
        "body": "fixes bug",
        "additions": 3,
        "deletions": 1,
        "changedFiles": 1,
        "createdAt": "2026-11-10T00:00:00Z",
        "mergedAt": "2026-11-10T01:00:00Z",
        "author": {"__typename": "User", "login": author_login},
        "commits": {"totalCount": 1},
        "reviews": {
            "totalCount": review_count,
            "nodes": [{"author": {"__typename": "User", "login": reviewer_login}, "state": "APPROVED", "body": "lgtm"}],
        },
        "comments": {"totalCount": 0, "nodes": []},
        "reviewThreads": {"totalCount": 0, "nodes": []},
    }


class RetroScriptsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name).resolve()

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def run_collector(self, repo: Path, *extra: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "collect_history.py"), "--repo", str(repo), *extra],
            capture_output=True,
            text=True,
            env=env or BASE_ENV,
            check=False,
        )

    def test_graphql_errors_with_data_and_nonzero_exit_are_surfaced(self) -> None:
        """Planted-defect regression: top-level GraphQL errors must not be ignored when data is present."""
        repo = TempGitRepo(self.root / "repo")
        repo.write("app.py", "x = 1\n")
        repo.commit("feat: add app (#1)", days_ago=2)
        repo.write("app.py", "x = 2\n")
        repo.commit("fix: patch app (#2)", days_ago=1)

        fake_bin = self.root / "bin"
        fake_bin.mkdir()
        response = {
            "data": {"repository": {"p1": pr_node(1), "p2": None}},
            "errors": [{"message": "API rate limit exceeded for pullRequest 2"}],
        }
        env = make_fake_gh(fake_bin, exit_code=1, stdout_json=response, stderr_text="gh: GraphQL error")

        proc = self.run_collector(repo.root, "--ref", "main", "--days", "10", "--start-tracking", env=env)
        self.assertEqual(proc.returncode, 2)
        report = json.loads(proc.stdout)
        self.assertIsNone(report["coverage"]["marker_advance"])
        self.assertEqual(report["coverage"]["confidence_cap"], "candidate")
        self.assertTrue(
            any("API rate limit exceeded" in gap for gap in report["coverage"]["gaps"]),
            report["coverage"]["gaps"],
        )

    def test_graphql_errors_with_null_repository_mark_unavailable(self) -> None:
        repo = TempGitRepo(self.root / "repo_null")
        repo.write("app.py", "x = 1\n")
        repo.commit("feat: add app (#1)", days_ago=1)

        fake_bin = self.root / "bin_null"
        fake_bin.mkdir()
        response = {
            "data": {"repository": None},
            "errors": [{"message": "Could not resolve to a Repository"}],
        }
        env = make_fake_gh(fake_bin, exit_code=1, stdout_json=response, stderr_text="gh failed")

        proc = self.run_collector(repo.root, "--ref", "main", "--days", "10", env=env)
        self.assertEqual(proc.returncode, 2)
        report = json.loads(proc.stdout)
        self.assertEqual(report["coverage"]["tier"], "git")
        self.assertTrue(any("Could not resolve to a Repository" in g for g in report["coverage"]["gaps"]))

    def test_confidence_cap_requires_human_review_and_untruncated_threads(self) -> None:
        repo = TempGitRepo(self.root / "repo_cap")
        repo.write("a.py", "x = 1\n")
        repo.commit("feat: self reviewed (#10)", days_ago=2)

        fake_bin = self.root / "bin_cap"
        fake_bin.mkdir()
        env_self = make_fake_gh(
            fake_bin,
            exit_code=0,
            stdout_json={"data": {"repository": {"p10": pr_node(10, "alice", "alice")}}},
        )
        proc_self = self.run_collector(repo.root, "--ref", "main", "--days", "10", env=env_self)
        self.assertEqual(proc_self.returncode, 0)
        self.assertEqual(json.loads(proc_self.stdout)["coverage"]["confidence_cap"], "candidate")

        env_human = make_fake_gh(
            fake_bin,
            exit_code=0,
            stdout_json={"data": {"repository": {"p10": pr_node(10, "alice", "bob")}}},
        )
        proc_human = self.run_collector(repo.root, "--ref", "main", "--days", "10", env=env_human)
        self.assertEqual(proc_human.returncode, 0)
        self.assertEqual(json.loads(proc_human.stdout)["coverage"]["confidence_cap"], "confirmed")

        env_trunc = make_fake_gh(
            fake_bin,
            exit_code=0,
            stdout_json={"data": {"repository": {"p10": pr_node(10, "alice", "bob", review_count=31)}}},
        )
        proc_trunc = self.run_collector(repo.root, "--ref", "main", "--days", "10", env=env_trunc)
        self.assertEqual(proc_trunc.returncode, 2)
        trunc_report = json.loads(proc_trunc.stdout)
        self.assertEqual(trunc_report["coverage"]["confidence_cap"], "candidate")
        self.assertTrue(any("truncated" in g for g in trunc_report["coverage"]["gaps"]))

    def test_non_ancestor_marker_and_dash_marker_produce_gap_and_hold_advance(self) -> None:
        repo = TempGitRepo(self.root / "repo_marker", remote=None)
        repo.write("a.py", "x = 1\n")
        repo.commit("feat: main", days_ago=2)
        repo.git("checkout", "-q", "--orphan", "other")
        repo.write("b.py", "y = 1\n")
        orphan_sha = repo.commit("feat: orphan", days_ago=1)
        repo.git("checkout", "-q", "main")

        for bad_marker in (orphan_sha, "deadbeef" * 5, "--help"):
            proc = self.run_collector(repo.root, "--ref", "main", f"--since-sha={bad_marker}", "--no-gh")
            self.assertEqual(proc.returncode, 2, bad_marker)
            cov = json.loads(proc.stdout)["coverage"]
            self.assertIsNone(cov["marker_advance"])
            self.assertTrue(any("marker is missing or not an ancestor" in g for g in cov["gaps"]))

    def test_shallow_clone_is_reported_as_gap(self) -> None:
        upstream = TempGitRepo(self.root / "upstream", remote=None)
        upstream.write("a.py", "x = 1\n")
        upstream.commit("feat: c1", days_ago=3)
        upstream.write("a.py", "x = 2\n")
        upstream.commit("fix: c2", days_ago=1)

        shallow = self.root / "shallow"
        subprocess.run(
            ["git", "clone", "-q", "--depth", "1", f"file://{upstream.root}", str(shallow)],
            env=BASE_ENV,
            check=True,
        )
        proc = self.run_collector(shallow, "--ref", "HEAD", "--days", "10", "--no-gh")
        self.assertEqual(proc.returncode, 2)
        cov = json.loads(proc.stdout)["coverage"]
        self.assertIn("shallow clone", cov["gaps"])
        self.assertIsNone(cov["marker_advance"])

    def test_rename_chains_and_non_ascii_paths(self) -> None:
        repo = TempGitRepo(self.root / "repo_rename", remote=None)
        body = "".join(f"line {i}\n" for i in range(25))
        repo.write("café_v1.py", body)
        c1 = repo.commit("feat: add file", days_ago=4)
        (repo.root / "café_v1.py").unlink()
        repo.write("café_v2.py", body)
        c2 = repo.commit("refactor: rename 1", days_ago=3)
        (repo.root / "café_v2.py").unlink()
        repo.write("café_v3.py", body + "x = 1\n")
        c3 = repo.commit("fix: rename 2 and fix", days_ago=1)

        commits, renames, issues = git_evidence.read_commits(repo.root, [c1, c2, c3])
        self.assertEqual(sum(issues.values()), 0)
        self.assertEqual(git_evidence.canonical("café_v1.py", renames), "café_v3.py")
        summary = git_evidence.summarize(commits, renames)
        self.assertIn("café_v3.py", summary["most_changed_paths"])
        self.assertEqual(summary["fix_like_commits"], [c3[:12]])

    def test_output_guard_and_parent_creation(self) -> None:
        repo = TempGitRepo(self.root / "repo_out", remote=None)
        repo.write("a.py", "x = 1\n")
        repo.commit("feat: init", days_ago=1)

        inside = repo.root / "leak.json"
        bad = self.run_collector(repo.root, "--ref", "main", "--no-gh", "--output", str(inside))
        self.assertNotEqual(bad.returncode, 0)
        self.assertFalse(inside.exists())

        outside = self.root / "nested" / "dir" / "history.json"
        good = self.run_collector(repo.root, "--ref", "main", "--no-gh", "--start-tracking", "--output", str(outside))
        self.assertEqual(good.returncode, 0)
        self.assertTrue(outside.is_file())
        stdout_data = json.loads(good.stdout)
        self.assertNotIn("commits", stdout_data)
        self.assertIsNotNone(stdout_data["coverage"]["marker_advance"])
        file_data = json.loads(outside.read_text(encoding="utf-8"))
        self.assertEqual(len(file_data["commits"]), 1)

    def test_repo_controls_detects_gemini_claude_and_agents_skills_at_ref(self) -> None:
        repo = TempGitRepo(self.root / "repo_ctrl", remote=None)
        repo.write("AGENTS.md", "# rules\n")
        repo.write(".github/workflows/ci.yml", "name: ci\n")
        repo.write(".agents/skills/a/SKILL.md", "---\nname: a\ndescription: a\n---\n")
        repo.write(".claude/skills/b/SKILL.md", "---\nname: b\ndescription: b\n---\n")
        repo.write(".gemini/skills/c/SKILL.md", "---\nname: c\ndescription: c\n---\n")
        head = repo.commit("chore: add controls", days_ago=1)
        repo.write("CLAUDE.md", "# uncommitted\n")

        controls = repo_controls.repo_controls(repo.root, head)
        self.assertEqual([f["path"] for f in controls["instruction_files"]], ["AGENTS.md"])
        self.assertIn(".github/workflows/ci.yml", controls["control_files"])
        self.assertEqual(
            controls["skill_roots"],
            [".agents/skills", ".claude/skills", ".gemini/skills"],
        )

    def test_retro_state_key_determinism_and_non_git_failure(self) -> None:
        ssh_remote = "git" + "@" + "github.com:Org/Demo.git"
        clone_a = TempGitRepo(self.root / "clone_a", remote=ssh_remote)
        clone_b = TempGitRepo(self.root / "clone_b", remote="https://github.com/org/demo/")
        self.assertEqual(retro_state.repo_key(clone_a.root), retro_state.repo_key(clone_b.root))

        local = TempGitRepo(self.root / "local", remote=None)
        local.write("f.txt", "1\n")
        local.commit("init")
        wt = self.root / "local_wt"
        local.git("worktree", "add", "-q", str(wt))
        self.assertEqual(retro_state.repo_key(local.root), retro_state.repo_key(wt))

        non_git = self.root / "not_a_repo"
        non_git.mkdir()
        proc = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "retro_state.py"), "--repo", str(non_git), "--focus", "guardrails"],
            capture_output=True,
            text=True,
            env=BASE_ENV,
            check=False,
        )
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("not a git repository", proc.stderr)

        no_git_env = {**BASE_ENV, "PATH": ""}
        proc_no_git = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "retro_state.py"), "--repo", str(local.root), "--focus", "guardrails"],
            capture_output=True,
            text=True,
            env=no_git_env,
            check=False,
        )
        self.assertNotEqual(proc_no_git.returncode, 0)

    def test_github_helpers(self) -> None:
        ssh_remote = "git" + "@" + "github.com:org/repo.git"
        self.assertEqual(github_evidence.github_slug(ssh_remote), "org/repo")
        self.assertEqual(github_evidence.github_slug("https://github.com/org/repo/"), "org/repo")
        self.assertIsNone(github_evidence.github_slug("https://gitlab.com/org/repo.git"))
        nums, unref = github_evidence.pr_numbers([
            {"subject": "feat: one (#12)"},
            {"subject": "Merge pull request #15 from org/branch"},
            {"subject": "chore: direct commit"},
        ])
        self.assertEqual(nums, [12, 15])
        self.assertEqual(unref, 1)


if __name__ == "__main__":
    unittest.main()
