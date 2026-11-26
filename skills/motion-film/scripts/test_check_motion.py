"""Planted-defect unit tests for motion-film/scripts/check_motion.py."""

import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).with_name("check_motion.py")
sys.path.insert(0, str(SCRIPT.parent))
import check_motion


def make_pam(width: int, height: int, pixels: bytes) -> bytes:
    header = (
        f"P7\nWIDTH {width}\nHEIGHT {height}\nDEPTH 3\nMAXVAL 255\nTUPLTYPE RGB\nENDHDR\n"
    ).encode("ascii")
    return header + pixels


class CheckMotionUnitTests(unittest.TestCase):
    def test_parse_freezedetect_uses_duration_line_and_supports_eof_hold(self):
        sample = (
            "[freezedetect @ 0x1] lavfi.freezedetect.freeze_start: 1.000\n"
            "[freezedetect @ 0x1] lavfi.freezedetect.freeze_duration: 1.500\n"
            "[freezedetect @ 0x1] lavfi.freezedetect.freeze_end: 2.500\n"
            "[freezedetect @ 0x1] lavfi.freezedetect.freeze_start: 8.000\n"
        )
        parsed = check_motion.parse_freezedetect(sample)
        self.assertEqual(len(parsed), 2)
        self.assertEqual(parsed[0]["duration"], 1.5)
        self.assertIsNone(parsed[1]["end"])
        holds = check_motion.parse_hold_windows(["1.0:2.5", "8.0:10.0"])
        self.assertTrue(check_motion.is_allowed_hold(parsed[1], holds, media_duration=10.0))
        self.assertFalse(check_motion.is_allowed_hold(parsed[1], holds, media_duration=None))

    def test_parse_ebur128_detects_clipping_and_handles_digital_silence(self):
        clipped = (
            "[Parsed_ebur128_0 @ 0x1] Summary:\n"
            "  Integrated loudness:\n    I:         -14.2 LUFS\n"
            "  True peak:\n    Peak:        0.3 dBFS\n"
        )
        metrics = check_motion.parse_ebur128(clipped)
        self.assertEqual(metrics["integrated_lufs"], -14.2)
        self.assertEqual(metrics["true_peak_dbtp"], 0.3)
        self.assertFalse(metrics["silent_track"])

        silent = (
            "[Parsed_ebur128_0 @ 0x1] Summary:\n"
            "  Integrated loudness:\n    I:         -inf LUFS\n"
            "  True peak:\n    Peak:      -inf dBFS\n"
        )
        silent_metrics = check_motion.parse_ebur128(silent)
        self.assertTrue(silent_metrics["silent_track"])
        self.assertIsNone(silent_metrics["true_peak_dbtp"])

    def test_pam_parser_survives_embedded_p7_bytes_in_pixel_payload(self):
        frame_a = make_pam(2, 2, b"P7\n" + bytes([10, 20, 30, 40, 50, 60, 70, 80, 90]))
        frame_b = make_pam(2, 2, bytes([1, 2, 3]) + b"P7\n" + bytes([4, 5, 6, 7, 8, 9]))
        width, height, pixels = check_motion.parse_last_pam_frame(frame_a + frame_b)
        self.assertEqual((width, height), (2, 2))
        self.assertEqual(pixels, bytes([1, 2, 3]) + b"P7\n" + bytes([4, 5, 6, 7, 8, 9]))

    def test_compare_rgb_frames_flags_exact_and_lossy_duplicate_endpoints(self):
        frame_a = (2, 2, bytes([10, 20, 30] * 4))
        frame_b = (2, 2, bytes([10, 20, 30] * 4))
        frame_lossy = (2, 2, bytes([11, 20, 30] * 4))
        frame_c = (2, 2, bytes([25, 20, 30] * 4))
        dup = check_motion.compare_rgb_frames(frame_a, frame_b)
        self.assertTrue(dup["identical_endpoints"])
        self.assertTrue(dup["duplicate_endpoints"])
        lossy = check_motion.compare_rgb_frames(frame_a, frame_lossy, max_mean_delta=1.0)
        self.assertFalse(lossy["identical_endpoints"])
        self.assertTrue(lossy["duplicate_endpoints"])
        moved = check_motion.compare_rgb_frames(frame_a, frame_c, max_mean_delta=1.0)
        self.assertFalse(moved["duplicate_endpoints"])

    def test_invalid_hold_window_and_noise_rejected(self):
        with self.assertRaises(ValueError):
            check_motion.parse_hold_windows(["5.0:2.0"])
        res = subprocess.run(
            [sys.executable, str(SCRIPT), str(SCRIPT), "--noise", "-60dB,scale=10:10"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(res.returncode, 2)

    @unittest.skipUnless(shutil.which("ffmpeg"), "ffmpeg required for live synthetic video check")
    def test_live_ffmpeg_catches_frozen_and_lossy_duplicate_loop_and_passes_moving(self):
        with tempfile.TemporaryDirectory() as tmp:
            frozen = Path(tmp) / "frozen.mp4"
            moving = Path(tmp) / "moving.mp4"
            dup_loop = Path(tmp) / "dup_loop.mp4"
            subprocess.run(
                [
                    "ffmpeg", "-v", "error", "-f", "lavfi", "-i", "color=c=blue:s=64x64:d=1.5:r=10",
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", str(frozen),
                ],
                check=True,
            )
            res_frozen = subprocess.run(
                [sys.executable, str(SCRIPT), str(frozen), "--min-freeze", "0.5", "--check-loop-seam"],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(res_frozen.returncode, 1, res_frozen.stdout + res_frozen.stderr)
            payload = json.loads(res_frozen.stdout)
            self.assertEqual(payload["checks"]["freezes"]["status"], "FAIL")
            self.assertEqual(payload["checks"]["loop_seam"]["status"], "FAIL")

            subprocess.run(
                [
                    "ffmpeg", "-v", "error", "-f", "lavfi", "-i", "testsrc2=s=64x64:d=1.5:r=10",
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", str(moving),
                ],
                check=True,
            )
            res_moving = subprocess.run(
                [sys.executable, str(SCRIPT), str(moving), "--min-freeze", "0.5", "--check-loop-seam"],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(res_moving.returncode, 0, res_moving.stdout + res_moving.stderr)
            payload_m = json.loads(res_moving.stdout)
            self.assertEqual(payload_m["checks"]["freezes"]["status"], "PASS")
            self.assertEqual(payload_m["checks"]["loop_seam"]["status"], "PASS")

            subprocess.run(
                [
                    "ffmpeg", "-v", "error", "-f", "lavfi", "-i", "testsrc2=s=128x128:d=1.5:r=10",
                    "-filter_complex",
                    "[0:v]split[a][b];[b]trim=start_frame=0:end_frame=1,setpts=PTS-STARTPTS[f0];[a][f0]concat=n=2:v=1:a=0[v]",
                    "-map", "[v]", "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", str(dup_loop),
                ],
                check=True,
            )
            res_dup = subprocess.run(
                [sys.executable, str(SCRIPT), str(dup_loop), "--skip-freezes", "--check-loop-seam"],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(res_dup.returncode, 1, res_dup.stdout + res_dup.stderr)
            payload_d = json.loads(res_dup.stdout)
            self.assertEqual(payload_d["checks"]["loop_seam"]["status"], "FAIL")
            self.assertTrue(payload_d["checks"]["loop_seam"]["duplicate_endpoints"])


if __name__ == "__main__":
    unittest.main()
