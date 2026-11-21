"""Antigravity friction counting, queue reset, deduplication, and redaction tests."""

from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
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


class AntigravityFrictionTests(unittest.TestCase):
    def test_antigravity_brain_friction_counts_and_locate_redaction(self):
        with tempfile.TemporaryDirectory() as home:
            home = Path(home).resolve()
            env = make_env(home)
            repo = home / 'repo'
            init_repo(repo, env)
            ag = home / '.gemini' / 'antigravity'
            (ag / 'brain').mkdir(parents=True)
            db = ag / 'conversation_summaries.db'
            conn = sqlite3.connect(db)
            conn.execute(
                'CREATE TABLE conversation_summaries ('
                'conversation_id TEXT PRIMARY KEY, workspace_uris TEXT, '
                'parent_conversation_id TEXT, nesting_depth INTEGER)'
            )
            conn.execute(
                'INSERT INTO conversation_summaries VALUES (?, ?, ?, ?)',
                ('cid-1', json.dumps([repo.as_uri()]), '', 0),
            )
            conn.commit()
            conn.close()

            now = iso_at(-30)
            later = iso_at(-5)
            rows = [
                {'step_index': 0, 'source': 'USER_EXPLICIT', 'type': 'USER_INPUT', 'status': 'DONE',
                 'created_at': now, 'content': '<USER_REQUEST>Check</USER_REQUEST>'},
                {'step_index': 1, 'source': 'MODEL', 'type': 'PLANNER_RESPONSE', 'status': 'DONE',
                 'created_at': now, 'output_tokens': 55, 'tool_calls': [
                     {'name': 'run_command', 'args': {'CommandLine': json.dumps(f'gmail --version {SECRET}')}},
                     {'name': 'edit_file', 'args': {'Path': json.dumps(str(repo / 'a.py'))}},
                     {'name': 'run_command', 'args': {'CommandLine': json.dumps('make check')}},
                     {'name': 'run_command', 'args': {'CommandLine': json.dumps('pytest -q')}},
                 ]},
                {'step_index': 2, 'source': 'MODEL', 'type': 'GENERIC', 'status': 'DONE', 'created_at': now,
                 'content': (
                     f'Created At: {now}\nCompleted At: {now}\n'
                     'Command exited with code 127.\n\nCommand output:\n'
                     f'zsh:1: no such file or directory: {home}/bin/gmail ' + ' '.join(LEAKS)
                 )},
                {'step_index': 3, 'source': 'MODEL', 'type': 'GENERIC', 'status': 'ERROR', 'created_at': now,
                 'error': 'target content not found',
                 'content': f'Created At: {now}\nCompleted At: {now}\nEncountered error in step execution: target content not found in the file'},
                {'step_index': 4, 'source': 'MODEL', 'type': 'GENERIC', 'status': 'DONE', 'created_at': now,
                 'content': (
                     f'Created At: {now}\nCompleted At: {now}\n'
                     "The tool's output was truncated due to being too long. "
                     f'You can find the full output in a file at file://{home}/out.txt\nCommand exited with code 0.'
                 )},
                {'step_index': 5, 'source': 'MODEL', 'type': 'GENERIC', 'status': 'RUNNING', 'created_at': now,
                 'content': f'Created At: {now}\nTool is running as a background task with task id: cid-1/task-5'},
                {'step_index': 6, 'source': 'SYSTEM', 'type': 'CHECKPOINT', 'status': 'DONE',
                 'created_at': now, 'content': '# Resuming from a compaction'},
                {'step_index': 7, 'source': 'SYSTEM', 'type': 'SYSTEM_MESSAGE', 'status': 'DONE',
                 'created_at': later,
                 'content': (
                     'The following is a <SYSTEM_MESSAGE>\n<SYSTEM_MESSAGE>\n'
                     'Task id "cid-1/task-5" finished with result:\nCommand exited with code 2.\n\nmake: *** [check] Error 1'
                 )},
            ]
            write(ag / 'brain/cid-1/.system_generated/logs/transcript.jsonl', rows)

            run = subprocess.run([sys.executable, str(SCRIPT), '--repo', str(repo), '--days', '1'],
                                 text=True, capture_output=True, check=False, env=env)
            self.assertEqual((run.returncode, run.stderr), (0, ''))
            self.assertNotIn(SECRET, run.stdout)
            self.assertNotIn(str(home), run.stdout)
            report = json.loads(run.stdout)
            events = {row['category']: row['events'] for row in report['categories']}
            for name in ('shell_alias_or_syntax', 'tool_input_error', 'output_too_large', 'compaction', 'command_failed'):
                self.assertGreaterEqual(events.get(name, 0), 1, name)
            self.assertEqual(report['totals']['output_tokens_source_reported'], 55)

            sh_row = next(row for row in report['categories'] if row['category'] == 'shell_alias_or_syntax')
            located = subprocess.run([sys.executable, str(SCRIPT), '--repo', str(repo), '--days', '1',
                                      '--locate', sh_row['top_hashes'][0]['hash'], '--limit', '1'],
                                     text=True, capture_output=True, check=False, env=env)
            self.assertEqual(located.returncode, 0)
            self.assertIn('shell_alias_or_syntax', located.stdout)
            for private in (str(home), 'hidden-value', 'hunter2pw', 'Pa55word', 's3cr3tpw', 'AKIAIOSFODNN7EXAMPLE'):
                self.assertNotIn(private, located.stdout)

    def test_antigravity_ignores_stdout_exit_codes_and_resets_queue_per_planner_turn(self):
        with tempfile.TemporaryDirectory() as home:
            home = Path(home).resolve()
            env = make_env(home)
            repo = home / 'repo'
            init_repo(repo, env)
            ag = home / '.gemini' / 'antigravity'
            (ag / 'brain').mkdir(parents=True)
            db = ag / 'conversation_summaries.db'
            conn = sqlite3.connect(db)
            conn.execute(
                'CREATE TABLE conversation_summaries ('
                'conversation_id TEXT PRIMARY KEY, workspace_uris TEXT, '
                'parent_conversation_id TEXT, nesting_depth INTEGER)'
            )
            conn.execute(
                'INSERT INTO conversation_summaries VALUES (?, ?, ?, ?)',
                ('cid-q', json.dumps([repo.as_uri()]), '', 0),
            )
            conn.execute(
                'INSERT INTO conversation_summaries VALUES (?, ?, ?, ?)',
                ('cid-q-fork', json.dumps([repo.as_uri()]), '', 0),
            )
            conn.commit()
            conn.close()

            now = iso_at(-20)
            shared_rows = [
                {'step_index': 0, 'source': 'USER_EXPLICIT', 'type': 'USER_INPUT', 'status': 'DONE',
                 'created_at': now, 'content': '<USER_REQUEST>Run</USER_REQUEST>'},
                {'step_index': 1, 'source': 'MODEL', 'type': 'PLANNER_RESPONSE', 'status': 'DONE',
                 'created_at': now, 'tool_calls': [
                     {'name': 'run_command', 'args': {'CommandLine': json.dumps('git status')}},
                     {'name': 'read_file', 'args': {'Path': json.dumps(str(repo / 'log.txt'))}},
                 ]},
                {'step_index': 2, 'source': 'MODEL', 'type': 'GENERIC', 'status': 'DONE', 'created_at': now,
                 'content': (
                     f'Created At: {now}\nCompleted At: {now}\nCommand exited with code 0.\n\n'
                     'Command output:\nCommand exited with code 2.'
                 )},
                {'step_index': 3, 'source': 'MODEL', 'type': 'PLANNER_RESPONSE', 'status': 'DONE',
                 'created_at': now, 'tool_calls': [
                     {'name': 'run_command', 'args': {'CommandLine': json.dumps('pytest -q')}},
                 ]},
                {'step_index': 4, 'source': 'MODEL', 'type': 'GENERIC', 'status': 'DONE', 'created_at': now,
                 'content': (
                     f'Created At: {now}\nCompleted At: {now}\nCommand exited with code 1.\n\n'
                     'Command output:\n1 failed'
                 )},
                {'step_index': 5, 'source': 'MODEL', 'type': 'PLANNER_RESPONSE', 'status': 'DONE',
                 'created_at': now, 'tool_calls': [
                     {'name': 'read_file', 'args': {'Path': json.dumps(str(repo / 'test.py'))}},
                 ]},
                {'step_index': 6, 'source': 'MODEL', 'type': 'GENERIC', 'status': 'DONE', 'created_at': now,
                 'content': f'Created At: {now}\nCompleted At: {now}\nShowing lines 1-2 of 2\n1: Command exited with code 127.'},
            ]
            write(ag / 'brain/cid-q/.system_generated/logs/transcript.jsonl', shared_rows)
            write(ag / 'brain/cid-q-fork/.system_generated/logs/transcript.jsonl', shared_rows)

            run = subprocess.run([sys.executable, str(SCRIPT), '--repo', str(repo), '--days', '1'],
                                 text=True, capture_output=True, check=False, env=env)
            self.assertEqual((run.returncode, run.stderr), (0, ''))
            report = json.loads(run.stdout)
            self.assertEqual(len(report['categories']), 1)
            row = report['categories'][0]
            self.assertEqual((row['category'], row['events'], row['sessions']), ('command_failed', 1, 1))
            self.assertEqual(row['programs'], {'pytest': 1})

    def test_module_and_typecheck_errors_do_not_misclassify_and_locate_skips_wrappers(self):
        with tempfile.TemporaryDirectory() as home:
            home = Path(home).resolve()
            env = make_env(home)
            repo = home / 'repo'
            init_repo(repo, env)
            ag = home / '.gemini' / 'antigravity'
            (ag / 'brain').mkdir(parents=True)
            db = ag / 'conversation_summaries.db'
            conn = sqlite3.connect(db)
            conn.execute(
                'CREATE TABLE conversation_summaries ('
                'conversation_id TEXT PRIMARY KEY, workspace_uris TEXT, '
                'parent_conversation_id TEXT, nesting_depth INTEGER)'
            )
            conn.execute(
                'INSERT INTO conversation_summaries VALUES (?, ?, ?, ?)',
                ('cid-m', json.dumps([repo.as_uri()]), '', 0),
            )
            conn.commit()
            conn.close()

            now = iso_at(-15)
            later = iso_at(-5)
            write(ag / 'brain/cid-m/.system_generated/logs/transcript.jsonl', [
                {'step_index': 0, 'source': 'USER_EXPLICIT', 'type': 'USER_INPUT', 'status': 'DONE',
                 'created_at': now, 'content': '<USER_REQUEST>Run</USER_REQUEST>'},
                {'step_index': 1, 'source': 'MODEL', 'type': 'PLANNER_RESPONSE', 'status': 'DONE',
                 'created_at': now, 'tool_calls': [
                     {'name': 'run_command', 'args': {'CommandLine': json.dumps('python3 -c "import boto3"')}},
                     {'name': 'run_command', 'args': {'CommandLine': json.dumps('mypy app.py')}},
                     {'name': 'run_command', 'args': {'CommandLine': json.dumps('make ci')}},
                     {'name': 'run_command', 'args': {'CommandLine': json.dumps('curl -s https://example.com')}},
                 ]},
                {'step_index': 2, 'source': 'MODEL', 'type': 'GENERIC', 'status': 'DONE', 'created_at': now,
                 'content': (
                     f'Created At: {now}\nCompleted At: {now}\nCommand exited with code 1.\n\n'
                     "Command output:\nModuleNotFoundError: No module named 'boto3'\n"
                     'token=secretvalue\nfinished with result: trailing'
                 )},
                {'step_index': 3, 'source': 'MODEL', 'type': 'GENERIC', 'status': 'DONE', 'created_at': now,
                 'content': (
                     f'Created At: {now}\nCompleted At: {now}\n'
                     "The tool's output was truncated due to being too long. You can find the full output in a file at file:///x.\n\n"
                     'Here is a preview with the middle of the output truncated:\n'
                     f'Created At: {now}\nCompleted At: {now}\nCommand exited with code 1.\n\n'
                     'Command output:\nInstalled types-pyOpenSSL\nhandler.py:55: error: No overload variant'
                 )},
                {'step_index': 4, 'source': 'MODEL', 'type': 'GENERIC', 'status': 'RUNNING', 'created_at': now,
                 'content': f'Created At: {now}\nTool is running as a background task with task id: cid-m/task-4'},
                {'step_index': 5, 'source': 'MODEL', 'type': 'GENERIC', 'status': 'DONE', 'created_at': now,
                 'content': (
                     f'Created At: {now}\nCompleted At: {now}\nCommand exited with code 35.\n\n'
                     'Command output:\ncurl: (35) LibreSSL SSL_connect: SSL_ERROR_SYSCALL'
                 )},
                {'step_index': 6, 'source': 'SYSTEM', 'type': 'SYSTEM_MESSAGE', 'status': 'DONE', 'created_at': later,
                 'content': (
                     'The following is a <SYSTEM_MESSAGE>\n<SYSTEM_MESSAGE>\n'
                     '[Message] timestamp=2026-11-21T20:30:06Z sender=cid-m/task-4 priority=MESSAGE_PRIORITY_HIGH '
                     'content=Task id "cid-m/task-4" finished with result:\nCommand exited with code 2.\n\nmake: *** [ci] Error 2'
                 )},
            ])

            run = subprocess.run([sys.executable, str(SCRIPT), '--repo', str(repo), '--days', '1'],
                                 text=True, capture_output=True, check=False, env=env)
            self.assertEqual((run.returncode, run.stderr), (0, ''))
            report = json.loads(run.stdout)
            events = {row['category']: row['events'] for row in report['categories']}
            self.assertEqual(events.get('network_failure', 0), 0)
            self.assertEqual(events.get('tls_failure', 0), 1)
            self.assertEqual(events.get('command_failed', 0), 3)

            cf_row = next(row for row in report['categories'] if row['category'] == 'command_failed')
            for h in cf_row['top_hashes']:
                loc = subprocess.run([sys.executable, str(SCRIPT), '--repo', str(repo), '--days', '1', '--locate', h['hash']],
                                     text=True, capture_output=True, check=True, env=env)
                self.assertIn('Command exited with code', loc.stdout)
                self.assertNotIn('truncated due to being too long', loc.stdout)
                self.assertNotIn('secretvalue', loc.stdout)


if __name__ == '__main__':
    unittest.main()
