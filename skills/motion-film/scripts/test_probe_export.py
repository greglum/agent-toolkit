"""Protect against a correct container hiding shortened or absent film streams."""

from copy import deepcopy
import unittest

from probe_export import inspect


class DeliveryContractTests(unittest.TestCase):
    def setUp(self):
        self.contract = dict(width=1920, height=1080, fps=30000 / 1001,
                             duration=10, require_audio=True)
        self.probe = {"format": {"duration": "10.01"}, "streams": [
            {"codec_type": "video", "width": 1920, "height": 1080,
             "avg_frame_rate": "30000/1001", "duration": "10.01", "start_time": "0"},
            {"codec_type": "audio", "duration": "10", "start_time": "0"}]}

    def test_correct_container_does_not_hide_truncated_streams(self):
        self.assertEqual(inspect(self.probe, **self.contract)["status"], "PASS")
        for index in (0, 1):
            with self.subTest(stream=index):
                probe = deepcopy(self.probe)
                probe["streams"][index]["duration"] = "7"
                self.assertEqual(inspect(probe, **self.contract)["status"], "FAIL")

    def test_missing_required_audio_is_a_failure(self):
        self.probe["streams"].pop()
        self.assertEqual(inspect(self.probe, **self.contract)["status"], "FAIL")

    def test_unknown_stream_timing_is_not_a_pass(self):
        for value in (None, "N/A", "NaN", "Infinity"):
            with self.subTest(value=value):
                self.probe["streams"][0]["duration"] = value
                self.assertEqual(inspect(self.probe, **self.contract)["status"], "UNAVAILABLE")

    def test_timestamps_can_supply_duration_without_container_fallback(self):
        stream = self.probe["streams"][0]
        del stream["duration"]
        stream.update(duration_ts=300000, time_base="1/30000")
        self.assertEqual(inspect(self.probe, **self.contract)["status"], "PASS")

    def test_rate_change_and_audio_offset_are_not_valid_delivery(self):
        for index, field, value in ((0, "avg_frame_rate", "15/1"), (1, "start_time", "0.5")):
            with self.subTest(field=field):
                probe = deepcopy(self.probe)
                probe["streams"][index][field] = value
                self.assertEqual(inspect(probe, **self.contract)["status"], "FAIL")


if __name__ == "__main__":
    unittest.main()
