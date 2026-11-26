#!/usr/bin/env python3
"""Unit and planted-defect tests for check_launch_hygiene.py."""

from __future__ import annotations

import contextlib
import io
import os
import pathlib
import plistlib
import sys
import tempfile
import unittest
from unittest import mock

SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import check_launch_hygiene as clh
import macho_inspect as mi

CLEAN_OTOOL_L = """Load command 8
      cmd LC_BUILD_VERSION
  platform 1
    minos 15.0
      sdk 26.5
Load command 11
      cmd LC_DYLD_CHAINED_FIXUPS
"""

CLEAN_SIZE_M = """Segment __PAGEZERO: 4294967296
Segment __TEXT: 2400000
\tSection __text: 1800000
\tSection __init_offsets: 20
\tSection __const: 420000
\tSection __cstring: 45000
\tSection __gcc_except_tab: 5200
\tSection __unwind_info: 18000
\tSection __eh_frame: 32000
Segment __DATA_CONST: 163840
\tSection __const: 999999
Segment __DATA: 16384
\tSection __thread_bss: 512
\tSection __objc_nlclslist: 16
\tSection __objc_nlcatlist: 8
"""

CLEAN_DYLD_DYLIBS = """/path/to/app [arm64]:
    -linked_dylibs:
        attributes     load path
                       /System/Library/Frameworks/CoreFoundation.framework/Versions/A/CoreFoundation
                       /System/Library/Frameworks/AppKit.framework/Versions/C/AppKit
        weak           /usr/lib/swift/libswiftCore.dylib
                       /usr/lib/libSystem.B.dylib
    -rpaths:
        @executable_path
        @executable_path/Frameworks
/path/to/app [arm64e]:
    -linked_dylibs:
        attributes     load path
                       /usr/lib/libSystem.B.dylib
"""

CLEAN_FIXUPS = """/path/to/app [arm64]:
    -fixups:
        segment      section          address     type      target
        __DATA_CONST __got            0x00240000  bind      CoreFoundation/_CFArrayCreate
        __DATA_CONST __const          0x00240008  rebase    0x00123450
/path/to/app [arm64e]:
    -fixups:
        segment      section          address     type      target
        __DATA_CONST __got            0x00240000  bind      CoreFoundation/_CFArrayCreate
"""

CLEAN_EXPORTS = """/path/to/app [arm64]:
    -exports:
        offset      symbol
"""


class CheckLaunchHygieneTests(unittest.TestCase):
    def _clean_eval(self, **overrides):
        kwargs = dict(
            exact_bytes=2_500_000,
            file_out="Mach-O 64-bit executable arm64",
            lipo_out="arm64",
            otool_l_out=CLEAN_OTOOL_L,
            size_m_out=CLEAN_SIZE_M,
            dylibs=clh.parse_dyld_dylibs(CLEAN_DYLD_DYLIBS),
            fixup_count=clh.parse_dyld_fixup_count(CLEAN_FIXUPS),
            export_count=clh.parse_dyld_export_count(CLEAN_EXPORTS),
            require_zero_exports=True,
        )
        kwargs.update(overrides)
        return clh.evaluate_hygiene(**kwargs)

    def test_segment_scoped_sections_and_single_slice_dyld_parsing(self):
        result = self._clean_eval()
        self.assertTrue(result["passed"])
        self.assertEqual(result["__const_bytes"], 420_000)
        self.assertEqual(result["objc_load_bytes"], 24)
        self.assertEqual(result["linked_dylib_count"], 4)
        self.assertEqual(result["weak_system_dylib_count"], 1)
        self.assertEqual(result["non_system_dylibs"], [])
        self.assertEqual(result["fixup_count"], 2)

        otool_big_l = """/bin/ls (architecture x86_64):
\t/usr/lib/libSystem.B.dylib (compatibility version 1.0.0)
/bin/ls (architecture arm64e):
\t/usr/lib/libSystem.B.dylib (compatibility version 1.0.0)
"""
        self.assertEqual(len(clh.parse_otool_big_l(otool_big_l)), 1)

    def test_universal_wrong_platform_and_low_minos_fail(self):
        universal = self._clean_eval(
            file_out="Mach-O universal binary with 2 architectures: [x86_64] [arm64]",
            lipo_out="x86_64 arm64",
        )
        self.assertFalse(universal["passed"])
        self.assertFalse(universal["checks"]["single_arch_arm64"])

        sim = self._clean_eval(
            otool_l_out="cmd LC_BUILD_VERSION\n  platform 7\n  minos 26.0\ncmd LC_DYLD_CHAINED_FIXUPS\n",
            expected_platform="macos",
        )
        self.assertFalse(sim["passed"])
        self.assertFalse(sim["checks"]["platform_ok"])

        old = self._clean_eval(otool_l_out="cmd LC_VERSION_MIN_MACOSX\n  version 11.0\n")
        self.assertFalse(old["passed"])
        self.assertEqual(old["minos"], "11.0")
        self.assertFalse(old["checks"]["minos_ok"])
        self.assertFalse(old["checks"]["chained_fixups"])
        self.assertTrue(mi.version_ge("15.0", "15.0.0"))

    def test_inits_unwind_exports_and_debug_stub_fail(self):
        bloated = self._clean_eval(
            size_m_out="Segment __TEXT: 4000000\n\tSection __mod_init_func: 56\n\tSection __eh_frame: 120000\n"
        )
        self.assertFalse(bloated["checks"]["static_initializers_ok"])
        self.assertFalse(bloated["checks"]["unwind_bytes_ok"])

        exports_out = "        offset      symbol\n        0x00004464  _main\n"
        self.assertEqual(clh.parse_dyld_export_count(exports_out), 1)
        exported = self._clean_eval(export_count=1, require_zero_exports=True)
        self.assertFalse(exported["checks"]["exports_ok"])

        stub = self._clean_eval(dylibs=[{"path": "@rpath/Sample.debug.dylib", "weak": False}])
        self.assertFalse(stub["checks"]["not_debug_stub"])

    def test_unavailable_reports_cleanly_without_false_pass(self):
        res = self._clean_eval(fixup_count=None, export_count=None, require_zero_exports=False)
        report = clh.format_report(res, None)
        self.assertIn("fixup_count=UNAVAILABLE", report)
        self.assertNotIn("fixup_count=UNAVAILABLE (PASS)", report)
        self.assertIn("export_count=UNAVAILABLE", report)
        self.assertNotIn("export_count=UNAVAILABLE (PASS)", report)

    def test_bundle_metadata_malformed_plist_and_ios_non_macho(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = pathlib.Path(tmpdir)
            ios_app = root / "Mobile.app"
            ios_app.mkdir()
            with (ios_app / "Info.plist").open("wb") as fh:
                plistlib.dump({"CFBundleExecutable": "Mobile"}, fh)
            (ios_app / "Mobile").write_bytes(b"\xcf\xfa\xed\xfeabc")
            (ios_app / "Assets.car").write_bytes(b"car")
            (ios_app / "Sidecar").write_bytes(b"\xcf\xfa\xed\xfexyz")
            _, info = clh.inspect_bundle_metadata(ios_app)
            self.assertEqual(info["sibling_executables"], ["Sidecar"])

            bad_app = root / "Broken.app"
            (bad_app / "Contents").mkdir(parents=True)
            (bad_app / "Contents/Info.plist").write_text("not xml", encoding="utf-8")
            with self.assertRaises(ValueError):
                clh.inspect_bundle_metadata(bad_app)

    def test_source_staleness_multi_stack_and_empty_root(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = pathlib.Path(tmpdir)
            exe = root / "app"
            exe.write_bytes(b"macho")
            os.utime(exe, (1_000_000.0, 1_000_000.0))

            stale_none, _, count = clh.check_source_staleness(exe, root)
            self.assertIsNone(stale_none)
            self.assertEqual(count, 0)

            tauri_dir = root / "apps/desktop/src"
            tauri_dir.mkdir(parents=True)
            ts = tauri_dir / "main.ts"
            ts.write_text("console.log(1);", encoding="utf-8")
            os.utime(ts, (1_000_120.0, 1_000_120.0))
            stale, delta, watched = clh.check_source_staleness(exe, root)
            self.assertTrue(stale)
            self.assertGreater(delta, 50.0)
            self.assertEqual(watched, 1)

    def test_bench_log_with_version_metadata_and_cli_exits(self):
        bench_log = "\n".join(
            [
                "env macos=26.5.2 rustc=1.95.0",
                "run=1 total_click_to_frame1_ms=520.00 external_window_visible_ms=490.00",
                "run=2 total_click_to_frame1_ms=225.00 external_window_visible_ms=210.00",
                "run=3 total_click_to_frame1_ms=235.00 external_window_visible_ms=218.00",
            ]
        )
        passing = clh.evaluate_bench_log(bench_log, budget_ms=235.0)
        self.assertTrue(passing["budget_passed"])
        report = clh.format_report(self._clean_eval(), passing)
        self.assertIn("run1_ms=520.00", report)
        self.assertIn("external_window_visible_ms=214.00", report)

        with self.assertRaises(ValueError):
            clh.evaluate_bench_log(bench_log, budget_ms=-5.0)

        with tempfile.TemporaryDirectory() as tmpdir:
            fake_bin = pathlib.Path(tmpdir) / "app"
            fake_bin.write_bytes(b"macho")
            fake_log = pathlib.Path(tmpdir) / "bench.txt"
            fake_log.write_text(bench_log, encoding="utf-8")
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(clh.main([str(pathlib.Path(tmpdir) / "missing")]), 2)
                with mock.patch.object(clh, "inspect_live_binary", return_value=self._clean_eval()):
                    self.assertEqual(clh.main([str(fake_bin), "--profile", "swift", "--bench-log", str(fake_log), "--budget-ms", "235"]), 0)
                    self.assertEqual(clh.main([str(fake_bin), "--bench-log", str(fake_log), "--budget-ms", "220"]), 1)


if __name__ == "__main__":
    unittest.main()
