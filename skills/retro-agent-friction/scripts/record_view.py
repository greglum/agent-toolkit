"""Bounded, redacted views of one session record, for verifying a friction candidate."""

from __future__ import annotations

import json
from pathlib import Path
import re

from antigravity_records import BG_DONE_RE, HEADER_SKIP_PREFIXES, parse_antigravity_step
from session_records import MAX_FILE_BYTES, MAX_LINE_BYTES


def block_text(content):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return '\n'.join(b.get('text', '') for b in content if isinstance(b, dict) and isinstance(b.get('text'), str))
    return ''


REDACTIONS = [(re.compile(pattern, re.I), label) for pattern, label in (
    (r'\b[a-z][\w+.-]*://\S+', '<url>'),
    (r'[\w.%+-]+@[\w-]+(?:\.[\w-]+)+', '<email>'),
    (r'\bAKIA[0-9A-Z]{16}\b', '<redacted>'),
    (r'\b(?:bearer|basic)\s+\S+', '<redacted>'),
    (r'[\w-]*(?:token|secret|pass(?:word|wd)?|api[_-]?key|auth\w*|credential)[\w-]*["\']?\s*[:=]\s*(?:(?:is|was)\s+)?\S+', '<redacted>'),
    (r'\b[\w.-]+:[^\s@/]+@', '<redacted>@'),
    (r'(?<!\S)(?:-u|--user|--pass(?:word)?|--token|--api-key|--secret)(?:=|\s+)\S+', '<redacted>'),
    (r'(?<!\S)-p\S+', '<redacted>'),
    (r'[A-Za-z0-9_+/=-]{32,}', '<redacted>'),
    (r'(?<![\w.~])(?:~|/)(?:[\w.@+-]+/)+[\w.@+-]*', '<path>'),
    (r'\b(?:[a-z0-9-]+\.)+(?:com|net|org|io|dev|gov|edu|example|test|internal|local|cloud|ai|app)\b', '<host>'),
)]


KEY_BLOCK = re.compile(r'-----BEGIN[^-]*-----.*', re.S)
LABEL = re.compile(r'^<\w+>@?$')
FLAG = re.compile(r'^--?[A-Za-z][\w-]*$')
SECRET_NAME = re.compile(r'key|token|secret|pass|pwd|auth|cookie|session|credential|webhook|private|bearer', re.I)


def hides_next(token):
    """A secret-named word or key, or a short or secret-named flag, whose next token may be a credential."""
    name = token.strip('"\',[]{}:')
    if FLAG.match(name):
        return len(name.lstrip('-')) == 1 or bool(SECRET_NAME.search(name))
    return bool(SECRET_NAME.search(name))
MIXED = re.compile(r'(?=.*[A-Za-z])(?=.*\d)')


def risky(token):
    """A token that could carry a secret: paths, @, or letters mixed with digits beyond a short code."""
    bare = token.strip('"\'(),;[]{}')
    if not bare or LABEL.match(bare):
        return False
    return any(c in bare for c in '/@\\') or (len(bare) > 5 and bool(MIXED.match(bare)))


def redact(text):
    """Deny by default: a value after ':' or '=', after a flag, or with risky shape is redacted."""
    text = KEY_BLOCK.sub(' REDACTEDKEYBLOCK ', str(text))
    text = ' '.join(re.sub(r'[,<>\[\]{}"\']', ' ', text).split()).replace('REDACTEDKEYBLOCK', '<redacted>')
    for pattern, label in REDACTIONS:
        text = pattern.sub(label, text)
    words, hide_next = [], False
    for token in text.split(' '):
        if hide_next and token and not LABEL.match(token):
            words.append('<redacted>')
            hide_next = token.lower() in {'is', 'was', 'of', 'to', 'as', 'set', 'equals', ':', '='} or hides_next(token)
            continue
        hide_next = False
        head, sep, tail = token.partition('=')
        if sep and tail:
            token = head + sep + ('<redacted>' if not LABEL.match(tail) else tail)
        elif hides_next(token):
            hide_next = True
        elif risky(token):
            token = '<redacted>'
        words.append(token)
    return ' '.join(words)


def view(record, harness):
    """Native labels plus a redacted 200-character prefix of the error text."""
    if harness == 'claude':
        a = record.get('attachment') if isinstance(record.get('attachment'), dict) else {}
        message = record.get('message') if isinstance(record.get('message'), dict) else {}
        blocks = [b for b in message.get('content') or [] if isinstance(b, dict)]
        text = a.get('blockingError') or a.get('stderr') or next(
            (block_text(b.get('content')) for b in blocks if b.get('type') == 'tool_result'), '')
        labels = [record.get('type'), a.get('type'), a.get('hookEvent'), a.get('hookName'),
                  record.get('toolDenialKind'), record.get('subtype')]
        labels += [b.get('name') for b in blocks if b.get('type') == 'tool_use']
    elif harness == 'antigravity':
        raw = str(record.get('content') or record.get('error') or '')
        if record.get('type') == 'SYSTEM_MESSAGE':
            match = BG_DONE_RE.search(raw[:600])
            if match:
                raw = raw[match.end():]
        skip = HEADER_SKIP_PREFIXES + ('The following is a <SYSTEM_MESSAGE>', '<SYSTEM_MESSAGE>')
        lines = [ln for ln in raw.splitlines() if not ln.startswith(skip)]
        text = '\n'.join(lines).strip() or raw
        labels = [record.get('type'), record.get('status'), record.get('source')]
    else:
        payload = record.get('payload') if isinstance(record.get('payload'), dict) else {}
        item = payload.get('item') if isinstance(payload.get('item'), dict) else payload
        text = item.get('aggregated_output') or item.get('stderr') or ''
        labels = [item.get('type'), item.get('status'), item.get('exit_code')]
    text = redact(text)
    return ' '.join(str(x) for x in labels if x not in (None, '')) + ' | ' + text[:200]


def numbered_records(path, issues=None):
    """Line-numbered records for --locate, with read_export's file and record limits."""
    try:
        if Path(path).stat().st_size > MAX_FILE_BYTES:
            if issues is not None:
                issues['file_limit'] += 1
            return
        with Path(path).open('rb') as stream:
            number = 0
            while True:
                line = stream.readline(MAX_LINE_BYTES + 1)
                if not line:
                    return
                number += 1
                if len(line) > MAX_LINE_BYTES:
                    while line and not line.endswith(b'\n'):
                        line = stream.readline(MAX_LINE_BYTES)
                    continue
                if not line.strip():
                    continue
                try:
                    record = json.loads(line)
                except (ValueError, UnicodeDecodeError, RecursionError):
                    continue
                if isinstance(record, dict):
                    yield number, record
    except OSError:
        if issues is not None:
            issues['unreadable_input'] += 1
        return


def feed_antigravity(session, r, line, bypass_re, program_fn, short_hash_fn):
    """Feed one Antigravity step into a friction Session with cross-file step deduplication."""
    if session.agy_seed is None:
        session.agy_seed = short_hash_fn(
            f"{r.get('created_at', '')}\0{r.get('type', '')}\0{str(r.get('content') or '')[:64]}"
        )
    step_id = f"{session.agy_seed}:{r.get('step_index', line)}:{r.get('created_at', '')}"
    if not session.fresh(step_id):
        return
    step = parse_antigravity_step(r)
    kind = step['kind']
    if kind == 'USER_INPUT':
        session.agy_queue.clear()
        return
    if kind == 'CHECKPOINT':
        session.emit('compaction', line)
        return
    if kind == 'ERROR_MESSAGE':
        session.emit('api_error', line)
        return
    if kind == 'PLANNER_RESPONSE':
        session.agy_queue.clear()
        session.output_tokens += step['output_tokens']
        for _, command, sig in step['tool_calls']:
            if command and bypass_re.search(command):
                session.emit('gate_bypass_flag', line, sig, program=program_fn(command))
            session.agy_queue.append((sig, command, session.ts))
        return
    if kind == 'GENERIC':
        sig, command, started = session.agy_queue.pop(0) if session.agy_queue else (f'step:{line}', None, session.ts)
        if step['bg_task_id']:
            session.agy_bg[step['bg_task_id']] = (sig, command, started)
            return
        key = f'agy:{line}'
        session.pending[key] = (sig, command, started)
        session.result(key, line, step['failed'], step['content'],
                       large=step['is_truncated'], duration=step['duration'])
        return
    if kind == 'SYSTEM_MESSAGE' and step['bg_completion']:
        task_id, canceled, failed, text = step['bg_completion']
        sig, command, started = session.agy_bg.pop(task_id, (f'task:{task_id}', None, None))
        key = f'agy-bg:{line}'
        session.pending[key] = (sig, command, started)
        session.result(key, line, failed, text, interrupted=canceled, large=step['is_truncated'])
