"""Real decoder checks for paginated contact sheets, manifest accuracy, and error bounds."""

import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).with_name("contact_sheet.py")


@unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"), "FFmpeg/ffprobe unavailable")
class ContactSheetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory()
        cls.root = Path(cls.temporary.name)
        subprocess.run(
            [
                "ffmpeg", "-v", "error", "-n", "-f", "lavfi", "-i",
                "color=blue:size=160x90:rate=10:duration=2",
                "-c:v", "ffv1", str(cls.root / "sample.mkv"),
            ],
            check=True,
            capture_output=True,
        )
        subprocess.run(
            [
                "ffmpeg", "-v", "error", "-n", "-f", "lavfi", "-i",
                "color=red:size=1600x8:rate=4:duration=1",
                "-c:v", "ffv1", str(cls.root / "ultrawide.mkv"),
            ],
            check=True,
            capture_output=True,
        )
        subprocess.run(
            [
                "ffmpeg", "-v", "error", "-n", "-f", "lavfi", "-i",
                "sine=frequency=440:duration=0.5",
                str(cls.root / "audio-only.wav"),
            ],
            check=True,
            capture_output=True,
        )

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def invoke(self, media_name, out_name, every="1"):
        output = self.root / out_name
        result = subprocess.run(
            [
                sys.executable, "-B", str(SCRIPT),
                str(self.root / media_name), str(output), "--every", str(every),
            ],
            text=True,
            capture_output=True,
        )
        return result, output

    def test_paginated_sheets_manifest_timestamps_and_refusal_to_overwrite(self):
        result, output = self.invoke("sample.mkv", "paginated", every="0.09")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        summary = json.loads(result.stdout)
        self.assertEqual(summary["status"], "EXTRACTED")
        self.assertEqual(summary["sheets"], 2)
        self.assertEqual(summary["samples"], 20)
        self.assertTrue((output / "sheet-0001.png").is_file())
        self.assertTrue((output / "sheet-0002.png").is_file())

        manifest = json.loads((output / "manifest.json").read_text())
        self.assertEqual(len(manifest["samples"]), 20)
        self.assertEqual(manifest["samples"][0], {"sheet": "sheet-0001.png", "row": 1, "column": 1, "seconds": 0.0})
        self.assertEqual(manifest["samples"][16], {"sheet": "sheet-0002.png", "row": 1, "column": 1, "seconds": 1.6})
        self.assertAlmostEqual(manifest["samples"][-1]["seconds"], 1.9, places=5)

        before = (output / "manifest.json").read_bytes()
        rerun, _ = self.invoke("sample.mkv", "paginated", every="0.09")
        self.assertEqual(rerun.returncode, 2)
        self.assertEqual(json.loads(rerun.stdout)["status"], "UNAVAILABLE")
        self.assertEqual((output / "manifest.json").read_bytes(), before)

    def test_ultrawide_aspect_clamps_height_to_at_least_two(self):
        result, output = self.invoke("ultrawide.mkv", "ultrawide", every="0.5")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        probe = json.loads(
            subprocess.check_output(
                [
                    "ffprobe", "-v", "error", "-show_entries", "stream=width,height",
                    "-of", "json", str(output / "sheet-0001.png"),
                ],
                text=True,
            )
        )
        stream = probe["streams"][0]
        self.assertEqual(stream["height"], 28)

    def test_invalid_every_and_missing_video_stream(self):
        for index, value in enumerate(("0", "-0.5", "nan", "inf", "not-a-number")):
            with self.subTest(every=value):
                result, output = self.invoke("sample.mkv", f"bad-every-{index}", every=value)
                self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                self.assertFalse(output.exists())

        result, output = self.invoke("audio-only.wav", "no-video", every="0.5")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)["status"], "FAIL")
        self.assertFalse((output / "manifest.json").exists())
        self.assertTrue((output / "ffmpeg.log").is_file())


if __name__ == "__main__":
    unittest.main()
