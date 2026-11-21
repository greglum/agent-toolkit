import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPTS = Path(__file__).parent
ASSETS = SCRIPTS.parent / "assets"
CLEAN = sorted(ASSETS.glob("clean-*.md"))


def run(*paths):
    process = subprocess.run([sys.executable, "-B", str(SCRIPTS / "check_domain_notes.py"), *map(str, paths)],
                             capture_output=True, text=True)
    return process.returncode, json.loads(process.stdout or process.stderr)


def run_mutated(name, old, new, *more):
    """Run the checker on the clean set with replacements (name, old, new, ...) in clean files."""
    edits = [(name, old, new), *zip(more[0::3], more[1::3], more[2::3])]
    with tempfile.TemporaryDirectory() as scratch:
        paths = []
        for path in CLEAN:
            text = path.read_text()
            for name, old, new in edits:
                if path.name == f"clean-{name}.md":
                    assert old in text, f"{old!r} not in {path.name}"
                    text = text.replace(old, new, 1)
            target = Path(scratch) / path.name
            target.write_text(text)
            paths.append(target)
        return run(*paths)


def checks(report):
    return {(f["check"], f["line"]) for f in report["findings"]}


class DomainNotesTests(unittest.TestCase):
    def test_clean_set_passes(self):
        code, report = run(*CLEAN)
        self.assertEqual(code, 0, report["findings"])
        self.assertEqual(report["counts"], {"sources": 5, "terms": 5, "questions": 5, "primer_claims": 10})
        code, report = run(ASSETS / "clean-sources.md")
        self.assertEqual((code, {f["check"] for f in report["findings"]}), (1, {"missing_section"}))

    def test_defective_file_reports_exactly_the_planted_defects(self):
        code, report = run(ASSETS / "defective-notes.md")
        self.assertEqual(code, 1)
        self.assertEqual(checks(report), {("missing_status", 17), ("uncited_claim", 24),
                                          ("avoided_synonym_used", 28), ("checked_without_locator", 32),
                                          ("question_missing_evidence", 43)})

    def test_each_rule_fires_on_a_single_mutation(self):
        cases = [
            ("sources", "| 2023-06 |", "| undated |", "source_missing_date"),
            ("sources", "https://standards.example.org/lsg-4", "-", "source_missing_locator"),
            ("sources", "| vendor |", "| forum |", "source_unknown_kind"),
            ("sources", "| none |", "| - |", "source_missing_scope"),
            ("sources", "| S5 |", "| S4 |", "duplicate_id"),
            ("glossary", "| Grade | LSG-4 quality class assigned after a reel test |", "| Grade | |",
             "glossary_missing_meaning"),
            ("glossary", "| Reel length |", "| Grade |", "duplicate_term"),
            ("glossary", "| thread length |", "| moisture reading |", "avoid_is_term"),
            ("glossary", "| Reported |", "| Verified |", "invalid_status"),
            ("glossary", "| S4 p. 6 |", "| S9 p. 6 |", "unknown_source"),
            ("glossary", "| S2 §4.2 |", "| S2 |", "checked_without_locator"),
            ("glossary", "Percent water by mass", "Percent humidity by mass", "avoided_synonym_used"),
            ("primer", "  by grade and weight.", "by grade and weight.", "uncited_claim"),
            ("primer", "[S4 p. 9; Reported]", "[S4 p. 9]", "missing_status"),
            ("primer", "[S1 §1; Reported]", "[S1 §1; Reported]\n  - Shells darken after nine days.",
             "uncited_claim"),
            ("primer", "[S1 §1; Reported]", "[S1 §1; Reported]\n\n  Shells darken after nine days.",
             "uncited_claim"),
            ("primer", "[S1 §1; Reported]", "[S1 §1, farm records; Reported]", "bad_reference"),
            ("glossary", "| S4 p. 6 |", "| - |", "missing_source"),
            ("glossary", "| Rework rate |", "| |", "glossary_missing_term"),
            ("sources", "| S5 |", "| Source 5 |", "bad_id"),
            ("questions", "| Q5 | 5 |", "| Q5 | 4 |", "question_bad_rank"),
            ("questions", "| Are grade D lots ever re-reeled and regraded? |", "| |",
             "question_missing_question"),
            ("primer", "a `batch`, but", "a batches, but", "avoided_synonym_used"),
            ("sources", "| S5 | Cocoon sorting notes from one farm | practitioner |",
             "\n| S5 | Cocoon sorting notes from one farm | forum |", "source_unknown_kind"),
            ("sources", "| S5 |", "Farms are paid fast.\n| S5 |", "untabled_prose"),
            ("glossary", "| S2 §4.2 |", "| S2 it is in there |", "checked_without_locator"),
            ("primer", "[S2 §4.2; Checked]", "[S2 see manual; Checked]", "checked_without_locator"),
            ("primer", "[S4 p. 9; Reported]", "[S4 somewhere; Reported]", "bad_locator"),
            ("sources", "| 2023-06 |", "| rev 1234 |", "source_missing_date"),
            ("sources", "https://standards.example.org/lsg-4", "somewhere", "source_missing_locator"),
            ("primer", "### Newcomer mistakes", "### Newcomer mistakes\n\n#### Lots vanish after nine days",
             "uncited_claim"),
            ("primer", "when the shells darken. [S1", "when the shells darken. Payment takes three days. [S1",
             "multi_sentence_claim"),
            ("primer", "[S4 p. 9; Reported]", "[S4 p. 9; Reported] Fees are four percent.", "uncited_claim"),
            ("questions", "| Q5 | 5 |", "| Q5 | \u00b2 |", "question_bad_rank"),
            ("questions", "| Intake clerk |", "| jane.doe@example.org |", "answerer_not_role"),
            ("questions", "| Intake clerk |", "| Jane Doe |", "answerer_not_role"),
            ("primer", "[Q2; Open]", "[Q2; Reported]", "question_ref_not_open"),
            ("primer", "[Q2; Open]", "[Q7; Open]", "unknown_question"),
            ("primer", "### Newcomer mistakes", "### Other notes", "missing_primer_section"),
            ("primer", "| Reel test | Intake draws a ten-cocoon sample from a lot | [S2 §3.1; Checked] |",
             "| Reel test | Intake draws a ten-cocoon sample from a lot |", "uncited_claim"),
            ("questions", "| Which lots to exclude from the yield baseline |", "| |", "question_missing_decision"),
            ("questions", "| Intake clerk |", "| |", "question_missing_answerer"),
            ("questions", "gap: S1 and S2 are silent", "S1 and S2 are silent", "question_evidence_kind"),
            ("questions", "S3 rule 7.3 says 14, S1 §4 says 15", "S3 says 14 or 15", "conflict_needs_two_sources"),
            ("questions", "| Are grade D lots", "| Is the humidity of grade D lots", "avoided_synonym_used"),
        ]
        for name, old, new, check in cases:
            with self.subTest(check=check, old=old):
                code, report = run_mutated(name, old, new)
                self.assertEqual(code, 1, report)
                self.assertEqual({f["check"] for f in report["findings"]}, {check}, report["findings"])

    def test_slug_question_ids_are_accepted(self):
        code, report = run_mutated("questions", "| Q2 | 2 |", "| Q-lot_codes-02 | 2 |",
                                   "primer", "[Q2; Open]", "[Q-lot_codes-02; Open]")
        self.assertEqual(code, 0, report["findings"])

    def test_header_only_tables_are_vacuous(self):
        with tempfile.TemporaryDirectory() as scratch:
            path = Path(scratch) / "empty.md"
            path.write_text("".join(f"## {name}\n\n| {' | '.join(cols)} |\n|{' --- |' * len(cols)}\n\n"
                                    for name, cols in [("Sources", ["ID", "Source", "Kind", "Date", "Locator",
                                                                    "Proves", "Claims"]),
                                                       ("Glossary", ["Term", "Meaning", "Not", "Avoid", "Units",
                                                                     "Source", "Status"]),
                                                       ("Questions", ["ID", "Rank", "Question", "Decision",
                                                                      "Evidence", "Answerer"])])
                            + "## Primer\n\n" + "".join(f"### {p}\n\n" for p in
                                                       ("How it works", "Entities and processes",
                                                        "Metrics and traps", "Newcomer mistakes")))
            code, report = run(path)
        self.assertEqual(code, 1)
        self.assertEqual([f["check"] for f in report["findings"]], ["vacuous"] * 4)

    def test_code_span_mention_is_allowed_but_bare_use_is_not(self):
        line = "- Newcomers call a cocoon lot a `batch`, but"
        code, report = run_mutated("primer", line, line.replace("`batch`", "batch"))
        self.assertEqual((code, {f["check"] for f in report["findings"]}), (1, {"avoided_synonym_used"}))

    def test_invalid_input_exits_2(self):
        with tempfile.TemporaryDirectory() as scratch:
            none = Path(scratch) / "none.md"
            none.write_text("# Notes\n\nNo recognized sections.\n")
            narrow = Path(scratch) / "narrow.md"
            narrow.write_text("## Glossary\n\n| Term | Meaning |\n| --- | --- |\n| Lot | A tray |\n")
            tableless = Path(scratch) / "tableless.md"
            tableless.write_text("## Questions\n\nNone yet.\n")
            for path, message in [(none, "no Sources"), (narrow, "lacks columns"), (tableless, "has no table"),
                                  (Path(scratch) / "missing.md", "cannot read")]:
                code, error = run(path)
                self.assertEqual(code, 2)
                self.assertIn(message, error["error"])

    def test_common_two_word_role_titles_pass(self):
        for role in ("Data Architect", "Principal Scientist", "General Counsel", "Operations Coordinator"):
            with self.subTest(role=role):
                code, report = run_mutated("questions", "| Intake clerk |", f"| {role} |")
                self.assertEqual(code, 0, report["findings"])
        code, report = run_mutated("questions", "| Intake clerk |", "| Jane Doe |")
        self.assertEqual((code, {f["check"] for f in report["findings"]}), (1, {"answerer_not_role"}))


if __name__ == "__main__":
    unittest.main()
