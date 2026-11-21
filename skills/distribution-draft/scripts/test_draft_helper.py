"""Tests for draft_helper.py character counting and ledger validation."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import draft_helper  # noqa: E402

SCRIPT = Path(__file__).with_name("draft_helper.py")


class DraftHelperTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()

    def run_cli(self, *args, stdin=None):
        return subprocess.run(
            [sys.executable, "-I", str(SCRIPT), *args],
            input=stdin,
            capture_output=True,
            text=True,
        )

    def make_record(self, **overrides):
        base = {
            "source": {"key": "PR#42", "locator": "docs/release.md:1", "owner_confirmed": True},
            "platform": "x",
            "text": "Shipped the deterministic helper today.",
            "count": {"value": 40, "limit": 280, "method": "x-weighted"},
            "link": {"url": "https://example.com/posts/42", "placement": "body"},
            "claims": [{"text": "Deterministic helper shipped", "locator": "docs/release.md:1"}],
            "flags": [],
            "deslop": "passed",
            "decision": "accepted",
            "decided_at": "2026-11-20T12:00:00Z",
        }
        base.update(overrides)
        return base

    def test_url_fixed_weight_catches_over_limit_that_raw_count_would_miss(self):
        body = "a" * 258 + "https://x.co/1"
        self.assertEqual(len(body), 272)
        res = self.run_cli("count", "--platform", "x", "--text", body, "--url-weight", "23", "--limit", "280")
        self.assertEqual(res.returncode, 1)
        data = json.loads(res.stdout)
        self.assertEqual(data["normalized_chars"], 272)
        self.assertEqual(data["weighted_chars"], 281)
        self.assertFalse(data["within_limit"])

    def test_long_url_passes_under_fixed_weight_and_wide_chars_weight_two(self):
        long_url = "https://example.com/" + "path/" * 30
        res = self.run_cli("count", "--platform", "x", "--text", f"Note {long_url}", "--url-weight", "23", "--limit", "280")
        self.assertEqual(res.returncode, 0, res.stderr)
        self.assertEqual(json.loads(res.stdout)["weighted_chars"], 28)

        nfd = "cafe\u0301 \U0001f680"
        res_wide = self.run_cli("count", "--platform", "x", "--text", nfd, "--wide-weight", "2", "--limit", "8")
        self.assertEqual(res_wide.returncode, 0, res_wide.stderr)
        data = json.loads(res_wide.stdout)
        self.assertEqual(data["normalized_chars"], 6)
        self.assertEqual(data["weighted_chars"], 7)

    def test_unconfirmed_linkedin_limit_omits_pass_fail_claim(self):
        res = self.run_cli("count", "--platform", "linkedin", "--text", "Short draft.")
        self.assertEqual(res.returncode, 0, res.stderr)
        data = json.loads(res.stdout)
        self.assertIsNone(data["limit"])
        self.assertIsNone(data["within_limit"])
        self.assertEqual(data["rule_status"], "unconfirmed")

    def test_ledger_url_normalization_blocks_duplicates_until_new_angle(self):
        ledger = self.root / "ledger.jsonl"
        rec_path = self.root / "rec.json"
        rec = self.make_record(
            source={"key": "https://Example.COM/post/?utm_source=x", "locator": "blog", "owner_confirmed": True},
            platform="linkedin",
        )
        rec_path.write_text(json.dumps(rec))
        res = self.run_cli("ledger-append", "--ledger", str(ledger), "--record", str(rec_path))
        self.assertEqual(res.returncode, 0, res.stderr)

        chk = self.run_cli(
            "ledger-check", "--ledger", str(ledger), "--source-key", "https://example.com/post", "--platform", "linkedin"
        )
        self.assertEqual(chk.returncode, 1)
        self.assertTrue(json.loads(chk.stdout)["matched"])

        chk_x = self.run_cli(
            "ledger-check", "--ledger", str(ledger), "--source-key", "https://example.com/post", "--platform", "x"
        )
        self.assertEqual(chk_x.returncode, 0)

        dup = self.run_cli("ledger-append", "--ledger", str(ledger), "--record", str(rec_path))
        self.assertEqual(dup.returncode, 1)
        new_angle = self.run_cli(
            "ledger-append", "--ledger", str(ledger), "--record", str(rec_path), "--allow-new-angle"
        )
        self.assertEqual(new_angle.returncode, 0, new_angle.stderr)

    def test_rejects_pending_flagged_dropped_with_text_and_symlink_ledger(self):
        ledger = self.root / "ledger.jsonl"
        bad_cases = [
            self.make_record(decision="pending"),
            self.make_record(flags=["private-id"]),
            self.make_record(decision="dropped", text="Should not store dropped text"),
            self.make_record(decision="accepted", text="   "),
        ]
        for idx, rec in enumerate(bad_cases):
            with self.subTest(case=idx):
                p = self.root / f"bad_{idx}.json"
                p.write_text(json.dumps(rec))
                res = self.run_cli("ledger-append", "--ledger", str(ledger), "--record", str(p))
                self.assertEqual(res.returncode, 2)
        self.assertFalse(ledger.exists())

        dropped_ok = self.make_record(decision="dropped")
        del dropped_ok["text"]
        p_ok = self.root / "dropped_ok.json"
        p_ok.write_text(json.dumps(dropped_ok))
        self.assertEqual(self.run_cli("ledger-append", "--ledger", str(ledger), "--record", str(p_ok)).returncode, 0)

        if hasattr(os, "symlink"):
            link = self.root / "link.jsonl"
            link.symlink_to(ledger)
            chk = self.run_cli("ledger-check", "--ledger", str(link), "--source-key", "PR#42", "--platform", "x")
            self.assertEqual(chk.returncode, 2)


if __name__ == "__main__":
    unittest.main()
