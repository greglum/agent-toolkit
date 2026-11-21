import copy
import csv
import json
from pathlib import Path
import random
import subprocess
import sys
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parent
ASSETS = SCRIPTS.parent / "assets"
TEMPORAL = SCRIPTS / "temporal.py"
BASELINE = SCRIPTS / "baseline.py"
DAY = 86400


def run(*args):
    process = subprocess.run([sys.executable, "-B", *map(str, args)], capture_output=True, text=True)
    return process.returncode, json.loads(process.stdout or process.stderr)


def read(path):
    with open(path, newline="") as handle:
        return list(csv.DictReader(handle))


def write(path, rows, columns=None):
    with open(path, "w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns or list(rows[0]), extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    return path


class TemporalTests(unittest.TestCase):
    def setUp(self):
        scratch = tempfile.TemporaryDirectory()
        self.addCleanup(scratch.cleanup)
        self.root = Path(scratch.name)
        self.contract = json.loads((ASSETS / "contract.json").read_text())

    def plan(self, rows, *options, expect=0):
        source = rows if isinstance(rows, Path) else ASSETS / rows
        out = self.root / (source.stem + "-plan.csv")
        code, summary = run(TEMPORAL, "plan", source, "--out", out, "--folds", "2", *options)
        self.assertEqual(code, expect, summary)
        return out, summary

    def audit(self, assignments, **changes):
        path = self.root / "contract.json"
        path.write_text(json.dumps({**self.contract, **changes}))
        return run(TEMPORAL, "audit", assignments, path)

    def checks(self, report):
        return {item["check"] for item in report["findings"]}

    def test_clean_plans_pass_audit(self):
        for rows in ("laps.csv", "stints.csv"):
            code, report = self.audit(self.plan(rows)[0])
            self.assertEqual((code, report["status"], report["findings"]), (0, "pass", []), rows)

    def test_planted_lookahead_feature_fails(self):
        code, report = self.audit(self.plan("laps_lookahead.csv")[0])
        self.assertEqual(code, 1)
        self.assertEqual(self.checks(report), {"lookahead"})
        self.assertIn("official_gap", report["findings"][0]["detail"])
        self.assertEqual(report["findings"][0]["rows"], 30)

    def test_group_split_and_forward_order_fail(self):
        path = self.plan("laps.csv")[0]
        rows = read(path)
        moved = next(r for r in rows if r["fold"] == "0" and r["split"] == "test")
        rows.append({**moved, "row_id": "copy-" + moved["row_id"], "split": "train"})
        code, report = self.audit(write(path, rows))
        self.assertEqual(code, 1)
        self.assertTrue({"group_leak", "forward_order"} <= self.checks(report))
        self.assertEqual(next(f for f in report["findings"] if f["check"] == "group_leak")["fold"], "0")

    def test_label_overlap_without_purge_fails(self):
        code, report = self.audit(self.plan("stints.csv", "--no-purge")[0])
        self.assertEqual(code, 1)
        self.assertEqual(self.checks(report), {"label_overlap"})
        self.assertEqual([(f["fold"], f["rows"]) for f in report["findings"]], [("0", 2), ("1", 2)])

    def test_missing_label_end_time_needs_a_horizon(self):
        rows = read(ASSETS / "stints.csv")
        bare = write(self.root / "bare.csv", rows, [c for c in rows[0] if c != "label_end_time"])
        self.plan(bare, expect=2)
        path, summary = self.plan(bare, "--label-horizon", "180")
        self.assertEqual([f["rows"]["purged"] for f in summary["folds"]], [2, 2])
        self.assertEqual(self.audit(path)[0], 0)
        code, report = self.audit(self.plan(bare, "--label-horizon", "0")[0])
        self.assertEqual((code, self.checks(report)), (1, {"label_window_short"}))

    def test_embargo_and_sliding_window(self):
        path, summary = self.plan("laps.csv", "--embargo-time", str(15 * DAY))
        self.assertEqual(summary["folds"][0]["rows"]["embargo"], 6)
        self.assertEqual(self.audit(path, embargo_time=15 * DAY)[0], 0)
        code, report = self.audit(self.plan("laps.csv")[0], embargo_time=15 * DAY)
        self.assertEqual((code, self.checks(report)), (1, {"embargo"}))
        path, summary = self.plan("laps.csv", "--embargo-groups", "1")
        self.assertEqual((summary["folds"][0]["embargo_groups"], summary["folds"][0]["train_groups"]),
                         (["race3"], ["race1", "race2"]))
        self.assertFalse([r for r in read(path) if r["fold"] == "0" and r["group"] == "race3"
                          and r["split"] == "train"])
        path, summary = self.plan("laps.csv", "--window", "sliding", "--max-train-groups", "2")
        self.assertEqual(summary["folds"][1]["train_groups"], ["race3", "race4"])
        self.assertEqual({r["group"] for r in read(path) if r["fold"] == "1" and r["split"] == "train"},
                         {"race3", "race4"})

    def test_random_split_is_flagged_as_heuristic(self):
        rng = random.Random(1)
        rows = [dict(r, group=r["row_id"], split=rng.choice(["train", "test"]))
                for r in read(self.plan("laps.csv")[0]) if r["fold"] == "1"]
        code, report = self.audit(write(self.root / "shuffled.csv", rows), forward_only=False)
        self.assertEqual(code, 1)
        flagged = [f for f in report["findings"] if f["check"] == "shuffle_suspect"]
        self.assertEqual([f.get("heuristic") for f in flagged], [True])

    def test_invalid_contract_is_input_error(self):
        del self.contract["label_horizon_time"]
        code, report = self.audit(self.plan("laps.csv")[0])
        self.assertEqual(code, 2)
        self.assertIn("label_horizon_time", report["error"])

    def test_embargo_zero_allows_train_at_test_end_when_not_forward_only(self):
        rows = read(self.plan("laps.csv")[0])
        fold0 = [r for r in rows if r["fold"] == "0"]
        test_end = max(r["label_end_time"] for r in fold0 if r["split"] == "test")
        template = next(r for r in fold0 if r["split"] == "train")
        after = {**template, "row_id": "after-end", "group": "race_after",
                 "prediction_time": test_end, "label_end_time": "2026-05-17T14:12:00Z"}
        code, report = self.audit(write(self.root / "after.csv", fold0 + [after]),
                                  forward_only=False, embargo_time=0)
        self.assertEqual(code, 0, report)
        self.assertEqual(report["findings"], [])

    def test_availability_missing_fold_incomplete_and_regime_notes(self):
        path = self.plan("laps.csv")[0]
        rows = read(path)
        no_col = [{k: v for k, v in r.items() if k != "tyre_age__available_at"} for r in rows]
        code, report = self.audit(write(self.root / "no_col.csv", no_col))
        self.assertEqual(code, 1)
        self.assertIn("availability_missing", self.checks(report))

        blank_cell = copy.deepcopy(rows)
        blank_cell[0]["gap_ahead__available_at"] = ""
        code, report = self.audit(write(self.root / "blank_cell.csv", blank_cell))
        self.assertEqual(code, 1)
        self.assertIn("availability_missing", self.checks(report))

        no_train = [r for r in rows if not (r["fold"] == "0" and r["split"] == "train")]
        code, report = self.audit(write(self.root / "no_train.csv", no_train))
        self.assertEqual(code, 1)
        self.assertIn("fold_incomplete", self.checks(report))

        fold1 = [r for r in rows if r["fold"] == "1"]
        code, report = self.audit(write(self.root / "regime.csv", fold1))
        self.assertEqual(code, 0, report["findings"])
        self.assertEqual(len(report["regime_notes"]), 1)
        self.assertIn("hypothetical mid-season tyre compound change", report["regime_notes"][0]["breaks_in_span"])


class BaselineTests(unittest.TestCase):
    def setUp(self):
        scratch = tempfile.TemporaryDirectory()
        self.addCleanup(scratch.cleanup)
        self.path = Path(scratch.name) / "forecasts.json"
        self.data = json.loads((ASSETS / "forecasts.json").read_text())

    def score(self, data=None):
        self.path.write_text(json.dumps(self.data if data is None else data))
        return run(BASELINE, self.path)

    def test_naive_forecast_scores_mase_one_on_its_own_series(self):
        series = [80.0, 81.5, 80.7, 82.1, 81.0, 80.2, 81.8]
        code, report = self.score({"schema_version": 1, "season_length": 1, "quantiles": [], "folds": [
            {"fold": "0", "train": series, "actual": series[1:], "point": series[:-1]}]})
        self.assertEqual(code, 0, report)
        self.assertAlmostEqual(report["folds"][0]["model_mase"], 1.0, places=9)

    def test_bundled_forecasts_score_by_hand(self):
        code, report = self.score()
        self.assertEqual(code, 0, report)
        fold = report["folds"][0]
        self.assertAlmostEqual(fold["scale"], 0.2, places=9)
        self.assertAlmostEqual(fold["baseline_mase"], 4 / 3, places=9)
        self.assertAlmostEqual(fold["pinball"]["0.1"], 0.04, places=9)
        self.assertAlmostEqual(fold["pinball"]["0.9"], 0.06, places=9)

    def test_seasonal_scale_and_two_sided_coverage(self):
        data = copy.deepcopy(self.data)
        data["season_length"] = 2
        data["folds"][0]["actual"] = [79.0, 82.0, 80.2]
        code, report = self.score(data)
        self.assertEqual(code, 0, report)
        fold = report["folds"][0]
        self.assertAlmostEqual(fold["scale"], 1.1 / 6, places=9)
        self.assertAlmostEqual(fold["interval"]["coverage"], 1 / 3, places=9)

    def test_crossed_quantiles_and_huge_values_are_input_errors(self):
        data = copy.deepcopy(self.data)
        data["folds"][0]["quantile_forecasts"]["0.9"][0] = 79.0
        self.assertEqual(self.score(data)[0], 2)
        data = copy.deepcopy(self.data)
        data["folds"][0]["train"] = [1e308, -1e308, 1e308]
        self.assertEqual(self.score(data)[0], 2)

    def test_constant_train_and_short_train_fail_fold_with_exit_one(self):
        data = copy.deepcopy(self.data)
        data["folds"][0]["train"] = [80.0, 80.0, 80.0, 80.0]
        data["folds"][1]["train"] = [80.0]
        code, report = self.score(data)
        self.assertEqual(code, 1, report)
        self.assertEqual(report["summary"]["folds_failed"], 2)
        self.assertEqual([f["status"] for f in report["folds"]], ["failed", "failed"])
        self.assertIn("zero", report["folds"][0]["reason"])
        self.assertIn("season_length", report["folds"][1]["reason"])


if __name__ == "__main__":
    unittest.main()
