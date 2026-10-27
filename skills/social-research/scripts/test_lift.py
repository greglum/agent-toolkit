"""Check lift.py's comparison rules and output boundaries."""

import csv
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import lift  # noqa: E402

SCRIPT = Path(__file__).with_name("lift.py")
HEADER = lift.COLUMNS


def row(post, value, status="complete", **changes):
    base = {"account": "peer-a", "platform": "youtube", "format": "video", "post_id": post,
            "url": f"https://example.com/{post}", "published_at": "2026-10-01", "observed_at": "2026-10-20T12:00Z",
            "age_window": "7d", "metric": "views", "value": value, "status": status, "source": "page"}
    return {**base, **changes}


class LiftTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)

    def run_cli(self, rows, *extra, out="out", raw=None):
        path = self.root / "in.csv"
        if raw is None:
            stream = io.StringIO()
            writer = csv.DictWriter(stream, fieldnames=HEADER)
            writer.writeheader()
            writer.writerows(rows)
            raw = stream.getvalue()
        path.write_text(raw, encoding="utf-8")
        result = subprocess.run([sys.executable, "-I", str(SCRIPT), str(path), "--out", str(self.root / out), *extra],
                                capture_output=True, text=True)
        data = json.loads((self.root / out / "lift.json").read_text()) if result.returncode == 0 else None
        return result, data

    def rows_by_id(self, data):
        return {r["post_id"]: r for c in data["cohorts"] for r in c["rows"]}

    def test_leave_one_out_median_and_partial_rows_visible(self):
        result, data = self.run_cli([row("a", 10), row("b", 20), row("c", 30), row("d", 80),
                                     row("p", 9999, "partial"), row("u", "", "unavailable")])
        self.assertEqual(result.returncode, 0, result.stderr)
        rows = self.rows_by_id(data)
        self.assertEqual((rows["d"]["peer_count"], rows["d"]["peer_median"], rows["d"]["lift"]), (3, 20, 4.0))
        self.assertEqual(rows["a"]["peer_median"], 30)
        self.assertEqual(rows["p"]["excluded"], "status partial")
        self.assertIsNone(rows["u"]["value"])
        self.assertEqual(data["cohorts"][0]["total"], 6)
        report = (self.root / "out" / "lift.md").read_text()
        self.assertIn("status partial", report)
        self.assertIn("status unavailable", report)

    def test_cohorts_split_by_account_platform_format_metric_and_window(self):
        rows = [row(p, 10) for p in "abc"] + [row("x", 1000, account="peer-b"), row("y", 1000, format="short"),
                                              row("z", 1000, metric="likes"), row("w", 1000, age_window="30d", observed_at="2026-11-01")]
        result, data = self.run_cli(rows)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len(data["cohorts"]), 5)
        for post in "xyzw":
            self.assertEqual(self.rows_by_id(data)[post]["excluded"], "fewer than 3 comparable peers")

    def test_equivalent_windows_share_a_cohort(self):
        result, data = self.run_cli([row("a", 10, age_window="24h"), row("b", 10, age_window="1d"),
                                     row("c", 10), row("d", 10)])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.rows_by_id(data)["a"]["peer_count"], 1)

    def test_zero_baseline_is_excluded(self):
        result, data = self.run_cli([row("a", 0), row("b", 0), row("c", 0), row("d", 5)])
        self.assertEqual(self.rows_by_id(data)["d"]["excluded"], "zero peer median")

    def test_display_cap_keeps_totals_and_json(self):
        rows = [row(str(i), i + 1) for i in range(8)]
        result, data = self.run_cli(rows, "--top", "2")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((data["cohorts"][0]["total"], data["cohorts"][0]["scored"]), (8, 8))
        self.assertEqual(len(data["cohorts"][0]["rows"]), 8)
        self.assertIn("showing 2 of 8 scored", (self.root / "out" / "lift.md").read_text())

    def test_refuses_existing_output(self):
        (self.root / "out").mkdir()
        result, _ = self.run_cli([row("a", 1)])
        self.assertEqual(result.returncode, 1)
        self.assertEqual(list((self.root / "out").iterdir()), [])

    def test_formula_and_markdown_cells_neutralized(self):
        rows = [row("=HYPERLINK(\"x\")", 10), row("b|c", 10), row("c", 10), row("d", 10)]
        result, data = self.run_cli(rows)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("=HYPERLINK(\"x\")", self.rows_by_id(data))
        report = (self.root / "out" / "lift.md").read_text()
        self.assertIn("'=HYPERLINK", report)
        self.assertNotIn("| =", report)
        self.assertIn("b\\|c", report)

    def test_rejects_bad_input(self):
        cases = {"lifetime window": [row("a", 1, age_window="lifetime")],
                 "negative": [row("a", -1)],
                 "unavailable with value": [row("a", 5, "unavailable")],
                 "complete without value": [row("a", "")],
                 "http url": [row("a", 1, url="http://example.com/a")],
                 "duplicate": [row("a", 1), row("a", 2)],
                 "uppercase platform": [row("a", 1, platform="YouTube")],
                 "uppercase format": [row("a", 1, format="Video")],
                 "missing observed_at": [row("a", 1, observed_at="")],
                 "unknown source": [row("a", 1, source="scraper")],
                 "observed before published": [row("a", 1, "partial", observed_at="2026-09-30")],
                 "complete before window": [row("a", 1, observed_at="2026-10-07T23:59Z")],
                 "offset timestamp": [row("a", 1, published_at="2026-10-01T00:00+00:00")]}
        for i, (name, rows) in enumerate(cases.items()):
            with self.subTest(name):
                result, _ = self.run_cli(rows, out=f"bad{i}")
                self.assertEqual(result.returncode, 1)
                self.assertFalse((self.root / f"bad{i}").exists())
        result, _ = self.run_cli([], raw="account,value\nx,1\n", out="badheader")
        self.assertEqual(result.returncode, 1)

    def test_window_boundary_and_partial_before_window(self):
        rows = [row("a", 1, observed_at="2026-10-09T00:00Z"), row("b", 1, "partial", observed_at="2026-10-02"),
                row("c", 1, published_at="2026-10-01T06:00Z", observed_at="2026-10-08T06:00Z")]
        result, data = self.run_cli(rows)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.rows_by_id(data)["a"]["observed_at"], "2026-10-09T00:00Z")

    def test_date_only_publication_counts_from_end_of_day(self):
        result, _ = self.run_cli([row("a", 1, observed_at="2026-10-08T00:00Z")])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("age window had not elapsed", result.stderr)

    def test_source_reaches_both_outputs(self):
        rows = [row(p, 10, source="export") for p in "abcd"]
        result, data = self.run_cli(rows)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.rows_by_id(data)["a"]["source"], "export")
        self.assertIn("| export |", (self.root / "out" / "lift.md").read_text())

    def test_quoted_cell_with_newline_parses(self):
        rows = [row("a\nb", 10), row("c", 10), row("d", 10), row("e", 10)]
        result, data = self.run_cli(rows)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(data["input_rows"], 4)
        self.assertIn("a\nb", self.rows_by_id(data))

    def test_time_formats_match_python_310(self):
        for text in ("2026-10-01", "2026-10-01Z", "2026-10-01T09:30", "2026-10-01T09:30:15Z"):
            with self.subTest(text):
                lift.parse_time(text)
        for text in ("20261001", "2026-10-01 09:30", "2026-10-01T09", "2026-10-01T09:30+00:00",
                     "2026-10-01T09:30:15.5", "2026-02-30"):
            with self.subTest(text):
                with self.assertRaises(ValueError):
                    lift.parse_time(text)


if __name__ == "__main__":
    unittest.main()
