#!/usr/bin/env python3
"""Load apply_candidate.py and build the tree and bundle fixtures its tests share."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

SCRIPT = Path(__file__).with_name("apply_candidate.py")
SPEC = importlib.util.spec_from_file_location("apply_candidate", SCRIPT)
assert SPEC and SPEC.loader
APPLY = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = APPLY
SPEC.loader.exec_module(APPLY)
MANIFEST = sys.modules["bundle_manifest"]


class CandidateTrees:
    """Fixture builders for candidate application tests."""

    def make_trees(self, root: Path) -> tuple[Path, Path, Path]:
        target = root / "target"
        candidate = root / "candidate"
        target.mkdir()
        candidate.mkdir()
        (target / "SKILL.md").write_text("baseline\n", encoding="utf-8")
        (target / "obsolete.txt").write_text("remove\n", encoding="utf-8")
        (candidate / "SKILL.md").write_text("candidate\n", encoding="utf-8")
        (candidate / "added.txt").write_text("add\n", encoding="utf-8")
        manifest = root / "manifest.json"
        APPLY.write_manifest(target, manifest)
        return target, candidate, manifest

    def make_bundle_trees(self, root: Path) -> tuple[Path, Path, Path, Path, list[str]]:
        """Create canonical, wrapper, and shared-file bundle fixtures."""
        target = root / "target"
        candidate = root / "candidate"
        paths = [
            ".agents/skills/demo",
            ".claude/skills/demo",
            "setup/repo/skill_evals.json",
        ]
        for bundle_root in (target, candidate):
            (bundle_root / ".agents/skills/demo").mkdir(parents=True)
            (bundle_root / ".claude/skills/demo").mkdir(parents=True)
            (bundle_root / "setup/repo").mkdir(parents=True)
        (target / ".agents/skills/demo/SKILL.md").write_text("baseline\n", encoding="utf-8")
        (target / ".agents/skills/demo/obsolete.txt").write_text("remove\n", encoding="utf-8")
        (target / ".claude/skills/demo/SKILL.md").write_text("baseline\n", encoding="utf-8")
        (target / "setup/repo/skill_evals.json").write_text("baseline\n", encoding="utf-8")
        (candidate / ".agents/skills/demo/SKILL.md").write_text("candidate\n", encoding="utf-8")
        (candidate / ".agents/skills/demo/added.txt").write_text("add\n", encoding="utf-8")
        (candidate / ".claude/skills/demo/SKILL.md").write_text("candidate\n", encoding="utf-8")
        (candidate / "setup/repo/skill_evals.json").write_text("candidate\n", encoding="utf-8")
        baseline_manifest = root / "bundle-baseline.json"
        candidate_manifest = root / "bundle-candidate.json"
        APPLY.write_bundle_manifest(target, paths, baseline_manifest)
        APPLY.write_bundle_manifest(candidate, paths, candidate_manifest)
        return target, candidate, baseline_manifest, candidate_manifest, paths
