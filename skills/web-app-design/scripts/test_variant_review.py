"""Protect packet boundaries, inert rendering and content-bound review identity."""

import base64
import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path

SCRIPT = Path(__file__).with_name("review_variants.py")
SPEC = importlib.util.spec_from_file_location("review_variants", SCRIPT)
BOARD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BOARD)
PNG = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+aL1sAAAAASUVORK5CYII=")


class ParsedBoard(HTMLParser):
    def __init__(self, rendered):
        super().__init__()
        self.payload = ""
        self.in_payload = False
        self.images = []
        self.feed(rendered)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "script":
            self.in_payload = attrs.get("id") == "review-data"
        if tag == "img":
            self.images.append(attrs)

    def handle_endtag(self, tag):
        if tag == "script":
            self.in_payload = False

    def handle_data(self, data):
        if self.in_payload:
            self.payload += data


class ReviewBoardChecks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.packet = self.root / "packet"
        self.packet.mkdir()
        (self.packet / "image.png").write_bytes(PNG)
        self.manifest = self.packet / "comparison.json"
        self.data = {"version": 1, "title": "Compare __CARDS__", "question": "Which works?",
                     "context": {"viewport": {"width": 1280, "height": 800},
                                 "theme": "light", "state": "same fixture"},
                     "variants": [{"id": "reportValidity", "label": "</script><img src=x>",
                                   "image": "image.png", "image_size": {"width": 1, "height": 1},
                                   "source_revision": "abc123"}]}

    def write(self):
        self.manifest.write_text(json.dumps(self.data))

    def test_inert_static_comparison_and_identity_bind_capture_and_source(self):
        self.write()
        rendered, original = BOARD.build(self.manifest)
        parsed = ParsedBoard(rendered)
        payload = json.loads(parsed.payload)
        self.assertEqual(len(parsed.images), 1, "hostile label introduced markup")
        self.assertEqual(parsed.images[0]["alt"], self.data["variants"][0]["label"])
        self.assertIn("<h1>Compare __CARDS__</h1>", rendered)
        self.assertEqual(payload["baseline"], "reportValidity")
        self.assertEqual(payload["variants"][0]["sha256"], hashlib.sha256(PNG).hexdigest())
        for owner, key, value in [(self.data["context"], "theme", "dark"),
                                  (self.data["context"], "state", "other fixture"),
                                  (self.data["context"]["viewport"], "width", 390),
                                  (self.data["variants"][0], "source_revision", "def456")]:
            with self.subTest(key=key):
                previous = owner[key]
                owner[key] = value
                self.write()
                self.assertNotEqual(BOARD.build(self.manifest)[1], original)
                owner[key] = previous

    def test_outside_absolute_and_symlink_paths_reject_before_output(self):
        outside = self.root / "outside.png"
        outside.write_bytes(PNG)
        (self.packet / "alias").symlink_to(self.root, target_is_directory=True)
        (self.packet / "linked.png").symlink_to(self.packet / "image.png")
        for image in ("../outside.png", str(outside), "alias/outside.png", "linked.png"):
            with self.subTest(image=image):
                self.data["variants"][0]["image"] = image
                self.write()
                with self.assertRaises(ValueError):
                    BOARD.build(self.manifest)

    def test_ambiguous_manifest_and_active_image_reject(self):
        self.write()
        raw = self.manifest.read_text().replace('"version": 1', '"version": 1, "version": 1')
        self.manifest.write_text(raw)
        with self.assertRaisesRegex(ValueError, "duplicate JSON"):
            BOARD.build(self.manifest)
        self.write()
        (self.packet / "image.png").write_text('<svg onload="alert(1)"></svg>')
        with self.assertRaisesRegex(ValueError, "active formats"):
            BOARD.build(self.manifest)

    def test_cli_refuses_overwrite_and_preserves_inputs(self):
        self.write()
        target = self.root / "review.html"
        command = [sys.executable, str(SCRIPT), str(self.manifest), str(target)]
        first = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(first.returncode, 0, first.stderr)
        before = target.read_bytes()
        second = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(second.returncode, 2)
        self.assertEqual(target.read_bytes(), before)
        self.assertEqual((self.packet / "image.png").read_bytes(), PNG)
        self.assertEqual(json.loads(self.manifest.read_text()), self.data)


if __name__ == "__main__":
    unittest.main()
