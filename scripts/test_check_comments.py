"""Regression tests for scripts/check_comments.py."""

from contextlib import redirect_stderr, redirect_stdout
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

import check_comments
import comment_scanners


def run_cli(argv: list[str]) -> tuple[int, str, str]:
    stdout = io.StringIO()
    stderr = io.StringIO()
    with redirect_stdout(stdout), redirect_stderr(stderr):
        code = check_comments.main(argv)
    return code, stdout.getvalue(), stderr.getvalue()


class ScannerTests(unittest.TestCase):
    def test_python_docstrings_and_strings_exempted(self):
        source = (
            '#!/usr/bin/env python3\n'
            '"""Module docstring # not a comment."""\n'
            "\n"
            "class Example:\n"
            '    """Class docstring."""\n'
            "\n"
            "    def method(self):\n"
            '        """Method docstring."""\n'
            '        text = "# not a comment"\n'
            '        formatted = f"value {1} # also not a comment"\n'
            "        x = 1  # inline comment\n"
            "        # standalone comment\n"
            "        return text + formatted + str(x)\n"
        )
        findings = comment_scanners.scan_python(source)
        non_exempt = [f for f in findings if not f.exempt]
        exempt = [f for f in findings if f.exempt]
        self.assertEqual([(f.line, f.text, f.is_inline, f.standalone_lines) for f in non_exempt], [
            (11, "# inline comment", True, 0),
            (12, "# standalone comment", False, 1),
        ])
        self.assertEqual([(f.line, f.text) for f in exempt], [
            (1, "#!/usr/bin/env python3"),
        ])

    def test_shebangs_only_exempt_on_line_one(self):
        py_src = "#!/usr/bin/env python3\n#!/not/a/shebang\n"
        py_findings = comment_scanners.scan_python(py_src)
        self.assertEqual([f.exempt for f in py_findings], [True, False])

        sh_src = "#!/bin/sh\n#!/not/a/shebang\n"
        sh_findings = comment_scanners.scan_shell(sh_src)
        self.assertEqual([f.exempt for f in sh_findings], [True, False])

    def test_tool_directives_exempted(self):
        py_directives = [
            "# noqa",
            "# noqa: E501",
            "# type: ignore[arg-type]",
            "# pragma: no cover",
            "# ruff: noqa: F401",
            "# pylint: disable=missing-docstring",
            "# mypy: ignore-errors",
            "# pyright: reportMissingImports=false",
            "# fmt: off",
            "# isort: skip",
            "# -*- coding: utf-8 -*-",
            "# coding: utf-8",
        ]
        py_src = "\n".join(f"x = 1  {d}" for d in py_directives) + "\n# real comment\n"
        py_findings = comment_scanners.scan_python(py_src)
        self.assertEqual([f.text for f in py_findings if not f.exempt], ["# real comment"])
        self.assertEqual(len([f for f in py_findings if f.exempt]), len(py_directives))

        sh_src = "#!/bin/sh\n# shellcheck disable=SC2086\n# real shell comment\necho ok\n"
        sh_findings = comment_scanners.scan_shell(sh_src)
        self.assertEqual([f.text for f in sh_findings if not f.exempt], ["# real shell comment"])
        self.assertEqual([f.text for f in sh_findings if f.exempt], ["#!/bin/sh", "# shellcheck disable=SC2086"])

        js_directives = [
            "// eslint-disable-next-line no-console",
            "// @ts-expect-error",
            "// @ts-ignore",
            "// prettier-ignore",
            "// biome-ignore lint/suspicious: ok",
            "/* eslint-disable no-unused-vars */",
            "/* istanbul ignore next */",
            "/* c8 ignore start */",
            "/* v8 ignore next 2 */",
        ]
        js_src = "\n".join(js_directives) + "\n// real js comment\n"
        js_findings = comment_scanners.scan_js(js_src)
        self.assertEqual([f.text for f in js_findings if not f.exempt], ["// real js comment"])
        self.assertEqual(len([f for f in js_findings if f.exempt]), len(js_directives))

    def test_shell_strings_and_parameter_expansions_not_flagged(self):
        source = (
            "#!/bin/sh\n"
            "a='# not a comment'\n"
            'b="# not a comment"\n'
            "c=$'# not a comment'\n"
            "d=foo#bar\n"
            "e=\\#escaped\n"
            "if [ $# -eq 0 ] || [ ${#a} -gt 0 ]; then\n"
            '  echo "${b#prefix}"\n'
            "fi\n"
            "echo ok # trailing shell comment\n"
            "# standalone shell comment\n"
        )
        findings = [f for f in comment_scanners.scan_shell(source) if not f.exempt]
        self.assertEqual([(f.line, f.text, f.is_inline) for f in findings], [
            (10, "# trailing shell comment", True),
            (11, "# standalone shell comment", False),
        ])

    def test_js_ts_strings_templates_and_regexes_not_flagged(self):
        source = (
            "const s1 = '// not a comment';\n"
            'const s2 = "/* not a comment */";\n'
            "const tpl = `head // not a comment\n"
            "  ${value /* template expr comment */} tail /* not comment */`;\n"
            "const re1 = /^https?:\\/\\//;\n"
            "const re2 = /(?:^|[/\\\\])Chrome/;\n"
            "const div = (10 / 2) / 5;\n"
            "const ok = 1; // inline js comment\n"
            "// standalone js comment\n"
            "/*\n"
            " * multi-line block\n"
            " */\n"
        )
        findings = [f for f in comment_scanners.scan_js(source) if not f.exempt]
        self.assertEqual(
            [(f.line, f.end_line, f.is_inline, f.standalone_lines) for f in findings],
            [
                (4, 4, True, 0),
                (8, 8, True, 0),
                (9, 9, False, 1),
                (10, 12, False, 3),
            ],
        )


class RatchetCliTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "scripts").mkdir()
        (self.root / ".githooks").mkdir()

    def write(self, rel: str, content: str) -> None:
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def test_ratchet_check_pass_fail_and_tighten(self):
        self.write("app.py", "x = 1  # baseline\n")
        self.write("mod.ts", "export const y: number = 1;\n")
        self.write(".githooks/pre-commit", "#!/bin/sh\n# hook comment\necho ok\n")

        code, out, err = run_cli(["--root", str(self.root), "--update-ratchet"])
        self.assertEqual(code, 0, out + err)
        ratchet = json.loads((self.root / "scripts/comment-ratchet.json").read_text())
        self.assertEqual(ratchet, {"files": {".githooks/pre-commit": 1, "app.py": 1}})

        code, out, _ = run_cli(["--root", str(self.root)])
        self.assertEqual(code, 0, out)

        self.write("mod.ts", "// new ts comment\nexport const y: number = 1;\n")
        code, out, _ = run_cli(["--root", str(self.root)])
        self.assertEqual(code, 1)
        self.assertIn("mod.ts:1: // new ts comment", out)

        self.write("mod.ts", "export const y: number = 1;\n")
        self.write("app.py", "x = 1\n")
        code, out, _ = run_cli(["--root", str(self.root)])
        self.assertEqual(code, 0)
        self.assertIn("--update-ratchet", out)

        code, out, _ = run_cli(["--root", str(self.root), "--strict-ratchet"])
        self.assertEqual(code, 1)
        self.assertIn("Strict ratchet check failed", out)

        code, out, err = run_cli(["--root", str(self.root), "--update-ratchet"])
        self.assertEqual(code, 0, out + err)
        ratchet = json.loads((self.root / "scripts/comment-ratchet.json").read_text())
        self.assertEqual(ratchet, {"files": {".githooks/pre-commit": 1}})

    def test_update_ratchet_refuses_increase_without_flag(self):
        self.write("a.mjs", "// one\nexport const a = 1;\n")
        code, _, _ = run_cli(["--root", str(self.root), "--update-ratchet"])
        self.assertEqual(code, 0)

        self.write("a.mjs", "// one\n// two\nexport const a = 1;\n")
        code, _, err = run_cli(["--root", str(self.root), "--update-ratchet"])
        self.assertEqual(code, 1)
        self.assertIn("--allow-increase", err)
        ratchet = json.loads((self.root / "scripts/comment-ratchet.json").read_text())
        self.assertEqual(ratchet, {"files": {"a.mjs": 1}})

        code, _, err = run_cli(["--root", str(self.root), "--update-ratchet", "--allow-increase"])
        self.assertEqual(code, 0, err)
        ratchet = json.loads((self.root / "scripts/comment-ratchet.json").read_text())
        self.assertEqual(ratchet, {"files": {"a.mjs": 2}})

    def test_estimate_output(self):
        self.write(
            "sample.py",
            "#!/usr/bin/env python3\n"
            "# noqa\n"
            "# standalone one\n"
            "x = 1  # inline one\n",
        )
        self.write(
            "sample.cjs",
            "/* standalone\n"
            "   block */\n"
            "const a = 1; // inline two\n"
            "// eslint-disable-next-line\n",
        )
        code, out, err = run_cli(["--root", str(self.root), "--estimate"])
        self.assertEqual(code, 0, err)
        self.assertIn("Total non-directive comments: 4", out)
        self.assertIn("Standalone comment lines that will be shed: 3", out)
        self.assertIn("Inline comments: 2", out)
        self.assertIn("Exempted directives and shebangs: 3", out)

    def test_untracked_files_scanned_in_git_and_hidden_dirs_skipped_without_git(self):
        self.write(".venv/ignored.py", "# should be ignored\n")
        self.write(".githooks/pre-commit", "#!/bin/sh\necho ok\n")
        self.assertEqual(check_comments.discover_code_files(self.root), [".githooks/pre-commit"])

        subprocess.run(["git", "-C", str(self.root), "init", "-q"], check=True)
        self.write(".gitignore", ".venv/\n")
        self.write("tracked.py", "x = 1\n")
        subprocess.run(["git", "-C", str(self.root), "add", ".gitignore", "tracked.py"], check=True)
        code, _, err = run_cli(["--root", str(self.root), "--update-ratchet"])
        self.assertEqual(code, 0, err)

        self.write("untracked_new.py", "y = 2  # untracked comment\n")
        code, out, _ = run_cli(["--root", str(self.root)])
        self.assertEqual(code, 1)
        self.assertIn("untracked_new.py:1: # untracked comment", out)

    def test_comment_checker_files_have_zero_non_directive_comments(self):
        scripts_dir = Path(__file__).resolve().parent
        for name in ("comment_scanners.py", "check_comments.py", "test_check_comments.py"):
            findings = comment_scanners.scan_python((scripts_dir / name).read_text(encoding="utf-8"))
            non_exempt = [f for f in findings if not f.exempt]
            self.assertEqual(non_exempt, [], f"{name} must have zero non-directive comments")


if __name__ == "__main__":
    unittest.main()
