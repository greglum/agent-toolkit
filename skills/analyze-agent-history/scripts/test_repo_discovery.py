"""Repository session discovery CLI boundaries using synthetic stores only."""

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
import unittest

SCRIPT = Path(__file__).with_name('analyze_history.py')


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

            def claude(cwd, rows):
                base = {'sessionId': cwd.name + secret, 'cwd': str(cwd), 'userType': 'external',
                        'timestamp': '2026-10-30T00:00:00Z'}
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
                    'timestamp': '2026-10-30T00:00:00Z', 'type': 'user'}
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


if __name__ == '__main__':
    unittest.main()
