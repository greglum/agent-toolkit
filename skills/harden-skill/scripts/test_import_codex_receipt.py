import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from import_codex_receipt import import_receipt


def stream(*events):
    return ("\n".join(json.dumps(event) for event in events) + "\n").encode()


def completed(usage=None):
    return stream({"type": "thread.started", "thread_id": "do-not-export"},
                  {"type": "turn.started"},
                  {"type": "item.completed", "item": {"type": "agent_message", "text": "Private response"}},
                  {"type": "turn.completed", "usage": usage})


class CodexReceiptEvidence(unittest.TestCase):
    def test_cached_tokens_are_not_double_counted_and_private_content_is_not_copied(self):
        report = import_receipt(completed({"input_tokens": 100, "cached_input_tokens": 80,
                                            "output_tokens": 20, "reasoning_output_tokens": 5}), 0, 2.5)
        self.assertEqual(report["total_tokens"], 120)
        self.assertEqual(report["token_usage"]["cached_input_tokens"], 80)
        self.assertEqual(report["duration_seconds"], 2.5)
        self.assertEqual(report["run_status"], "completed")
        self.assertNotIn("Private response", json.dumps(report))
        self.assertNotIn("do-not-export", json.dumps(report))
        self.assertNotIn("grading", report)

    def test_failed_truncated_and_missing_metric_runs_cannot_become_zero_cost_passes(self):
        failure = stream({"type": "turn.started"}, {"type": "turn.failed", "error": {"message": "Private"}})
        self.assertEqual(import_receipt(failure, 1)["run_status"], "failed")
        truncated = stream({"type": "turn.started"})
        self.assertEqual(import_receipt(truncated, 0)["run_status"], "incomplete")
        missing = import_receipt(completed(), 0)
        self.assertIsNone(missing["total_tokens"])
        self.assertIsNone(missing["duration_seconds"])
        self.assertTrue(missing["warnings"])
        self.assertEqual(import_receipt(completed({}), 2)["run_status"], "failed")
        message = {"type": "item.completed", "item": {"type": "agent_message", "text": "Private"}}
        turn = [{"type": "turn.started"}, {"type": "turn.completed", "usage": {
            "input_tokens": 10, "output_tokens": 2}}]
        for events in [[message, *turn], [*turn, message]]:
            with self.subTest(events=events):
                report = import_receipt(stream(*events), 0)
                self.assertEqual(report["run_status"], "incomplete")
                self.assertFalse(report["agent_message_observed"])
                self.assertIsNone(report["total_tokens"])
                self.assertTrue(all(value is None for value in report["token_usage"].values()))
                self.assertNotIn("Private", json.dumps(report))

    def test_invalid_native_usage_and_broken_json_are_rejected_at_the_boundary(self):
        for raw in [b"", b"not-json\n", b"[]\n",
                    completed({"input_tokens": True}),
                    completed({"input_tokens": 2, "cached_input_tokens": 3}),
                    completed({"input_tokens": -1})]:
            with self.subTest(raw=raw[:50]), self.assertRaises(ValueError):
                import_receipt(raw, 0)

    def test_cli_writes_only_new_timing_record_and_preserves_existing_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            receipt, output = root / "events.jsonl", root / "timing.json"
            receipt.write_bytes(completed({"input_tokens": 10, "output_tokens": 4}))
            command = [sys.executable, str(Path(__file__).with_name("import_codex_receipt.py")),
                       str(receipt), "--exit-code", "0", "--output", str(output)]
            result = subprocess.run(command, capture_output=True, text=True, check=False)
            self.assertEqual(result.returncode, 0, result.stderr)
            before = output.read_bytes()
            self.assertEqual(json.loads(before)["total_tokens"], 14)
            result = subprocess.run(command, capture_output=True, text=True, check=False)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(output.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
