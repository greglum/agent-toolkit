"""A pixel gate must not hide small changes or confuse color and area budgets."""

import unittest

from compare_frames import compare


class PixelContractTests(unittest.TestCase):
    def test_single_channel_and_alpha_changes_fail_exact_comparison(self):
        expected = (2, 1, bytes([10, 20, 30, 255, 40, 50, 60, 0]))
        for index in (0, 7):
            with self.subTest(channel=index):
                changed = bytearray(expected[2])
                changed[index] -= 1 if changed[index] else -1
                report = compare(expected, (2, 1, bytes(changed)))
                self.assertEqual((report["status"], report["different_pixels"]), ("FAIL", 1))

    def test_color_threshold_and_pixel_budget_are_separate(self):
        expected = (2, 1, bytes([0, 0, 0, 255, 0, 0, 0, 255]))
        actual = (2, 1, bytes([2, 0, 0, 255, 3, 0, 0, 255]))
        for channel, count, status in [(2, 0, "FAIL"), (2, 1, "PASS"), (3, 0, "PASS")]:
            with self.subTest(channel=channel, count=count):
                report = compare(expected, actual, max_channel_delta=channel,
                                 max_different_pixels=count)
                self.assertEqual(report["status"], status)

    def test_equal_pixel_count_does_not_hide_different_dimensions(self):
        pixels = bytes([0, 0, 0, 255] * 2)
        self.assertEqual(compare((2, 1, pixels), (1, 2, pixels))["status"], "FAIL")


if __name__ == "__main__":
    unittest.main()
