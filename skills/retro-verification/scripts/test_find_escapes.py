"""Cases where find_escapes.py would otherwise mis-attribute an escape without any error."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "find_escapes.py"
ENV = {
    **os.environ,
    "GIT_CONFIG_GLOBAL": os.devnull,
    "GIT_CONFIG_NOSYSTEM": "1",
    "GIT_AUTHOR_NAME": "fixture",
    "GIT_AUTHOR_EMAIL": "fixture@localhost",
    "GIT_COMMITTER_NAME": "fixture",
    "GIT_COMMITTER_EMAIL": "fixture@localhost",
}


class Repo:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.git("init", "-q", "-b", "main")

    def git(self, *args: str, days_ago: int | None = None) -> str:
        env = dict(ENV)
        if days_ago is not None:
            stamp = (datetime.now(timezone.utc) - timedelta(days=days_ago)).isoformat()
            env.update(GIT_AUTHOR_DATE=stamp, GIT_COMMITTER_DATE=stamp)
        result = subprocess.run(["git", "-C", str(self.root), *args], capture_output=True, text=True, env=env, check=True)
        return result.stdout.strip()

    def write(self, path: str, text: str) -> None:
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")

    def commit(self, subject: str, days_ago: int) -> str:
        self.git("add", "-A")
        self.git("commit", "-q", "-m", subject, days_ago=days_ago)
        return self.git("rev-parse", "HEAD")[:12]

    def escapes(self, *extra: str) -> dict:
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--repo", str(self.root), "--ref", "main", "--days", "90", *extra],
            capture_output=True, text=True, env=ENV, check=False,
        )
        self.exit_code = result.returncode
        return json.loads(result.stdout)


class FindEscapesTest(unittest.TestCase):
    def setUp(self) -> None:
        self.folder = tempfile.TemporaryDirectory()
        self.repo = Repo(Path(self.folder.name))

    def tearDown(self) -> None:
        self.folder.cleanup()

    def rename_repo(self) -> tuple[str, str]:
        self.repo.write("README", "seed\n")
        self.repo.commit("chore: seed", 70)
        body = "".join(f"line {n}\n" for n in range(1, 30))
        self.repo.write("src/a.py", body + "limit = 10\n")
        intro = self.repo.commit("feat: add limit (#3)", 60)
        (self.repo.root / "src/a.py").unlink()
        self.repo.write("src/b.py", body + "limit = 100\n")
        fix = self.repo.commit("fix: correct limit (#7)", 30)
        return intro, fix

    def test_fix_that_renames_blames_the_old_path(self) -> None:
        intro, fix = self.rename_repo()
        escape = next(e for e in self.repo.escapes()["escapes"] if e["fix"] == fix)
        self.assertEqual(escape["blamed_paths"], ["src/a.py"])
        self.assertEqual([(i["sha"], i["pr"], i["lines"]) for i in escape["introducers"]], [(intro, 3, 1)])
        self.assertEqual(escape["pr"], 7)

    def test_lines_older_than_lookback_are_not_introducers(self) -> None:
        _, fix = self.rename_repo()
        escape = next(e for e in self.repo.escapes("--lookback-days", "10")["escapes"] if e["fix"] == fix)
        self.assertEqual(escape["introducers"], [])
        self.assertEqual(escape["lines_older_than_lookback"], 1)

    def test_merge_fix_blames_first_parent_and_root_is_skipped(self) -> None:
        self.repo.write("app.py", "x = 1\n")
        self.repo.commit("fix: initial import", 50)
        self.repo.write("app.py", "x = 2\n")
        intro = self.repo.commit("feat: change x", 40)
        self.repo.git("checkout", "-q", "-b", "side")
        self.repo.write("app.py", "x = 3\n")
        self.repo.write("tests/test_app.py", "assert True\n")
        self.repo.write("new.py", "added = True\n")
        self.repo.commit("fix: restore x", 20)
        self.repo.git("checkout", "-q", "main")
        self.repo.git("merge", "-q", "--no-ff", "-m", "Merge pull request #9 from fork/side", "side", days_ago=19)
        report = self.repo.escapes()
        self.assertEqual(report["coverage"]["root_commits_skipped"], 1)
        (escape,) = report["escapes"]
        self.assertEqual((escape["shape"], escape["pr"]), ("merge", 9))
        self.assertEqual([i["sha"] for i in escape["introducers"]], [intro])
        self.assertEqual(escape["fix_added_tests"], ["tests/test_app.py"])
        self.assertEqual(escape["unattributed_added_paths"], ["new.py"])

    def test_spaced_path_is_blamed_and_cap_spares_small_files(self) -> None:
        self.repo.write("README", "seed\n")
        self.repo.commit("chore: seed", 70)
        self.repo.write("sp ace.py", "x = 1\n")
        self.repo.write("big.py", "".join(f"v{n} = {n}\n" for n in range(50)))
        intro = self.repo.commit("feat: add files", 60)
        self.repo.write("sp ace.py", "x = 2\n")
        self.repo.write("big.py", "".join(f"v{n} = {n + 1}\n" for n in range(50)))
        fix = self.repo.commit("fix: correct values", 30)
        report = self.repo.escapes("--max-lines", "10")
        escape = next(e for e in report["escapes"] if e["fix"] == fix)
        self.assertEqual(self.repo.exit_code, 0)
        self.assertIn("sp ace.py", escape["blamed_paths"])
        self.assertEqual(escape["capped_paths"], ["big.py"])
        self.assertEqual([i["sha"] for i in escape["introducers"]], [intro])

    def test_git_blame_ignore_revs_excludes_formatting_commit(self) -> None:
        self.repo.write("app.py", "x = 1\n")
        intro = self.repo.commit("feat: add value", 60)
        self.repo.write("app.py", "x = 1  # formatted\n")
        fmt_sha = self.repo.commit("style: format comment", 40)
        full_fmt = self.repo.git("rev-parse", fmt_sha)
        self.repo.write(".git-blame-ignore-revs", f"{full_fmt}\n")
        self.repo.commit("chore: add blame ignore", 35)
        self.repo.write("app.py", "x = 2  # fixed\n")
        fix = self.repo.commit("fix: correct value", 10)

        report = self.repo.escapes()
        self.assertEqual(self.repo.exit_code, 0)
        escape = next(e for e in report["escapes"] if e["fix"] == fix)
        self.assertEqual([i["sha"] for i in escape["introducers"]], [intro])
        self.assertTrue(
            any(".git-blame-ignore-revs" in lim for lim in report["coverage"]["limits"]),
            report["coverage"]["limits"],
        )

    def test_invalid_since_sha_returns_exit_2_with_gap(self) -> None:
        self.repo.write("app.py", "x = 1\n")
        self.repo.commit("feat: init", 20)
        self.repo.write("app.py", "x = 2\n")
        self.repo.commit("fix: patch", 10)

        report = self.repo.escapes("--since-sha", "deadbeef" * 5)
        self.assertEqual(self.repo.exit_code, 2)
        self.assertTrue(
            any("marker is missing or not an ancestor" in gap for gap in report["coverage"]["gaps"]),
            report["coverage"]["gaps"],
        )

    def test_rejects_leading_dash_ref_and_in_repo_output(self) -> None:
        self.repo.write("app.py", "x = 1\n")
        self.repo.commit("feat: init", 10)
        bad_ref = subprocess.run(
            [sys.executable, str(SCRIPT), "--repo", str(self.repo.root), "--ref", "--all"],
            capture_output=True, text=True, env=ENV, check=False,
        )
        self.assertNotEqual(bad_ref.returncode, 0)

        inside = self.repo.root / "escapes.json"
        bad_out = subprocess.run(
            [sys.executable, str(SCRIPT), "--repo", str(self.repo.root), "--ref", "main", "--output", str(inside)],
            capture_output=True, text=True, env=ENV, check=False,
        )
        self.assertNotEqual(bad_out.returncode, 0)
        self.assertFalse(inside.exists())

    def test_output_creates_missing_parent_directory(self) -> None:
        self.repo.write("app.py", "x = 1\n")
        self.repo.commit("feat: init", 10)
        with tempfile.TemporaryDirectory() as out_dir:
            out_path = Path(out_dir) / "nested" / "escapes.json"
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--repo", str(self.repo.root), "--ref", "main", "--output", str(out_path)],
                capture_output=True, text=True, env=ENV, check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(out_path.is_file())


if __name__ == "__main__":
    unittest.main()
