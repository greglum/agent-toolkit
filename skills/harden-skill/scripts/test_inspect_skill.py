#!/usr/bin/env python3
# ruff: noqa: D102
"""Tests for inspect_skill.py using only temporary fixtures."""

from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPT = Path(__file__).with_name("inspect_skill.py")
SPEC = importlib.util.spec_from_file_location("inspect_skill", SCRIPT)
assert SPEC and SPEC.loader
INSPECTOR = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = INSPECTOR
SPEC.loader.exec_module(INSPECTOR)


def write_skill(
    root: Path, name: str, frontmatter: str, body: str = "# Test\n\nDo the work.\n"
) -> Path:
    """Create a fixture skill and return its directory."""
    directory = root / name
    directory.mkdir(parents=True)
    (directory / "SKILL.md").write_text(
        f"---\n{frontmatter.strip()}\n---\n\n{body}", encoding="utf-8"
    )
    return directory


def codes(report: dict[str, object], severity: str | None = None) -> set[str]:
    """Return finding codes, optionally filtered by severity."""
    findings = report["findings"]
    assert isinstance(findings, list)
    return {
        str(item["code"])
        for item in findings
        if isinstance(item, dict) and (severity is None or item["severity"] == severity)
    }


class InspectSkillTests(unittest.TestCase):
    """Exercise specification, harness, link, size, and wrapper checks."""

    def test_valid_minimal_skill(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            skill = write_skill(
                Path(temp), "valid-skill", "name: valid-skill\ndescription: Valid test skill."
            )
            report = INSPECTOR.inspect(skill)
            self.assertEqual(report["summary"]["errors"], 0)

    def test_bundle_links_are_rejected_before_any_content_read(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            sentinel = root / "outside.txt"
            sentinel.write_text("Outside the reviewed bundle\n")
            skill = write_skill(root, "valid-skill", "name: valid-skill\ndescription: Valid.")
            for relative in ("SKILL.md", "reference.md", "helper.py", "assets"):
                with self.subTest(entry=relative):
                    link = skill / relative
                    if link.exists():
                        link.unlink()
                    link.symlink_to(sentinel)
                    with patch.object(Path, "read_text", side_effect=AssertionError("content read")):
                        report = INSPECTOR.inspect(skill)
                    self.assertIn("bundle-symlink", codes(report, "error"))
                    self.assertEqual(sentinel.read_text(), "Outside the reviewed bundle\n")
                    link.unlink()
                    if relative == "SKILL.md":
                        (skill / "SKILL.md").write_text("---\nname: valid-skill\ndescription: Valid.\n---\nBody\n")
            # The root link is an intended harness install, unlike internal links.
            installed = root / "installed" / "valid-skill"
            installed.parent.mkdir()
            installed.symlink_to(skill, target_is_directory=True)
            self.assertEqual(INSPECTOR.inspect(installed)["summary"]["errors"], 0)

    @unittest.skipUnless(hasattr(os, "mkfifo"), "named pipes are not available")
    def test_special_entry_is_rejected_before_read(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            skill = write_skill(Path(temp), "valid-skill", "name: valid-skill\ndescription: Valid.")
            os.mkfifo(skill / "reference.md")
            with patch.object(Path, "read_text", side_effect=AssertionError("content read")):
                report = INSPECTOR.inspect(skill)
            self.assertIn("bundle-special-file", codes(report, "error"))

    @unittest.skipUnless(os.name == "posix", "requires POSIX directory permissions")
    def test_unreadable_inventory_is_rejected_before_read(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            skill = write_skill(root, "valid-skill", "name: valid-skill\ndescription: Valid.")
            outside = root / "outside.yaml"
            outside.write_text("policy:\n  allow_implicit_invocation: false\n")
            blocked = skill / "agents"
            blocked.mkdir()
            (blocked / "openai.yaml").symlink_to(outside)
            original_mode = blocked.stat().st_mode & 0o7777
            blocked.chmod(0o111)
            try:
                if os.access(blocked, os.R_OK):
                    self.skipTest("current user bypasses directory read restrictions")
                with patch.object(Path, "read_text", side_effect=AssertionError("content read")):
                    report = INSPECTOR.inspect(skill)
                self.assertIn("bundle-inventory", codes(report, "error"))
            finally:
                blocked.chmod(original_mode)

    def test_invalid_name_and_directory_parity(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            skill = write_skill(
                Path(temp), "different", "name: Bad_Name\ndescription: Invalid naming."
            )
            report = INSPECTOR.inspect(skill)
            self.assertTrue({"name-invalid", "directory-parity"} <= codes(report, "error"))

    def test_folded_description_is_resolved(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            skill = write_skill(
                Path(temp),
                "folded",
                """
name: folded
description: >-
  Inspect an existing skill and
  report structural findings.
""",
            )
            report = INSPECTOR.inspect(skill)
            self.assertEqual(report["summary"]["errors"], 0)

    def test_optional_agent_skills_fields(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            skill = write_skill(
                Path(temp),
                "optional-fields",
                """
name: optional-fields
description: Exercise standard optional fields.
license: Apache-2.0
compatibility: Requires Python 3.
metadata:
  author: test
  version: "1"
allowed-tools: Read Bash
""",
            )
            report = INSPECTOR.inspect(skill, "agent-skills")
            self.assertEqual(report["summary"]["errors"], 0)

    def test_claude_extensions_are_checked_and_warned(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            skill = write_skill(
                Path(temp),
                "claude-skill",
                """
name: claude-skill
description: Exercise Claude extensions.
disable-model-invocation: true
arguments: "[path]"
argument-hint: <path>
""",
            )
            report = INSPECTOR.inspect(skill, "claude")
            self.assertEqual(report["summary"]["errors"], 0)
            self.assertIn("harness-extension", codes(report, "warning"))
            self.assertNotIn("field-unknown", codes(report))

    def test_current_claude_fields_warn_with_portability_notes(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            skill = write_skill(
                Path(temp),
                "current-fields",
                """
name: current-fields
description: Exercise current Claude fields.
when_to_use: When testing.
effort: high
model: sonnet
paths: "src/**"
disallowed-tools: Bash
shell: bash
background: true
""",
            )
            report = INSPECTOR.inspect(skill, "claude")
            self.assertEqual(report["summary"]["errors"], 0)
            messages = " ".join(str(item["message"]) for item in report["findings"])
            self.assertIn("keep trigger text in description", messages)
            self.assertIn("overrides the user's effort setting", messages)
            self.assertIn("overrides the user's model setting", messages)
            (skill / "SKILL.md").write_text(
                "---\nname: current-fields\ndescription: Bad boolean.\nbackground: yes\n---\n\nBody\n"
            )
            self.assertIn("extension-boolean", codes(INSPECTOR.inspect(skill), "error"))

    def test_codex_explicit_policy_matches_claude_extension(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            skill = write_skill(
                Path(temp),
                "codex-skill",
                """
name: codex-skill
description: Exercise Codex metadata.
disable-model-invocation: true
""",
            )
            sidecar = skill / "agents" / "openai.yaml"
            sidecar.parent.mkdir()
            sidecar.write_text(
                'interface:\n  display_name: "Codex Skill"\npolicy:\n'
                "  allow_implicit_invocation: false\n",
                encoding="utf-8",
            )
            report = INSPECTOR.inspect(skill, "codex")
            self.assertEqual(report["summary"]["errors"], 0)
            self.assertNotIn("invocation-conflict", codes(report))

    def test_codex_implicit_conflicts_with_claude_extension(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            skill = write_skill(
                Path(temp),
                "conflicting-skill",
                """
name: conflicting-skill
description: Exercise a cross-harness invocation conflict.
disable-model-invocation: true
""",
            )
            sidecar = skill / "agents" / "openai.yaml"
            sidecar.parent.mkdir()
            sidecar.write_text(
                'interface:\n  display_name: "Conflicting Skill"\npolicy:\n'
                "  allow_implicit_invocation: true\n",
                encoding="utf-8",
            )
            report = INSPECTOR.inspect(skill, "codex")
            self.assertIn("invocation-conflict", codes(report, "error"))

    def test_codex_policy_must_be_nested_under_policy(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            skill = write_skill(
                Path(temp),
                "misnested-policy",
                """
name: misnested-policy
description: Reject a misnested Codex policy.
disable-model-invocation: true
""",
            )
            sidecar = skill / "agents" / "openai.yaml"
            sidecar.parent.mkdir()
            sidecar.write_text(
                "interface:\n  allow_implicit_invocation: false\n",
                encoding="utf-8",
            )
            report = INSPECTOR.inspect(skill, "codex")
            self.assertIn("codex-policy-missing", codes(report, "error"))

    def test_broken_relative_link_is_error(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            skill = write_skill(
                Path(temp),
                "broken-link",
                "name: broken-link\ndescription: Find broken links.",
                "# Broken\n\nRead [missing](references/missing.md).\n",
            )
            report = INSPECTOR.inspect(skill)
            self.assertIn("link-broken", codes(report, "error"))

    def test_oversized_skill_is_warning_not_structural_error(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            body = "# Large\n\n" + "\n".join(f"Instruction {index}." for index in range(510))
            skill = write_skill(
                Path(temp),
                "large-skill",
                "name: large-skill\ndescription: A deliberately large skill.",
                body,
            )
            report = INSPECTOR.inspect(skill)
            self.assertEqual(report["summary"]["errors"], 0)
            self.assertIn("skill-size", codes(report, "warning"))

    def test_wrapper_frontmatter_drift_is_error(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            canonical = write_skill(
                root / ".agents" / "skills",
                "paired-skill",
                "name: paired-skill\ndescription: Canonical description.",
            )
            write_skill(
                root / ".claude" / "skills",
                "paired-skill",
                "name: paired-skill\ndescription: Drifted description.",
            )
            report = INSPECTOR.inspect(canonical)
            self.assertIn("wrapper-drift", codes(report, "error"))

    def test_invalid_invocation_exits_two(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            result = subprocess.run(
                [sys.executable, str(SCRIPT), str(Path(temp) / "missing")],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 2)


if __name__ == "__main__":
    unittest.main()
