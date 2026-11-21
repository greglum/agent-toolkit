"""Keep files that several bundles carry identical to their canonical source.

Each bundle must install alone, so shared scripts and references are copied rather than linked.
Any bundle that carries a file with a canonical name must match the canonical copy byte for byte.
Any other same-named pair that differs but is at least DRIFT_SIMILARITY alike is treated as a
drifted copy and fails; unrelated files that only share a name pass.
"""

import unittest
from difflib import SequenceMatcher
from pathlib import Path

SKILLS = Path(__file__).resolve().parents[1] / "skills"

SHARED = {
    ("retro-guardrails", "retro-*"): (
        "scripts/collect_history.py",
        "scripts/git_evidence.py",
        "scripts/github_evidence.py",
        "scripts/repo_controls.py",
        "scripts/retro_state.py",
        "references/ledger.md",
    ),
    ("analyze-agent-history", "retro-*"): ("scripts/session_records.py",),
    ("repository-cleanup", "refresh-worktrees"): (
        "scripts/inventory.py",
        "scripts/test_inventory.py",
    ),
}

PER_BUNDLE = {"SKILL.md", "agents/openai.yaml", "references/sources.md", "LICENSE", "SOURCE.md"}
DRIFT_SIMILARITY = 0.6


def likely_drifted(first: bytes, second: bytes) -> bool:
    """True when two differing files look like edited copies of one original."""
    if first == second:
        return False
    a = first.decode("utf-8", "replace").splitlines()
    b = second.decode("utf-8", "replace").splitlines()
    matcher = SequenceMatcher(None, a, b, autojunk=False)
    return matcher.real_quick_ratio() >= DRIFT_SIMILARITY and matcher.ratio() >= DRIFT_SIMILARITY


def bundle_files() -> dict[str, list[Path]]:
    """Relative path -> the copies of it across bundles, ignoring caches and Finder files."""
    found: dict[str, list[Path]] = {}
    for path in sorted(SKILLS.glob("*/**/*")):
        relative = path.relative_to(SKILLS)
        if path.is_file() and "__pycache__" not in relative.parts and path.name != ".DS_Store":
            found.setdefault(Path(*relative.parts[1:]).as_posix(), []).append(path)
    return found


class SharedCopies(unittest.TestCase):
    def test_copies_match_their_canonical_source(self):
        for (owner, pattern), files in SHARED.items():
            for relative in files:
                canonical = SKILLS / owner / relative
                self.assertTrue(canonical.is_file(), f"canonical {owner}/{relative} is missing")
                copies = [
                    bundle / relative
                    for bundle in sorted(SKILLS.glob(pattern))
                    if bundle.name != owner and (bundle / relative).exists()
                ]
                self.assertTrue(copies, f"no bundle carries a copy of {owner}/{relative}; remove the entry")
                for copy in copies:
                    with self.subTest(copy=str(copy.relative_to(SKILLS))):
                        self.assertEqual(
                            copy.read_bytes(),
                            canonical.read_bytes(),
                            f"{copy.relative_to(SKILLS)} differs from {owner}/{relative}; "
                            f"copy the canonical file over it",
                        )

    def test_same_named_files_are_not_drifted_copies(self):
        for relative, copies in bundle_files().items():
            if len(copies) < 2 or relative in PER_BUNDLE:
                continue
            for i, first in enumerate(copies):
                for second in copies[i + 1:]:
                    with self.subTest(pair=f"{first.relative_to(SKILLS)} vs {second.relative_to(SKILLS)}"):
                        self.assertFalse(
                            likely_drifted(first.read_bytes(), second.read_bytes()),
                            "these look like copies of one file that have drifted; make them match "
                            "and register the canonical copy in SHARED, or rename one",
                        )

    def test_drift_detector_flags_an_edited_copy_and_ignores_unrelated_files(self):
        original = "".join(f"line {n}\n" for n in range(40)).encode()
        edited = original.replace(b"line 7\n", b"line seven\n")
        unrelated = "".join(f"other {n}\n" for n in range(40)).encode()
        self.assertTrue(likely_drifted(original, edited))
        self.assertFalse(likely_drifted(original, unrelated))


if __name__ == "__main__":
    unittest.main()
