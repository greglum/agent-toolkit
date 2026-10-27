"""Protect sentence snapping, duration limits, overlap suppression, and no-overwrite output."""

import json
import math
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from select_clips import InputError, main, select


def words(start, text, step=0.5):
    """One segment per word, as a word-level transcriber would emit."""
    return [{"start": start + i * step, "end": start + (i + 1) * step - 0.05, "text": w}
            for i, w in enumerate(text.split())]


# Sentences: A 0.0-3.95, B 4.0-7.95, C 8.0-11.95, D 12.0-15.95 (eight words each).
SEGMENTS = (words(0, "Alpha one two three four five six done.")
            + words(4, "Beta one two three four five six done.")
            + words(8, "But gamma two three four five six done.")
            + words(12, "Delta one two three four five six done."))


def run(candidates, count=3, lo=3, hi=9, overlap=0.5, segments=SEGMENTS):
    """Give each candidate without an id a unique default one."""
    cands = [{"id": f"c{i + 1}", **c} for i, c in enumerate(candidates)]
    return select({"segments": segments, "candidates": cands}, count, lo, hi, overlap)


class SelectionTests(unittest.TestCase):
    def test_snaps_outward_to_whole_sentences(self):
        out = run([{"start": 5.2, "end": 9.1, "score": 80, "reason": "r"}])
        clip = out["kept"][0]
        self.assertEqual((clip["start"], clip["end"]), (4.0, 11.95))
        self.assertTrue(clip["text"].startswith("Beta") and clip["text"].endswith("done."))

    def test_over_max_drops_trailing_sentences_not_words(self):
        out = run([{"start": 0.5, "end": 15.0, "score": 80, "reason": "r"}], hi=8.5)
        clip = out["kept"][0]
        self.assertEqual((clip["start"], clip["end"]), (0.0, 7.95))

    def test_duration_limits_reject_with_reason(self):
        out = run([{"start": 0.2, "end": 1.0, "score": 80, "reason": "r"}], lo=5)
        self.assertEqual(out["kept"], [])
        self.assertIn("shorter than 5 s", out["rejected"][0]["rejected_because"])

    def test_overlap_keeps_higher_score(self):
        out = run([{"id": "low", "start": 4.5, "end": 15.0, "score": 60, "reason": "r"},
                   {"id": "high", "start": 0.5, "end": 11.0, "score": 90, "reason": "r"}], hi=13)
        self.assertEqual([k["id"] for k in out["kept"]], ["high"])
        self.assertIn("overlaps kept 'high'", out["rejected"][0]["rejected_because"])

    def test_overlap_below_threshold_keeps_both(self):
        out = run([{"id": "a", "start": 0.5, "end": 11.0, "score": 90, "reason": "r"},
                   {"id": "b", "start": 4.5, "end": 15.0, "score": 60, "reason": "r"}], hi=13, overlap=0.7)
        self.assertEqual({k["id"] for k in out["kept"]}, {"a", "b"})

    def test_top_n_by_score_and_rest_rejected(self):
        cands = [{"id": f"s{i}", "start": i * 4 + 0.5, "end": i * 4 + 3.0, "score": s, "reason": "r"}
                 for i, s in enumerate([10, 40, 30, 20])]
        out = run(cands, count=2, lo=1)
        self.assertEqual([k["id"] for k in out["kept"]], ["s1", "s2"])
        self.assertEqual([k["rank"] for k in out["kept"]], [1, 2])
        self.assertEqual(sorted(r["id"] for r in out["rejected"]), ["s0", "s3"])
        self.assertTrue(all("top 2" in r["rejected_because"] for r in out["rejected"]))

    def test_invalid_candidates_are_rejected_not_dropped(self):
        out = run([{"start": 5, "end": 4, "score": 1, "reason": "r"},
                   {"start": 1, "end": 3, "score": "high", "reason": "r"},
                   {"start": 1, "end": 3, "score": 5}])
        self.assertEqual(len(out["rejected"]), 3)
        self.assertTrue(all(r["rejected_because"].startswith("invalid") for r in out["rejected"]))

    def test_dangling_opener_is_flagged(self):
        out = run([{"start": 8.5, "end": 11.0, "score": 50, "reason": "r"}])
        self.assertTrue(out["kept"][0]["review_flags"])

    def test_unpunctuated_transcript_is_an_input_error(self):
        flat = [{"start": 0, "end": 5, "text": "no punctuation here"}]
        with self.assertRaises(InputError):
            run([{"start": 0, "end": 5, "score": 1, "reason": "r"}], segments=flat)

    def test_non_finite_settings_are_input_errors(self):
        cand = [{"start": 0.5, "end": 7.0, "score": 9, "reason": "r"}]
        for kwargs in ({"lo": math.nan}, {"hi": math.nan}, {"hi": math.inf}, {"overlap": math.nan}):
            with self.subTest(kwargs=kwargs), self.assertRaises(InputError):
                run(cand, **kwargs)

    def test_missing_null_or_duplicate_ids_are_input_errors(self):
        base = {"start": 0.5, "end": 7.0, "score": 9, "reason": "r"}
        for cands in ([base], [{**base, "id": None}], [{**base, "id": ""}],
                      [{**base, "id": "a"}, {**base, "id": "a"}]):
            with self.subTest(cands=cands), self.assertRaises(InputError):
                select({"segments": SEGMENTS, "candidates": cands}, 3, 3, 9, 0.5)

    def test_identical_span_suppressed_even_at_full_overlap(self):
        out = run([{"id": "a", "start": 0.5, "end": 7.0, "score": 90, "reason": "r"},
                   {"id": "b", "start": 1.0, "end": 6.0, "score": 80, "reason": "r"}], overlap=1)
        self.assertEqual([k["id"] for k in out["kept"]], ["a"])
        self.assertIn("same snapped span as kept 'a'", out["rejected"][0]["rejected_because"])

    def test_shortfall_recorded(self):
        out = run([{"start": 0.5, "end": 3.0, "score": 9, "reason": "r"}], count=3)
        self.assertEqual(out["settings"]["shortfall"], 2)
        out = run([{"start": i * 4 + 0.5, "end": i * 4 + 3.0, "score": 9, "reason": "r"}
                   for i in range(4)], count=2)
        self.assertEqual(out["settings"]["shortfall"], 0)

    def test_unterminated_tail_is_recorded(self):
        out = run([{"start": 0.5, "end": 3.0, "score": 9, "reason": "r"}],
                  segments=SEGMENTS + words(16, "Epsilon trails off"))
        tail = out["settings"]["unterminated_tail"]
        self.assertEqual((tail["start"], tail["text"]), (16.0, "Epsilon trails off"))
        self.assertIsNone(run([{"start": 0.5, "end": 3.0, "score": 9, "reason": "r"}])
                          ["settings"]["unterminated_tail"])


class OutputTests(unittest.TestCase):
    def test_existing_output_is_never_overwritten(self):
        with tempfile.TemporaryDirectory() as tmp:
            src, out = Path(tmp, "in.json"), Path(tmp, "out.json")
            src.write_text(json.dumps({"segments": SEGMENTS, "candidates": [
                {"id": "a", "start": 0.5, "end": 7.0, "score": 9, "reason": "r"}]}))
            args = [str(src), "--out", str(out), "--count", "1", "--min-seconds", "3", "--max-seconds", "9"]
            self.assertEqual(main(args), 0)
            first = out.read_text()
            self.assertEqual(main(args), 2)
            self.assertEqual(out.read_text(), first)

    def test_nan_setting_writes_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            src, out = Path(tmp, "in.json"), Path(tmp, "out.json")
            src.write_text(json.dumps({"segments": SEGMENTS, "candidates": [
                {"id": "a", "start": 0.5, "end": 7.0, "score": 9, "reason": "r"}]}))
            args = [str(src), "--out", str(out), "--count", "1", "--min-seconds", "3",
                    "--max-seconds", "nan"]
            self.assertEqual(main(args), 2)
            self.assertFalse(out.exists())

    def test_huge_number_rejects_the_candidate(self):
        result = run([{"start": 0.5, "end": 10 ** 400, "score": 9, "reason": "r"}])
        self.assertEqual(result["kept"], [])
        self.assertIn("too large", result["rejected"][0]["rejected_because"])

    def test_non_utf8_input_is_an_input_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            src, out = Path(tmp, "in.json"), Path(tmp, "out.json")
            src.write_bytes('{"segments": [], "candidates": [], "x": "\xe9"}'.encode("latin-1"))
            args = [str(src), "--out", str(out), "--count", "1", "--min-seconds", "3",
                    "--max-seconds", "9"]
            self.assertEqual(main(args), 2)
            self.assertFalse(out.exists())


if __name__ == "__main__":
    unittest.main()
