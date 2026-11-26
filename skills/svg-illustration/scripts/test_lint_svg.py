"""Planted-defect unit tests for svg-illustration/scripts/lint_svg.py."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).with_name("lint_svg.py")
sys.path.insert(0, str(SCRIPT.parent))
import lint_svg


CLEAN_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 480 360" role="img">
  <title>Bakery at dawn</title>
  <defs>
    <filter id="bakery-ink" x="-5%" y="-5%" width="110%" height="110%">
      <feTurbulence type="fractalNoise" baseFrequency="0.02" numOctaves="2" result="n"/>
    </filter>
    <linearGradient id="bakery-abc"><stop offset="0" stop-color="#faf6ef"/></linearGradient>
  </defs>
  <rect class="pp" width="480" height="360" style="fill: url(#bakery-abc); filter: url(#f00)"/>
  <path id="bakery-roof" d="M20 120 Q240 40 460 120" stroke="currentColor" fill="none"/>
  <circle cx="90" cy="80" r="18" fill="#c84b31"/>
</svg>
"""


class LintSvgTests(unittest.TestCase):
    def test_clean_svg_passes_with_prefix_palette_and_style_url_refs(self):
        report = lint_svg.lint_svg_text(
            CLEAN_SVG,
            id_prefix="bakery-",
            palette={"#faf6ef", "#1c1b18", "#c84b31"},
        )
        self.assertEqual(report["status"], "PASS", report)
        self.assertEqual(report["findings"], [])

    def test_planted_missing_viewbox_fails(self):
        bad = '<svg xmlns="http://www.w3.org/2000/svg"><rect width="10" height="10"/></svg>'
        report = lint_svg.lint_svg_text(bad)
        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any(f["rule"] == "viewbox" for f in report["findings"]))

    def test_planted_unscoped_and_duplicate_ids_fail(self):
        bad = (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">'
            '<g id="clip1"/><g id="clip1"/></svg>'
        )
        report = lint_svg.lint_svg_text(bad, id_prefix="card-")
        rules = {f["rule"] for f in report["findings"]}
        self.assertIn("id-prefix", rules)
        self.assertIn("duplicate-id", rules)

    def test_planted_raster_image_and_style_tag_fail(self):
        bad = (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">'
            '<style>.a{fill:red}</style><image href="x.png" width="10" height="10"/></svg>'
        )
        report = lint_svg.lint_svg_text(bad)
        rules = {f["rule"] for f in report["findings"]}
        self.assertIn("no-inline-style-tag", rules)
        self.assertIn("no-raster-image", rules)

    def test_planted_off_palette_hex_named_and_rgb_fail_and_invalid_hex_rejected(self):
        for bad in (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><rect fill="#ff00ff"/></svg>',
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><rect fill="magenta"/></svg>',
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><rect style="fill: rgb(255,0,255)"/></svg>',
        ):
            with self.subTest(bad=bad):
                report = lint_svg.lint_svg_text(bad, palette={"#faf6ef", "#1c1b18"})
                self.assertEqual(report["status"], "FAIL")
                self.assertTrue(any(f["rule"] == "off-palette" for f in report["findings"]))
        with self.assertRaises(ValueError):
            lint_svg.parse_palette("#12345")

    def test_planted_high_float_or_inf_turbulence_octaves_fail(self):
        for val in ("5", "2.9", "inf", "0"):
            with self.subTest(val=val):
                bad = (
                    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">'
                    f'<defs><filter id="f"><feTurbulence numOctaves="{val}"/></filter></defs></svg>'
                )
                report = lint_svg.lint_svg_text(bad)
                self.assertEqual(report["status"], "FAIL")
                self.assertTrue(any(f["rule"] == "turbulence-octaves" for f in report["findings"]))

    def test_smil_and_comment_only_reduced_motion_fail_while_real_css_guard_passes(self):
        smil_with_css = (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">'
            '<style>@media (prefers-reduced-motion: reduce) { .a { animation: none; } }</style>'
            '<circle cx="10" cy="10" r="5"><animate attributeName="cx" from="10" to="90" dur="2s"/></circle></svg>'
        )
        rep_smil = lint_svg.lint_svg_text(smil_with_css, allow_style=True)
        self.assertEqual(rep_smil["status"], "FAIL")
        self.assertTrue(any(f["rule"] == "reduced-motion" for f in rep_smil["findings"]))

        comment_only = (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">'
            '<style>@keyframes spin { to { transform: rotate(360deg); } } /* prefers-reduced-motion */</style></svg>'
        )
        rep_comment = lint_svg.lint_svg_text(comment_only, allow_style=True)
        self.assertEqual(rep_comment["status"], "FAIL")
        self.assertTrue(any(f["rule"] == "reduced-motion" for f in rep_comment["findings"]))

        valid_css = (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">'
            '<style>@keyframes spin { to { transform: rotate(360deg); } } '
            '@media (prefers-reduced-motion: reduce) { .s { animation: none; } }</style></svg>'
        )
        rep_ok = lint_svg.lint_svg_text(valid_css, allow_style=True)
        self.assertEqual(rep_ok["status"], "PASS", rep_ok)

    def test_cli_exit_codes_for_clean_and_broken_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            good = Path(tmp) / "good.svg"
            good.write_text(CLEAN_SVG, encoding="utf-8")
            res = subprocess.run(
                [sys.executable, str(SCRIPT), str(good), "--id-prefix", "bakery-", "--palette", "#faf6ef,#c84b31"],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(res.returncode, 0, res.stdout + res.stderr)
            self.assertEqual(json.loads(res.stdout)["status"], "PASS")

            broken = Path(tmp) / "bad.svg"
            broken.write_text("<svg><unclosed>", encoding="utf-8")
            res_bad = subprocess.run(
                [sys.executable, str(SCRIPT), str(broken)],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(res_bad.returncode, 2, res_bad.stdout + res_bad.stderr)


if __name__ == "__main__":
    unittest.main()
