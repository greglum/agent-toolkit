"""Regression checks for the scanner's target scope and CLI status contract."""

import subprocess
import tempfile
import unittest
from pathlib import Path


SCANNER = Path(__file__).with_name("ui-tells.sh")


class ScannerContractTests(unittest.TestCase):
    def scan(self, root, *targets):
        return subprocess.run(
            ["bash", str(SCANNER), *map(str, targets)],
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
        )

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


if __name__ == "__main__":
    unittest.main()
