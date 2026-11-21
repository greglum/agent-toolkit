"""Unit tests for comment_audit.py."""

from __future__ import annotations

import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import comment_audit
import scanners


class CliAndRatchetTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def _run_cli(self, argv: list[str]) -> tuple[int, str, str]:
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = comment_audit.main(argv)
        return code, out.getvalue(), err.getvalue()

    def test_estimate_and_inventory_json(self) -> None:
        (self.root / "a.py").write_text(
            "#!/usr/bin/env python3\n# line one\n# line two\nx = 1  # inline\n# noqa\n",
            encoding="utf-8",
        )
        code, out, _ = self._run_cli(["estimate", str(self.root), "--json"])
        self.assertEqual(code, 0)
        data = json.loads(out)
        self.assertEqual(data["files_scanned"], 1)
        self.assertEqual(data["comments"], 3)
        self.assertEqual(data["comment_blocks"], 2)
        self.assertEqual(data["standalone_lines_shed"], 2)
        self.assertEqual(data["inline_comments"], 1)
        self.assertEqual(data["exempted_directives"], 2)

        code, inv_out, _ = self._run_cli(
            ["inventory", str(self.root), "--format", "json", "--context", "1"]
        )
        self.assertEqual(code, 0)
        items = json.loads(inv_out)
        self.assertEqual(len(items), 3)
        self.assertEqual(items[0]["text"], "# line one")
        self.assertIn("after", items[0]["context"])

    def test_ratchet_check_fail_pass_and_tighten(self) -> None:
        target = self.root / "mod.py"
        ratchet = self.root / "ratchet.json"
        target.write_text("# first\nx = 1\n", encoding="utf-8")

        code, _, _ = self._run_cli(
            ["update-ratchet", "--ratchet", str(ratchet), str(self.root)]
        )
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(ratchet.read_text())["files"], {"mod.py": 1})

        code, out, _ = self._run_cli(["check", "--ratchet", str(ratchet), str(self.root)])
        self.assertEqual(code, 0)
        self.assertIn("Ratchet check passed.", out)

        target.write_text("# first\n# second\nx = 1\n", encoding="utf-8")
        code, out, _ = self._run_cli(["check", "--ratchet", str(ratchet), str(self.root)])
        self.assertEqual(code, 1)
        self.assertIn("ceiling 1", out)

        code, _, err = self._run_cli(
            ["update-ratchet", "--ratchet", str(ratchet), str(self.root)]
        )
        self.assertEqual(code, 1)
        self.assertIn("exceeds existing ceiling", err)

        target.write_text("x = 1\n", encoding="utf-8")
        code, out, _ = self._run_cli(["check", "--ratchet", str(ratchet), str(self.root)])
        self.assertEqual(code, 0)
        self.assertIn("below ceiling", out)

        code, _, _ = self._run_cli(
            ["update-ratchet", "--ratchet", str(ratchet), str(self.root)]
        )
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(ratchet.read_text())["files"], {})

        target.write_text("# sneaks past empty ratchet\nx = 1\n", encoding="utf-8")
        code, _, err = self._run_cli(
            ["update-ratchet", "--ratchet", str(ratchet), str(self.root)]
        )
        self.assertEqual(code, 1)
        self.assertIn("exceeds existing ceiling 0", err)

    def test_python_syntax_token_and_indentation_errors_fail_nonzero(self) -> None:
        bad_cases = {
            "token_err.py": "x = (\n# comment before eof\n",
            "indent_err.py": "def f():\n    x = 1\n  y = 2\n",
            "syntax_err.py": "def :\n# comment\n",
        }
        for name, content in bad_cases.items():
            case_dir = self.root / name.replace(".py", "")
            case_dir.mkdir()
            bad_file = case_dir / name
            bad_file.write_text(content, encoding="utf-8")
            with self.subTest(case=name):
                with self.assertRaises(scanners.ScanError):
                    scanners.scan_python(name, content)
                for cmd in (
                    ["estimate", str(bad_file)],
                    ["inventory", str(bad_file)],
                    ["update-ratchet", "--ratchet", str(case_dir / "ratchet.json"), "--init", str(bad_file)],
                ):
                    code, _, err = self._run_cli(cmd)
                    self.assertEqual(code, 1)
                    self.assertTrue(err.strip())

    def test_unreadable_file_oserror_fails_nonzero(self) -> None:
        target = self.root / "secret.py"
        target.write_text("x = 1\n", encoding="utf-8")
        ratchet = self.root / "ratchet.json"
        ratchet.write_text('{"files": {}}\n', encoding="utf-8")

        real_open = Path.open

        target_resolved = target.resolve()

        def failing_open(path_obj: Path, *args, **kwargs):
            if path_obj.resolve() == target_resolved:
                raise PermissionError("permission denied")
            return real_open(path_obj, *args, **kwargs)

        with mock.patch.object(Path, "open", autospec=True, side_effect=failing_open):
            for cmd in (
                ["estimate", str(self.root)],
                ["check", "--ratchet", str(ratchet), str(self.root)],
            ):
                code, out, err = self._run_cli(cmd)
                self.assertEqual(code, 1)
                self.assertIn("permission denied", err)
                self.assertNotIn("Ratchet check passed", out)

        with mock.patch.object(Path, "read_bytes", autospec=True, side_effect=PermissionError("read denied")):
            with self.assertRaises(scanners.ScanError):
                scanners.scan_file(target, "secret.py")

    def test_nonexistent_target_path_fails_nonzero(self) -> None:
        ratchet = self.root / "ratchet.json"
        ratchet.write_text('{"files": {}}\n', encoding="utf-8")
        missing = str(self.root / "does_not_exist.py")
        for cmd in (
            ["estimate", missing],
            ["inventory", missing],
            ["check", "--ratchet", str(ratchet), missing],
            ["update-ratchet", "--ratchet", str(ratchet), missing],
        ):
            with self.subTest(cmd=cmd[0]):
                code, out, err = self._run_cli(cmd)
                self.assertEqual(code, 1)
                self.assertIn("not found", err.lower())
                self.assertNotIn("Ratchet check passed", out)

    def test_corrupt_ratchet_json_and_bad_schema_fail_cleanly(self) -> None:
        target = self.root / "mod.py"
        target.write_text("x = 1\n", encoding="utf-8")
        ratchet = self.root / "ratchet.json"
        bad_payloads = [
            "{not valid json",
            "[]",
            "{}",
            '{"files": []}',
            '{"files": {"mod.py": -1}}',
            '{"files": {"mod.py": true}}',
            '{"files": {"mod.py": "2"}}',
            '{"files": {"mod.py": 1.5}}',
        ]
        for payload in bad_payloads:
            ratchet.write_text(payload, encoding="utf-8")
            with self.subTest(payload=payload):
                for cmd in (
                    ["check", "--ratchet", str(ratchet), str(self.root)],
                    ["update-ratchet", "--ratchet", str(ratchet), str(self.root)],
                ):
                    code, _, err = self._run_cli(cmd)
                    self.assertEqual(code, 1)
                    self.assertTrue(err.strip())

    def test_inventory_include_exempted_surfaces_directives(self) -> None:
        target = self.root / "dir.py"
        target.write_text(
            "#!/usr/bin/env python3\n"
            "import os  # noqa: F401  # trailing excuse\n"
            "x = 1  # ordinary\n",
            encoding="utf-8",
        )
        code, default_out, _ = self._run_cli(
            ["inventory", str(self.root), "--format", "json", "--context", "0"]
        )
        self.assertEqual(code, 0)
        default_items = json.loads(default_out)
        self.assertEqual([item["text"] for item in default_items], ["# ordinary"])

        code, all_out, _ = self._run_cli(
            ["inventory", str(self.root), "--format", "json", "--context", "0", "--include-exempted"]
        )
        self.assertEqual(code, 0)
        all_items = json.loads(all_out)
        self.assertEqual(len(all_items), 3)
        self.assertTrue(all_items[0]["exempted"])
        self.assertTrue(all_items[1]["exempted"])
        self.assertIn("trailing excuse", all_items[1]["text"])
        self.assertFalse(all_items[2]["exempted"])

        code, text_out, _ = self._run_cli(
            ["inventory", str(self.root), "--format", "text", "--context", "0", "--include-exempted"]
        )
        self.assertEqual(code, 0)
        self.assertIn("trailing excuse", text_out)
        self.assertIn("exempted", text_out)

    def test_exclude_and_update_ratchet_init_vs_tighten(self) -> None:
        keep = self.root / "keep.py"
        vendor = self.root / "vendor"
        vendor.mkdir()
        skip = vendor / "skip.py"
        ratchet = self.root / "ratchet.json"

        keep.write_text("# c1\nx = 1\n", encoding="utf-8")
        skip.write_text("# v1\n# v2\ny = 2\n", encoding="utf-8")

        code, est_out, _ = self._run_cli(
            ["estimate", str(self.root), "--exclude", "vendor/*", "--json"]
        )
        self.assertEqual(code, 0)
        est = json.loads(est_out)
        self.assertEqual(est["files_scanned"], 1)
        self.assertEqual(est["comments"], 1)

        code, inv_out, _ = self._run_cli(
            ["inventory", str(self.root), "--exclude", "vendor/*", "--format", "json"]
        )
        self.assertEqual(code, 0)
        self.assertEqual([item["file"] for item in json.loads(inv_out)], ["keep.py"])

        code, _, _ = self._run_cli(
            ["update-ratchet", "--ratchet", str(ratchet), "--init", str(self.root)]
        )
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(ratchet.read_text())["files"], {"keep.py": 1, "vendor/skip.py": 2})

        keep.write_text("# c1\n# c2\nx = 1\n", encoding="utf-8")
        code, _, err = self._run_cli(
            ["update-ratchet", "--ratchet", str(ratchet), str(self.root)]
        )
        self.assertEqual(code, 1)
        self.assertIn("exceeds existing ceiling 1", err)

        code, out, _ = self._run_cli(
            ["check", "--ratchet", str(ratchet), "--exclude", "vendor/*", str(self.root)]
        )
        self.assertEqual(code, 1)
        self.assertIn("keep.py", out)

        code, out, _ = self._run_cli(
            ["check", "--ratchet", str(ratchet), "--exclude", "vendor/*", "--exclude", "keep.py", str(self.root)]
        )
        self.assertEqual(code, 0)
        self.assertIn("Ratchet check passed.", out)

        code, _, _ = self._run_cli(
            ["update-ratchet", "--ratchet", str(ratchet), "--init", str(self.root)]
        )
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(ratchet.read_text())["files"], {"keep.py": 2, "vendor/skip.py": 2})

        keep.write_text("x = 1\n", encoding="utf-8")
        code, _, _ = self._run_cli(
            ["update-ratchet", "--ratchet", str(ratchet), "--exclude", "vendor/*", str(self.root)]
        )
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(ratchet.read_text())["files"], {"vendor/skip.py": 2})

    def test_skill_scripts_have_zero_non_directive_comments(self) -> None:
        scripts_dir = Path(__file__).resolve().parent
        for py_file in sorted(scripts_dir.glob("*.py")):
            hits = scanners.scan_file(py_file, py_file.name)
            active = [h for h in hits if not h.exempted]
            self.assertEqual(
                active,
                [],
                f"{py_file.name} must have zero non-directive comments, found {active}",
            )


if __name__ == "__main__":
    unittest.main()
