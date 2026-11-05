"""Regression checks for portable bundles and matching invocation controls."""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from check import check_catalog, check_private_names, check_reader_links, check_skill, only_leftovers


class BundleChecks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.skill = self.root / "example"
        self.skill.mkdir()

    def write_skill(self, description="Example", extra="", body="Body\n"):
        (self.skill / "SKILL.md").write_text(
            f"---\nname: example\ndescription: {description}\n{extra}---\n\n{body}"
        )

    def test_standard_folded_description_at_limit(self):
        self.write_skill(
            description=">-\n  " + "a" * 1024,
        )
        self.assertFalse(any("limit is 1024" in error for error in check_skill(self.skill)))
        self.write_skill(description=">-\n  " + "a" * 1025)
        self.assertTrue(any("limit is 1024" in error for error in check_skill(self.skill)))
        self.write_skill(extra="compatibility: " + "a" * 500 + "\n")
        self.assertEqual(check_skill(self.skill), [])
        self.write_skill(extra="compatibility: " + "a" * 501 + "\n")
        self.assertTrue(any("500-character limit" in error for error in check_skill(self.skill)))

    def test_description_budget_depends_on_invocation(self):
        self.write_skill(description="a" * 360)
        self.assertEqual(check_skill(self.skill), [])
        self.write_skill(description="a" * 361)
        self.assertTrue(any("budget is 360" in error for error in check_skill(self.skill)))
        (self.skill / "agents").mkdir()
        (self.skill / "agents/openai.yaml").write_text("policy:\n  allow_implicit_invocation: false\n")
        self.write_skill(description="a" * 600, extra="disable-model-invocation: true\n")
        self.assertEqual(check_skill(self.skill), [])
        self.write_skill(description="a" * 601, extra="disable-model-invocation: true\n")
        self.assertTrue(any("budget is 600" in error for error in check_skill(self.skill)))

    def test_invocation_booleans_must_be_bare(self):
        for value in ("yes", "True", '"true"', "1"):
            with self.subTest(value=value):
                self.write_skill(extra=f"disable-model-invocation: {value}\n")
                self.assertTrue(any("must be a bare true or false" in error
                                    for error in check_skill(self.skill)))
        self.write_skill(extra="disable-model-invocation: false\n")
        self.assertEqual(check_skill(self.skill), [])

    def test_metadata_preserves_user_settings_and_rejects_unknown_fields(self):
        for field in ("model: alternate-model", "effort: low", "descripton: Typo"):
            with self.subTest(field=field):
                self.write_skill(extra=field + "\n")
                errors = check_skill(self.skill)
                self.assertEqual(len(errors), 1)
                self.assertIn(field.split(":")[0], errors[0])
        self.write_skill(extra="compatibility: Needs local read access.\nargument-hint: '[path]'\n")
        self.assertEqual(check_skill(self.skill), [])

    def test_em_dash_rejected_outside_fenced_code(self):
        self.write_skill(body="```\na \u2014 b\n```\n")
        self.assertEqual(check_skill(self.skill), [])
        self.write_skill(body="Prose \u2014 here\n")
        self.assertTrue(any("em dash" in error for error in check_skill(self.skill)))

    def test_explicit_only_metadata_matches_both_harnesses(self):
        self.write_skill(extra="disable-model-invocation: true\n")
        policy = self.skill / "agents/openai.yaml"
        policy.parent.mkdir()
        for value in (None, "true", "false"):
            with self.subTest(policy=value):
                if value is not None:
                    policy.write_text(f"policy:\n  allow_implicit_invocation: {value}\n")
                errors = check_skill(self.skill)
                self.assertEqual(bool(errors), value != "false")
        for extra in ("", "disable-model-invocation: false\n"):
            with self.subTest(claude_metadata=extra):
                self.write_skill(extra=extra)
                self.assertTrue(any("disable-model-invocation: true" in error
                                    for error in check_skill(self.skill)))

    def test_links_cannot_depend_on_files_outside_bundle(self):
        outside = self.root / "outside.md"
        outside.write_text("Other package\n")
        for target in ("../outside.md", "%2e%2e/outside.md"):
            with self.subTest(target=target):
                self.write_skill(body=f"[Reference]({target})\n")
                self.assertTrue(any("leaves its skill bundle" in error for error in check_skill(self.skill)))
        (self.skill / "linked.md").symlink_to(outside)
        with patch.object(Path, "read_text", side_effect=AssertionError("read before bundle guard")):
            self.assertTrue(any("symbolic link" in error for error in check_skill(self.skill)))
        (self.skill / "linked.md").unlink()
        (self.skill / "local reference.md").write_text("Local\n")
        self.write_skill(body="[Reference](<local reference.md>)\n")
        self.assertEqual(check_skill(self.skill), [])

    def test_heading_anchors_follow_github_slugs(self):
        (self.skill / "ref.md").write_text(
            "# SQL \u2192 Java\n\n## Same\n\n## Same\n\n```\n# Hidden\n```\n\n## Snake_case, 2!\n"
        )
        (self.skill / "data.txt").write_text("not markdown\n")

        def anchor_errors(link):
            self.write_skill(body=f"# Top\n\n[x]({link})\n")
            return [e for e in check_skill(self.skill) if "heading anchor" in e]

        for link in ("#top", "ref.md", "ref.md#", "ref.md#sql--java", "ref.md#same", "ref.md#same-1",
                     "ref.md#snake_case-2", "data.txt#anything"):
            with self.subTest(valid=link):
                self.assertEqual(anchor_errors(link), [])
        for link in ("#missing", "ref.md#sql-java", "ref.md#same-2", "ref.md#hidden", "ref.md#renamed"):
            with self.subTest(broken=link):
                found = anchor_errors(link)
                self.assertEqual(len(found), 1)
                self.assertIn(f"broken heading anchor '{link}'", found[0])

    def test_private_names_skip_when_absent_and_never_echo_the_name(self):
        names = self.root / "private-names.txt"
        errors, notice = check_private_names(names, self.skill)
        self.assertEqual(errors, [])
        self.assertIn("skipped", notice)
        names.write_text("# comment\nAcme Health\n")
        self.write_skill(body="Built for ACME HEALTH.\nAcmeHealthy is a different word.\n")
        (self.skill / ".git").write_text("gitdir: /local/ACME HEALTH/metadata\n")
        errors, notice = check_private_names(names, self.skill)
        self.assertIsNone(notice)
        self.assertEqual(len(errors), 1)
        self.assertIn("SKILL.md:6: private name pattern 1", errors[0])
        self.assertNotIn("acme", errors[0].lower())

    def test_skill_text_rejects_email_and_temporary_paths(self):
        self.write_skill(body="Mail someone@example.org about /private/tmp/run.\n")
        errors = check_skill(self.skill)
        self.assertTrue(any("email address" in e for e in errors))
        self.assertTrue(any("temporary path" in e for e in errors))

    def test_catalog_table_and_skills_folder_agree(self):
        (self.root / "docs").mkdir()
        head = "| Skill | Runs |\n| --- | --- |\n"
        row = "| [`{0}`](../skills/{0}/SKILL.md) | Automatic |\n"
        cases = {
            "good, indented and unbackticked rows": (head + row.format("kept") + "  | [real](../skills/real/SKILL.md) | x |\n", set()),
            "plain name": (head + row.format("kept") + "| ghost | x |\n", {"does not link"}),
            "backticked name with no link": (head + row.format("kept") + "| `ghost` | x |\n", {"does not link"}),
            "name and folder disagree": (head + "| [`kept`](../skills/real/SKILL.md) | x |\n", {"links to the 'real' folder", "no row for skill"}),
            "duplicate": (head + row.format("kept") * 2 + row.format("real"), {"more than one row"}),
            "blank first cell": (head + row.format("kept") + row.format("real") + "|  | x |\n", {"does not link"}),
            "commented and over-indented rows": (
                head + row.format("kept") + row.format("real") + "<!-- | ghost | -->\n    | ghost |\n", set(),
            ),
            "unknown": (head + row.format("kept") + row.format("real") + row.format("ghost"), {"not a catalog skill"}),
            "only row is fenced": ("```\n" + head + row.format("real") + "```\n" + head + row.format("kept"), {"no row for skill 'real'"}),
            "other tables and fences ignored": (
                head + row.format("kept") + row.format("real") + "\nText\n\n| Tool | Use |\n| --- | --- |\n| `ffmpeg` | x |\n```\n| `ghost` |\n```\n",
                set(),
            ),
        }
        for label, (text, expected) in cases.items():
            with self.subTest(label):
                (self.root / "docs/catalog.md").write_text(text)
                errors = check_catalog(self.root, {"kept", "real"})
                self.assertEqual(not errors, not expected, errors)
                for words in expected:
                    self.assertTrue(any(words in error for error in errors), errors)
        (self.root / "docs/catalog.md").write_text("No table\n")
        self.assertIn("no skill table", check_catalog(self.root, {"kept"})[0])

    def test_folder_with_only_python_caches_is_not_a_skill(self):
        (self.skill / "scripts/__pycache__").mkdir(parents=True)
        (self.skill / "scripts/__pycache__/tool.pyc").write_bytes(b"x")
        self.assertTrue(only_leftovers(self.skill))
        (self.skill / ".DS_Store").write_text("x")
        self.assertTrue(only_leftovers(self.skill))
        (self.skill / "scripts/tool.py").write_text("x")
        self.assertFalse(only_leftovers(self.skill))

    def test_reader_links_survive_a_release_without_internal_research(self):
        (self.root / "README.md").write_text("[Guide](docs/guide.md#start)\n")
        docs = self.root / "docs"
        docs.mkdir()
        guide = docs / "guide.md"
        guide.write_text("# Start\n\n[Skill](../example/SKILL.md)\n")
        self.write_skill()
        self.assertEqual(check_reader_links(self.root), [])
        for link, message in (("research/internal.md", "broken relative link"),
                              ("guide.md#retired", "broken heading anchor"),
                              ("../../private.md", "link leaves the repository")):
            with self.subTest(link=link):
                guide.write_text(f"# Start\n\n[Details]({link})\n")
                errors = check_reader_links(self.root)
                self.assertEqual(len(errors), 1)
                self.assertIn(message, errors[0])


if __name__ == "__main__":
    unittest.main()
