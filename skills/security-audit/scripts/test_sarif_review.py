"""Consumer-boundary checks: avoid dropping findings or inventing successful scans."""

import contextlib
import copy
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest

from sarif_review import InvalidSarif, main, review_log


def scan():
    return {"version": "2.1.0", "runs": [{
        "tool": {"driver": {"name": "SyntheticAnalyzer", "rules": [
            {"id": "SYN001", "defaultConfiguration": {"level": "error"}}]}},
        "invocations": [{"executionSuccessful": True}],
        "results": [{"ruleIndex": 0, "message": {"text": "Review an input boundary"}}]}]}


class SarifReviewTests(unittest.TestCase):
    def test_preserves_multiple_tools_rules_locations_and_triage_metadata(self):
        log = scan()
        run = log["runs"][0]
        run["tool"]["extensions"] = [{"name": "Plugin", "guid": "plugin-guid", "rules": [
            {"id": "EXT001", "defaultConfiguration": {"level": "note"}}]}]
        run["artifacts"] = [{"location": {"uri": "src/input.py", "uriBaseId": "ROOT"}}]
        run["originalUriBaseIds"] = {"ROOT": {"uri": "file:///synthetic-project/"}}
        result = run["results"][0]
        result.update({"baselineState": "unchanged", "fingerprints": {"stable/v1": "first"},
                       "suppressions": [{"kind": "external", "status": "underReview"}],
                       "locations": [{"physicalLocation": {"artifactLocation": {"index": 0},
                                      "region": {"startLine": 7}}}]})
        run["results"].append({"rule": {"index": 0, "toolComponent": {"index": 0}},
                               "level": "warning", "message": {"text": "Plugin evidence"}})
        second = copy.deepcopy(run)
        second["results"] = [{"ruleId": "SYN001", "kind": "review", "message": {"text": "Human review"}}]
        log["runs"].append(second)
        before = copy.deepcopy(log)
        ledger = review_log(log)
        self.assertTrue(ledger["complete"])
        self.assertEqual(ledger["result_count"], 3)
        first, plugin = ledger["runs"][0]["findings"]
        self.assertEqual((first["level"], first["level_source"]), ("error", "rule"))
        self.assertEqual(first["locations"][0]["uri"], "src/input.py")
        self.assertEqual(first["locations"][0]["region"]["startLine"], 7)
        self.assertEqual(first["locations"][0]["uri_base"], {"uri": "file:///synthetic-project/"})
        self.assertEqual(first["baseline_state"], "unchanged")
        self.assertEqual(first["suppressions"][0]["status"], "underReview")
        self.assertEqual(first["fingerprints"], {"stable/v1": "first"})
        self.assertEqual((plugin["component"], plugin["rule_id"], plugin["level"]), ("Plugin", "EXT001", "warning"))
        self.assertEqual(ledger["runs"][1]["findings"][0]["level"], "none")
        self.assertEqual(log, before)

    def test_overrides_are_visible_and_never_report_the_wrong_inherited_level(self):
        log = scan()
        log["runs"][0]["invocations"][0]["ruleConfigurationOverrides"] = [
            {"descriptor": {"index": 0}, "configuration": {"level": "note"}}]
        unresolved = review_log(log)
        self.assertFalse(unresolved["complete"])
        self.assertIsNone(unresolved["runs"][0]["findings"][0]["level"])
        self.assertIn("overrides", " ".join(unresolved["diagnostics"]))
        log["runs"][0]["results"][0]["level"] = "error"
        self.assertEqual(review_log(log)["runs"][0]["findings"][0]["level"], "error")

    def test_scan_failures_absent_results_and_missing_execution_never_look_complete(self):
        for change in ("failed", "missing-invocations", "missing-success", "missing-results", "error-notification"):
            with self.subTest(change=change):
                log = scan()
                run = log["runs"][0]
                if change == "failed":
                    run["invocations"][0].update(executionSuccessful=False, exitCode=0)
                elif change == "missing-invocations":
                    del run["invocations"]
                elif change == "missing-success":
                    run["invocations"][0] = {"exitCode": 0}
                elif change == "error-notification":
                    run["invocations"][0]["toolExecutionNotifications"] = [{"level": "error", "message": {"text": "Partial scanner failure"}}]
                else:
                    del run["results"]
                ledger = review_log(log)
                self.assertFalse(ledger["complete"])
                self.assertTrue(ledger["diagnostics"])
        log = scan()
        log["runs"][0]["results"] = []
        self.assertTrue(review_log(log)["complete"])

    def test_invalid_boundaries_do_not_become_default_severity_or_wrong_locations(self):
        mutations = [
            lambda x: x.update(version="2.2"),
            lambda x: x["runs"][0]["results"][0].update(level={}),
            lambda x: x["runs"][0]["results"][0].update(level=None),
            lambda x: x["runs"][0]["invocations"][0].update(exitCode=1.5),
            lambda x: x["runs"][0]["results"][0].update(ruleIndex=True),
            lambda x: x["runs"][0]["results"][0].update(ruleIndex=8),
            lambda x: x["runs"][0]["results"][0].update(ruleId="DIFFERENT"),
            lambda x: x["runs"][0]["results"][0].update(kind="pass", level="error"),
            lambda x: x["runs"][0]["results"][0].update(locations=[{"physicalLocation": {
                "artifactLocation": {"index": 9}}}]),
        ]
        for n, mutate in enumerate(mutations):
            with self.subTest(case=n):
                log = scan()
                mutate(log)
                with self.assertRaises(InvalidSarif):
                    review_log(log)

    def test_external_properties_and_message_lookup_are_explicit_gaps(self):
        log = scan()
        log["runs"][0]["externalPropertyFileReferences"] = {"results": [{"location": {"uri": "https://example.invalid/never-fetch.sarif"}}]}
        log["runs"][0]["results"][0]["message"] = {"id": "message-key"}
        ledger = review_log(log)
        self.assertFalse(ledger["complete"])
        self.assertEqual(ledger["result_count"], 1)
        self.assertEqual(ledger["runs"][0]["findings"][0]["message"]["id"], "message-key")
        self.assertTrue(any("external properties" in d for d in ledger["diagnostics"]))
        self.assertTrue(any("message-string" in d for d in ledger["diagnostics"]))

    def test_notification_metadata_is_not_silently_treated_as_warning(self):
        for feature in ("descriptor", "notificationConfigurationOverrides"):
            with self.subTest(feature=feature):
                log = scan()
                run = log["runs"][0]
                run["tool"]["driver"]["notifications"] = [
                    {"id": "N1", "defaultConfiguration": {"level": "error"}}]
                invocation = run["invocations"][0]
                if feature == "descriptor":
                    invocation["toolExecutionNotifications"] = [
                        {"descriptor": {"index": 0}, "message": {"text": "A rule failed"}}]
                else:
                    invocation["notificationConfigurationOverrides"] = [
                        {"descriptor": {"index": 0}, "configuration": {"level": "error"}}]
                ledger = review_log(log)
                self.assertFalse(ledger["complete"])
                self.assertIn("notification", " ".join(ledger["diagnostics"]))
                self.assertEqual(ledger["result_count"], 1)

    def test_index_disambiguates_duplicate_rule_ids_and_hierarchical_ids(self):
        log = scan()
        run = log["runs"][0]
        run["tool"]["driver"]["rules"].append(
            {"id": "SYN001", "defaultConfiguration": {"level": "note"}})
        run["results"][0].update(ruleId="SYN001/detail")
        run["results"].append({"ruleId": "SYN001", "ruleIndex": 1,
                               "message": {"text": "A different descriptor"}})
        ledger = review_log(log)
        first, second = ledger["runs"][0]["findings"]
        self.assertTrue(ledger["complete"])
        self.assertEqual((first["rule_id"], first["level"]), ("SYN001/detail", "error"))
        self.assertEqual(second["level"], "note")
        for invalid_id in ("SYN001/", "SYN001/detail/more"):
            with self.subTest(invalid_id=invalid_id):
                run["results"][0]["ruleId"] = invalid_id
                with self.assertRaises(InvalidSarif):
                    review_log(log)
        run["results"][0]["ruleId"] = "SYN001/detail"
        del run["results"][0]["ruleIndex"]
        with self.assertRaises(InvalidSarif):
            review_log(log)

    def test_null_results_preserves_other_runs_and_marks_only_missing_evidence(self):
        log = scan()
        second = copy.deepcopy(log["runs"][0])
        second["results"] = None
        log["runs"].append(second)
        ledger = review_log(log)
        self.assertFalse(ledger["complete"])
        self.assertEqual((ledger["run_count"], ledger["result_count"]), (2, 1))
        self.assertEqual(ledger["runs"][0]["findings"][0]["level"], "error")
        self.assertIn("null", " ".join(ledger["runs"][1]["diagnostics"]))

    def test_cli_provenance_exit_status_and_duplicate_key_rejection(self):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / "report.sarif"
            content = json.dumps(scan()).encode()
            source.write_bytes(content)
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                code = main([str(source)])
            ledger = json.loads(output.getvalue())
            self.assertEqual(code, 0)
            self.assertEqual(ledger["source_sha256"], hashlib.sha256(content).hexdigest())
            self.assertEqual(source.read_bytes(), content)
            for bad in ('{"version":"2.1.0","version":"2.2","runs":[]}',
                        '{"version":"2.1.0","runs":NaN}', '{broken',
                        json.dumps(scan()).replace('"executionSuccessful": true',
                                                   '"executionSuccessful": true, "exitCode": 1e400'),
                        '{"version":"2.1.0","runs":[],"large":' + '9' * 5000 + '}'):
                source.write_text(bad)
                output = io.StringIO()
                with contextlib.redirect_stdout(output):
                    code = main([str(source)])
                self.assertEqual(code, 2)
                self.assertFalse(json.loads(output.getvalue())["complete"])

    def test_cli_keeps_valid_results_when_execution_is_incomplete(self):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / "incomplete.sarif"
            log = scan()
            log["runs"][0]["invocations"][0]["executionSuccessful"] = False
            source.write_text(json.dumps(log))
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                code = main([str(source)])
            ledger = json.loads(output.getvalue())
            self.assertEqual(code, 2)
            self.assertEqual(ledger["result_count"], 1)
            self.assertEqual(ledger["runs"][0]["execution"], "failed")
            self.assertEqual(ledger["runs"][0]["findings"][0]["triage_status"], "needs-validation")


if __name__ == "__main__":
    unittest.main()
