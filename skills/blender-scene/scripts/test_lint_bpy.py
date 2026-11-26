"""Planted-defect unit tests for blender-scene/scripts/lint_bpy.py."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).with_name("lint_bpy.py")
sys.path.insert(0, str(SCRIPT.parent))
import lint_bpy


PORTABLE_BPY = """import bpy
from bpy_extras.anim_utils import action_get_channelbag_for_slot

def setup(mat, scene, obj, action, slot):
    nodes = mat.node_tree.nodes
    bsdf = next(n for n in nodes if n.type == "BSDF_PRINCIPLED")
    sock = bsdf.inputs.get("Emission Color") or bsdf.inputs.get("Emission")
    if sock is not None:
        sock.default_value = (1.0, 0.5, 0.2, 1.0)
    try:
        scene.render.engine = "BLENDER_EEVEE_NEXT"
    except TypeError:
        scene.render.engine = "BLENDER_EEVEE"
    try:
        bpy.ops.object.mode_set(mode="EDIT")
    finally:
        bpy.ops.object.mode_set(mode="OBJECT")
    channelbag = action_get_channelbag_for_slot(action, slot)
    curves = channelbag.fcurves
    if hasattr(action, "fcurves"):
        legacy = action.fcurves
    assert_not_equal("127.0.0.1", "0.0.0.0")
    return curves
"""


class LintBpyTests(unittest.TestCase):
    def test_portable_script_passes(self):
        report = lint_bpy.lint_source(PORTABLE_BPY)
        self.assertEqual(report["status"], "PASS", report)
        self.assertEqual(report["findings"], [])

    def test_planted_localized_node_lookup_subscript_and_get_fail(self):
        for bad in (
            'bsdf = mat.node_tree.nodes["Principled BSDF"]\n',
            'bsdf = mat.node_tree.nodes.get("Principled BSDF")\n',
        ):
            with self.subTest(bad=bad):
                report = lint_bpy.lint_source(bad)
                self.assertEqual(report["status"], "FAIL")
                self.assertTrue(any(f["rule"] == "localized-node-name" for f in report["findings"]))

    def test_planted_renamed_bsdf_socket_fails(self):
        bad = 'bsdf.inputs["Emission"].default_value = (1, 1, 1, 1)\n'
        report = lint_bpy.lint_source(bad)
        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any(f["rule"] == "renamed-bsdf-socket" for f in report["findings"]))

    def test_planted_unguarded_eevee_enum_fails_even_inside_broad_try(self):
        bad = (
            'try:\n'
            '    a = 1\n    b = 2\n    c = 3\n    d = 4\n    e = 5\n'
            '    scene.render.engine = "BLENDER_EEVEE_NEXT"\n'
            '    curves = action.fcurves\n'
            'except Exception:\n'
            '    pass\n'
        )
        report = lint_bpy.lint_source(bad)
        rules = {f["rule"] for f in report["findings"]}
        self.assertIn("hardcoded-eevee-enum", rules)
        self.assertIn("deprecated-action-fcurves", rules)

    def test_planted_blender5_fcurves_access_fails_while_channelbag_passes(self):
        bad = 'curves = action.fcurves\n'
        report = lint_bpy.lint_source(bad)
        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any(f["rule"] == "deprecated-action-fcurves" for f in report["findings"]))

        good = 'bag = action_get_channelbag_for_slot(action, slot)\ncurves = bag.fcurves\n'
        report_ok = lint_bpy.lint_source(good)
        self.assertEqual(report_ok["status"], "PASS", report_ok)

    def test_planted_mode_set_without_object_restore_and_wildcard_bind_fail(self):
        bad = (
            'try:\n'
            '    bpy.ops.object.mode_set(mode="EDIT")\n'
            'finally:\n'
            '    cleanup()\n'
            'sock.bind(("0.0.0.0", 9876))\n'
        )
        report = lint_bpy.lint_source(bad)
        rules = {f["rule"] for f in report["findings"]}
        self.assertIn("unguarded-mode-set", rules)
        self.assertIn("wildcard-bind", rules)

    def test_cli_exit_codes(self):
        with tempfile.TemporaryDirectory() as tmp:
            good = Path(tmp) / "good.py"
            good.write_text(PORTABLE_BPY, encoding="utf-8")
            res = subprocess.run([sys.executable, str(SCRIPT), str(good)], capture_output=True, text=True, check=False)
            self.assertEqual(res.returncode, 0, res.stdout + res.stderr)
            self.assertEqual(json.loads(res.stdout)["status"], "PASS")

            bad = Path(tmp) / "bad.py"
            bad.write_text("def broken(:\n", encoding="utf-8")
            res_err = subprocess.run([sys.executable, str(SCRIPT), str(bad)], capture_output=True, text=True, check=False)
            self.assertEqual(res_err.returncode, 2, res_err.stdout + res_err.stderr)


if __name__ == "__main__":
    unittest.main()
