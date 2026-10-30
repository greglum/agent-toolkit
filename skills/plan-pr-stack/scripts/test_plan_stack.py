import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("plan_stack.py")
REPO = "github.com/example/project"


def ref(branch, sha="a", repo=REPO):
    return {"repository": repo, "branch": branch, "sha": sha * 40}


def pr(number, branch, base="main", files=None, dependencies=None, repo=REPO):
    return {"number": number, "head": ref(branch, repo=repo), "base": ref(base),
            "files": files if files is not None else [], "depends_on": dependencies or []}


def snapshot(prs, orderings=None):
    return {"version": 1, "observed_at": "2026-10-30T00:00:00Z", "repository": REPO,
            "default_branch": "main", "prs": prs, "orderings": orderings or []}


def dependency(number, state="unknown", repo=REPO):
    return {"repository": repo, "number": number, "state": state,
            "evidence": "reviewed dependency declaration in supplied fixture"}


class StackPlannerTests(unittest.TestCase):
    def run_plan(self, data):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "snapshot.json"
            path.write_text(json.dumps(data))
            result = subprocess.run([sys.executable, str(SCRIPT), str(path)],
                                    capture_output=True, text=True)
            self.assertEqual(json.loads(path.read_text()), data, "input snapshot was changed")
            return result, json.loads(result.stdout) if result.stdout else None

    def test_stack_waves_ignore_same_named_fork_branch(self):
        rows = [pr(10, "feature"), pr(20, "feature", repo="github.com/contributor/project"),
                pr(30, "child", base="feature")]
        result, plan = self.run_plan(snapshot(rows))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(plan["candidate_waves"], [[10, 20], [30]])
        self.assertEqual([(edge["before"], edge["after"]) for edge in plan["edges"]], [(10, 30)])
        self.assertEqual(plan["prs"][1]["head"]["repository"], "github.com/contributor/project")

    def test_unresolved_external_blocks_descendants_but_merged_evidence_releases(self):
        rows = [pr(1, "first", dependencies=[dependency(91)]), pr(2, "second", base="first"), pr(3, "independent")]
        result, plan = self.run_plan(snapshot(rows))
        self.assertEqual(result.returncode, 1)
        self.assertEqual(plan["blocked_prs"], [1, 2])
        self.assertEqual(plan["candidate_waves"], [[3]])
        rows[0]["depends_on"][0]["state"] = "merged"
        result, plan = self.run_plan(snapshot(rows))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(plan["candidate_waves"], [[1, 3], [2]])

    def test_closed_external_is_not_merged_and_cross_repo_number_is_external(self):
        rows = [pr(1, "one", dependencies=[dependency(2, "closed", "github.com/other/project")]), pr(2, "two")]
        result, plan = self.run_plan(snapshot(rows))
        self.assertEqual(result.returncode, 1)
        self.assertEqual(plan["blocked_prs"], [1])
        self.assertEqual(plan["edges"], [])
        self.assertEqual(plan["unresolved"][0]["dependency"]["state"], "closed")

    def test_overlap_needs_evidenced_order_and_can_order_higher_number_first(self):
        data = snapshot([pr(1, "one", files=["schema.sql"]), pr(2, "two", files=["schema.sql"])])
        result, plan = self.run_plan(data)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(plan["blocked_prs"], [1, 2])
        self.assertEqual(plan["candidate_waves"], [])
        data["orderings"] = [{"before": 2, "after": 1, "reason": "producer schema must precede consumer"}]
        result, plan = self.run_plan(data)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(plan["candidate_waves"], [[2], [1]])
        self.assertEqual(plan["edges"][0]["reason"], "producer schema must precede consumer")

    def test_cycle_is_reported_and_does_not_make_a_parallel_wave(self):
        data = snapshot([pr(1, "one", dependencies=[dependency(2)]), pr(2, "two", dependencies=[dependency(1)]), pr(3, "free")])
        result, plan = self.run_plan(data)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(set(plan["cycle"]), {1, 2})
        self.assertEqual(plan["blocked_prs"], [1, 2])
        self.assertEqual(plan["candidate_waves"], [[3]])

    def test_unknowns_and_divergent_parent_sha_remain_visible(self):
        child = pr(2, "two", base="one")
        child["base"]["sha"] = "b" * 40
        child["files"] = None
        child["head"]["sha"] = None
        result, plan = self.run_plan(snapshot([pr(1, "one"), child]))
        self.assertEqual(result.returncode, 1)
        self.assertEqual(len(plan["unknowns"]), 3)
        self.assertEqual(plan["candidate_waves"], [[1], [2]])
        self.assertIsNone(plan["prs"][1]["head"]["sha"])

    def test_external_base_and_duplicate_or_short_identity_fail_explicitly(self):
        row = pr(1, "one", base="unselected-parent")
        result, plan = self.run_plan(snapshot([row]))
        self.assertEqual(result.returncode, 1)
        self.assertEqual(plan["blocked_prs"], [1])
        for data in (snapshot([row, row]), snapshot([pr(1, "same"), pr(2, "same")])):
            result, plan = self.run_plan(data)
            self.assertEqual(result.returncode, 2)
            self.assertIsNone(plan)
            self.assertIn("invalid snapshot", result.stderr)
        row["head"]["sha"] = "a1b2c3"
        result, plan = self.run_plan(snapshot([row]))
        self.assertEqual(result.returncode, 2)
        self.assertIn("full 40/64-character", result.stderr)


    def test_duplicate_json_member_cannot_erase_a_dependency(self):
        data = snapshot([pr(1, "one", dependencies=[dependency(91)])])
        original = json.dumps(data)
        dependency_field = '"depends_on": ' + json.dumps(data["prs"][0]["depends_on"])
        duplicates = [original.replace(dependency_field, dependency_field + ', "depends_on": []'),
                      original.replace('"version": 1', '"version": 1, "version": 1')]
        for raw in duplicates:
            with self.subTest(raw=raw), tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "duplicate.json"
                path.write_text(raw)
                result = subprocess.run([sys.executable, str(SCRIPT), str(path)],
                                        capture_output=True, text=True)
                self.assertEqual(result.returncode, 2)
                self.assertEqual(result.stdout, "")
                self.assertIn("duplicate JSON object member", result.stderr)


if __name__ == "__main__":
    unittest.main()
