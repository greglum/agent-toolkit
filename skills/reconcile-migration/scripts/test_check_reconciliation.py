"""Planted-defect tests for migration reconciliation without raw value leakage."""

import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).with_name('check_reconciliation.py')
SECRET = 'PRIVATE_SENTINEL_never_emit'


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(''.join(json.dumps(r) + '\n' for r in rows), encoding='utf-8')


def build_clean_fixture(root: Path) -> Path:
    write_jsonl(root / 'extracts/src_items.jsonl', [
        {'key': 1, 'payload': {'name': SECRET, 'state': 'open'}},
        {'key': 2, 'payload': {'name': 'beta', 'state': 'closed'}},
    ])
    write_jsonl(root / 'extracts/tgt_items.jsonl', [
        {'key': 1, 'payload': {'state': 'open', 'name': SECRET}},
        {'key': 2, 'payload': {'state': 'closed', 'name': 'beta'}},
    ])
    manifest = {
        'source_schema_revision': '0044',
        'target_schema_revision': '0020',
        'cutoff_timestamp': '2026-11-19T12:00:00Z',
        'source_tables': ['items', 'legacy_sessions'],
        'table_mappings': {'items': 'app.items'},
        'dropped_tables': {'legacy_sessions': 'ephemeral login tokens never migrated'},
        'column_inventory': {
            'items': {
                'source_schema': 'public',
                'source_columns': ['id', 'name', 'state', 'deleted_at'],
                'copied_columns': ['id', 'name'],
                'transformed_columns': ['state'],
                'dropped_columns': {'deleted_at': 'soft-deleted rows excluded before staging'},
            }
        },
        'row_checks': [{
            'table': 'items',
            'source_extract': 'extracts/src_items.jsonl',
            'target_extract': 'extracts/tgt_items.jsonl',
            'source_row_count': 3,
            'target_row_count': 2,
            'named_drops': {'soft-deleted records excluded by target rule': 1},
            'source_cutoff': '2026-11-19T12:00:00Z',
            'target_cutoff': '2026-11-19T12:00:00Z',
        }],
    }
    manifest_path = root / 'manifest.json'
    manifest_path.write_text(json.dumps(manifest), encoding='utf-8')
    return manifest_path


class ReconciliationCheckerTests(unittest.TestCase):
    def run_cli(self, manifest_path: Path, *extra_args: str):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), str(manifest_path), *extra_args],
            text=True, capture_output=True, check=False,
        )
        self.assertNotIn(SECRET, result.stdout)
        self.assertNotIn(SECRET, result.stderr)
        payload = json.loads(result.stdout) if result.stdout.strip() else None
        return result, payload

    def test_clean_manifest_passes_and_emits_no_raw_values(self):
        with tempfile.TemporaryDirectory() as tmp:
            manifest_path = build_clean_fixture(Path(tmp))
            result, report = self.run_cli(manifest_path, '--strict-drops')
            self.assertEqual((result.returncode, result.stderr), (0, ''))
            self.assertEqual(report['status'], 'pass')
            self.assertEqual(report['tables_checked'], 1)
            self.assertEqual(report['findings'], [])

    def test_planted_defects_fail_for_each_invariant_without_leaks(self):
        cases = [
            ('unaccounted_source_table', lambda r, m: m['source_tables'].append('history')),
            ('undeclared_mapped_table', lambda r, m: m['table_mappings'].__setitem__('ghost', 'app.ghost')
             or m['column_inventory'].__setitem__('ghost', m['column_inventory']['items'])),
            ('conflicting_column_disposition', lambda r, m: m['column_inventory']['items']['copied_columns'].append('deleted_at')),
            ('unscoped_column_inventory', lambda r, m: m['column_inventory']['items'].pop('source_schema')),
            ('unaccounted_source_column', lambda r, m: m['column_inventory']['items']['source_columns'].append('notes')),
            ('catchall_drop_rule', lambda r, m: m['row_checks'][0]['named_drops'].__setitem__('other', 1)
             or m['row_checks'][0].__setitem__('source_row_count', 4)),
            ('split_cutoff_clock', lambda r, m: m['row_checks'][0].__setitem__('target_cutoff', '2026-11-19T12:00:05Z')),
            ('collapsed_duplicate_keys', lambda r, m: m['row_checks'][0].__setitem__('source_row_count', 4)
             or write_jsonl(r / 'extracts/src_items.jsonl', [
                 {'key': 1, 'payload': {'name': SECRET, 'state': 'open'}},
                 {'key': 1, 'payload': {'name': SECRET, 'state': 'duplicate'}},
                 {'key': 2, 'payload': {'name': 'beta', 'state': 'closed'}},
             ])),
            ('hash_mismatch', lambda r, m: write_jsonl(r / 'extracts/tgt_items.jsonl', [
                {'key': 1, 'payload': {'name': SECRET, 'state': 'corrupted'}},
                {'key': 2, 'payload': {'name': 'beta', 'state': 'closed'}},
            ])),
            ('missing_target_key', lambda r, m: write_jsonl(r / 'extracts/tgt_items.jsonl', [
                {'key': 2, 'payload': {'name': 'beta', 'state': 'closed'}},
            ])),
            ('extra_target_key', lambda r, m: write_jsonl(r / 'extracts/tgt_items.jsonl', [
                {'key': 1, 'payload': {'name': SECRET, 'state': 'open'}},
                {'key': 2, 'payload': {'name': 'beta', 'state': 'closed'}},
                {'key': 99, 'payload': {'name': SECRET, 'state': 'extra'}},
            ])),
            ('extract_count_mismatch', lambda r, m: write_jsonl(r / 'extracts/src_items.jsonl', [])
             or write_jsonl(r / 'extracts/tgt_items.jsonl', [])
             or m['row_checks'][0].__setitem__('source_row_count', 1000)
             or m['row_checks'][0].__setitem__('target_row_count', 1000)
             or m['row_checks'][0].__setitem__('named_drops', {})),
            ('missing_row_check', lambda r, m: m['row_checks'].clear()),
            ('unmapped_row_check', lambda r, m: m['row_checks'][0].__setitem__('table', 'typo_items')),
            ('duplicate_row_check', lambda r, m: m['row_checks'].append(copy.deepcopy(m['row_checks'][0]))),
            ('unexplained_row_delta', lambda r, m: m['row_checks'][0].__setitem__('target_row_count', 9)),
        ]
        for expected_code, mutate in cases:
            with self.subTest(defect=expected_code), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                manifest_path = build_clean_fixture(root)
                manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
                mutate(root, manifest)
                manifest_path.write_text(json.dumps(manifest), encoding='utf-8')
                result, report = self.run_cli(manifest_path)
                self.assertEqual((result.returncode, result.stderr), (1, ''))
                self.assertEqual(report['status'], 'fail')
                codes = {f['code'] for f in report['findings']}
                self.assertIn(expected_code, codes)

    def test_allow_fold_rejects_corrupt_nonfolded_key_and_count_mismatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest_path = build_clean_fixture(root)
            manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
            write_jsonl(root / 'extracts/src_items.jsonl', [
                {'key': 1, 'payload': {'name': SECRET, 'state': 'open'}},
                {'key': 1, 'payload': {'name': SECRET, 'state': 'open-2'}},
                {'key': 2, 'payload': {'name': 'beta', 'state': 'closed'}},
            ])
            manifest['row_checks'][0]['allow_fold'] = True
            manifest['row_checks'][0]['expected_folded_rows'] = 1
            manifest['row_checks'][0]['source_row_count'] = 4
            manifest_path.write_text(json.dumps(manifest), encoding='utf-8')
            ok_res, ok_rep = self.run_cli(manifest_path)
            self.assertEqual((ok_res.returncode, ok_rep['status']), (0, 'pass'))

            bad_hash = root / 'bad_hash.json'
            bad_hash.write_text(json.dumps(manifest), encoding='utf-8')
            write_jsonl(root / 'extracts/tgt_items.jsonl', [
                {'key': 1, 'payload': {'state': 'open', 'name': SECRET}},
                {'key': 2, 'payload': {'state': 'corrupted', 'name': 'beta'}},
            ])
            hash_res, hash_rep = self.run_cli(bad_hash)
            self.assertEqual(hash_res.returncode, 1)
            self.assertIn('hash_mismatch', {f['code'] for f in hash_rep['findings']})

            write_jsonl(root / 'extracts/tgt_items.jsonl', [
                {'key': 1, 'payload': {'state': 'open', 'name': SECRET}},
                {'key': 2, 'payload': {'state': 'closed', 'name': 'beta'}},
            ])
            bad_fold = copy.deepcopy(manifest)
            bad_fold['row_checks'][0]['expected_folded_rows'] = 2
            bad_fold['row_checks'][0]['source_row_count'] = 5
            bad_fold_path = root / 'bad_fold.json'
            bad_fold_path.write_text(json.dumps(bad_fold), encoding='utf-8')
            fold_res, fold_rep = self.run_cli(bad_fold_path)
            self.assertEqual(fold_res.returncode, 1)
            self.assertIn('fold_count_mismatch', {f['code'] for f in fold_rep['findings']})

            vague = copy.deepcopy(manifest)
            vague['dropped_tables']['legacy_sessions'] = 'legacy'
            manifest_path.write_text(json.dumps(vague), encoding='utf-8')
            strict_res, strict_rep = self.run_cli(manifest_path, '--strict-drops')
            self.assertEqual(strict_res.returncode, 1)
            self.assertIn('vague_drop_rule', {f['code'] for f in strict_rep['findings']})

    def test_static_only_checks_mappings_without_extracts(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest_path = build_clean_fixture(root)
            manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
            manifest['row_checks'] = []
            manifest_path.write_text(json.dumps(manifest), encoding='utf-8')

            default_res, default_rep = self.run_cli(manifest_path)
            self.assertEqual(default_res.returncode, 1)
            self.assertIn('missing_row_check', {f['code'] for f in default_rep['findings']})

            static_res, static_rep = self.run_cli(manifest_path, '--static-only')
            self.assertEqual((static_res.returncode, static_rep['status']), (0, 'pass'))

    def test_path_escape_and_bad_args_exit_two(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            outside = root / 'outside.jsonl'
            write_jsonl(outside, [{'key': 1, 'hash': 'abc'}])
            sub = root / 'bundle'
            sub.mkdir()
            manifest_path = build_clean_fixture(sub)
            manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
            manifest['row_checks'][0]['source_extract'] = '../outside.jsonl'
            manifest_path.write_text(json.dumps(manifest), encoding='utf-8')
            res, payload = self.run_cli(manifest_path)
            self.assertEqual(res.returncode, 2)
            self.assertIsNone(payload)
            self.assertIn('escapes manifest directory', res.stderr)

            missing_res, _ = self.run_cli(root / 'missing.json')
            self.assertEqual(missing_res.returncode, 2)


if __name__ == '__main__':
    unittest.main()
