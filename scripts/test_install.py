"""Exercise installation without writing the user's harness configuration."""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from install import REPO, link_agents


class InstallChecks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name)

    def run_install(self, *args):
        return subprocess.run(
            [sys.executable, str(REPO / "scripts/install.py"), "--home", str(self.home), *args],
            capture_output=True, text=True, check=False,
        )

    def test_harness_selection_and_idempotence(self):
        for harness, selected, absent in (
            ("codex", ".agents", ".claude"),
            ("claude", ".claude", ".agents"),
        ):
            with self.subTest(harness=harness), tempfile.TemporaryDirectory() as directory:
                self.home = Path(directory)
                args = ("--harness", harness, "--only", "find-docs")
                dry = self.run_install(*args, "--dry-run")
                self.assertEqual(dry.returncode, 0, dry.stderr)
                self.assertEqual(list(self.home.iterdir()), [])
                first = self.run_install(*args)
                self.assertEqual(first.returncode, 0, first.stderr)
                link = self.home / selected / "skills/find-docs"
                self.assertEqual(link.resolve(), REPO / "skills/find-docs")
                self.assertFalse((self.home / absent).exists())
                stamp = link.lstat().st_mtime_ns
                second = self.run_install(*args)
                self.assertEqual(second.returncode, 0, second.stderr)
                self.assertEqual(link.lstat().st_mtime_ns, stamp)

    def test_conflicting_install_is_preserved(self):
        dest = self.home / ".claude/skills/find-docs"
        dest.mkdir(parents=True)
        personal = dest / "SKILL.md"
        personal.write_text("Personal changes\n")
        result = self.run_install("--harness", "claude", "--only", "find-docs")
        self.assertEqual(result.returncode, 1)
        self.assertEqual(personal.read_text(), "Personal changes\n")
        self.assertFalse(dest.is_symlink())
        self.assertFalse((self.home / ".agents").exists())

    def test_unknown_selection_changes_nothing(self):
        result = self.run_install("--only", "find-docs,does-not-exist")
        self.assertEqual(result.returncode, 2)
        self.assertEqual(list(self.home.iterdir()), [])

    def test_stale_catalog_links_are_reported_and_pruned_only_on_request(self):
        agents, claude = self.home / ".agents/skills", self.home / ".claude/skills"
        agents.mkdir(parents=True)
        claude.mkdir(parents=True)
        removed = agents / "removed-skill"
        removed.symlink_to(REPO / "skills/removed-skill")
        removed_claude = claude / "removed-skill"
        removed_claude.symlink_to(Path("../../.agents/skills/removed-skill"))
        codex_only = claude / "acp"
        codex_only.symlink_to(REPO / "skills/acp")
        foreign = agents / "foreign"
        foreign.symlink_to(self.home / "elsewhere/foreign")
        (claude / "personal").mkdir()
        stale = (removed, removed_claude, codex_only)
        for args in (("--dry-run",), ("--dry-run", "--prune-stale"), ()):
            with self.subTest(args=args):
                result = self.run_install("--harness", "codex", "--only", "find-docs", *args)
                self.assertEqual(result.returncode, 0, result.stdout)
                self.assertEqual(result.stdout.count("stale: "), 3)
                self.assertTrue(all(link.is_symlink() for link in stale))
        result = self.run_install("--harness", "codex", "--only", "find-docs", "--prune-stale")
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertFalse(any(link.is_symlink() for link in stale))
        self.assertTrue(foreign.is_symlink())
        self.assertTrue((claude / "personal").is_dir())

    def test_failed_link_restores_identical_installed_copy(self):
        import shutil

        dest = self.home / ".agents/skills/find-docs"
        shutil.copytree(REPO / "skills/find-docs", dest)
        original = (dest / "SKILL.md").read_bytes()
        archive = self.home / "archive"
        with patch.object(Path, "symlink_to", side_effect=OSError("link denied")):
            with self.assertRaises(OSError):
                link_agents("find-docs", self.home, archive, dry=False)
        self.assertFalse(dest.is_symlink())
        self.assertEqual((dest / "SKILL.md").read_bytes(), original)
        self.assertFalse((archive / "find-docs").exists())


if __name__ == "__main__":
    unittest.main()
