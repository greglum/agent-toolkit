"""CLI contract checks for evidence, abstention, invalid data and preservation."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name('design_reference.py')
CORPUS = SCRIPT.parent.parent / 'assets' / 'design-recipes.json'


class DesignReferenceCLI(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True)

    def test_queries_and_no_match(self):
        cases = [('dense inventory table sorting', 'data-table'),
                 ('incident monitoring dashboard', 'monitoring'),
                 ('long forms validation submission', 'long-form'),
                 ('editorial article publication', 'editorial'),
                 ('ecommerce product purchase', 'commerce')]
        for query, expected in cases:
            with self.subTest(query=query):
                result = self.run_cli('search', query, '--limit', '1')
                self.assertEqual(result.returncode, 0, result.stderr)
                data = json.loads(result.stdout)
                self.assertEqual(data['results'][0]['id'], expected)
                self.assertTrue(data['results'][0]['matched_terms'])
                self.assertTrue(data['sources'])
        for query in ('quantum tokamak accelerator', 'design a web app interface', ''):
            with self.subTest(query=query):
                result = self.run_cli('search', query)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(json.loads(result.stdout)['status'], 'no-match')

    def test_invalid_corpus_fails_before_output(self):
        original = json.loads(CORPUS.read_text())
        mutations = [lambda d: d.update(schema_version=True),
                     lambda d: d['recipes'].append(d['recipes'][0]),
                     lambda d: d['recipes'][0]['sources'].append('missing'),
                     lambda d: d['recipes'][0]['palette'].update(text='#F7F9FC'),
                     lambda d: d['sources'][0].update(observed='2026-99-99')]
        with tempfile.TemporaryDirectory() as directory:
            path, output = Path(directory) / 'bad.json', Path(directory) / 'draft.md'
            for mutate in mutations:
                with self.subTest(mutation=mutate):
                    data = json.loads(json.dumps(original))
                    mutate(data)
                    path.write_text(json.dumps(data))
                    result = self.run_cli('--corpus', str(path), 'draft', 'workbench', '--output', str(output))
                    self.assertEqual(result.returncode, 2)
                    self.assertIn('design-reference:', result.stderr)
                    self.assertFalse(output.exists())

    def test_draft_boundary_and_preservation(self):
        result = self.run_cli('draft', 'workbench', '--format', 'json')
        self.assertEqual(result.returncode, 0, result.stderr)
        draft = json.loads(result.stdout)
        self.assertFalse(draft['accepted'])
        self.assertTrue(draft['mapping_required'])
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'draft.md'
            result = self.run_cli('draft', 'workbench', '--output', str(output))
            self.assertEqual(result.returncode, 0, result.stderr)
            content = output.read_bytes()
            self.assertIn(b'# Draft design brief', content)
            self.assertIn(b'Product mapping still required', content)
            result = self.run_cli('draft', 'monitoring', '--output', str(output))
            self.assertEqual(result.returncode, 2)
            self.assertEqual(output.read_bytes(), content)

    def test_contrast_values_and_unsupported_colors(self):
        for foreground, background, expected, status in [('#000', '#fff', 21.0, 0),
                ('#222222', '#222222', 1.0, 1), ('#ab6400', '#fefbe9', 4.432952188282118, 1)]:
            with self.subTest(foreground=foreground, background=background):
                result = self.run_cli('contrast', foreground, background)
                self.assertEqual(result.returncode, status, result.stderr)
                self.assertAlmostEqual(json.loads(result.stdout)['ratio'], expected, places=12)
        result = self.run_cli('contrast', '#ab6400', '#fefbe9', '--kind', 'large')
        self.assertEqual(result.returncode, 0, result.stderr)
        for unsupported in ('#1234', '#ffffff80', 'red', 'color(display-p3 1 0 0)'):
            self.assertEqual(self.run_cli('contrast', unsupported, '#fff').returncode, 2)


if __name__ == '__main__':
    unittest.main()
