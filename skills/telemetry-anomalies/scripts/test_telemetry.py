"""Synthetic fixtures: assets/session.csv is 60 s at 10 Hz with a fuel-pressure spike at 15.0 s,
an oil-temperature ramp of +4 C from 30.0 s that stays, and pit limiter on from 42.0 to 54.0 s
(speed steps from about 250 to 80 kph). assets/reference.csv is clean with its own pit stop."""
import json
from pathlib import Path
import random
import subprocess
import sys
import tempfile
import unittest

SCRIPTS = Path(__file__).parent
ASSETS = SCRIPTS.parent / "assets"
SESSION, REFERENCE, LABELS = ASSETS / "session.csv", ASSETS / "reference.csv", ASSETS / "labels.json"
CHANNELS = "oil_temp_c,fuel_pressure_kpa,speed_kph"


def run(script, *args):
    process = subprocess.run([sys.executable, "-B", str(SCRIPTS / script), *map(str, args)],
                             capture_output=True, text=True)
    return process.returncode, json.loads(process.stdout or process.stderr or "{}")


def overlap(event, start, end):
    return event["start"] <= end and event["end"] >= start


class TelemetryTests(unittest.TestCase):
    def setUp(self):
        scratch = tempfile.TemporaryDirectory()
        self.addCleanup(scratch.cleanup)
        self.root = Path(scratch.name)

    def detect(self, path=SESSION, *extra):
        code, report = run("detect.py", path, "--channels", CHANNELS, "--merge-gap", 0.5, *extra)
        self.assertEqual(code, 0, report)
        return report

    def test_spike_and_drift_are_detected(self):
        events = self.detect(SESSION, "--mode-column", "mode", "--threshold", 5)["events"]
        self.assertTrue(any(e["channel"] == "fuel_pressure_kpa" and overlap(e, 15.0, 15.2) for e in events))
        self.assertTrue(any(e["channel"] == "oil_temp_c" and overlap(e, 30.0, 33.0) for e in events))

    def test_mode_change_flagged_only_without_mode_column(self):
        def pit_events(report):
            return [e for e in report["events"] if e["channel"] == "speed_kph" and overlap(e, 42.0, 56.0)]
        with_mode = self.detect(SESSION, "--mode-column", "mode", "--threshold", 5)
        self.assertEqual(pit_events(with_mode), [])
        without = self.detect(SESSION, "--threshold", 5)
        self.assertTrue(pit_events(without))
        self.assertTrue(any("No mode column" in note for note in without["notes"]))
        excluded = self.detect(SESSION, "--mode-column", "mode", "--exclude-modes", "pit", "--threshold", 5)
        self.assertEqual(excluded["channels"]["speed_kph"]["excluded"], 120)

    def test_calibration_keeps_total_alarms_within_budget(self):
        for budget, per_channel in ((0, False), (2, False), (3, True)):
            with self.subTest(budget=budget, per_channel=per_channel):
                flags = ["--per-channel"] if per_channel else []
                code, calibration = run("calibrate.py", REFERENCE, "--channels", CHANNELS, "--mode-column", "mode",
                                        "--merge-gap", 0.5, "--budget", budget, "--min-threshold", 1, *flags)
                self.assertEqual(code, 0, calibration)
                self.assertLessEqual(calibration["alarms_total"], budget)
                self.assertEqual(calibration["alarms_total"],
                                 sum(c["alarms"] for c in calibration["channels"].values()))
                path = self.root / "calibration.json"
                path.write_text(json.dumps(calibration))
                code, replay = run("detect.py", REFERENCE, "--calibration", path)
                self.assertEqual(code, 0, replay)
                self.assertEqual(replay["total_events"], calibration["alarms_total"])
        looser = self.detect(REFERENCE, "--mode-column", "mode", "--threshold", 2.5)
        self.assertGreater(looser["total_events"], 2)

    def test_random_scorer_has_low_event_precision_without_point_adjust(self):
        rows = SESSION.read_text().splitlines()[1:]
        times = [float(row.split(",")[0]) for row in rows]
        rng = random.Random(3)
        events = []
        for channel in CHANNELS.split(","):
            flagged = [rng.random() > 0.9 for _ in times]
            for i, hit in enumerate(flagged):
                if hit and (i == 0 or not flagged[i - 1]):
                    j = i
                    while j + 1 < len(times) and flagged[j + 1]:
                        j += 1
                    events.append({"channel": channel, "start": times[i], "end": times[j]})
        code, real = run("detect.py", SESSION, "--channels", CHANNELS, "--threshold", 5)
        self.assertEqual(code, 0, real)
        path = self.root / "random.json"
        path.write_text(json.dumps({**real, "events": events}))
        code, report = run("score.py", path, LABELS, "--data", SESSION)
        self.assertEqual(code, 0, report)
        self.assertIs(report["point_adjust"], False)
        self.assertLess(report["detector"]["precision"], 0.2)
        labels = json.loads(LABELS.read_text())
        flagged_points = {(e["channel"], t) for e in events for t in times if e["start"] <= t <= e["end"]}
        label_points = {(l["channel"], t) for l in labels for t in times if l["start"] <= t <= l["end"]}
        adjusted = set(flagged_points)
        for label in labels:
            points = {(label["channel"], t) for t in times if label["start"] <= t <= label["end"]}
            if points & flagged_points:
                adjusted |= points
        tp = len(adjusted & label_points)
        pa_precision, pa_recall = tp / len(adjusted), tp / len(label_points)
        pa_f1 = 2 * pa_precision * pa_recall / (pa_precision + pa_recall)
        self.assertGreater(pa_f1, 2 * (report["detector"]["f1"] or 0))

    def test_score_reports_detector_and_baseline_counts(self):
        report = self.detect(SESSION, "--mode-column", "mode", "--threshold", 5)
        path = self.root / "events.json"
        path.write_text(json.dumps(report))
        code, scored = run("score.py", path, LABELS, "--data", SESSION, "--baseline-reference", REFERENCE)
        self.assertEqual(code, 0, scored)
        self.assertEqual(scored["detector"]["labels_detected"], 2)
        for key in ("detections", "false_detections", "labels_missed", "false_alarms_per_hour"):
            self.assertIn(key, scored["baseline"])

    def test_invalid_input_exits_nonzero(self):
        bad = self.root / "bad.csv"
        bad.write_text("t,oil_temp_c\n0.0,1\n0.0,2\n")
        self.assertEqual(run("detect.py", bad, "--channels", "oil_temp_c", "--threshold", 5)[0], 2)
        self.assertEqual(run("detect.py", SESSION, "--channels", "missing", "--threshold", 5)[0], 2)
        self.assertEqual(run("detect.py", SESSION, "--channels", CHANNELS)[0], 2)
        self.assertEqual(run("calibrate.py", REFERENCE, "--channels", CHANNELS)[0], 2)
        self.assertEqual(run("detect.py", SESSION, "--channels", CHANNELS, "--threshold", 5,
                             "--window", 5, "--min-history", 6)[0], 2)
        self.assertEqual(run("calibrate.py", REFERENCE, "--channels", CHANNELS, "--alarms-per-hour", 2)[0], 2)
        flat = self.root / "flat.csv"
        flat.write_text("t,x\n" + "".join(f"{i},5\n" for i in range(10)))
        params = {"time_column": "t", "channels": ["x"], "mode_column": None, "exclude_modes": [],
                  "window": 5, "min_history": 5, "min_scale": 1e-6, "min_duration": 0, "merge_gap": 0}
        for change in ({"min_scale": 0}, {"exclude_modes": None}, {"min_history": 6}):
            with self.subTest(change=change):
                path = self.root / "calibration.json"
                path.write_text(json.dumps({"params": {**params, **change}, "thresholds": {"x": 5}}))
                self.assertEqual(run("detect.py", flat, "--calibration", path)[0], 2)
        events = self.root / "events.json"
        events.write_text(json.dumps({"params": params, "thresholds": {"x": "5"}, "events": []}))
        labels = self.root / "labels.json"
        labels.write_text("[]")
        self.assertEqual(run("score.py", events, labels, "--data", flat)[0], 2)

    def test_exact_score_uses_mad_constant_and_window(self):
        hand = self.root / "hand.csv"
        values = [50, 60, 70, 80, 90, 0, 1, 2, 3, 4, 10]
        hand.write_text("t,x\n" + "".join(f"{i},{v}\n" for i, v in enumerate(values)))
        code, report = run("detect.py", hand, "--channels", "x", "--window", 5, "--min-history", 5,
                           "--threshold", 5)
        self.assertEqual(code, 0, report)
        self.assertEqual([(e["start"], e["peak_score"]) for e in report["events"]], [(10.0, round(8 / 1.4826, 3))])

    def test_min_duration_keeps_an_event_of_exactly_that_length(self):
        def spikes(minimum):
            report = self.detect(SESSION, "--mode-column", "mode", "--threshold", 5, "--min-duration", minimum)
            return [e for e in report["events"] if e["channel"] == "fuel_pressure_kpa" and overlap(e, 15.0, 15.2)]
        self.assertEqual(len(spikes(0.2)), 1)
        self.assertEqual(spikes(0.25), [])

    def test_calibrated_threshold_is_lowest_adjacent_fit(self):
        code, calibration = run("calibrate.py", REFERENCE, "--channels", CHANNELS, "--mode-column", "mode",
                                "--merge-gap", 0.5, "--budget", 2, "--min-threshold", 1)
        self.assertEqual(code, 0, calibration)
        chosen = calibration["thresholds"]["oil_temp_c"]
        self.assertGreater(chosen, 1)
        lower = {c: chosen - 1e-9 for c in calibration["thresholds"]}
        path = self.root / "lower.json"
        path.write_text(json.dumps({**calibration, "thresholds": lower}))
        code, replay = run("detect.py", REFERENCE, "--calibration", path)
        self.assertEqual(code, 0, replay)
        self.assertGreater(replay["total_events"], 2)

    def test_whole_session_detection_is_exposed_by_flagged_share(self):
        code, real = run("detect.py", SESSION, "--channels", CHANNELS, "--threshold", 5)
        self.assertEqual(code, 0, real)
        session = real["session"]
        blanket = [{"channel": c, "start": session["start"], "end": session["end"]} for c in CHANNELS.split(",")]
        path = self.root / "blanket.json"
        path.write_text(json.dumps({**real, "events": blanket}))
        code, report = run("score.py", path, LABELS, "--data", SESSION)
        self.assertEqual(code, 0, report)
        alarm_time = report["detector"]["alarm_time"]
        self.assertGreater(alarm_time["flagged_share_overall"], 0.99)
        self.assertEqual(len(alarm_time["warnings"]), 3)
        self.assertLess(report["labeled_share_overall"], 0.05)

    def test_channelless_labels_count_toward_labeled_share_overall(self):
        code, real = run("detect.py", SESSION, "--channels", CHANNELS, "--threshold", 5)
        self.assertEqual(code, 0, real)
        events_path = self.root / "events.json"
        events_path.write_text(json.dumps(real))
        labels_path = self.root / "channelless_labels.json"
        labels_path.write_text(json.dumps([{"start": 10.0, "end": 16.0, "kind": "fleet_fault"}]))
        code, report = run("score.py", events_path, labels_path, "--data", SESSION)
        self.assertEqual(code, 0, report)
        expected_share = round(6.0 / report["session"]["duration_s"], 4)
        self.assertAlmostEqual(report["labeled_share_overall"], expected_share, places=4)
        self.assertAlmostEqual(report["channelless_labeled_s"], 6.0, places=6)


if __name__ == "__main__":
    unittest.main()
