"""Repository session discovery CLI boundaries using synthetic stores only."""

from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import time
import unittest

SCRIPT = Path(__file__).with_name('analyze_history.py')


def iso_at(offset_seconds=0):
    return (datetime.now(timezone.utc) + timedelta(seconds=offset_seconds)).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


class RepoDiscoveryTests(unittest.TestCase):
    def git_env(self):
        return {
            'GIT_AUTHOR_NAME': 't',
            'GIT_AUTHOR_EMAIL': 't',
            'GIT_COMMITTER_NAME': 't',
            'GIT_COMMITTER_EMAIL': 't',
            'GIT_CONFIG_GLOBAL': '/dev/null',
            'PATH': '/usr/bin:/bin',
            'TMPDIR': tempfile.gettempdir(),
        }

    def init_repo(self, path, commit=False):
        env = self.git_env()
        path.mkdir(parents=True, exist_ok=True)
        subprocess.run(['git', 'init', '-q', str(path)], check=True, env=env)
        if commit:
            subprocess.run(['git', '-C', str(path), 'commit', '-q', '--allow-empty', '-m', 'x'],
                           check=True, env=env)

    def run_repo(self, repo, home):
        env = {**self.git_env(), 'HOME': str(home)}
        return subprocess.run([sys.executable, str(SCRIPT), '--repo', str(repo), '--days', '1'],
                              text=True, capture_output=True, check=False, env=env)

    def write_nested(self, path, rows):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(''.join(json.dumps(row) + '\n' for row in rows))

    def test_repo_mode_matches_worktrees_not_lookalikes_and_keeps_only_typed_prompts(self):
        secret = 'PRIVATE_SENTINEL_never_emit'
        with tempfile.TemporaryDirectory() as home:
            home = Path(home).resolve()
            git = self.git_env()
            repo, twin, linked = home / 'repo', home / 'repo-bare', home / 'linked'
            sibling = home / 'sibling'
            for folder in (repo, twin, sibling):
                self.init_repo(folder, commit=True)
            gone, nested = home / 'wts' / 'gone', repo / 'vendor' / 'other'
            for worktree in (linked, gone):
                subprocess.run(['git', '-C', str(repo), 'worktree', 'add', '-q', str(worktree)], check=True, env=git)
            self.init_repo(nested)
            origin = 'ssh://git@github.com/example/repo.git'
            subprocess.run(['git', '-C', str(repo), 'remote', 'add', 'origin', origin], check=True, env=git)
            clone, locked = home / 'clone', home / 'locked'
            subprocess.run(['git', 'clone', '-q', str(repo), str(clone)], check=True, env=git)
            subprocess.run(['git', '-C', str(clone), 'remote', 'set-url', 'origin', origin], check=True, env=git)
            (locked / 'work').mkdir(parents=True)

            now_iso = iso_at(-30)

            def claude(cwd, rows):
                base = {'sessionId': cwd.name + secret, 'cwd': str(cwd), 'userType': 'external',
                        'timestamp': now_iso}
                return [{**base, 'type': 'user', 'uuid': f'{cwd.name}-{n}', **row} for n, row in enumerate(rows)]
            cue = {'message': {'role': 'user', 'content': 'I already asked ' + secret}}
            sessions = {
                'p1/a.jsonl': claude(linked, [cue, {**cue, 'isMeta': True}, {**cue, 'turnOrigin': 'peer'},
                                              {**cue, 'origin': {'kind': 'task-notification'}},
                                              {**cue, 'promptSource': 'system'}, {**cue, 'isCompactSummary': True},
                                              {'message': {'content': [{'type': 'tool_result', 'content': 'I already asked'}]}},
                                              {'message': {'content': [{'type': 'text', 'text': '<command-name>/x I already asked'}]}}]),
                'p1/fork.jsonl': claude(linked, [cue]),
                'p2/b.jsonl': claude(gone / 'x', [{'message': {'content': 'Normal request.'}}]),
                'p4/d.jsonl': claude(nested / 'sub', [cue]),
                'p5/e.jsonl': claude(sibling / 'src', [cue]),
                'p3/c.jsonl': claude(twin, [cue]),
                'p6/f.jsonl': claude(clone, [{'message': {'content': 'Normal request.'}}]),
                'p7/g.jsonl': claude(locked / 'work', [cue]),
                'p1/a/subagents/agent-1.jsonl': claude(linked, [{**cue, 'isSidechain': True}]),
            }
            sessions['p1/fork.jsonl'][0]['sessionId'] = 'fork'
            for name, rows in sessions.items():
                self.write_nested(home / '.claude/projects' / name, rows)
            shutil.rmtree(gone)
            shutil.rmtree(nested)
            shutil.rmtree(sibling)
            self.write_nested(home / '.codex/sessions/2026/10/30/rollout-1.jsonl', [
                {'type': 'session_meta', 'payload': {'id': 'codex-1', 'source': 'cli', 'cwd': str(linked)}},
                {'type': 'event_msg', 'payload': {'type': 'item_completed', 'item': {
                    'type': 'UserMessage', 'id': 'u1', 'content': [{'type': 'text', 'text': 'Normal request.'}]}}},
                {'type': 'token_usage_record', 'payload': {}}])
            locked.chmod(0)
            try:
                result = self.run_repo(linked, home)
            finally:
                locked.chmod(0o755)
            self.assertEqual(result.stderr, '')
            report = json.loads(result.stdout)
            self.assertEqual(result.returncode, 0)
            found = report['discovery']['harnesses']
            self.assertEqual((found['claude']['matched'], found['claude']['other_repository']), (4, 1))
            self.assertEqual(found['claude']['matched_other_clone'], 1)
            self.assertEqual(found['claude']['matched_via_deleted_worktree'], 1)
            self.assertEqual(found['claude']['unresolved_cwd'], 2)
            self.assertEqual(found['claude']['unreadable_cwd'], 1)
            self.assertEqual(found['claude']['subagent_transcripts_skipped'], 1)
            self.assertEqual(found['codex']['matched'], 1)
            self.assertEqual(report['totals']['eligible_messages'], 4)
            self.assertEqual(report['totals']['duplicate_messages'], 1)
            categories = {row['category']: row for row in report['candidate_categories']}
            self.assertEqual(categories['repeated_request']['messages'], 1)
            self.assertNotIn(secret, result.stdout)
            self.assertNotIn(str(home), result.stdout)

    def test_store_that_cannot_be_listed_is_blocked_not_empty(self):
        with tempfile.TemporaryDirectory() as home:
            home = Path(home).resolve()
            repo, store = home / 'repo', home / '.codex' / 'sessions'
            self.init_repo(repo)
            store.mkdir(parents=True)
            store.chmod(0o111)
            try:
                result = self.run_repo(repo, home)
            finally:
                store.chmod(0o755)
            report = json.loads(result.stdout)
            self.assertEqual(report['discovery']['blocked'], ['codex session store'])
            self.assertEqual((result.returncode, report['status']), (2, 'partial'))

    def test_repo_mode_caps_oldest_sessions_and_reads_newest_first(self):
        with tempfile.TemporaryDirectory() as home:
            home = Path(home).resolve()
            repo = home / 'repo'
            self.init_repo(repo, commit=True)
            base = {'sessionId': 's', 'cwd': str(repo), 'userType': 'external',
                    'timestamp': iso_at(-30), 'type': 'user'}
            files = {
                'old.jsonl': ([{**base, 'sessionId': 'old', 'uuid': 'u-old', 'message': {'content': 'I already asked'}}], 100),
                'mid.jsonl': ([{**base, 'sessionId': 'mid', 'uuid': 'u-mid', 'message': {'content': 'Normal request.'}}, '{bad'], 200),
                'new.jsonl': ([{**base, 'sessionId': 'new', 'uuid': 'u-new', 'message': {'content': 'Normal request.'}}], 300),
            }
            now = time.time()
            for name, (rows, age) in files.items():
                path = home / '.claude' / 'projects' / 'p1' / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(''.join((row if isinstance(row, str) else json.dumps(row)) + '\n' for row in rows))
                mtime = now - (400 - age)
                os.utime(path, (mtime, mtime))
            runner = (
                'import sys; sys.path.insert(0, sys.argv[1]); '
                'import analyze_history; analyze_history.MAX_REPO_INPUTS = 2; '
                'sys.argv = ["analyze_history.py", "--repo", sys.argv[2], "--days", "1"]; '
                'sys.exit(analyze_history.main())'
            )
            result = subprocess.run(
                [sys.executable, '-c', runner, str(SCRIPT.parent), str(repo)],
                text=True, capture_output=True, check=False, env={**self.git_env(), 'HOME': str(home)},
            )
            self.assertEqual(result.stderr, '')
            self.assertEqual(result.returncode, 2)
            report = json.loads(result.stdout)
            self.assertEqual(report['discovery']['sessions_found'], 3)
            self.assertEqual(report['discovery']['sessions_capped'], 1)
            self.assertEqual([item['status'] for item in report['inputs']], ['parsed', 'partial'])
            categories = {row['category']: row for row in report['candidate_categories']}
            self.assertEqual(categories['repeated_request']['messages'], 0)

    def test_broken_antigravity_db_entry_does_not_crash_discovery(self):
        with tempfile.TemporaryDirectory() as home:
            home = Path(home).resolve()
            repo = home / 'repo'
            self.init_repo(repo)
            ag = home / '.gemini' / 'antigravity' / 'conversations'
            ag.mkdir(parents=True)
            (ag / 'good.db').write_bytes(b'')
            (ag / 'broken.db').symlink_to(ag / 'missing.db')
            result = self.run_repo(repo, home)
            self.assertEqual((result.returncode, result.stderr), (0, ''))
            report = json.loads(result.stdout)
            self.assertEqual(report['discovery']['uncovered_stores']['antigravity_sqlite_not_parsed'], 1)

    def test_unreadable_session_file_exits_two_partial(self):
        with tempfile.TemporaryDirectory() as home:
            home = Path(home).resolve()
            repo = home / 'repo'
            self.init_repo(repo)
            broken = home / '.claude' / 'projects' / 'p1' / 'broken.jsonl'
            broken.parent.mkdir(parents=True)
            broken.symlink_to(home / 'missing.jsonl')
            result = self.run_repo(repo, home)
            self.assertEqual((result.returncode, result.stderr), (2, ''))
            report = json.loads(result.stdout)
            self.assertEqual(report['status'], 'partial')
            self.assertEqual(report['discovery']['harnesses']['claude']['unreadable'], 1)

    def test_unreadable_antigravity_store_exits_two_partial(self):
        with tempfile.TemporaryDirectory() as home:
            home = Path(home).resolve()
            repo = home / 'repo'
            self.init_repo(repo)
            ag = home / '.gemini' / 'antigravity' / 'conversations'
            ag.mkdir(parents=True)
            ag.chmod(0o111)
            try:
                result = self.run_repo(repo, home)
            finally:
                ag.chmod(0o755)
            self.assertEqual((result.returncode, result.stderr), (2, ''))
            report = json.loads(result.stdout)
            self.assertEqual(report['status'], 'partial')
            self.assertTrue(report['discovery']['uncovered_stores']['antigravity_store_unreadable'])

    def test_antigravity_brain_discovery_matches_worktrees_and_skips_subagents(self):
        secret = 'PRIVATE_SENTINEL_never_emit'
        with tempfile.TemporaryDirectory() as home:
            home = Path(home).resolve()
            git = self.git_env()
            repo, linked, other = home / 'repo', home / 'linked', home / 'other'
            for folder in (repo, other):
                self.init_repo(folder, commit=True)
            subprocess.run(['git', '-C', str(repo), 'worktree', 'add', '-q', str(linked)], check=True, env=git)

            ag = home / '.gemini' / 'antigravity'
            (ag / 'brain').mkdir(parents=True)
            (ag / 'conversations').mkdir(parents=True)
            db = ag / 'conversation_summaries.db'
            conn = sqlite3.connect(db)
            conn.execute(
                'CREATE TABLE conversation_summaries ('
                'conversation_id TEXT PRIMARY KEY, workspace_uris TEXT, '
                'parent_conversation_id TEXT, nesting_depth INTEGER)'
            )
            rows = [
                ('cid-main', json.dumps([repo.as_uri()]), '', 0),
                ('cid-sub', json.dumps([linked.as_uri()]), 'cid-main', 1),
                ('cid-other', json.dumps([other.as_uri()]), '', 0),
                ('cid-mixed', json.dumps([other.as_uri(), str(home / 'locked_ws' / 'work')]), '', 0),
            ]
            conn.executemany('INSERT INTO conversation_summaries VALUES (?, ?, ?, ?)', rows)
            conn.commit()
            conn.close()

            now_iso = iso_at(-30)
            (home / 'locked_ws' / 'work').mkdir(parents=True)
            self.write_nested(ag / 'brain/cid-main/.system_generated/logs/transcript.jsonl', [
                {'step_index': 0, 'source': 'USER_EXPLICIT', 'type': 'USER_INPUT', 'status': 'DONE',
                 'created_at': now_iso,
                 'content': f'<USER_REQUEST>I already asked {secret}</USER_REQUEST>\n<ADDITIONAL_METADATA>Preserve</ADDITIONAL_METADATA>'},
            ])
            self.write_nested(ag / 'brain/cid-sub/.system_generated/logs/transcript.jsonl', [
                {'step_index': 0, 'source': 'SYSTEM', 'type': 'SYSTEM_MESSAGE', 'status': 'DONE',
                 'created_at': now_iso, 'content': 'You have just started. Your assignment'},
            ])
            self.write_nested(ag / 'brain/cid-other/.system_generated/logs/transcript.jsonl', [
                {'step_index': 0, 'source': 'USER_EXPLICIT', 'type': 'USER_INPUT', 'status': 'DONE',
                 'created_at': now_iso, 'content': 'I already asked'},
            ])
            self.write_nested(ag / 'brain/cid-mixed/.system_generated/logs/transcript.jsonl', [
                {'step_index': 0, 'source': 'USER_EXPLICIT', 'type': 'USER_INPUT', 'status': 'DONE',
                 'created_at': now_iso, 'content': 'Mixed'},
            ])
            (ag / 'conversations/cid-main.db').write_bytes(b'')
            (ag / 'conversations/legacy-only.db').write_bytes(b'')

            (home / 'locked_ws').chmod(0)
            try:
                result = self.run_repo(linked, home)
            finally:
                (home / 'locked_ws').chmod(0o755)
            self.assertEqual((result.returncode, result.stderr), (0, ''))
            report = json.loads(result.stdout)
            ag_cov = report['discovery']['harnesses']['antigravity']
            self.assertEqual(ag_cov['matched'], 1)
            self.assertEqual(ag_cov['other_repository'], 1)
            self.assertEqual(ag_cov['unreadable_cwd'], 1)
            self.assertEqual(ag_cov['subagent_transcripts_skipped'], 1)
            self.assertEqual(report['discovery']['uncovered_stores']['antigravity_sqlite_not_parsed'], 1)
            self.assertEqual(report['totals']['eligible_messages'], 1)
            self.assertNotIn(secret, result.stdout)
            self.assertNotIn(str(home), result.stdout)

            if os.geteuid() != 0:
                db.chmod(0)
                try:
                    blocked = self.run_repo(linked, home)
                finally:
                    db.chmod(0o644)
                self.assertEqual(blocked.returncode, 2)
                b_report = json.loads(blocked.stdout)
                self.assertIn('antigravity session store', b_report['discovery']['blocked'])

    def test_stale_mtime_and_codex_external_import_excluded_from_repo_window(self):
        with tempfile.TemporaryDirectory() as home:
            home = Path(home).resolve()
            repo = home / 'repo'
            self.init_repo(repo, commit=True)
            old_ts = iso_at(-3 * 86400)
            now_ts = iso_at(-10)
            self.write_nested(home / '.claude/projects/p1/stale.jsonl', [
                {'sessionId': 's-old', 'cwd': str(repo), 'userType': 'external',
                 'timestamp': old_ts, 'type': 'user', 'uuid': 'u-old',
                 'message': {'content': 'I already asked to fix it.'}},
                {'type': 'cost-state', 'sessionId': 's-old', 'totalCostUSD': 1.2},
                {'type': 'mode', 'mode': 'normal', 'sessionId': 's-old'},
            ])
            self.write_nested(home / '.codex/sessions/2026/11/20/rollout-imp.jsonl', [
                {'type': 'session_meta', 'timestamp': now_ts,
                 'payload': {'id': 'imp-1', 'source': 'vscode', 'cwd': str(repo)}},
                {'type': 'event_msg', 'timestamp': now_ts,
                 'payload': {'type': 'task_started', 'turn_id': 'external-import-turn-1'}},
                {'type': 'event_msg', 'timestamp': now_ts,
                 'payload': {'type': 'user_message', 'message': 'I already asked once.'}},
            ])
            result = self.run_repo(repo, home)
            self.assertEqual((result.returncode, result.stderr), (0, ''))
            report = json.loads(result.stdout)
            self.assertEqual(report['totals'].get('eligible_messages', 0), 0)
            self.assertEqual(report['distinct_eligible_sessions'], 0)
            statuses = {item['status'] for item in report['inputs']}
            self.assertEqual(statuses, {'stale_mtime_session', 'external_import_session'})


if __name__ == '__main__':
    unittest.main()
