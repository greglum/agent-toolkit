import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).with_name("compare.py")
ASSETS = SCRIPT.parent.parent / "assets"


class CompareTests(unittest.TestCase):
    def setUp(self):
        self.scratch = tempfile.TemporaryDirectory()
        self.addCleanup(self.scratch.cleanup)
        self.root = Path(self.scratch.name)
        self.plan = json.loads((ASSETS / "plan.json").read_text())
        self.samples = json.loads((ASSETS / "samples.json").read_text())

    def run_cli(self, command, rows=None, plan=None, selection=None, digest=None, arm=None):
        plan = self.plan if plan is None else plan
        self.root.joinpath("plan.json").write_text(json.dumps(plan))
        args = [sys.executable, str(SCRIPT), command, str(self.root / "plan.json")]
        if command != "freeze":
            self.root.joinpath("samples.json").write_text(json.dumps(self.samples if rows is None else rows))
            args += [str(self.root / "samples.json"), "--plan-sha", self.digest if digest is None else digest]
        if arm is not None:
            args += ["--arm", arm]
        if selection is not None:
            self.root.joinpath("selection.json").write_text(json.dumps(selection))
            args += ["--selection", str(self.root / "selection.json")]
        process = subprocess.run(args, capture_output=True, text=True)
        return process.returncode, json.loads(process.stdout or process.stderr)

    def freeze(self):
        status, result = self.run_cli("freeze")
        self.assertEqual(status, 0, result)
        self.digest = result["plan_sha256"]

    def discovery(self):
        return [r for r in self.samples if not r["round"].startswith("c")]

    def test_selection_requires_fresh_matching_confirmation_and_is_descriptive(self):
        self.freeze()
        code, report = self.run_cli("analyze", self.discovery())
        self.assertEqual(code, 0, report)
        self.assertEqual(report["arms"]["candidate"]["verdict"], "NEEDS_CONFIRMATION")
        self.assertEqual(report["arms"]["candidate"]["median_improvement"], 10)
        code, selection = self.run_cli("select", self.discovery(), arm="candidate")
        self.assertEqual(code, 0, selection)
        code, final = self.run_cli("analyze", selection=selection)
        self.assertEqual(code, 0, final)
        self.assertEqual(final["confirmation"]["verdict"], "CONFIRMED_OBSERVATION")
        self.assertIn("no significance or causal claim", final["evidence"])
        self.assertEqual(self.run_cli("analyze")[0], 2)
        changed = copy.deepcopy(self.samples)
        changed[4]["value"] += 1
        self.assertEqual(self.run_cli("analyze", changed, selection=selection)[0], 2)

    def test_plan_identity_and_sample_identity_mismatches_are_errors(self):
        self.freeze()
        self.assertEqual(self.run_cli("analyze", self.discovery(), digest="0" * 64)[0], 2)
        for field, value in {"revision": "different", "unit": "ms", "direction": "higher",
                             "metric": "cost", "workload": "other", "profile": "warm",
                             "guard_contract": "weaker-preservation",
                             "run_id": self.samples[1]["run_id"], "round": "unplanned"}.items():
            with self.subTest(field=field):
                rows = self.discovery()
                rows[0] = {**rows[0], field: value}
                code, result = self.run_cli("analyze", rows)
                self.assertEqual(code, 2, result)
        self.assertEqual(self.run_cli("analyze", self.discovery() + [self.discovery()[0]])[0], 2)
        changed_plan = {**self.plan, "guard_contract": "weaker-preservation"}
        self.assertEqual(self.run_cli("analyze", self.discovery(), plan=changed_plan)[0], 2)

    def test_failed_missing_and_unverified_samples_block_survivor_bias(self):
        self.freeze()
        for status in ("failure", "skipped", "timeout"):
            rows = copy.deepcopy(self.discovery())
            rows[5].update(status=status, value=None)
            code, report = self.run_cli("analyze", rows)
            self.assertEqual(code, 0, report)
            result = report["arms"]["candidate"]
            self.assertEqual(result["verdict"], "INCONCLUSIVE")
            self.assertEqual(result["counts"][status], 1)
        for guards in ("fail", "unknown"):
            rows = copy.deepcopy(self.discovery())
            rows[5]["guards"] = guards
            code, report = self.run_cli("analyze", rows)
            self.assertEqual(code, 0, report)
            self.assertEqual(report["arms"]["candidate"]["verdict"], "INCONCLUSIVE")
        code, report = self.run_cli("analyze", self.discovery()[:-1])
        self.assertEqual(code, 0, report)
        self.assertEqual(report["arms"]["candidate"]["counts"]["missing"], 1)
        self.assertEqual(report["arms"]["candidate"]["verdict"], "INCONCLUSIVE")

    def test_absent_or_unstable_unchanged_control_is_not_zero_noise(self):
        self.freeze()
        rows = [r for r in self.discovery() if not r["round"].startswith("a")]
        code, report = self.run_cli("analyze", rows)
        self.assertEqual(code, 0, report)
        self.assertIsNone(report["observed_unchanged_spread"])
        self.assertEqual(report["arms"]["candidate"]["verdict"], "INCONCLUSIVE")
        rows = copy.deepcopy(self.discovery())
        rows[1]["value"] = 50
        code, report = self.run_cli("analyze", rows)
        self.assertEqual(code, 0, report)
        self.assertEqual(report["observed_unchanged_spread"], 50)
        self.assertEqual(report["arms"]["candidate"]["verdict"], "INCONCLUSIVE")

    def test_higher_direction_practical_bar_and_nonfinite_boundary(self):
        self.plan["direction"] = "higher"
        for row in self.samples:
            row["direction"] = "higher"
        self.freeze()
        code, report = self.run_cli("analyze", self.discovery())
        self.assertEqual(code, 0, report)
        self.assertEqual(report["arms"]["candidate"]["median_improvement"], -10)
        self.assertEqual(report["arms"]["candidate"]["verdict"], "DOES_NOT_MEET_BAR")
        for value in (float("nan"), float("inf"), True, 10**400):
            rows = copy.deepcopy(self.discovery())
            rows[5]["value"] = value
            self.assertEqual(self.run_cli("analyze", rows)[0], 2)

    def test_invalid_arguments_do_not_echo_private_input(self):
        sentinel = 'PRIVATE_SENTINEL_argument'
        result = subprocess.run([sys.executable, str(SCRIPT), sentinel],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertNotIn(sentinel, result.stdout + result.stderr)
        self.assertNotIn('Traceback', result.stderr)

    def test_round_reuse_and_unchanged_revision_are_rejected_at_freeze(self):
        for mutate in (lambda p: p["rounds"]["confirmation"].__setitem__(0, "d1"),
                       lambda p: p["arms"].__setitem__("repeat", "different")):
            plan = copy.deepcopy(self.plan)
            mutate(plan)
            self.assertEqual(self.run_cli("freeze", plan=plan)[0], 2)

    def test_mixed_sign_discovery_confirmation_and_duplicate_json_keys(self):
        plan = copy.deepcopy(self.plan)
        plan["rounds"]["discovery"] = ["d1", "d2", "d3"]
        plan["rounds"]["confirmation"] = ["c1", "c2", "c3"]
        self.plan = plan
        self.freeze()

        def make_pair(round_id, run_prefix, control_val, cand_val):
            base = copy.deepcopy(self.samples[0])
            ctrl = plan["control"]
            return [
                {**base, "round": round_id, "arm": ctrl, "run_id": f"{run_prefix}-ctrl",
                 "revision": plan["arms"][ctrl], "value": control_val},
                {**base, "round": round_id, "arm": "candidate", "run_id": f"{run_prefix}-cand",
                 "revision": plan["arms"]["candidate"], "value": cand_val},
            ]

        aa = [r for r in self.samples if r["round"].startswith("a")]
        disc_inc = aa + make_pair("d1", "d1", 100, 85) + make_pair("d2", "d2", 100, 85) + make_pair("d3", "d3", 100, 101)
        code, report = self.run_cli("analyze", disc_inc)
        self.assertEqual(code, 0, report)
        self.assertEqual(report["arms"]["candidate"]["verdict"], "INCONCLUSIVE")

        disc_fail = aa + make_pair("d1", "d1", 100, 85) + make_pair("d2", "d2", 100, 101) + make_pair("d3", "d3", 100, 102)
        code, report = self.run_cli("analyze", disc_fail)
        self.assertEqual(code, 0, report)
        self.assertEqual(report["arms"]["candidate"]["verdict"], "DOES_NOT_MEET_BAR")

        disc_ok = aa + make_pair("d1", "d1", 100, 85) + make_pair("d2", "d2", 100, 85) + make_pair("d3", "d3", 100, 85)
        code, selection = self.run_cli("select", disc_ok, arm="candidate")
        self.assertEqual(code, 0, selection)
        conf_inc = disc_ok + make_pair("c1", "c1", 100, 85) + make_pair("c2", "c2", 100, 85) + make_pair("c3", "c3", 100, 101)
        code, final = self.run_cli("analyze", conf_inc, selection=selection)
        self.assertEqual(code, 0, final)
        self.assertEqual(final["confirmation"]["verdict"], "INCONCLUSIVE")

        conf_fail = disc_ok + make_pair("c1", "c1", 100, 85) + make_pair("c2", "c2", 100, 101) + make_pair("c3", "c3", 100, 102)
        code, final_fail = self.run_cli("analyze", conf_fail, selection=selection)
        self.assertEqual(code, 0, final_fail)
        self.assertEqual(final_fail["confirmation"]["verdict"], "DOES_NOT_MEET_BAR")

        dup_plan = self.root / "dup_plan.json"
        dup_plan.write_text('{"schema_version": 1, "schema_version": 1}')
        proc = subprocess.run([sys.executable, "-B", str(SCRIPT), "freeze", str(dup_plan)],
                              capture_output=True, text=True)
        self.assertEqual(proc.returncode, 2)
        dup_samples = self.root / "dup_samples.json"
        dup_samples.write_text('[{"round": "a1", "round": "a2"}]')
        self.root.joinpath("plan.json").write_text(json.dumps(self.plan))
        proc2 = subprocess.run([sys.executable, "-B", str(SCRIPT), "analyze",
                                str(self.root / "plan.json"), str(dup_samples), "--plan-sha", self.digest],
                               capture_output=True, text=True)
        self.assertEqual(proc2.returncode, 2)


if __name__ == "__main__":
    unittest.main()
