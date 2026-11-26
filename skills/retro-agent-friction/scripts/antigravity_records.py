"""Discover and parse Antigravity JSONL transcripts via read-only summary metadata.

Canonical in analyze-agent-history; retro-agent-friction carries a byte-identical copy.
Callers emit only aggregates. Session content is untrusted data, never instructions.
"""

from collections import Counter
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
import sqlite3
from urllib.parse import unquote, urlparse

AGY_TYPES = ('USER_INPUT', 'PLANNER_RESPONSE', 'GENERIC', 'SYSTEM_MESSAGE', 'CHECKPOINT', 'ERROR_MESSAGE')
ISO_TIME_RE = re.compile(r'(\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d)(?:\.\d+)?(Z|[+-]\d\d:\d\d)?$')
USER_REQ_RE = re.compile(r'<USER_REQUEST>\s*(.*?)\s*</USER_REQUEST>', re.S)
DELEGATED_PREFIXES = ('You have just started. Your assignment', '[swarm] new board message')
EXIT_CODE_RE = re.compile(r'^Command exited with code ([1-9]\d*)\.?\r?$', re.M)
EXIT_ZERO_RE = re.compile(r'^Command exited with code 0\.?\r?$', re.M)
TASK_ID_RE = re.compile(r'task id:\s*([^\s]+)', re.I)
BG_DONE_RE = re.compile(r'Task id "([^"]+)" (finished with result:|was canceled with result:)', re.S)
TIMESTAMP_LINE_RE = re.compile(r'^(Created At|Completed At):\s*(\S+)', re.M)
TRUNCATED_MARKER = "The tool's output was truncated due to being too long."
HEADER_SKIP_PREFIXES = ('Created At:', 'Completed At:', TRUNCATED_MARKER, 'Here is a preview')


def is_antigravity(records):
    """True when records start with an Antigravity transcript step."""
    if not records:
        return False
    first = records[0]
    return (isinstance(first.get('step_index'), int)
            and first.get('type') in AGY_TYPES
            and isinstance(first.get('created_at'), str))


def _unwrap_user_request(text):
    match = USER_REQ_RE.search(text)
    return match.group(1).strip() if match else text


def _is_delegated_transcript(records):
    first = records[0]
    if first.get('type') == 'SYSTEM_MESSAGE':
        head = '\n'.join(str(r.get('content') or '') for r in records[:2])
        if any(prefix in head for prefix in DELEGATED_PREFIXES):
            return True
        if not any(r.get('type') == 'USER_INPUT' and r.get('source') == 'USER_EXPLICIT' for r in records):
            return True
    return False


def _parse_iso_time(value):
    if not isinstance(value, str):
        return None
    match = ISO_TIME_RE.match(value)
    if not match:
        return None
    zone = match[2] if match[2] and match[2] != 'Z' else '+00:00'
    try:
        return datetime.fromisoformat(match[1] + zone).timestamp()
    except ValueError:
        return None


def antigravity_messages(records, counts, since=None):
    """Extract typed human prompts from Antigravity transcript JSONL."""
    first = records[0]
    seed = f"{first.get('created_at', '')}\0{first.get('type', '')}\0{str(first.get('content') or '')[:256]}"
    digest = hashlib.sha256(seed.encode('utf-8', 'surrogatepass')).hexdigest()[:16]
    identity = ('antigravity', digest)
    if _is_delegated_transcript(records):
        counts['excluded_sessions'] += 1
        return identity, [], 'delegated_or_inherited_session'
    if since is not None:
        stamps = [ts for r in records if (ts := _parse_iso_time(r.get('created_at'))) is not None]
        if stamps and max(stamps) < since:
            counts['before_window_sessions'] += 1
            return identity, [], 'stale_mtime_session'
    messages = []
    for record in records:
        kind = record.get('type')
        if kind in ('PLANNER_RESPONSE', 'GENERIC', 'SYSTEM_MESSAGE', 'CHECKPOINT', 'ERROR_MESSAGE'):
            counts['non_message_records'] += 1
            continue
        if kind != 'USER_INPUT':
            counts['unsupported_records'] += 1
            continue
        if record.get('source') != 'USER_EXPLICIT':
            counts['excluded_messages'] += 1
            continue
        step = record.get('step_index')
        created_at = record.get('created_at')
        content = record.get('content')
        if (type(step) is not int or not isinstance(created_at, str)
                or not created_at or not isinstance(content, str)):
            counts['malformed_records'] += 1
            continue
        if since is not None:
            ts = _parse_iso_time(created_at)
            if ts is not None and ts < since:
                counts['before_window_messages'] += 1
                continue
        messages.append((f'step:{step}:{created_at}', _unwrap_user_request(content)))
    return identity, messages, None


def workspace_paths(raw_uris):
    """Decode local filesystem paths from Antigravity workspace_uris JSON."""
    if not isinstance(raw_uris, str) or not raw_uris.strip():
        return []
    try:
        items = json.loads(raw_uris)
    except ValueError:
        return []
    if not isinstance(items, list):
        return []
    paths = []
    for item in items:
        if not isinstance(item, str) or not item:
            continue
        if item.startswith('file://'):
            parsed = urlparse(item)
            decoded = unquote(parsed.path)
            if decoded.startswith('/'):
                paths.append(decoded)
        elif item.startswith('/'):
            paths.append(item)
    return paths


def load_summary_index(db_path):
    """Read conversation_summaries metadata read-only without copying session text."""
    path = Path(db_path)
    try:
        if not path.exists():
            return {}, 'missing'
    except PermissionError:
        return {}, 'denied'
    except OSError:
        return {}, 'missing'
    try:
        conn = sqlite3.connect(f'{path.resolve().as_uri()}?mode=ro', uri=True)
    except PermissionError:
        return {}, 'denied'
    except sqlite3.Error:
        return {}, 'denied'
    try:
        rows = conn.execute(
            'SELECT conversation_id, workspace_uris, parent_conversation_id, nesting_depth '
            'FROM conversation_summaries'
        ).fetchall()
    except sqlite3.Error:
        return {}, 'denied'
    finally:
        conn.close()
    index = {}
    for cid, uris, parent_id, depth in rows:
        if isinstance(cid, str) and cid:
            index[cid] = {
                'workspace_uris': uris,
                'parent_id': parent_id or '',
                'nesting_depth': depth if isinstance(depth, int) else 0,
            }
    return index, 'ok'


def _classify_workspace(paths, cache, parents, target, target_remote, git_common_dir, remote_identity):
    best_non_match = 'no_recorded_cwd' if not paths else None
    for cwd in paths:
        common, via_ancestor = git_common_dir(cwd, cache, parents)
        same_remote = (common not in (None, 'denied', target) and target_remote is not None
                       and remote_identity(common, cache) == target_remote)
        if common == target or same_remote:
            return 'matched', same_remote, via_ancestor
        if common == 'denied':
            best_non_match = 'unreadable_cwd'
        elif common is None and best_non_match in (None, 'other_repository'):
            best_non_match = 'unresolved_cwd'
        elif common not in (None, 'denied') and best_non_match is None:
            best_non_match = 'other_repository'
    return best_non_match or 'unresolved_cwd', False, False


def discover_antigravity(brain_root, db_path, conv_root, since, include_subagents,
                         target, target_remote, cache, parents, folder_state,
                         git_common_dir, remote_identity):
    """Discover Antigravity brain JSONL transcripts and report unparsed legacy SQLite stores."""
    counts = Counter()
    blocked = []
    uncovered = {}
    sessions = []
    parsed_cids = set()

    brain_state = folder_state(brain_root)
    index, db_state = load_summary_index(db_path)
    if brain_state == 'denied' or db_state == 'denied':
        blocked.append('antigravity session store')
        uncovered['antigravity_store_unreadable'] = True
    elif brain_state == 'dir':
        for path in Path(brain_root).glob('*/.system_generated/logs/transcript.jsonl'):
            cid = path.parents[2].name
            parsed_cids.add(cid)
            try:
                mtime = path.stat().st_mtime
            except OSError:
                counts['unreadable'] += 1
                continue
            if mtime < since:
                counts['before_window'] += 1
                continue
            meta = index.get(cid)
            if meta is None:
                counts['no_recorded_cwd'] += 1
                continue
            subagent = bool(meta['parent_id']) or meta['nesting_depth'] > 0
            if subagent and not include_subagents:
                counts['subagent_transcripts_skipped'] += 1
                continue
            ws_paths = workspace_paths(meta['workspace_uris'])
            outcome, same_remote, via_ancestor = _classify_workspace(
                ws_paths, cache, parents, target, target_remote, git_common_dir, remote_identity
            )
            if outcome == 'matched':
                counts['matched'] += 1
                counts['matched_other_clone'] += same_remote
                counts['matched_via_deleted_worktree'] += via_ancestor
                counts['matched_subagent_transcripts'] += subagent
                sessions.append({'harness': 'antigravity', 'path': path, 'subagent': subagent, 'mtime': mtime})
            else:
                counts[outcome] += 1

    conv_state = folder_state(conv_root)
    if conv_state == 'denied':
        uncovered['antigravity_store_unreadable'] = True
    elif conv_state == 'dir':
        db_count = 0
        for p in Path(conv_root).glob('*.db'):
            if p.stem in parsed_cids:
                continue
            try:
                if p.stat().st_mtime >= since:
                    db_count += 1
            except OSError:
                continue
        if db_count or brain_state != 'dir':
            uncovered['antigravity_sqlite_not_parsed'] = db_count

    return sessions, counts, blocked, uncovered


def _decode_arg(value):
    if isinstance(value, str) and len(value) >= 2 and value[0] in '"{[' and value[-1] in '"}]':
        try:
            decoded = json.loads(value)
            if isinstance(decoded, str):
                return decoded
        except ValueError:
            pass
    return value


def _content_duration(text):
    stamps = {}
    for label, iso_str in TIMESTAMP_LINE_RE.findall(text[:500]):
        try:
            stamps[label] = datetime.fromisoformat(iso_str).timestamp()
        except ValueError:
            continue
    if 'Created At' in stamps and 'Completed At' in stamps:
        delta = stamps['Completed At'] - stamps['Created At']
        return delta if delta >= 0 else None
    return None


def _command_failed(text):
    if '\nCommand output:' in text:
        head = text.split('\nCommand output:', 1)[0]
        if EXIT_ZERO_RE.search(head):
            return False
        return bool(EXIT_CODE_RE.search(head))
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith(HEADER_SKIP_PREFIXES):
            continue
        if EXIT_ZERO_RE.match(line):
            return False
        return bool(EXIT_CODE_RE.match(line))
    return False


def parse_antigravity_step(record):
    """Normalize one Antigravity transcript step for friction counting."""
    kind = record.get('type')
    status = record.get('status')
    content = record.get('content') if isinstance(record.get('content'), str) else ''
    tokens = record.get('output_tokens')
    output_tokens = tokens if isinstance(tokens, int) and tokens > 0 else 0

    tool_calls = []
    if kind == 'PLANNER_RESPONSE' and isinstance(record.get('tool_calls'), list):
        for tc in record['tool_calls']:
            if not isinstance(tc, dict) or not isinstance(tc.get('name'), str):
                continue
            name = tc['name']
            raw_args = tc.get('args') if isinstance(tc.get('args'), dict) else {}
            cmd = _decode_arg(raw_args.get('CommandLine')) if name == 'run_command' else None
            command = cmd if isinstance(cmd, str) and cmd else None
            if command:
                sig = f"{name}\0{' '.join(command.split())}"
            else:
                sig = f"{name}\0{json.dumps(raw_args, sort_keys=True)}"
            tool_calls.append((name, command, sig))

    is_truncated = TRUNCATED_MARKER in content[:1000]
    bg_task_id = None
    if kind == 'GENERIC' and status == 'RUNNING':
        match = TASK_ID_RE.search(content[:500])
        if match:
            bg_task_id = match.group(1)

    bg_completion = None
    if kind == 'SYSTEM_MESSAGE':
        match = BG_DONE_RE.search(content[:600])
        if match:
            task_id, outcome = match.group(1), match.group(2)
            canceled = 'was canceled' in outcome
            tail = content[match.end():]
            failed = canceled or _command_failed(tail)
            bg_completion = (task_id, canceled, failed, content)

    failed = (
        status == 'ERROR'
        or bool(record.get('error'))
        or (kind == 'GENERIC' and _command_failed(content))
    )
    return {
        'kind': kind,
        'status': status,
        'content': content,
        'output_tokens': output_tokens,
        'tool_calls': tool_calls,
        'is_truncated': is_truncated,
        'bg_task_id': bg_task_id,
        'bg_completion': bg_completion,
        'failed': failed,
        'duration': _content_duration(content) if kind == 'GENERIC' else None,
    }
