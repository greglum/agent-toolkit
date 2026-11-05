"""Exercise installation without writing the user's harness configuration."""

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from install import REPO, link_agents, same_tree


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

    def test_unknown_selection_still_reports_stale_links_and_prunes_nothing(self):
        agents = self.home / ".agents/skills"
        agents.mkdir(parents=True)
        removed = agents / "removed-skill"
        removed.symlink_to(REPO / "skills/removed-skill")
        result = self.run_install("--only", "find-docs,removed-skill", "--prune-stale")
        self.assertEqual(result.returncode, 2)
        self.assertIn("stale: ", result.stdout)
        self.assertIn("left the catalog", result.stderr)
        self.assertTrue(removed.is_symlink())
        self.assertFalse((agents / "find-docs").exists())

    def test_only_refuses_empty_names_and_trims_spaces(self):
        for value in ("", "find-docs,", ",", "find-docs,,to-spec"):
            with self.subTest(value=value):
                result = self.run_install("--only", value)
                self.assertEqual(result.returncode, 2)
                self.assertIn("none empty", result.stderr)
                self.assertEqual(list(self.home.iterdir()), [])
        result = self.run_install("--dry-run", "--only", "find-docs, to-spec")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("to-spec", result.stdout)

    def test_prune_only_installs_nothing(self):
        agents = self.home / ".agents/skills"
        agents.mkdir(parents=True)
        removed = agents / "removed-skill"
        removed.symlink_to(REPO / "skills/removed-skill")
        dry = self.run_install("--prune-only", "--dry-run")
        self.assertIn("would remove", dry.stdout)
        self.assertTrue(removed.is_symlink())
        self.assertEqual(self.run_install("--prune-only").returncode, 0)
        self.assertEqual(list(agents.iterdir()), [])
        self.assertEqual(self.run_install("--prune-only", "--only", "find-docs").returncode, 2)

    def test_same_tree_needs_matching_kinds_but_ignores_caches(self):
        source = REPO / "skills/fit-surface"
        copy = self.home / "copy"
        shutil.copytree(source, copy, ignore=shutil.ignore_patterns("__pycache__"))
        (copy / "__pycache__").mkdir()
        self.assertTrue(same_tree(source, copy))
        directory = next(p for p in source.iterdir() if p.is_dir() and p.name != "__pycache__")
        shutil.rmtree(copy / directory.name)
        (copy / directory.name).write_text("a file where the catalog has a folder\n")
        self.assertFalse(same_tree(source, copy))

    def test_awkward_paths_give_plain_errors(self):
        self.home.joinpath(".agents").mkdir()
        self.home.joinpath(".agents/skills").write_text("a file\n")
        result = self.run_install("--only", "find-docs")
        self.assertEqual(result.returncode, 2)
        self.assertIn("Stopped:", result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        self.home.joinpath(".agents/skills").unlink()
        self.home.joinpath(".agents/skills").mkdir()
        loop = self.home / ".agents/skills/find-docs"
        loop.symlink_to(loop)
        result = self.run_install("--only", "find-docs")
        self.assertEqual(result.returncode, 1)
        self.assertIn("conflict:", result.stdout)

    def test_shared_folder_stale_links_prune_once(self):
        agents = self.home / ".agents/skills"
        agents.mkdir(parents=True)
        (self.home / ".claude").mkdir()
        (self.home / ".claude/skills").symlink_to(agents)
        (agents / "removed-skill").symlink_to(REPO / "skills/removed-skill")
        result = self.run_install("--only", "find-docs", "--prune-stale")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.count("stale: "), 1)

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
