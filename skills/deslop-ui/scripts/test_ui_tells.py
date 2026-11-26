"""Regression checks for the scanner's target scope and CLI status contract."""

import os
import subprocess
import tempfile
import unittest
from pathlib import Path


SCANNER = Path(os.environ.get("UI_TELLS_SCANNER") or Path(__file__).with_name("ui-tells.sh"))


class ScannerContractTests(unittest.TestCase):
    def scan(self, root, *targets):
        return subprocess.run(
            ["bash", str(SCANNER), *map(str, targets)],
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
        )

    def test_dash_named_target_is_a_path_not_a_find_expression(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "-delete"
            target.mkdir()
            source = target / "App.tsx"
            source.write_text('<p>Ship it \U0001F680</p>\n')
            result = self.scan(root, "-delete")
            self.assertTrue(source.exists(), "the scan deleted a file under the target")
            self.assertEqual(result.returncode, 1)
            self.assertIn("V8 emoji", result.stdout)

    def test_invalid_target_is_failure_even_with_valid_matches(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "App.tsx"
            source.write_text('<h1 className="bg-clip-text">Title</h1>\n')
            missing = root / "missing"
            for targets in [(missing,), (source, missing)]:
                with self.subTest(targets=targets):
                    result = self.scan(root, *targets)
                    self.assertEqual(result.returncode, 2)
                    self.assertIn(str(missing), result.stderr)
                    self.assertNotIn("no strong hits", result.stdout)

    def test_scan_does_not_treat_pattern_metadata_as_targets(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            requested = root / "App.tsx"
            requested.write_text('<h1 className="text-neutral-900">Tasks</h1>\n')
            unrelated = root / "strong"
            unrelated.mkdir()
            (unrelated / "Other.tsx").write_text(
                '<h1 className="bg-clip-text">Other</h1>\n'
            )
            result = self.scan(root, requested)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(result.stderr, "")
            self.assertNotIn("Other.tsx", result.stdout)

    def test_weak_and_strong_hits_keep_their_status_contract(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "App.tsx"
            cases = [
                ('<div className="rounded-2xl">Tasks</div>\n', 0, "V6"),
                ('<h1 className="bg-clip-text">Tasks</h1>\n', 1, "V2"),
                ('<h1>Tasks ✅</h1>\n', 1, "V8"),
            ]
            for content, status, group in cases:
                with self.subTest(group=group):
                    source.write_text(content)
                    result = self.scan(root, source)
                    self.assertEqual(result.returncode, status)
                    self.assertIn(group, result.stdout)
                    self.assertIn("App.tsx:1:", result.stdout)
                    self.assertEqual(result.stderr, "")

    def test_pipe_filename_does_not_execute_command(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            hostile = root / "|touch pwned #.tsx"
            hostile.write_text("<h1>Safe ✅</h1>\n", encoding="utf-8")
            result = self.scan(root, hostile.name)
            self.assertFalse((root / "pwned").exists(), "scanner executed shell pipe in filename")
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("V8", result.stdout)
            self.assertEqual(result.stderr, "")

    def test_dash_prefixed_target_scans_safely(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            dashed = root / "-name.tsx"
            dashed.write_text('<h1 className="bg-clip-text">Title</h1>\n', encoding="utf-8")
            result = self.scan(root, dashed.name)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("V2", result.stdout)
            self.assertEqual(result.stderr, "")

    def test_css_and_scss_files_scan_for_v8_emoji(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in ("App.css", "App.scss"):
                with self.subTest(name=name):
                    target = root / name
                    target.write_text("/* ✅ */\n", encoding="utf-8")
                    result = self.scan(root, target)
                    self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                    self.assertIn("V8", result.stdout)
                    self.assertEqual(result.stderr, "")

    def test_new_weak_tells_detect_arrow_cta_italic_heading_and_layout_hazards(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "Hero.tsx"
            cases = [
                ('<a href="/docs">Learn more →</a>\n', "V15"),
                ('<a href="/docs">Learn More -></a>\n', "V15"),
                ('<a href="/docs">GET STARTED →</a>\n', "V15"),
                ('<h1>Design <em>faster</em> today</h1>\n', "V16"),
                ('<div className="transition-all w-[100vw]">Box</div>\n', "V17"),
                ('<section className="w-screen">Wide</section>\n', "V17"),
            ]
            for content, group in cases:
                with self.subTest(group=group):
                    source.write_text(content, encoding="utf-8")
                    result = self.scan(root, source)
                    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                    self.assertIn(group, result.stdout)
                    self.assertEqual(result.stderr, "")


if __name__ == "__main__":
    unittest.main()
