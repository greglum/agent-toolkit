import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPTS = Path(__file__).parent
ASSETS = SCRIPTS.parent / "assets"
CONTRACT = json.loads((ASSETS / "contract.json").read_text())


def run(script, *args):
    process = subprocess.run([sys.executable, "-B", str(SCRIPTS / script), *map(str, args)],
                             capture_output=True, text=True)
    return process.returncode, json.loads(process.stdout or process.stderr)


def run_with(contract, data=ASSETS / "clean.csv", csv_text=None):
    with tempfile.TemporaryDirectory() as scratch:
        path = Path(scratch) / "contract.json"
        path.write_text(json.dumps(contract))
        if csv_text is not None:
            data = Path(scratch) / "data.csv"
            data.write_text(csv_text)
        return run("check_contract.py", path, data)


def by_check(report):
    return {(f.get("channel"), f["check"]): f for f in report["findings"]}


class CheckTests(unittest.TestCase):
    def test_clean_file_passes(self):
        code, report = run("check_contract.py", ASSETS / "contract.json", ASSETS / "clean.csv")
        self.assertEqual(code, 0, report["findings"])
        self.assertEqual(report["time"]["observed_rate_hz"], 10.0)

    def test_faulty_file_findings_stay_distinct(self):
        code, report = run("check_contract.py", ASSETS / "contract.json", ASSETS / "faulty.csv")
        self.assertEqual(code, 1)
        found = by_check(report)
        brake = found[("brake_pressure_front", "unit_scale_suspicion")]
        self.assertEqual([c["recorded_as"] for c in brake["candidates"]], ["bar"])
        self.assertTrue(found[("wheel_speed_fl", "unit_mismatch")]["same_family"])
        coolant = report["channels"]["coolant_temp"]["counts"]
        self.assertEqual((coolant["missing"], coolant["saturated"], coolant["out_of_range"]), (3, 2, 0))
        self.assertIn(("coolant_temp", "missing_over_allowed"), found)
        self.assertEqual(found[(None, "time_non_monotonic")]["count"], 1)
        self.assertEqual(found[(None, "time_duplicate")]["count"], 1)
        self.assertEqual(found[(None, "time_gap")]["gaps"][0]["seconds"], 1.1)
        self.assertEqual(found[(None, "lag_negative")]["count"], 2)
        self.assertEqual(found[(None, "lag_late")]["count"], 1)

    def test_limits_rates_and_temperature_conversions(self):
        contract = copy.deepcopy(CONTRACT)
        brake, coolant, wheel = contract["channels"]
        brake["min"] = 1
        coolant.update(unit="K", min=0, max=500, typical_min=330, typical_max=400)
        wheel["expected_rate_hz"] = 20
        contract["channels"].append({"name": "coolant_f", "column": "coolant_temp", "unit": "degF",
                                     "min": -40, "max": 90, "typical_min": 140, "typical_max": 250})
        code, report = run_with(contract)
        self.assertEqual(code, 1)
        found = by_check(report)
        self.assertEqual(found[("brake_pressure_front", "zero_outside_range")]["count"], 30)
        self.assertEqual(found[("coolant_f", "out_of_range")]["count"], 16)
        self.assertIn(("wheel_speed_fl", "rate_mismatch"), found)
        kelvin = found[("coolant_temp", "unit_scale_suspicion")]["candidates"]
        self.assertEqual([(c["recorded_as"], c["converted_median"]) for c in kelvin], [("degc", 362.65)])
        fahrenheit = found[("coolant_f", "unit_scale_suspicion")]["candidates"]
        self.assertEqual([(c["recorded_as"], c["converted_median"]) for c in fahrenheit], [("degc", 192.2)])

    def test_header_only_csv_is_a_finding(self):
        code, report = run_with(CONTRACT, csv_text="t_sensor,t_ingest,brake_pressure_front,coolant_temp,wheel_speed_fl\n")
        self.assertEqual(code, 1)
        found = by_check(report)
        self.assertIn((None, "no_data_rows"), found)
        self.assertIn(("coolant_temp", "no_valid_samples"), found)

    def test_invalid_contracts_exit_2(self):
        for change, message in [(lambda c: c["channels"][0].update(max_lag=1), "unknown keys"),
                                (lambda c: c["channels"][0].update(expected_rate_hz=0), "positive"),
                                (lambda c: c["channels"].append(dict(c["channels"][0])), "duplicate")]:
            contract = copy.deepcopy(CONTRACT)
            change(contract)
            code, error = run_with(contract)
            self.assertEqual(code, 2)
            self.assertIn(message, error["error"])


class InferTests(unittest.TestCase):
    def test_infer_drafts_without_units_and_check_rejects_the_draft(self):
        code, draft = run("infer_contract.py", ASSETS / "faulty.csv", "--sensor-time", "t_sensor",
                          "--ingest-time", "t_ingest")
        self.assertEqual(code, 0, draft)
        self.assertEqual(draft["status"], "draft")
        self.assertTrue(all(c["unit"] is None and c["unit_note"] for c in draft["channels"]))
        wheel = next(c for c in draft["channels"] if c["name"] == "wheel_speed_fl")
        self.assertIn("m/s", wheel["unit_note"])
        self.assertEqual(wheel["observed"]["rate_hz"], 10.0)
        code, report = run_with(draft, ASSETS / "faulty.csv")
        self.assertEqual(code, 1)
        found = by_check(report)
        self.assertIn((None, "contract_not_confirmed"), found)
        self.assertIn(("coolant_temp", "unit_undeclared"), found)


class EdgeCaseTests(unittest.TestCase):
    def test_zero_rate_tolerance_and_nonpositive_gap_factor(self):
        contract = copy.deepcopy(CONTRACT)
        contract["time"]["rate_tolerance"] = 0
        csv_text = "t_sensor,t_ingest,brake_pressure_front,coolant_temp,wheel_speed_fl\n" + "".join(
            f"{i * 0.102:.3f},{i * 0.102 + 0.1:.3f},1000,85,120\n" for i in range(10)
        )
        code, report = run_with(contract, csv_text=csv_text)
        self.assertEqual(code, 1)
        found = by_check(report)
        self.assertIn(("brake_pressure_front", "rate_mismatch"), found)

        for bad in ({"gap_factor": 0}, {"gap_factor": -1}, {"rate_tolerance": -0.1}):
            c = copy.deepcopy(CONTRACT)
            c["time"].update(bad)
            code, err = run_with(c)
            self.assertEqual(code, 2, (bad, err))

    def test_unparseable_sensor_time_does_not_flag_valid_ingest_time(self):
        csv_text = (
            "t_sensor,t_ingest,brake_pressure_front,coolant_temp,wheel_speed_fl\n"
            "0.0,0.1,1000,85,120\n"
            "bad-ts,0.2,1000,85,120\n"
            "0.2,0.3,1000,85,120\n"
        )
        code, report = run_with(CONTRACT, csv_text=csv_text)
        self.assertEqual(code, 1)
        found = by_check(report)
        self.assertIn((None, "time_unparseable"), found)
        self.assertNotIn((None, "ingest_time_unparseable"), found)

    def test_units_metadata_flag_and_iso8601_timestamps(self):
        with tempfile.TemporaryDirectory() as scratch:
            root = Path(scratch)
            contract = copy.deepcopy(CONTRACT)
            contract["time"]["unit"] = "iso8601"
            contract["time"]["max_lag_s"] = 2.0
            contract_path = root / "contract.json"
            contract_path.write_text(json.dumps(contract))
            data_path = root / "iso.csv"
            data_path.write_text(
                "t_sensor,t_ingest,brake_pressure_front,coolant_temp,wheel_speed_fl\n"
                "2026-05-01T12:00:00.000Z,2026-05-01T12:00:00.500Z,1000,85,120\n"
                "2026-05-01T12:00:00.100Z,2026-05-01T12:00:00.600Z,1000,85,120\n"
                "2026-05-01T12:00:00.200,2026-05-01T12:00:00.700,1000,85,120\n"
            )
            units_ok = root / "units_ok.json"
            units_ok.write_text(json.dumps({"brake_pressure_front": "kPa", "coolant_temp": "degC", "wheel_speed_fl": "km/h"}))
            code, report = run("check_contract.py", contract_path, data_path, "--units", units_ok)
            self.assertEqual(code, 0, report["findings"])
            self.assertEqual(report["time"]["lag_s"]["median"], 0.5)

            units_bad = root / "units_bad.json"
            units_bad.write_text(json.dumps({"brake_pressure_front": "bar"}))
            code, report_bad = run("check_contract.py", contract_path, data_path, "--units", units_bad)
            self.assertEqual(code, 1)
            self.assertIn(("brake_pressure_front", "unit_mismatch"), by_check(report_bad))


if __name__ == "__main__":
    unittest.main()
