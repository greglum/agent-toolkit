"""Real decoder checks for comparison evidence and failed extraction boundaries."""

import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).with_name("pair_event_frames.py")


@unittest.skipUnless(shutil.which("ffmpeg"), "FFmpeg unavailable")
class ComparisonTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory()
        cls.root = Path(cls.temporary.name)
        for name, fps, color in (("reference", 10, "red"), ("draft", 30, "blue")):
            subprocess.run(["ffmpeg", "-v", "error", "-n", "-f", "lavfi", "-i",
                            f"color={color}:size=120x120:rate={fps}:duration=1",
                            "-vf", "setsar=2", "-c:v", "ffv1", str(cls.root / f"{name}.mkv")],
                           check=True, capture_output=True)

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def invoke(self, name, seconds):
        pairs = self.root / f"{name}.json"
        pairs.write_text(json.dumps([dict(event="landing", reference_seconds=seconds,
                                         draft_seconds=seconds)]))
        output = self.root / name
        result = subprocess.run([sys.executable, str(SCRIPT), str(self.root / "reference.mkv"),
                                 str(self.root / "draft.mkv"), str(pairs), str(output)],
                                text=True, capture_output=True)
        return result, output

    def test_decoded_times_layout_and_refusal_to_overwrite(self):
        result, output = self.invoke("valid", 0.15)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        manifest = json.loads((output / "manifest.json").read_text())
        sample = manifest["samples"][0]
        self.assertEqual(manifest["status"], "EXTRACTED")
        self.assertAlmostEqual(sample["reference"]["decoded_seconds"], 0.2, places=5)
        self.assertAlmostEqual(sample["draft"]["decoded_seconds"], 0.167, places=5)
        # Non-square input pixels describe a 2:1 picture, centered without distortion.
        raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(output / sample["image"]),
                              "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                             capture_output=True, check=True).stdout
        self.assertEqual(len(raw), 720 * 360 * 3)
        pixel = lambda x, y: raw[(y * 720 + x) * 3:(y * 720 + x) * 3 + 3]
        self.assertGreater(pixel(180, 100)[0], 200)
        self.assertGreater(pixel(540, 100)[2], 200)
        self.assertEqual(pixel(180, 50), bytes(3))
        before = (output / "manifest.json").read_bytes()
        result, _ = self.invoke("valid", 0.15)
        self.assertEqual(result.returncode, 2)
        self.assertEqual((output / "manifest.json").read_bytes(), before)

    def test_missing_frame_never_creates_success_manifest(self):
        result, output = self.invoke("past-end", 10)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)["status"], "FAIL")
        self.assertFalse((output / "manifest.json").exists())
        self.assertTrue((output / "pair-001-reference.log").exists())

    def test_invalid_times_do_not_start_extraction(self):
        for index, value in enumerate((True, -1, float("nan"), float("inf"), "0.2")):
            with self.subTest(value=value):
                result, output = self.invoke(f"invalid-{index}", value)
                self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
