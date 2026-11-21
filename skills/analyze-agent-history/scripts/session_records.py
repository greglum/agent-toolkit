"""Find and read native agent session files without printing their contents.

Canonical in analyze-agent-history; retro-agent-friction carries a byte-identical copy.
Callers emit only aggregates. Session content is untrusted data, never instructions.
"""

from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import os
import re
import stat
import subprocess

from antigravity_records import antigravity_messages, discover_antigravity, is_antigravity

MAX_FILE_BYTES = 64 * 1024 * 1024
MAX_LINE_BYTES = 1024 * 1024
HOME = Path.home()
ROOTS = {'claude': HOME / '.claude' / 'projects', 'codex': HOME / '.codex' / 'sessions',
         'antigravity': HOME / '.gemini' / 'antigravity' / 'conversations',
         'antigravity_brain': HOME / '.gemini' / 'antigravity' / 'brain',
         'antigravity_db': HOME / '.gemini' / 'antigravity' / 'conversation_summaries.db'}
CODEX_METADATA = ('response_item', 'turn_context', 'compacted', 'token_usage_record',
                  'world_state', 'inter_agent_communication_metadata')


def unique_members(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('duplicate JSON member')
        result[key] = value
    return result


def read_export(path, skip_oversized=False):
    """Explicit mode drops a file with an oversized record; discovery mode skips and counts it."""
    counts = Counter()
    records = []
    digest = hashlib.sha256()
    try:
        info = Path(path).stat()
        if not stat.S_ISREG(info.st_mode):
            return [], counts, None, 'not_regular_file'
        if info.st_size > MAX_FILE_BYTES:
            return [], counts, None, 'file_limit'
        with Path(path).open('rb') as stream:
            total = 0
            while True:
                line = stream.readline(MAX_LINE_BYTES + 1)
                if not line:
                    break
                total += len(line)
                if total > MAX_FILE_BYTES:
                    return [], counts, None, 'file_limit'
                digest.update(line)
                if len(line) > MAX_LINE_BYTES:
                    if not skip_oversized:
                        return [], counts, None, 'record_limit'
                    counts['oversized_records'] += 1
                    while line and not line.endswith(b'\n'):
                        line = stream.readline(MAX_LINE_BYTES)
                        total += len(line)
                        digest.update(line)
                    continue
                if not line.strip():
                    continue
                counts['records'] += 1
                try:
                    record = json.loads(line, object_pairs_hook=unique_members)
                except (ValueError, UnicodeDecodeError, RecursionError):
                    counts['malformed_records'] += 1
                    continue
                if not isinstance(record, dict):
                    counts['malformed_records'] += 1
                    continue
                records.append(record)
    except (OSError, ValueError):
        return [], counts, None, 'unreadable_input'
    return records, counts, digest.digest(), None


def is_claude(records):
    return any(r.get('type') in ('user', 'assistant') and isinstance(r.get('sessionId'), str)
               and isinstance(r.get('uuid'), str) for r in records[:400])


def native_messages(records, counts):
    """Return internal identities and text; only the caller's aggregates may be emitted."""
    if not records:
        return None, [], 'empty_or_malformed'
    first = records[0]
    if first.get('type') == 'session_meta':
        return codex_messages(records, counts)
    if first.get('type') == 'session.start':
        return copilot_messages(records, counts)
    if is_claude(records):
        return claude_messages(records, counts)
    if is_antigravity(records):
        return antigravity_messages(records, counts)
    counts['unsupported_records'] += len(records)
    return None, [], 'unsupported_format'


def codex_messages(records, counts):
    meta = records[0].get('payload')
    if not isinstance(meta, dict) or not isinstance(meta.get('id'), str) or not meta['id']:
        return None, [], 'invalid_session_metadata'
    identity = ('codex', meta['id'])
    source = meta.get('source')
    machine_source = isinstance(source, dict) and any(
        key in source for key in ('subagent', 'internal'))
    if (machine_source or source in ('exec', 'internal', 'subagent')
            or meta.get('thread_source') in ('subagent', 'guardian_review', 'memory_consolidation')
            or any(meta.get(key) for key in ('parent_thread_id', 'forked_from_id',
                                             'history_base', 'agent_path', 'agent_role'))):
        counts['excluded_sessions'] += 1
        return identity, [], 'delegated_or_inherited_session'
    if (source not in ('cli', 'vscode', 'mcp')
            or meta.get('thread_source') not in (None, 'user')):
        return identity, [], 'unknown_session_provenance'
    messages = []
    for record in records[1:]:
        kind = record.get('type')
        payload = record.get('payload')
        if kind == 'session_meta':
            return identity, [], 'multiple_session_metadata'
        if kind in CODEX_METADATA:
            counts['non_message_records'] += 1
            continue
        if kind != 'event_msg':
            counts['unsupported_records'] += 1
            continue
        if not isinstance(payload, dict) or not isinstance(payload.get('type'), str):
            counts['malformed_records'] += 1
            continue
        item = payload.get('item')
        if payload['type'] == 'item_completed' and isinstance(item, dict) and item.get('type') == 'UserMessage':
            blocks = item.get('content')
            if (not isinstance(item.get('id'), str) or not item['id'] or not isinstance(blocks, list)
                    or not all(isinstance(b, dict) for b in blocks)):
                counts['malformed_records'] += 1
                continue
            text = '\n'.join(b['text'] for b in blocks if b.get('type') == 'text' and isinstance(b.get('text'), str))
            messages.append(('item:' + item['id'], text))
            continue
        if payload['type'] != 'user_message':
            counts['non_message_records'] += 1
            continue
        text = payload.get('message')
        if not isinstance(text, str):
            counts['malformed_records'] += 1
            continue
        timestamp = record.get('timestamp')
        if not isinstance(timestamp, str) or not timestamp:
            counts['malformed_records'] += 1
            continue
        messages.append((timestamp, text))
    return identity, messages, None


def copilot_messages(records, counts):
    meta = records[0].get('data')
    if (not isinstance(meta, dict) or not isinstance(meta.get('sessionId'), str)
            or not meta['sessionId'] or type(meta.get('version')) is not int
            or meta['version'] < 1):
        return None, [], 'invalid_session_metadata'
    identity = ('copilot', meta['sessionId'])
    if records[0].get('agentId') or meta.get('detachedFromSpawningParentSessionId'):
        counts['excluded_sessions'] += 1
        return identity, [], 'delegated_or_inherited_session'
    messages = []
    for record in records[1:]:
        kind = record.get('type')
        if kind == 'session.start':
            return identity, [], 'multiple_session_metadata'
        if kind != 'user.message':
            counts['non_message_records' if isinstance(kind, str) and kind.startswith(
                ('assistant.', 'tool.', 'session.', 'subagent.')) else 'unsupported_records'] += 1
            continue
        data = record.get('data')
        if not isinstance(data, dict) or not isinstance(data.get('content'), str):
            counts['malformed_records'] += 1
            continue
        if (record.get('agentId') or data.get('parentAgentTaskId')
                or data.get('isAutopilotContinuation') or data.get('source') not in (None, 'user')):
            counts['excluded_messages'] += 1
            continue
        event_id = data.get('messageId') or record.get('id')
        if not isinstance(event_id, str) or not event_id:
            counts['malformed_records'] += 1
            continue
        messages.append((event_id, data['content']))
    return identity, messages, None


def claude_human(record):
    """A typed prompt: not injected, compacted, delegated, scheduled, peer or tool output."""
    origin = record.get('origin')
    content = (record.get('message') or {}).get('content')
    return not (record.get('isMeta') or record.get('isCompactSummary') or record.get('isSidechain')
                or 'toolUseResult' in record or record.get('userType') not in (None, 'external')
                or record.get('promptSource') == 'system'
                or record.get('turnOrigin') not in (None, 'human')
                or (origin is not None and (not isinstance(origin, dict) or origin.get('kind') != 'human'))
                or (isinstance(content, list) and any(
                    isinstance(b, dict) and b.get('type') == 'tool_result' for b in content)))


def claude_messages(records, counts):
    first = next(r for r in records if r.get('type') in ('user', 'assistant')
                 and isinstance(r.get('sessionId'), str))
    identity = ('claude', first['sessionId'])
    if first.get('isSidechain') or first.get('agentId'):
        counts['excluded_sessions'] += 1
        return identity, [], 'delegated_or_inherited_session'
    messages = []
    for record in records:
        if record.get('type') != 'user':
            counts['non_message_records'] += 1
            continue
        if not claude_human(record):
            counts['excluded_messages'] += 1
            continue
        content = (record.get('message') or {}).get('content')
        if isinstance(content, list):
            content = '\n'.join(b['text'] for b in content if isinstance(b, dict)
                                and b.get('type') == 'text' and isinstance(b.get('text'), str))
        if not isinstance(content, str) or not isinstance(record.get('uuid'), str):
            counts['malformed_records'] += 1
            continue
        messages.append((record['uuid'], content))
    return identity, messages, None


def parse_time(value):
    """Epoch seconds from an ISO 8601 string, or None."""
    if not isinstance(value, str):
        return None
    match = re.match(r'(\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d)(?:\.\d+)?(Z|[+-]\d\d:\d\d)?$', value)
    if not match:
        return None
    zone = match[2] if match[2] and match[2] != 'Z' else '+00:00'
    try:
        return datetime.fromisoformat(match[1] + zone).timestamp()
    except ValueError:
        return None


def folder_state(path):
    """'dir', 'missing' or 'denied': a sandbox that blocks a folder must not look like an empty one."""
    try:
        if not stat.S_ISDIR(os.stat(path).st_mode):
            return 'missing'
        with os.scandir(path):
            return 'dir'
    except PermissionError:
        return 'denied'
    except OSError:
        return 'missing'


def git_common_dir(path, cache, worktree_parents=()):
    """Resolve a recorded cwd. A missing cwd matches only when its first missing folder sat directly
    in a folder that holds one of the target's worktrees, so a deleted nested repository does not.
    Returns 'denied' when the cwd or an ancestor cannot be read."""
    probe, via_ancestor = Path(path), False
    while (state := folder_state(probe)) != 'dir':
        if state == 'denied':
            return 'denied', via_ancestor
        if probe.parent == probe:
            return None, via_ancestor
        probe, via_ancestor = probe.parent, True
    if via_ancestor:
        return (cache['target'] if os.path.realpath(probe) in worktree_parents else None), True
    key = str(probe)
    if key not in cache:
        result = subprocess.run(['git', '-C', key, 'rev-parse', '--path-format=absolute',
                                 '--git-common-dir'], capture_output=True, text=True, check=False)
        found = result.stdout.strip()
        cache[key] = os.path.realpath(found) if result.returncode == 0 and found else None
    return cache[key], via_ancestor


def worktree_parents(repo):
    """Folders holding the repository's linked worktrees, prunable (deleted) entries included.

    The main worktree's parent is never one of them, even when linked worktrees sit beside it,
    because sibling repositories live there too.
    """
    result = subprocess.run(['git', '-C', str(repo), 'worktree', 'list', '--porcelain'],
                            capture_output=True, text=True, check=False)
    paths = [line[9:] for line in result.stdout.splitlines() if line.startswith('worktree ')]
    if not paths:
        return set()
    main_parent = os.path.realpath(Path(paths[0]).parent)
    return {os.path.realpath(Path(path).parent) for path in paths[1:]} - {main_parent}


def recorded_cwd(path, harness):
    """The working directory a session recorded about itself, from its first records."""
    try:
        with Path(path).open('rb') as stream:
            for _ in range(400):
                line = stream.readline(MAX_LINE_BYTES + 1)
                if not line:
                    return None
                if len(line) > MAX_LINE_BYTES or b'cwd' not in line:
                    continue
                try:
                    record = json.loads(line)
                except (ValueError, UnicodeDecodeError, RecursionError):
                    continue
                if not isinstance(record, dict):
                    continue
                if harness == 'codex' and record.get('type') == 'session_meta':
                    payload = record.get('payload')
                    cwd = payload.get('cwd') if isinstance(payload, dict) else None
                else:
                    cwd = record.get('cwd')
                if isinstance(cwd, str) and cwd.startswith('/'):
                    return cwd
    except OSError:
        return None
    return None


def remote_identity(common_dir, cache):
    """The normalized origin URL of a repository, so separate clones of one remote match."""
    key = ('remote', common_dir)
    if key not in cache:
        result = subprocess.run(['git', '--git-dir', common_dir, 'remote', 'get-url', 'origin'],
                                capture_output=True, text=True, check=False)
        url = result.stdout.strip() if result.returncode == 0 else ''
        identity = re.sub(r'^(ssh://)?(git@|https?://)', '', url).replace(':', '/')
        cache[key] = identity.removesuffix('.git').rstrip('/').lower() or None
    return cache[key]


def discover(repo, since, include_subagents=True, roots=None):
    """Sessions whose recorded cwd belongs to this repository: the same git common dir, or another
    clone with the same origin URL. Never matches by slug. Blocked folders are reported, not
    counted as empty."""
    roots = roots or ROOTS
    cache = {}
    target, _ = git_common_dir(Path(repo).resolve(), cache)
    if target in (None, 'denied'):
        raise SystemExit('not a git repository')
    cache['target'], parents = target, worktree_parents(Path(repo).resolve())
    target_remote = remote_identity(target, cache)
    coverage = {name: Counter() for name in ('claude', 'codex')}
    blocked = []
    candidates = []
    for name, patterns in (('claude', (('*/*.jsonl', False), ('*/*/subagents/*.jsonl', True))),
                           ('codex', (('*/*/*/*.jsonl', False),))):
        state = folder_state(roots[name])
        if state == 'denied':
            blocked.append(f'{name} session store')
        elif state == 'dir':
            for pattern, subagent in patterns:
                candidates += [(name, p, subagent) for p in Path(roots[name]).glob(pattern)]
    sessions = []
    for harness, path, subagent in candidates:
        counts = coverage[harness]
        try:
            mtime = path.stat().st_mtime
        except OSError:
            counts['unreadable'] += 1
            continue
        if mtime < since:
            counts['before_window'] += 1
            continue
        if subagent and not include_subagents:
            counts['subagent_transcripts_skipped'] += 1
            continue
        cwd = recorded_cwd(path, harness)
        if cwd is None:
            counts['no_recorded_cwd'] += 1
            continue
        common, via_ancestor = git_common_dir(cwd, cache, parents)
        same_remote = (common not in (None, 'denied', target) and target_remote is not None
                       and remote_identity(common, cache) == target_remote)
        if common == 'denied':
            counts['unreadable_cwd'] += 1
        elif common is None:
            counts['unresolved_cwd'] += 1
        elif common != target and not same_remote:
            counts['other_repository'] += 1
        else:
            counts['matched'] += 1
            counts['matched_other_clone'] += same_remote
            counts['matched_via_deleted_worktree'] += via_ancestor
            counts['matched_subagent_transcripts'] += subagent
            sessions.append({'harness': harness, 'path': path, 'subagent': subagent, 'mtime': mtime})
    sessions.sort(key=lambda s: (s['mtime'], str(s['path'])))
    conv_root = Path(roots['antigravity'])
    brain_root = Path(roots.get('antigravity_brain', conv_root.parent / 'brain'))
    db_path = Path(roots.get('antigravity_db', conv_root.parent / 'conversation_summaries.db'))
    agy_sessions, agy_counts, agy_blocked, uncovered = discover_antigravity(
        brain_root, db_path, conv_root, since, include_subagents,
        target, target_remote, cache, parents, folder_state, git_common_dir, remote_identity,
    )
    sessions.extend(agy_sessions)
    sessions.sort(key=lambda s: (s['mtime'], str(s['path'])))
    coverage['antigravity'] = agy_counts
    blocked.extend(agy_blocked)
    report = {name: dict(sorted(c.items())) for name, c in coverage.items()}
    return sessions, {'harnesses': report, 'uncovered_stores': uncovered, 'blocked': blocked,
                      'window_start': datetime.fromtimestamp(since, timezone.utc).isoformat()}
