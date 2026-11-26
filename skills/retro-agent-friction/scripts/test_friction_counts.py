"""Friction counts stay text-free and read native failure fields, using synthetic sessions."""

from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest

SCRIPTS_DIR = Path(os.environ.get('RETRO_SCRIPTS_DIR', Path(__file__).resolve().parent))
SCRIPT = SCRIPTS_DIR / 'friction_counts.py'
SECRET = 'PRIVATE_SENTINEL_never_emit'
LEAKS = ('token=hidden-value', 'https://alice:hunter2pw@git.example.com/x',
         'DATABASE_URL=postgres://admin:Pa55word@db.example/x', 'PGPASSWORD=s3cr3tpw',
         'GITHUB_TOKEN=abc123short', 'AKIAIOSFODNN7EXAMPLE', 'bob@corp.example', 'see git.example.com')


def write(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(''.join(json.dumps(row) + '\n' for row in rows), encoding='utf-8')


def make_env(home):
    return {
        'GIT_AUTHOR_NAME': 't', 'GIT_AUTHOR_EMAIL': 't',
        'GIT_COMMITTER_NAME': 't', 'GIT_COMMITTER_EMAIL': 't',
        'GIT_CONFIG_GLOBAL': '/dev/null', 'PATH': '/usr/bin:/bin',
        'HOME': str(home), 'TMPDIR': tempfile.gettempdir(),
    }


def init_repo(repo, env):
    repo.mkdir(parents=True, exist_ok=True)
    subprocess.run(['git', 'init', '-q', str(repo)], check=True, env=env)


def iso_at(offset_seconds=0):
    return (datetime.now(timezone.utc) + timedelta(seconds=offset_seconds)).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


class FrictionCountsTests(unittest.TestCase):
    def test_native_failures_are_counted_without_text_commands_or_paths(self):
        with tempfile.TemporaryDirectory() as home:
            home = Path(home).resolve()
            env = make_env(home)
            repo = home / 'repo'
            init_repo(repo, env)
            now = iso_at(0)
            base = {'sessionId': SECRET, 'cwd': str(repo), 'timestamp': now}
            command = f'gh api {SECRET}'

            def call(n, sandbox_off=False):
                return {**base, 'type': 'assistant', 'uuid': f'a{n}', 'message': {'id': f'm{n}', 'usage': {
                    'output_tokens': 10}, 'content': [{'type': 'tool_use', 'id': f't{n}', 'name': 'Bash',
                    'input': {'command': command, 'dangerouslyDisableSandbox': sandbox_off}}]}}

            def result(n, text, **extra):
                return {**base, 'type': 'user', 'uuid': f'r{n}', 'toolUseResult': {}, **extra, 'message': {
                    'content': [{'type': 'tool_result', 'tool_use_id': f't{n}', 'is_error': True, 'content': text}]}}
            write(home / '.claude/projects/p/s.jsonl', [
                call(1), result(1, f'x509: certificate signed by unknown authority {home} ' + ' '.join(LEAKS)),
                call(2), result(2, SECRET, toolDenialKind='automode-unavailable'),
                call(3, sandbox_off=True), result(3, f'Operation not permitted {SECRET}'),
                call(4), result(4, f'PreToolUse: hook blocked {SECRET}'),
                {**base, 'type': 'attachment', 'uuid': 'h', 'attachment': {
                    'type': 'hook_blocking_error', 'hookEvent': 'PostToolUse', 'blockingError': SECRET}},
                {**base, 'type': 'system', 'uuid': 's', 'subtype': 'compact_boundary'}])
            write(home / '.codex/sessions/2026/01/01/rollout-1.jsonl', [
                {'type': 'session_meta', 'timestamp': now, 'payload': {'id': 'c', 'source': 'cli', 'cwd': str(repo)}},
                {'type': 'event_msg', 'timestamp': now, 'payload': {'type': 'item_completed', 'item': {
                    'type': 'CommandExecution', 'id': 'e1', 'command': ['zsh', '-lc', SECRET], 'exit_code': 127,
                    'status': 'failed', 'duration': {'secs': 200, 'nanos': 0},
                    'aggregated_output': f'zsh: command not found: {SECRET}'}}}])
            run = subprocess.run([sys.executable, str(SCRIPT), '--repo', str(repo), '--days', '1'],
                                 text=True, capture_output=True, check=False, env=env)
            self.assertEqual(run.stderr, '')
            self.assertEqual(run.returncode, 0)
            self.assertNotIn(SECRET, run.stdout)
            self.assertNotIn(str(home), run.stdout)
            report = json.loads(run.stdout)
            events = {row['category']: row['events'] for row in report['categories']}
            for name in ('tls_failure', 'classifier_no_verdict', 'sandbox_denied', 'rerun_without_sandbox',
                         'repeated_failing_call', 'hook_blocking_error', 'hook_blocked', 'compaction',
                         'shell_alias_or_syntax', 'slow_call'):
                self.assertGreaterEqual(events.get(name, 0), 1, name)
            self.assertEqual(report['totals']['output_tokens_source_reported'], 40)
            tls = next(row for row in report['categories'] if row['category'] == 'tls_failure')
            located = subprocess.run([sys.executable, str(SCRIPT), '--repo', str(repo), '--days', '1',
                                      '--locate', tls['top_hashes'][0]['hash'], '--limit', '1'],
                                     text=True, capture_output=True, check=False, env=env)
            self.assertEqual(located.returncode, 0)
            self.assertIn('record 2\ttls_failure', located.stdout)
            self.assertIn('x509', located.stdout)
            for private in (str(home), SECRET, 'hidden-value', 'hunter2pw', 'Pa55word', 's3cr3tpw',
                            'abc123short', 'AKIAIOSFODNN7EXAMPLE', 'alice', 'git.example.com', 'bob@'):
                self.assertNotIn(private, located.stdout)

    def test_blocked_store_returns_exit_2_in_normal_and_locate_modes(self):
        """Planted-defect regression: --locate must not exit 0 silently when a session store is blocked."""
        if os.geteuid() == 0:
            self.skipTest('root ignores directory chmod 000')
        with tempfile.TemporaryDirectory() as home:
            home = Path(home).resolve()
            env = make_env(home)
            repo = home / 'repo'
            init_repo(repo, env)
            now = iso_at(0)
            base = {'sessionId': 's1', 'cwd': str(repo), 'timestamp': now}
            write(home / '.claude/projects/p/s.jsonl', [
                {**base, 'type': 'assistant', 'uuid': 'a1', 'message': {'id': 'm1', 'content': [
                    {'type': 'tool_use', 'id': 't1', 'name': 'Bash', 'input': {'command': 'git status'}}]}},
                {**base, 'type': 'user', 'uuid': 'r1', 'message': {
                    'content': [{'type': 'tool_result', 'tool_use_id': 't1', 'is_error': True,
                                 'content': 'Operation not permitted'}]}},
            ])
            blocked = home / '.codex/sessions'
            blocked.mkdir(parents=True)
            blocked.chmod(0)
            try:
                counts_run = subprocess.run(
                    [sys.executable, str(SCRIPT), '--repo', str(repo), '--days', '1', '--start-tracking'],
                    text=True, capture_output=True, check=False, env=env,
                )
                self.assertEqual(counts_run.returncode, 2)
                report = json.loads(counts_run.stdout)
                self.assertIsNone(report['coverage']['marker_advance'])
                self.assertTrue(any('codex session store' in g for g in report['coverage']['gaps']))

                sandbox_hash = report['categories'][0]['top_hashes'][0]['hash']
                locate_run = subprocess.run(
                    [sys.executable, str(SCRIPT), '--repo', str(repo), '--days', '1', '--locate', sandbox_hash],
                    text=True, capture_output=True, check=False, env=env,
                )
                self.assertEqual(locate_run.returncode, 2)
                self.assertIn('codex session store', locate_run.stderr)
            finally:
                blocked.chmod(0o700)

    def test_since_start_tracking_max_sessions_output_and_dedup(self):
        with tempfile.TemporaryDirectory() as home:
            home = Path(home).resolve()
            env = make_env(home)
            repo = home / 'repo'
            init_repo(repo, env)
            t1, t2, t3 = iso_at(-300), iso_at(-200), iso_at(-100)

            def make_session(sid, ts, call_uuid, res_uuid, text):
                base = {'sessionId': sid, 'cwd': str(repo), 'timestamp': ts}
                return [
                    {**base, 'type': 'assistant', 'uuid': call_uuid, 'message': {'id': f'm-{call_uuid}', 'content': [
                        {'type': 'tool_use', 'id': f'tu-{call_uuid}', 'name': 'Bash', 'input': {'command': 'make test'}}]}},
                    {**base, 'type': 'user', 'uuid': res_uuid, 'message': {
                        'content': [{'type': 'tool_result', 'tool_use_id': f'tu-{call_uuid}', 'is_error': True, 'content': text}]}},
                ]

            p1 = home / '.claude/projects/p/s1.jsonl'
            p2 = home / '.claude/projects/p/s2_fork.jsonl'
            p3 = home / '.claude/projects/p/s3.jsonl'
            write(p1, make_session('s1', t1, 'u1', 'r1', 'timed out'))
            write(p2, make_session('s1', t1, 'u1', 'r1', 'timed out') + make_session('s2', t2, 'u2', 'r2', 'timed out'))
            write(p3, make_session('s3', t3, 'u3', 'r3', 'timed out'))
            base_mtime = time.time()
            os.utime(p1, (base_mtime - 250, base_mtime - 250))
            os.utime(p2, (base_mtime - 150, base_mtime - 150))
            os.utime(p3, (base_mtime - 50, base_mtime - 50))

            oneoff = subprocess.run(
                [sys.executable, str(SCRIPT), '--repo', str(repo), '--days', '1'],
                text=True, capture_output=True, check=True, env=env,
            )
            oneoff_data = json.loads(oneoff.stdout)
            self.assertIsNone(oneoff_data['coverage']['marker_advance'])
            self.assertEqual(oneoff_data['categories'][0]['events'], 3)

            out_file = home / 'out' / 'counts.json'
            out_file.parent.mkdir()
            batch = subprocess.run(
                [sys.executable, str(SCRIPT), '--repo', str(repo), '--days', '1',
                 '--start-tracking', '--max-sessions', '2', '--output', str(out_file)],
                text=True, capture_output=True, check=True, env=env,
            )
            cov_only = json.loads(batch.stdout)
            self.assertNotIn('categories', cov_only)
            self.assertEqual(cov_only['coverage']['sessions_remaining_after_batch'], 1)
            self.assertIsNotNone(cov_only['coverage']['marker_advance'])
            full_out = json.loads(out_file.read_text(encoding='utf-8'))
            self.assertEqual(full_out['categories'][0]['events'], 2)

            since_run = subprocess.run(
                [sys.executable, str(SCRIPT), '--repo', str(repo), '--since', t1],
                text=True, capture_output=True, check=True, env=env,
            )
            since_data = json.loads(since_run.stdout)
            self.assertEqual(since_data['categories'][0]['events'], 2)
            self.assertEqual(since_data['coverage']['marker_advance'], t3)

    def test_numbered_records_handles_missing_file(self):
        sys.path.insert(0, str(SCRIPTS_DIR))
        from record_view import numbered_records
        self.assertEqual(list(numbered_records(Path(tempfile.gettempdir()) / 'no_such_session_xyz.jsonl')), [])

    def test_redaction_covers_flag_and_header_credentials(self):
        sys.path.insert(0, str(SCRIPTS_DIR))
        from record_view import redact
        for text, secret in (('Authorization: Bearer shortTok9', 'shortTok9'),
                             ('curl -u admin:hunter2x https://h', 'hunter2x'),
                             ('psql --password hunter2y', 'hunter2y'),
                             ('mysql -phunter2z db', 'hunter2z'),
                             ('scp f alice:hunter2q@host:/tmp', 'hunter2q'),
                             ('curl -H "Cookie: session=abc123"', 'abc123'),
                             ('sshpass -p hunter2s', 'hunter2s'),
                             ('redis-cli -a hunter2r', 'hunter2r'),
                             ('gh auth login --with-token ghp_short', 'ghp_short'),
                             ('private_key: abc', 'abc'),
                             ('PGPASSWORD hunter2w', 'hunter2w'),
                             ('export SLACK_WEBHOOK=hooks/abc', 'hooks/abc'),
                             ('-----BEGIN OPENSSH PRIVATE KEY----- b3BlbnNzaC1rZXk', 'b3BlbnNzaC1rZXk'),
                             ('{"password":"hunterj"}', 'hunterj'),
                             ('"--token" "abcdefq"', 'abcdefq'),
                             ('password is huntere', 'huntere'),
                             ('DB_PASS hunterd', 'hunterd'),
                             ('["gh","auth","--with-token","abcdefa"]', 'abcdefa'),
                             ('<password>hunterm</password>', 'hunterm'),
                             ('password: is hunterk', 'hunterk')):
            self.assertNotIn(secret, redact(text), text)
        self.assertIn('x509', redact('tls: failed to verify certificate: x509: unknown authority'))
        self.assertIn('Operation not permitted', redact('mkdir: Operation not permitted'))

    def test_stale_mtime_and_codex_external_import_do_not_inflate_friction_or_marker(self):
        with tempfile.TemporaryDirectory() as home:
            home = Path(home).resolve()
            env = make_env(home)
            repo = home / 'repo'
            init_repo(repo, env)
            old_ts = iso_at(-3 * 86400)
            now_ts = iso_at(-10)
            write(home / '.claude/projects/p/stale.jsonl', [
                {'sessionId': 's-old', 'cwd': str(repo), 'timestamp': old_ts, 'type': 'assistant',
                 'uuid': 'a1', 'message': {'id': 'm1', 'usage': {'output_tokens': 5000}, 'content': [
                     {'type': 'tool_use', 'id': 't1', 'name': 'Bash', 'input': {'command': 'git status'}}]}},
                {'sessionId': 's-old', 'cwd': str(repo), 'timestamp': old_ts, 'type': 'user',
                 'uuid': 'r1', 'message': {'content': [
                     {'type': 'tool_result', 'tool_use_id': 't1', 'is_error': True, 'content': 'timed out'}]}},
                {'type': 'cost-state', 'sessionId': 's-old', 'totalCostUSD': 2.0},
            ])
            write(home / '.codex/sessions/2026/11/20/rollout-imp.jsonl', [
                {'type': 'session_meta', 'timestamp': now_ts,
                 'payload': {'id': 'imp-1', 'source': 'vscode', 'cwd': str(repo)}},
                {'type': 'event_msg', 'timestamp': now_ts,
                 'payload': {'type': 'task_started', 'turn_id': 'external-import-turn-1'}},
                {'type': 'event_msg', 'timestamp': now_ts,
                 'payload': {'type': 'item_completed', 'item': {
                     'type': 'CommandExecution', 'id': 'e1', 'command': ['git', 'status'],
                     'exit_code': 1, 'status': 'failed', 'aggregated_output': 'timed out'}}},
            ])
            run = subprocess.run(
                [sys.executable, str(SCRIPT), '--repo', str(repo), '--days', '1', '--start-tracking'],
                text=True, capture_output=True, check=False, env=env,
            )
            self.assertEqual((run.returncode, run.stderr), (0, ''))
            report = json.loads(run.stdout)
            self.assertEqual(report['coverage']['sessions_read'], 0)
            self.assertEqual(report['coverage']['external_imports_skipped'], 1)
            self.assertEqual(report['coverage']['stale_mtime_sessions_skipped'], 1)
            self.assertEqual(report['totals']['output_tokens_source_reported'], 0)
            self.assertEqual(report['categories'], [])
            self.assertNotEqual(report['coverage']['marker_advance'], now_ts)


if __name__ == '__main__':
    unittest.main()
