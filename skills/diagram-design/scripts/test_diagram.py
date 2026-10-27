"""Run the dependency-free graph contract regressions through catalog discovery."""

import shutil
import subprocess
import unittest
from pathlib import Path


class DiagramContract(unittest.TestCase):
    def test_graph_contract(self):
        node = shutil.which("node")
        self.assertIsNotNone(node, "Node.js 18+ is required for the diagram tooling checks")
        result = subprocess.run(
            [node, "--test", str(Path(__file__).with_name("test-graph.mjs"))],
            text=True, capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
