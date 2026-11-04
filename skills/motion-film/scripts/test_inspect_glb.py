"""Protect the inventory's file and resource boundaries without requiring Blender."""

import json
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest

from inspect_glb import inspect


def glb(document, extra=b""):
    data = json.dumps(document).encode()
    data += b" " * (-len(data) % 4)
    body = struct.pack("<I4s", len(data), b"JSON") + data + extra
    return struct.pack("<4sII", b"glTF", 2, len(body) + 12) + body


class GlbInventoryTests(unittest.TestCase):
    def test_cli_reports_loader_dependencies_without_loading_external_resources(self):
        document = {"asset": {"version": "2.0"},
                    "extensionsUsed": ["KHR_draco_mesh_compression"],
                    "extensionsRequired": ["KHR_draco_mesh_compression"],
                    "buffers": [{"uri": "https://invalid.example/private.bin"}],
                    "images": [{"uri": "missing.png"}, {"bufferView": 0, "mimeType": "image/png"}],
                    "meshes": [{"primitives": [{"attributes": {}, "targets": [{"POSITION": 1}]}]}],
                    "skins": [{"joints": [2, 3]}], "animations": [{"name": "Walk"}]}
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "fixture.glb"
            path.write_bytes(glb(document))
            result = subprocess.run([sys.executable, str(Path(__file__).with_name("inspect_glb.py")),
                                     str(path)], capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["status"], "INSPECTED")
        self.assertIn("NOT VALIDATED", report["scope"])
        self.assertEqual(report["extensions_required"], ["KHR_draco_mesh_compression"])
        self.assertEqual(report["external_resources"], [{"collection": "images", "index": 0},
                                                       {"collection": "buffers", "index": 0}])
        self.assertEqual(report["skins"], [{"joints": [2, 3]}])
        self.assertEqual(report["animations"], [{"name": "Walk"}])
        self.assertEqual(report["mesh_primitives"][0]["primitives"][0]["targets"], [{"POSITION": 1}])

    def test_truncated_or_misdeclared_files_cannot_produce_an_inventory(self):
        valid = glb({"asset": {"version": "2.0"}})
        chunk_overrun = struct.pack("<4sIIII", b"glTF", 2, 20, 100, 0x4E4F534A)
        for data in (b"glTF", valid[:-1], valid + b"junk", chunk_overrun):
            with self.subTest(length=len(data)), tempfile.TemporaryDirectory() as folder:
                path = Path(folder) / "broken.glb"
                path.write_bytes(data)
                with self.assertRaises(ValueError):
                    inspect(path)


if __name__ == "__main__":
    unittest.main()
