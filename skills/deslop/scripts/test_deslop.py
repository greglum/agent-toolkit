"""Regression and contract checks for deslop tells.sh and lint.sh."""

import os
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
TELLS = Path(os.environ.get("DESLOP_TELLS_SCRIPT") or (SCRIPTS_DIR / "tells.sh"))
LINT = Path(os.environ.get("DESLOP_LINT_SCRIPT") or (SCRIPTS_DIR / "lint.sh"))


class TellsScriptTests(unittest.TestCase):
    def run_tells(self, cwd, *args):
        return subprocess.run(
            ["sh", str(TELLS), *args],
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
        )

    def test_strong_weak_and_clean_exit_codes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            strong = root / "strong.md"
            strong.write_text("Let's delve into this — not just code but craft.\n", encoding="utf-8")
            res_strong = self.run_tells(root, str(strong))
            self.assertEqual(res_strong.returncode, 1, res_strong.stdout + res_strong.stderr)
            self.assertIn("[strong] stock AI words", res_strong.stdout)
            self.assertIn("[strong] dashes as connector", res_strong.stdout)
            self.assertIn("[strong] not X but Y", res_strong.stdout)

            weak = root / "weak.md"
            weak.write_text("Actually, use plain verbs rather than jargon.\n", encoding="utf-8")
            res_weak = self.run_tells(root, str(weak))
            self.assertEqual(res_weak.returncode, 0, res_weak.stdout + res_weak.stderr)
            self.assertIn("[weak] empty adverbs", res_weak.stdout)
            self.assertIn("strong: 0", res_weak.stdout)

            clean = root / "clean.md"
            clean.write_text("Plain text states one fact per sentence.\n", encoding="utf-8")
            res_clean = self.run_tells(root, str(clean))
            self.assertEqual(res_clean.returncode, 0, res_clean.stdout + res_clean.stderr)
            self.assertIn("strong: 0  weak: 0", res_clean.stdout)

    def test_word_boundaries_do_not_match_substrings(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            note = root / "clean-words.md"
            note.write_text("The delver kept a notable button and overall design.\n", encoding="utf-8")
            res = self.run_tells(root, str(note))
            self.assertEqual(res.returncode, 0, res.stdout + res.stderr)
            self.assertIn("strong: 0  weak: 0", res.stdout)

    def test_pipe_in_pwd_and_leading_dash_filename(self):
        with tempfile.TemporaryDirectory() as directory:
            pipe_dir = Path(directory) / "dir|pipe"
            pipe_dir.mkdir()
            dashed = pipe_dir / "-note.md"
            dashed.write_text("We should delve into this.\n", encoding="utf-8")
            res = self.run_tells(pipe_dir, str(pipe_dir / "-note.md"))
            self.assertEqual(res.returncode, 1, res.stdout + res.stderr)
            self.assertEqual(res.stderr, "")
            self.assertIn("-note.md:1:", res.stdout)

    def test_missing_file_returns_2(self):
        with tempfile.TemporaryDirectory() as directory:
            res = self.run_tells(directory, "missing.md")
            self.assertEqual(res.returncode, 2)
            self.assertIn("cannot read file", res.stderr)


class LintScriptTests(unittest.TestCase):
    def make_fake_vale(self, bin_dir: Path, log_path: Path, exit_code: int = 0) -> None:
        vale = bin_dir / "vale"
        vale.write_text(
            f"""#!/bin/sh
printf '%s\\n' "$*" >> "{log_path}"
if [ "$3" = "sync" ] || [ "$1" = "sync" ]; then
  cfg=""
  for a in "$@"; do
    case "$prev" in --config) cfg="$a" ;; esac
    prev="$a"
  done
  [ -n "$cfg" ] && d=$(dirname "$cfg") && mkdir -p "$d/styles/write-good" "$d/styles/proselint" "$d/styles/Readability"
  exit 0
fi
exit {exit_code}
""",
            encoding="utf-8",
        )
        vale.chmod(vale.stat().st_mode | stat.S_IXUSR)

    def run_lint(self, root: Path, bin_dir: Path, cache_dir: Path, *args):
        env = os.environ.copy()
        env["PATH"] = f"{bin_dir}:{env.get('PATH', '')}"
        env["XDG_CACHE_HOME"] = str(cache_dir)
        return subprocess.run(
            ["sh", str(LINT), *args],
            cwd=root,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )

    def test_cold_cache_fails_closed_without_sync(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            bin_dir = root / "bin"
            cache_dir = root / "cache"
            bin_dir.mkdir()
            log = root / "vale.log"
            self.make_fake_vale(bin_dir, log)
            doc = root / "doc.md"
            doc.write_text("Plain text.\n", encoding="utf-8")

            res = self.run_lint(root, bin_dir, cache_dir, str(doc))
            self.assertEqual(res.returncode, 2)
            self.assertIn("--sync", res.stderr)
            self.assertFalse(log.exists(), "lint.sh invoked vale sync without --sync")

    def test_sync_flag_populates_cache_and_passes_double_dash(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            bin_dir = root / "bin"
            cache_dir = root / "cache"
            bin_dir.mkdir()
            log = root / "vale.log"
            self.make_fake_vale(bin_dir, log, exit_code=1)
            dashed = root / "-doc.md"
            dashed.write_text("Plain text.\n", encoding="utf-8")

            res = self.run_lint(root, bin_dir, cache_dir, "--all", "--sync", "--", "-doc.md")
            self.assertEqual(res.returncode, 1, res.stdout + res.stderr)
            calls = log.read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(calls), 2)
            self.assertIn(" sync", calls[0])
            self.assertIn("--minAlertLevel=suggestion -- -doc.md", calls[1])


if __name__ == "__main__":
    unittest.main()
