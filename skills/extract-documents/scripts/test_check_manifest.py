import copy
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import json

from check_manifest import digest, reconcile


class ExtractionAccounting(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        (self.root / "source.txt").write_text("First line.\nSecond line.\n")
        (self.root / "text.md").write_text("First line.\nSecond line.\n")
        self.entry = {"source_id": "text-1", "source": "source.txt",
                      "source_sha256": digest(self.root / "source.txt"),
                      "status": "verified", "known_loss": [], "errors": [],
                      "output": {"path": "text.md", "sha256": digest(self.root / "text.md")},
                      "tool": {"name": "Python UTF-8 reader", "version": "3"},
                      "verification": {"coverage": "full", "locators": [
                          {"source": "lines 1-2", "output": "lines 1-2"}]}}

    def test_every_input_including_unsupported_is_reconciled_without_claiming_fidelity(self):
        (self.root / "unsupported.bin").write_bytes(b"\x00\xff")
        unsupported = {"source_id": "binary-1", "source": "unsupported.bin",
                       "source_sha256": digest(self.root / "unsupported.bin"),
                       "status": "unsupported", "known_loss": [],
                       "errors": ["No selected reader for this format"], "output": None,
                       "tool": None, "verification": {"coverage": "none", "locators": []}}
        unavailable = copy.deepcopy(unsupported)
        unavailable.update(source_id="missing-1", source="missing.txt", source_sha256=None,
                           status="failed", errors=["Requested input is unavailable"])
        manifest = [self.entry, unsupported, unavailable]
        report = reconcile(manifest, ["source.txt", "unsupported.bin", "missing.txt"], self.root)
        self.assertEqual(report["status"], "RECONCILED")
        self.assertEqual(report["source_statuses"], {"verified": 1, "unsupported": 1, "failed": 1})
        self.assertEqual(report["content_fidelity"], "not established by this checker")
        missing = reconcile([self.entry], ["source.txt", "unsupported.bin"], self.root)
        self.assertEqual(missing["status"], "MISMATCH")
        self.assertIn("manifest omits 1 requested input(s)", missing["errors"])
        duplicate = reconcile([self.entry, self.entry], ["source.txt"], self.root)
        self.assertEqual(duplicate["status"], "MISMATCH")

    def test_changed_sources_outputs_and_empty_extraction_cannot_reuse_verified_status(self):
        for target in ["source.txt", "text.md"]:
            with self.subTest(target=target):
                path = self.root / target
                original = path.read_bytes()
                path.write_text("Changed after extraction")
                self.assertEqual(reconcile([self.entry], ["source.txt"], self.root)["status"], "MISMATCH")
                path.write_bytes(original)
        (self.root / "text.md").write_bytes(b"")
        self.entry["output"]["sha256"] = digest(self.root / "text.md")
        report = reconcile([self.entry], ["source.txt"], self.root)
        self.assertIn("source 1: empty output cannot establish verified extraction", report["errors"])

    def test_unrequested_sources_and_output_escape_are_not_read_as_authorized_evidence(self):
        unrequested = copy.deepcopy(self.entry)
        unrequested["source"] = "another.txt"
        self.assertEqual(reconcile([unrequested], ["source.txt"], self.root)["status"], "MISMATCH")
        for output in ["../outside.txt", "https://example.invalid/document"]:
            with self.subTest(output=output):
                entry = copy.deepcopy(self.entry)
                entry["output"]["path"] = output
                self.assertEqual(reconcile([entry], ["source.txt"], self.root)["status"], "MISMATCH")
        alias = copy.deepcopy(self.entry)
        alias["output"]["path"] = "source.txt"
        alias["output"]["sha256"] = digest(self.root / "source.txt")
        self.assertIn("source 1: output aliases a requested original",
                      reconcile([alias], ["source.txt"], self.root)["errors"])
        linked = self.root / "linked-output.md"
        linked.hardlink_to(self.root / "source.txt")
        alias["output"]["path"] = linked.name
        self.assertIn("source 1: output aliases a requested original",
                      reconcile([alias], ["source.txt"], self.root)["errors"])

    @unittest.skipUnless(hasattr(os, "mkfifo"), "requires POSIX FIFOs")
    def test_cli_accounts_for_an_unsupported_fifo_without_opening_it(self):
        os.mkfifo(self.root / "source.pipe")
        entry = {"source_id": "pipe", "source": "source.pipe", "source_sha256": None,
                 "status": "unsupported", "known_loss": [], "errors": ["Not a regular file"],
                 "output": None, "tool": None, "verification": {"coverage": "none", "locators": []}}
        manifest = self.root / "manifest.json"
        manifest.write_text(json.dumps([entry]))
        result = subprocess.run([sys.executable, str(Path(__file__).with_name("check_manifest.py")),
                                 str(manifest), "--input", "source.pipe"],
                                capture_output=True, text=True, check=False, timeout=5)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["source_statuses"], {"unsupported": 1})
        result = subprocess.run([sys.executable, str(Path(__file__).with_name("check_manifest.py")),
                                 str(self.root / "source.pipe"), "--input", "source.txt"],
                                capture_output=True, text=True, check=False, timeout=5)
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertEqual(json.loads(result.stdout)["status"], "UNAVAILABLE")

    def test_cli_refuses_conflicting_duplicate_status(self):
        manifest = self.root / "manifest.json"
        entry = json.dumps(self.entry).replace('"status": "verified"', '"status": "failed", "status": "verified"')
        manifest.write_text(f"[{entry}]")
        result = subprocess.run([sys.executable, str(Path(__file__).with_name("check_manifest.py")),
                                 str(manifest), "--input", "source.txt"],
                                capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn("duplicate JSON object key", result.stdout)

    def test_cli_reads_a_prepared_utf8_bundle_without_mutating_originals(self):
        manifest = self.root / "manifest.json"
        manifest.write_text(json.dumps({"sources": [self.entry]}))
        before = {p.name: p.read_bytes() for p in self.root.iterdir()}
        result = subprocess.run([sys.executable, str(Path(__file__).with_name("check_manifest.py")),
                                 str(manifest), "--input", "source.txt"],
                                capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["status"], "RECONCILED")
        self.assertEqual(before, {p.name: p.read_bytes() for p in self.root.iterdir()})


if __name__ == "__main__":
    unittest.main()
