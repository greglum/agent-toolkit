"""Unit and planted-defect regression tests for YAML, TOML, SQL, and HCL scanners."""

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
import structured_scanners


class StructuredScannerTests(unittest.TestCase):
    def test_yaml_comments_directives_urls_quotes_apostrophes_and_blocks(self) -> None:
        source = (
            "# standalone yaml comment\n"
            "name: demo # inline yaml comment\n"
            "rule: ok # yamllint disable-line rule:line-length\n"
            "url: https://example.com/#frag\n"
            "tag: foo#bar\n"
            "single: 'not # comment ''escaped'''\n"
            'double: "not # comment \\"escaped\\""\n'
            "note: Don't panic # real after apostrophe\n"
            'multi: "line one\n'
            "  # literal inside multiline double quote\n"
            '  line three" # after multiline quote\n'
            "script: | # header inline comment\n"
            "  # bash comment inside block scalar\n"
            "  echo ok\n"
            "after_block: 1 # comment after block dedent\n"
            "steps:\n"
            "  - run: |2\n"
            "      # explicit indent block scalar\n"
            "    if: always() # comment after list mapping block\n"
            "  - >-\n"
            "    # folded sequence block\n"
            "    hello\n"
            "  - next # comment after sequence block\n"
        )
        hits = scanners.scan_yaml("ci.yaml", source)
        active = [h for h in hits if not h.exempted]
        exempted = [h for h in hits if h.exempted]
        self.assertEqual([h.text for h in exempted], ["# yamllint disable-line rule:line-length"])
        self.assertEqual(
            [(h.line, h.inline, h.text) for h in active],
            [
                (1, False, "# standalone yaml comment"),
                (2, True, "# inline yaml comment"),
                (8, True, "# real after apostrophe"),
                (11, True, "# after multiline quote"),
                (12, True, "# header inline comment"),
                (15, True, "# comment after block dedent"),
                (19, True, "# comment after list mapping block"),
                (23, True, "# comment after sequence block"),
            ],
        )

    def test_yaml_empty_block_and_single_quote_multiline(self) -> None:
        source = (
            "empty_block: |\n"
            "# real comment immediately after empty block\n"
            "msg: 'line 1\n"
            "  # not comment inside multiline single quote\n"
            "  line 2' # real after single quote\n"
            "title: The '90s # real after space apostrophe\n"
            'quote_word: Use "foo # real after mid-scalar quote\n'
            "dash_word: Foo - '90s # real after mid-scalar dash apostrophe\n"
            "next: 1 # still scanned after plain scalar quotes\n"
        )
        active = [h for h in structured_scanners.scan_yaml("edge.yml", source) if not h.exempted]
        self.assertEqual(
            [(h.line, h.inline, h.text) for h in active],
            [
                (2, False, "# real comment immediately after empty block"),
                (5, True, "# real after single quote"),
                (6, True, "# real after space apostrophe"),
                (7, True, "# real after mid-scalar quote"),
                (8, True, "# real after mid-scalar dash apostrophe"),
                (9, True, "# still scanned after plain scalar quotes"),
            ],
        )

    def test_yaml_document_root_block_scalar(self) -> None:
        source = (
            "--- |\n"
            "  # literal inside root block scalar\n"
            "  body\n"
            "...\n"
            "# real comment after document end\n"
        )
        active = [h for h in structured_scanners.scan_yaml("doc.yaml", source) if not h.exempted]
        self.assertEqual(
            [(h.line, h.inline, h.text) for h in active],
            [(5, False, "# real comment after document end")],
        )

    def test_yaml_indented_empty_nested_sequence_and_plain_continuations(self) -> None:
        source = (
            "empty_indented:\n"
            "  |\n"
            "next_after_empty: 1 # real after indented empty block\n"
            "nonempty_indented:\n"
            "  |\n"
            "  # inside indented block\n"
            "next_after_indented: 1 # real after indented block\n"
            "explicit_indented:\n"
            "  |2\n"
            "  # inside explicit indent block at col 2\n"
            "after_explicit: 1 # real after explicit indent block\n"
            "deep_header:\n"
            "    |\n"
            "  # inside block less indented than header\n"
            "after_deep_header: 1 # real after deep header block\n"
            "items:\n"
            "  - - run: |2\n"
            "        # inside nested sequence block\n"
            "      next: 1 # real after nested sequence block\n"
            '  - "my key": |2\n'
            "      # inside quoted-key sequence block\n"
            "    after_qkey: 1 # real after quoted-key block\n"
            "desc: Music from\n"
            "  '90s # real inside multiline plain scalar\n"
            "after_plain: 1 # real after multiline plain scalar\n"
            '"qkey": Music from\n'
            "  '90s # real inside quoted-key multiline plain\n"
            "wrapped_plain:\n"
            "  Music from the\n"
            "  '90s # real inside wrapped mapping plain\n"
            "wrapped_quoted:\n"
            "  'quoted # ok' # real after next-line quote\n"
            "list_plain:\n"
            "  - First line\n"
            "    '90s # real inside multiline list scalar\n"
            "  -\n"
            "    Wrapped list line\n"
            "    '90s # real inside wrapped list plain\n"
            "  - 'k': hello\n"
            "      '90s # real inside list quoted-key plain\n"
            "  - 'item # ok' # real after quoted list item\n"
            "obj: {\n"
            "  a: 1,\n"
            "    'key # not comment': 2 # real in flow map\n"
            "}\n"
            "---\n"
            "Root plain\n"
            "  '90s # real in root wrapped plain\n"
            "...\n"
            "'end_quoted # ok' # real after root doc\n"
            "note: Open [bracket in plain scalar\n"
            "script: |\n"
            "  # bash comment inside block after bracket\n"
            "after_bracket_block: 1 # real after bracket block\n"
            "brace_note: Open {brace in plain scalar\n"
            "desc_after_brace: Music from\n"
            "  '90s # real after brace plain\n"
            "after_brace_plain: 1 # real2 after brace plain\n"
        )
        active = [h for h in scanners.scan_yaml("complex.yaml", source) if not h.exempted]
        self.assertEqual(
            [(h.line, h.inline, h.text) for h in active],
            [
                (3, True, "# real after indented empty block"),
                (7, True, "# real after indented block"),
                (11, True, "# real after explicit indent block"),
                (15, True, "# real after deep header block"),
                (19, True, "# real after nested sequence block"),
                (22, True, "# real after quoted-key block"),
                (24, True, "# real inside multiline plain scalar"),
                (25, True, "# real after multiline plain scalar"),
                (27, True, "# real inside quoted-key multiline plain"),
                (30, True, "# real inside wrapped mapping plain"),
                (32, True, "# real after next-line quote"),
                (35, True, "# real inside multiline list scalar"),
                (38, True, "# real inside wrapped list plain"),
                (40, True, "# real inside list quoted-key plain"),
                (41, True, "# real after quoted list item"),
                (44, True, "# real in flow map"),
                (48, True, "# real in root wrapped plain"),
                (50, True, "# real after root doc"),
                (54, True, "# real after bracket block"),
                (57, True, "# real after brace plain"),
                (58, True, "# real2 after brace plain"),
            ],
        )

    def test_directive_matching_enforces_word_boundaries(self) -> None:
        for body in (
            "yamllint disable-line",
            "yamllint",
            "eslint-disable-next-line",
            "noqa: F401",
            "nolint:errcheck",
            "type: ignore[arg-type]",
            "checkov:skip=CKV_1",
        ):
            with self.subTest(exempt=body):
                self.assertTrue(scanners.is_directive(body))
        for body in ("yamllinting note", "shellchecking", "nosecure", "noqathing", "eslint_custom"):
            with self.subTest(non_exempt=body):
                self.assertFalse(scanners.is_directive(body))

    def test_toml_comments_and_all_string_forms(self) -> None:
        source = (
            "# top toml comment\n"
            'title = "val # not comment \\"#\\"" # inline toml\n'
            "lit = 'literal # not comment'\n"
            'multi_basic = """\n'
            "# inside multiline basic\n"
            'quote \\" # still inside\n'
            'end"""" # after 4-quote close\n'
            "multi_lit = '''\n"
            "# inside multiline literal\n"
            "''' # after multiline literal\n"
        )
        active = [h for h in scanners.scan_toml("pyproject.toml", source) if not h.exempted]
        self.assertEqual(
            [(h.line, h.inline, h.text) for h in active],
            [
                (1, False, "# top toml comment"),
                (2, True, "# inline toml"),
                (7, True, "# after 4-quote close"),
                (10, True, "# after multiline literal"),
            ],
        )

    def test_sql_comments_directives_identifiers_and_dollar_quotes(self) -> None:
        source = (
            "-- standalone sql comment\n"
            "-- noqa: LT01\n"
            "-- sqlfluff:disable=AL01\n"
            "SELECT 'it''s -- literal /* x */' AS s, -- inline sql\n"
            '  "col--name" AS c1, `col/*name*/` AS c2\n'
            "/* single-line block */\n"
            "/* multi-line\n"
            "   /* nested block */\n"
            "   end */\n"
            "CREATE FUNCTION f() RETURNS text AS $fn$\n"
            "BEGIN\n"
            "  -- inside dollar quote\n"
            "  /* also inside dollar quote */\n"
            "  RETURN '$$not nested';\n"
            "END;\n"
            "$fn$ LANGUAGE plpgsql; -- after function\n"
            "SELECT a$b$c, v$session$id, E'it\\'s -- not' FROM t; -- after dollar ident and E-string\n"
            "SELECT 'C:\\' AS win_path; -- after ansi backslash\n"
        )
        hits = scanners.scan_sql("query.sql", source)
        active = [h for h in hits if not h.exempted]
        exempted = [h for h in hits if h.exempted]
        self.assertEqual([h.text for h in exempted], ["-- noqa: LT01", "-- sqlfluff:disable=AL01"])
        self.assertEqual(
            [(h.line, h.kind, h.inline, h.standalone_lines, h.text) for h in active],
            [
                (1, "line", False, 1, "-- standalone sql comment"),
                (4, "line", True, 0, "-- inline sql"),
                (6, "block", False, 1, "/* single-line block */"),
                (7, "block", False, 3, "/* multi-line\n   /* nested block */\n   end */"),
                (16, "line", True, 0, "-- after function"),
                (17, "line", True, 0, "-- after dollar ident and E-string"),
                (18, "line", True, 0, "-- after ansi backslash"),
            ],
        )

    def test_hcl_comments_directives_interpolations_and_heredocs(self) -> None:
        source = (
            "# hash hcl comment\n"
            "// slash hcl comment\n"
            "# checkov:skip=CKV_AWS_1\n"
            "// tfsec:ignore:aws-s3-enable-bucket-logging\n"
            "# trivy:ignore:AVD-AWS-0089\n"
            "/* tflint-ignore: aws_instance_invalid_type */\n"
            'label = "x # // /* ${lookup(var.m, "k", "v")} # $${still}" # inline hcl\n'
            "user_data = <<EOF\n"
            "# literal inside plain heredoc\n"
            "  EOF\n"
            "EOF\n"
            "script = <<-IND\n"
            "  // literal inside indented heredoc\n"
            "  /* block inside heredoc */\n"
            "  IND\n"
            "/* standalone hcl\n"
            "   block comment */\n"
            "/* block before trailing */\n"
            "x = 1 # trailing after block\n"
        )
        hits = scanners.scan_hcl("main.tf", source)
        active = [h for h in hits if not h.exempted]
        exempted = [h for h in hits if h.exempted]
        self.assertEqual(len(exempted), 4)
        self.assertEqual(
            [(h.line, h.kind, h.inline, h.standalone_lines, h.text) for h in active],
            [
                (1, "line", False, 1, "# hash hcl comment"),
                (2, "line", False, 1, "// slash hcl comment"),
                (7, "line", True, 0, "# inline hcl"),
                (16, "block", False, 2, "/* standalone hcl\n   block comment */"),
                (18, "block", False, 1, "/* block before trailing */"),
                (19, "line", True, 0, "# trailing after block"),
            ],
        )

    def test_cli_estimate_inventory_and_ratchet_across_structured_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            wf = root / ".github" / "workflows" / "ci.yml"
            wf.parent.mkdir(parents=True)
            wf.write_text("# workflow note\nname: ci\n", encoding="utf-8")
            (root / "config.toml").write_text("# toml note\nk = 1\n", encoding="utf-8")
            (root / "view.sql").write_text("-- sql note\nSELECT 1;\n", encoding="utf-8")
            tf = root / "infra.tf"
            tf.write_text("# tf note\n# checkov:skip=CKV_1\nx = 1\n", encoding="utf-8")
            ratchet = root / ".comment-ratchet.json"

            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                code = comment_audit.main(["estimate", str(root), "--json"])
            self.assertEqual(code, 0, err.getvalue())
            est = json.loads(out.getvalue())
            self.assertEqual(est["files_scanned"], 4)
            self.assertEqual(est["comments"], 4)
            self.assertEqual(est["exempted_directives"], 1)

            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                code = comment_audit.main(
                    ["update-ratchet", "--ratchet", str(ratchet), "--init", str(root)]
                )
            self.assertEqual(code, 0, err.getvalue())
            self.assertEqual(
                json.loads(ratchet.read_text(encoding="utf-8"))["files"],
                {
                    ".github/workflows/ci.yml": 1,
                    "config.toml": 1,
                    "infra.tf": 1,
                    "view.sql": 1,
                },
            )

            tf.write_text("# tf note\n# planted regression\nx = 1\n", encoding="utf-8")
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                code = comment_audit.main(["check", "--ratchet", str(ratchet), str(root)])
            self.assertEqual(code, 1)
            self.assertIn("infra.tf", out.getvalue())

            tf.write_text("# checkov:skip=CKV_1\nx = 1\n", encoding="utf-8")
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                code = comment_audit.main(["update-ratchet", "--ratchet", str(ratchet), str(root)])
            self.assertEqual(code, 0, err.getvalue())
            self.assertNotIn("infra.tf", json.loads(ratchet.read_text(encoding="utf-8"))["files"])

            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                code = comment_audit.main(["check", "--ratchet", str(ratchet), str(root)])
            self.assertEqual(code, 0, err.getvalue())
            self.assertIn("Ratchet check passed.", out.getvalue())


if __name__ == "__main__":
    unittest.main()
