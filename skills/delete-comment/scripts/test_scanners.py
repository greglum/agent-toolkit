"""Unit tests for scanners.py."""

from __future__ import annotations

import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import comment_audit
import scanners


class ScannerTests(unittest.TestCase):
    def test_python_exempts_docstrings_shebang_directives_and_strings(self) -> None:
        source = (
            "#!/usr/bin/env python3\n"
            '"""Module docstring.\n\n# Not a comment.\n"""\n'
            "import os  # noqa: F401\n"
            'URL = "https://example.com/#frag"\n'
            "def add(a: int, b: int) -> int:\n"
            '    """Add two ints."""\n'
            "    # standalone note\n"
            "    return a + b  # inline note\n"
        )
        hits = scanners.scan_python("app.py", source)
        active = [h for h in hits if not h.exempted]
        exempted = [h for h in hits if h.exempted]
        self.assertEqual(len(exempted), 2)
        self.assertEqual(len(active), 2)
        self.assertFalse(active[0].inline)
        self.assertEqual(active[0].standalone_lines, 1)
        self.assertEqual(active[0].text, "# standalone note")
        self.assertTrue(active[1].inline)
        self.assertEqual(active[1].standalone_lines, 0)
        self.assertEqual(active[1].text, "# inline note")

    def test_js_ts_handles_strings_templates_regex_blocks_and_directives(self) -> None:
        source = (
            "// eslint-disable-next-line no-console\n"
            "/* c8 ignore next */\n"
            "// @ts-expect-error legacy\n"
            'const s = "// not a comment /* nope */";\n'
            "const re = /https?:\\/\\//g; // inline regex note\n"
            "const tpl = `hello ${x /* inside interp */} world // literal`;\n"
            "/*\n"
            " * multi-line block\n"
            " */\n"
            "const y = 1;\n"
        )
        hits = scanners.scan_c_like("app.ts", source, "js")
        active = [h for h in hits if not h.exempted]
        exempted = [h for h in hits if h.exempted]
        self.assertEqual(len(exempted), 3)
        self.assertEqual(len(active), 3)
        self.assertEqual(active[0].text, "// inline regex note")
        self.assertTrue(active[0].inline)
        self.assertEqual(active[1].text, "/* inside interp */")
        self.assertTrue(active[1].inline)
        self.assertEqual(active[2].kind, "block")
        self.assertFalse(active[2].inline)
        self.assertEqual(active[2].standalone_lines, 3)

    def test_js_postfix_inc_jsx_and_node_shebang(self) -> None:
        postfix = "let y = x++ / 2; // after postfix\nlet z = y-- / 3; /* block */\n"
        hits = [h for h in scanners.scan_c_like("calc.js", postfix, "js") if not h.exempted]
        self.assertEqual([h.text for h in hits], ["// after postfix", "/* block */"])

        jsx_apos = "const el = <div>It's fine</div> // jsx comment\n"
        hits = [h for h in scanners.scan_c_like("view.tsx", jsx_apos, "js") if not h.exempted]
        self.assertEqual([h.text for h in hits], ["// jsx comment"])

        jsx_frag = "const frag = <><span>a</span> /* c */ <span>b</span></>\n"
        hits = [h for h in scanners.scan_c_like("frag.jsx", jsx_frag, "js") if not h.exempted]
        self.assertEqual([h.text for h in hits], ["/* c */"])

        self.assertEqual(scanners.detect_language(Path("cli"), "#!/usr/bin/env node"), "js")

    def test_shell_exempts_quotes_and_parameter_expansions(self) -> None:
        source = (
            "#!/bin/sh\n"
            "# shellcheck disable=SC2086\n"
            "echo '# not a comment'\n"
            'echo "still # not a comment"\n'
            "count=${#items[@]}\n"
            "prefix=foo#bar\n"
            "# real shell comment\n"
            "echo ok # trailing\n"
        )
        hits = scanners.scan_shell("run.sh", source)
        active = [h for h in hits if not h.exempted]
        exempted = [h for h in hits if h.exempted]
        self.assertEqual(len(exempted), 2)
        self.assertEqual([h.text for h in active], ["# real shell comment", "# trailing"])
        self.assertEqual([h.inline for h in active], [False, True])

    def test_shell_heredoc_single_double_escaped_and_bare_delimiters(self) -> None:
        source = (
            "#!/bin/sh\n"
            "cat <<'EOF'\n"
            "# literal inside single-quoted heredoc\n"
            "value=1 # also literal\n"
            "EOF\n"
            'cat <<"END"\n'
            "# literal inside double-quoted heredoc\n"
            "END\n"
            "cat <<\\ESC\n"
            "# literal inside backslash-escaped heredoc\n"
            "ESC\n"
            "cat <<PLAIN\n"
            "# literal inside unquoted heredoc\n"
            "PLAIN\n"
            "# real comment after heredocs\n"
        )
        hits = scanners.scan_shell("heredocs.sh", source)
        active = [h for h in hits if not h.exempted]
        self.assertEqual([h.text for h in active], ["# real comment after heredocs"])
        self.assertEqual([h.line for h in active], [15])
        self.assertEqual([h.inline for h in active], [False])

    def test_shell_heredoc_dash_strips_only_leading_tabs(self) -> None:
        source = (
            "cat <<-EOF\n"
            "\t# literal inside tabbed heredoc\n"
            "  EOF\n"
            "\t# spaces did not close heredoc\n"
            "\t\tEOF\n"
            "# real comment after tabbed close\n"
        )
        hits = scanners.scan_shell("tabbed.sh", source)
        active = [h for h in hits if not h.exempted]
        self.assertEqual([h.text for h in active], ["# real comment after tabbed close"])
        self.assertEqual([h.line for h in active], [6])

    def test_shell_heredoc_opener_comment_and_false_shift_contexts(self) -> None:
        source = (
            "cat <<EOF | sed 's/a/b/' # opener inline comment\n"
            "# body line\n"
            "EOF\n"
            'echo "<<FAKE"\n'
            "# real comment after quoted shift\n"
            "echo '<<FAKE'\n"
            "# real comment after single-quoted shift\n"
            "val=${x:-<<FAKE}\n"
            "# real comment after parameter expansion\n"
            "cat <<< word # here-string inline comment\n"
            "# real comment after here-string\n"
        )
        hits = scanners.scan_shell("edge.sh", source)
        active = [h for h in hits if not h.exempted]
        self.assertEqual(
            [(h.line, h.inline, h.text) for h in active],
            [
                (1, True, "# opener inline comment"),
                (5, False, "# real comment after quoted shift"),
                (7, False, "# real comment after single-quoted shift"),
                (9, False, "# real comment after parameter expansion"),
                (10, True, "# here-string inline comment"),
                (11, False, "# real comment after here-string"),
            ],
        )

    def test_shell_nested_arith_brace_and_multi_heredoc(self) -> None:
        cases = [
            ("arith_simple.sh", "x=$(( 1 << 2 ))\n# real comment\n"),
            ("arith_paren.sh", "x=$(( (1 << 2) + 3 ))\n# real comment\n"),
            ("arith_double_paren.sh", "x=$(( ((1 << 2)) ))\n# real comment\n"),
            ("param_nested_brace.sh", "val=${x:-{<<FAKE}}\n# real comment\n"),
            ("cmd_nested_arith.sh", "val=$(echo $(( (1 << 2) )))\n# real comment\n"),
        ]
        for name, source in cases:
            with self.subTest(case=name):
                active = [h for h in scanners.scan_shell(name, source) if not h.exempted]
                self.assertEqual([(h.line, h.inline, h.text) for h in active], [(2, False, "# real comment")])

        multi = "cmd <<EOF1 <<EOF2\n# in 1\nEOF1\n# in 2\nEOF2\n# after\n"
        multi_active = [h for h in scanners.scan_shell("multi.sh", multi) if not h.exempted]
        self.assertEqual([(h.line, h.inline, h.text) for h in multi_active], [(6, False, "# after")])

    def test_shell_heredoc_comment_audit_integration(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            script = root / "deploy.sh"
            ratchet = root / "ratchet.json"
            ratchet.write_text('{"files": {}}\n', encoding="utf-8")
            script.write_text(
                "#!/bin/sh\n"
                "cat <<'EOF'\n"
                "# generated config header\n"
                "key=value\n"
                "EOF\n",
                encoding="utf-8",
            )
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                est_code = comment_audit.main(["estimate", str(root), "--json"])
            self.assertEqual(est_code, 0, err.getvalue())
            self.assertEqual(json.loads(out.getvalue())["comments"], 0)

            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                chk_code = comment_audit.main(["check", "--ratchet", str(ratchet), str(root)])
            self.assertEqual(chk_code, 0, err.getvalue())
            self.assertIn("Ratchet check passed.", out.getvalue())

    def test_go_rust_and_cpp_digit_separators(self) -> None:
        go_src = (
            "//go:build linux\n"
            "package main\n"
            "const raw = `// not a comment\n/* also literal */`\n"
            "// real go comment\n"
        )
        go_hits = [h for h in scanners.scan_c_like("main.go", go_src, "go") if not h.exempted]
        self.assertEqual([h.text for h in go_hits], ["// real go comment"])

        rust_src = (
            "fn borrow<'a>(s: &'a str) -> &'a str {\n"
            "    let slash = '/';\n"
            '    let raw = r#"// not a comment"#;\n'
            "    /* outer /* nested */ end */\n"
            "    // real rust comment\n"
            "    s\n"
            "}\n"
        )
        rust_hits = [h for h in scanners.scan_c_like("lib.rs", rust_src, "rust") if not h.exempted]
        self.assertEqual(len(rust_hits), 2)
        self.assertEqual(rust_hits[0].text, "/* outer /* nested */ end */")
        self.assertEqual(rust_hits[1].text, "// real rust comment")

        cpp_src = "int n = 1'000'000; // cpp digit sep\nint h = 0xFF'FF; // hex sep\n"
        cpp_hits = [h for h in scanners.scan_c_like("main.cpp", cpp_src, "c") if not h.exempted]
        self.assertEqual([h.text for h in cpp_hits], ["// cpp digit sep", "// hex sep"])


if __name__ == "__main__":
    unittest.main()
