"""Pin browser-selection failures at the two collector CLI boundaries, without launching browsers."""

import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SKILLS = ("diagram-design", "fit-surface")


class BrowserSelectionChecks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.node = shutil.which("node")
        self.assertIsNotNone(self.node, "Node.js 18+ is required")
        self.mock = self.root / "playwright.mjs"
        self.mock.write_text(
            "import { writeFileSync } from 'node:fs';\n"
            "export const chromium = { launch: async options => {\n"
            "writeFileSync(process.env.MOCK_LAUNCH_LOG, JSON.stringify(options));\n"
            "throw new Error('MOCK_LAUNCH_ONLY'); }};\n"
        )

    def executable(self, relative, mode=0o700):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("#!/bin/sh\nexit 99\n")
        path.chmod(mode)
        return path

    def probe(self, skill, configured):
        directory = self.root / skill
        directory.mkdir(exist_ok=True)
        output = directory / "evidence"
        marker = directory / "launch.json"
        env = os.environ.copy()
        env.pop("CHROME_PATH", None)
        env["MOCK_LAUNCH_LOG"] = str(marker)
        if configured is not None:
            env["CHROME_PATH"] = str(configured)
        result = subprocess.run(
            [self.node, str(REPO / "skills" / skill / "scripts" / "check-browser.mjs"),
             str(self.mock), str(output)],
            env=env, text=True, capture_output=True, check=False,
        )
        return result, output, marker

    def assert_rejected(self, configured):
        for skill in SKILLS:
            with self.subTest(skill=skill):
                result, output, marker = self.probe(skill, configured)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("CHROME_PATH", result.stderr)
                self.assertFalse(marker.exists(), result.stderr)
                self.assertFalse(output.exists(), "Rejected configuration created evidence output")

    def test_installed_chrome_and_disguised_alias_reject_before_output(self):
        installed = self.executable("Google Chrome.app/Contents/MacOS/Google Chrome")
        variants = [installed,
                    self.executable("Google Chrome Beta.app/Contents/MacOS/Google Chrome Beta"),
                    self.executable("bin/google-chrome-stable")]
        alias = self.root / "chrome-headless-shell"
        alias.symlink_to(installed)
        for path in [*variants, alias]:
            with self.subTest(configured=path.name):
                self.assert_rejected(path)

    def test_unusable_explicit_browser_rejects_before_output(self):
        for path in [self.root / "missing", self.executable("no-execute", 0o600), self.root]:
            with self.subTest(configured=path.name):
                self.assert_rejected(path)

    def test_bundled_default_and_explicit_browser_preserve_launch_options(self):
        shell = self.executable("bundled/chrome-headless-shell")
        alias = self.root / "selected-browser"
        alias.symlink_to(shell)
        for index, configured in enumerate([None, "", shell, alias]):
            for skill in SKILLS:
                with self.subTest(skill=skill, configured=configured):
                    result, output, marker = self.probe(skill, configured)
                    self.assertIn("MOCK_LAUNCH_ONLY", result.stderr)
                    self.assertNotEqual(result.returncode, 0)
                    options = json.loads(marker.read_text())
                    expected = {"headless": True}
                    if index >= 2:
                        expected["executablePath"] = str(shell)
                    self.assertEqual(options, expected)
                    self.assertTrue(output.is_dir())
                    marker.unlink()


if __name__ == "__main__":
    unittest.main()
