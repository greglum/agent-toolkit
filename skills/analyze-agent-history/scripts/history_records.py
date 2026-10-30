"""Read explicitly supplied native exports without printing their contents."""

from collections import Counter
from pathlib import Path
import hashlib
import json
import stat

MAX_FILE_BYTES = 64 * 1024 * 1024
MAX_LINE_BYTES = 1024 * 1024


def unique_members(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('duplicate JSON member')
        result[key] = value
    return result


def read_export(path):
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
                    return [], counts, None, 'record_limit'
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


def native_messages(records, counts):
    """Return internal identities and text; only the caller's aggregates may be emitted."""
    if not records:
        return None, [], 'empty_or_malformed'
    first = records[0]
    if first.get('type') == 'session_meta':
        return codex_messages(records, counts)
    if first.get('type') == 'session.start':
        return copilot_messages(records, counts)
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
    for index, record in enumerate(records[1:], 1):
        kind = record.get('type')
        payload = record.get('payload')
        if kind == 'session_meta':
            return identity, [], 'multiple_session_metadata'
        if kind in ('response_item', 'turn_context', 'compacted'):
            counts['non_message_records'] += 1
            continue
        if kind != 'event_msg':
            counts['unsupported_records'] += 1
            continue
        if not isinstance(payload, dict) or not isinstance(payload.get('type'), str):
            counts['malformed_records'] += 1
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
    for index, record in enumerate(records[1:], 1):
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
