"""Find and read native agent session files without printing their contents.

Canonical in analyze-agent-history; retro-agent-friction carries a byte-identical copy.
Callers emit only aggregates. Session content is untrusted data, never instructions.
"""

from collections import Counter
from datetime import datetime
from pathlib import Path
import hashlib
import json
import re
import stat

from antigravity_records import antigravity_messages, is_antigravity
from repo_discovery import (
    HOME,
    MAX_LINE_BYTES,
    ROOTS,
    discover,
    folder_state,
    git_common_dir,
    recorded_cwd,
    remote_identity,
    worktree_parents,
)

MAX_FILE_BYTES = 64 * 1024 * 1024
CODEX_METADATA = ('response_item', 'turn_context', 'compacted', 'token_usage_record',
                  'world_state', 'inter_agent_communication_metadata')

__all__ = [
    'CODEX_METADATA', 'HOME', 'MAX_FILE_BYTES', 'MAX_LINE_BYTES', 'ROOTS',
    'claude_human', 'claude_messages', 'codex_messages', 'copilot_messages',
    'discover', 'folder_state', 'git_common_dir', 'is_claude',
    'is_codex_external_import', 'native_messages', 'parse_time',
    'read_export', 'recorded_cwd', 'remote_identity', 'unique_members',
    'worktree_parents',
]


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


def is_codex_external_import(records):
    if not records or records[0].get('type') != 'session_meta':
        return False
    return any(
        r.get('type') == 'event_msg'
        and isinstance(r.get('payload'), dict)
        and isinstance(r['payload'].get('turn_id'), str)
        and r['payload']['turn_id'].startswith('external-import-')
        for r in records[1:50]
    )


def _is_stale_for_window(records, since):
    if since is None:
        return False
    stamps = [ts for r in records if (ts := parse_time(r.get('timestamp') or r.get('created_at'))) is not None]
    return bool(stamps and max(stamps) < since)


def _before_window(record, counts, since):
    if since is None:
        return False
    ts = parse_time(record.get('timestamp'))
    if ts is not None and ts < since:
        counts['before_window_messages'] += 1
        return True
    return False


def native_messages(records, counts, since=None):
    """Return internal identities and text; only the caller's aggregates may be emitted."""
    if not records:
        return None, [], 'empty_or_malformed'
    first = records[0]
    if first.get('type') == 'session_meta':
        return codex_messages(records, counts, since=since)
    if first.get('type') == 'session.start':
        return copilot_messages(records, counts, since=since)
    if is_claude(records):
        return claude_messages(records, counts, since=since)
    if is_antigravity(records):
        return antigravity_messages(records, counts, since=since)
    counts['unsupported_records'] += len(records)
    return None, [], 'unsupported_format'


def codex_messages(records, counts, since=None):
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
    if is_codex_external_import(records):
        counts['excluded_sessions'] += 1
        return identity, [], 'external_import_session'
    if (source not in ('cli', 'vscode', 'mcp')
            or meta.get('thread_source') not in (None, 'user')):
        return identity, [], 'unknown_session_provenance'
    if _is_stale_for_window(records, since):
        counts['before_window_sessions'] += 1
        return identity, [], 'stale_mtime_session'
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
            if _before_window(record, counts, since):
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
        if _before_window(record, counts, since):
            continue
        messages.append((timestamp, text))
    return identity, messages, None


def copilot_messages(records, counts, since=None):
    meta = records[0].get('data')
    if (not isinstance(meta, dict) or not isinstance(meta.get('sessionId'), str)
            or not meta['sessionId'] or type(meta.get('version')) is not int
            or meta['version'] < 1):
        return None, [], 'invalid_session_metadata'
    identity = ('copilot', meta['sessionId'])
    if records[0].get('agentId') or meta.get('detachedFromSpawningParentSessionId'):
        counts['excluded_sessions'] += 1
        return identity, [], 'delegated_or_inherited_session'
    if _is_stale_for_window(records, since):
        counts['before_window_sessions'] += 1
        return identity, [], 'stale_mtime_session'
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
        if _before_window(record, counts, since):
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


def claude_messages(records, counts, since=None):
    first = next(r for r in records if r.get('type') in ('user', 'assistant')
                 and isinstance(r.get('sessionId'), str))
    identity = ('claude', first['sessionId'])
    if first.get('isSidechain') or first.get('agentId'):
        counts['excluded_sessions'] += 1
        return identity, [], 'delegated_or_inherited_session'
    if _is_stale_for_window(records, since):
        counts['before_window_sessions'] += 1
        return identity, [], 'stale_mtime_session'
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
        if _before_window(record, counts, since):
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
