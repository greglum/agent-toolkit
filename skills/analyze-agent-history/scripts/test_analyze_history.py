"""Public CLI boundaries using synthetic exports only."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).with_name('analyze_history.py')
FIXTURES = Path(__file__).with_name('fixtures')


class HistoryCliTests(unittest.TestCase):
    def invoke(self, *paths):
        result = subprocess.run([sys.executable, str(SCRIPT), *map(str, paths)],
                                text=True, capture_output=True, check=False)
        self.assertEqual(result.stderr, '')
        return result, json.loads(result.stdout)

    def write(self, directory, name, rows):
        path = Path(directory) / name
        path.write_text(''.join(json.dumps(row) + '\n' for row in rows))
        return path

    def test_native_formats_exclude_machine_and_duplicate_views(self):
        result, report = self.invoke(FIXTURES / 'codex.jsonl', FIXTURES / 'copilot.jsonl')
        self.assertEqual(result.returncode, 0)
        self.assertEqual(report['totals']['eligible_messages'], 2)
        self.assertEqual(report['distinct_eligible_sessions'], 2)
        categories = {row['category']: row for row in report['candidate_categories']}
        self.assertEqual(categories['preservation_request']['messages'], 1)
        self.assertEqual(categories['repeated_request']['distinct_sessions'], 1)
        self.assertEqual(report['totals']['excluded_messages'], 3)
        self.assertNotIn('synthetic-', result.stdout)

    def test_child_inherited_and_harness_envelopes_are_not_human_incidents(self):
        with tempfile.TemporaryDirectory() as directory:
            paths = []
            for n, extra in enumerate(({'source': {'subagent': {'thread_spawn': {}}}},
                                       {'source': 'cli', 'forked_from_id': 'parent'},
                                       {'source': 'exec'}, {'source': 'cli'})):
                paths.append(self.write(directory, str(n), [
                    {'type': 'session_meta', 'payload': {'id': str(n), **extra}},
                    {'type': 'event_msg', 'timestamp': '2026-10-30T00:00:01Z',
                     'payload': {'type': 'user_message',
                     'message': '# AGENTS.md instructions\nPreserve the existing files.'}},
                ]))
            result, report = self.invoke(*paths)
            self.assertEqual(result.returncode, 0)
            self.assertEqual(report['distinct_eligible_sessions'], 0)
            self.assertEqual(report['totals']['excluded_envelopes'], 1)
            self.assertTrue(all(row['messages'] == 0 for row in report['candidate_categories']))

    def test_repeated_exports_do_not_inflate_distinct_incidents(self):
        with tempfile.TemporaryDirectory() as directory:
            first = FIXTURES / 'copilot.jsonl'
            copy = Path(directory) / 'copy.jsonl'
            copy.write_bytes(first.read_bytes())
            extended = Path(directory) / 'extended.jsonl'
            extended.write_bytes(first.read_bytes() + b'{"type":"session.idle","data":{}}\n')
            result, report = self.invoke(first, copy, extended)
            self.assertEqual(result.returncode, 0)
            self.assertEqual(report['totals']['eligible_messages'], 1)
            self.assertEqual(report['distinct_eligible_sessions'], 1)
            self.assertEqual(report['totals']['duplicate_exports'], 1)
            self.assertEqual(report['totals']['duplicate_messages'], 1)

    def test_conflicting_versions_do_not_masquerade_as_distinct_messages(self):
        with tempfile.TemporaryDirectory() as directory:
            rows = [json.loads(line) for line in (FIXTURES / 'copilot.jsonl').read_text().splitlines()]
            first = self.write(directory, 'first', rows)
            rows[1]['data']['content'] = 'Preserve the existing files.'
            second = self.write(directory, 'second', rows)
            result, report = self.invoke(first, second)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(report['totals']['eligible_messages'], 1)
            self.assertEqual(report['totals']['conflicting_message_versions'], 1)
            self.assertEqual(report['inputs'][1]['status'], 'conflicting_message_versions')

    def test_partial_unsupported_and_unreadable_inputs_report_no_private_strings(self):
        secret = 'PRIVATE_SENTINEL_never_emit'
        with tempfile.TemporaryDirectory() as directory:
            malformed = Path(directory) / (secret + '.jsonl')
            malformed.write_bytes((FIXTURES / 'codex.jsonl').read_bytes() +
                                  ('{"' + secret + '\n').encode())
            unknown = self.write(directory, 'unknown', [{'type': secret}])
            result, report = self.invoke(malformed, unknown, Path(directory) / secret)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(report['status'], 'partial')
            self.assertNotIn(secret, result.stdout)
            self.assertEqual([item['status'] for item in report['inputs']],
                             ['partial', 'unsupported_format', 'unreadable_input'])

    def test_quoted_examples_do_not_become_candidates_and_unknown_provenance_stays_partial(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self.write(directory, 'quotes', [
                {'type': 'session.start', 'data': {'sessionId': 'one', 'version': 1}},
                {'id': 'one', 'type': 'user.message', 'data': {
                    'content': '> I already asked\n```text\nPreserve the existing files\n```\nNormal request.'}},
            ])
            result, report = self.invoke(path)
            self.assertEqual(result.returncode, 0)
            self.assertTrue(all(row['messages'] == 0 for row in report['candidate_categories']))
            path = self.write(directory, 'unknown-source', [
                {'type': 'session_meta', 'payload': {'id': 'unknown'}},
                {'type': 'event_msg', 'payload': {'type': 'user_message', 'message': 'I already asked'}},
            ])
            result, report = self.invoke(path)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(report['distinct_eligible_sessions'], 0)

    def test_ambiguous_json_and_unidentified_events_cannot_inflate_candidates(self):
        with tempfile.TemporaryDirectory() as directory:
            ambiguous = Path(directory) / 'ambiguous'
            ambiguous.write_text(
                '{"type":"session_meta","payload":{"id":"one","source":"exec","source":"cli"}}\n'
                '{"type":"event_msg","timestamp":"2026-10-30T00:00:00Z",'
                '"payload":{"type":"user_message","message":"I already asked"}}\n')
            result, report = self.invoke(ambiguous)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(report['totals'].get('eligible_messages', 0), 0)
            untimed = self.write(directory, 'untimed', [
                {'type': 'session_meta', 'payload': {'id': 'one', 'source': 'cli'}},
                {'type': 'event_msg', 'payload': {'type': 'user_message', 'message': 'I already asked'}},
            ])
            result, report = self.invoke(untimed)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(report['totals'].get('eligible_messages', 0), 0)
            self.assertEqual(report['totals']['malformed_records'], 1)

    def test_oversized_record_stops_without_traceback_or_content(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'large'
            path.write_text('X' * (1024 * 1024 + 1))
            result, report = self.invoke(path)
            self.assertEqual(result.returncode, 2)
            self.assertEqual(report['inputs'][0]['status'], 'record_limit')


if __name__ == '__main__':
    unittest.main()
