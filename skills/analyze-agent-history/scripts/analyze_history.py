#!/usr/bin/env python3
"""Aggregate candidate correction signals from native JSONL sessions: explicit files or --repo discovery."""

import argparse
from collections import Counter, defaultdict
import hashlib
import json
import re
import sys
import time

from session_records import discover, native_messages, read_export

MAX_EXPLICIT_INPUTS, MAX_REPO_INPUTS = 128, 2000

CUES = {
    'repeated_request': re.compile(r'\b(?:i (?:already|previously) (?:asked|told)|still (?:broken|wrong|failing)|once again)\b', re.I),
    'scope_correction': re.compile(r'\b(?:not what i asked|i asked (?:you )?(?:for|to)|you (?:missed|ignored)|out of scope)\b', re.I),
    'verification_request': re.compile(r'\b(?:you (?:did not|didn.t|haven.t) (?:test|verify|check)|verify before|run the (?:tests|checks) first)\b', re.I),
    'preservation_request': re.compile(r'\b(?:preserve (?:my|the|unrelated|existing)|do not (?:delete|overwrite|reset)|don.t (?:delete|overwrite|reset))\b', re.I),
}
ENVELOPES = ('# AGENTS.md instructions', '<environment_context>', '<INSTRUCTIONS>',
             '<skill>', '<system-reminder>', '<developer', '<user_instructions>',
             '<subagent', 'Message Type:', 'You are a newly spawned',
             'You are an agent in a team', '<command-name>', '<command-message>',
             '<local-command-', '<bash-input>', '<bash-stdout>', '<task-notification>',
             'Caveat: The messages below', '[Request interrupted')


class PrivateArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        self.exit(1, 'Invalid arguments. Use --help for the accepted form.\n')


def aggregate(paths, skip_oversized=False, since=None):
    totals = Counter()
    inputs = []
    file_digests = set()
    event_versions = {}
    sessions = set()
    categories = Counter()
    category_sessions = defaultdict(set)
    for number, path in enumerate(paths, 1):
        records, counts, digest, issue = read_export(path, skip_oversized)
        summary = {'input': number}
        if digest is not None and digest in file_digests:
            summary['status'] = 'duplicate_export'
            inputs.append(summary)
            totals['duplicate_exports'] += 1
            continue
        if digest is not None:
            file_digests.add(digest)
        identity = None
        messages = []
        if issue is None:
            identity, messages, issue = native_messages(records, counts, since=since)
        summary['status'] = issue or ('partial' if counts['malformed_records'] or
                                     counts['unsupported_records'] or
                                     counts['oversized_records'] else 'parsed')
        summary['coverage'] = dict(sorted(counts.items()))
        inputs.append(summary)
        totals.update(counts)
        if issue:
            totals['unparsed_or_excluded_inputs'] += 1
            continue
        for event_id, text in messages:
            key = (identity[0], event_id) if identity[0] == 'claude' else (identity, str(event_id))
            version = hashlib.sha256(text.encode('utf-8', 'surrogatepass')).digest()
            if key in event_versions:
                if event_versions[key] != version:
                    totals['conflicting_message_versions'] += 1
                    summary['status'] = 'conflicting_message_versions'
                else:
                    totals['duplicate_messages'] += 1
                continue
            event_versions[key] = version
            if text.lstrip().startswith(ENVELOPES):
                totals['excluded_envelopes'] += 1
                continue
            totals['eligible_messages'] += 1
            sessions.add(identity)
            prose = []
            fenced = False
            for line in text.splitlines():
                if line.lstrip().startswith(('```', '~~~')):
                    fenced = not fenced
                elif not fenced and not line.lstrip().startswith('>'):
                    prose.append(line)
            for name, pattern in CUES.items():
                if pattern.search('\n'.join(prose)):
                    categories[name] += 1
                    category_sessions[name].add(identity)
    incomplete = any(item['status'] not in ('parsed', 'duplicate_export',
                     'delegated_or_inherited_session', 'external_import_session',
                     'stale_mtime_session') for item in inputs)
    return {
        'schema': 'agent-history-candidates/v1',
        'status': 'partial' if incomplete else 'complete_for_supported_messages',
        'inputs': inputs,
        'totals': dict(sorted(totals.items())),
        'distinct_eligible_sessions': len(sessions),
        'candidate_categories': [
            {'category': name, 'messages': categories[name],
             'distinct_sessions': len(category_sessions[name])}
            for name in sorted(CUES)
        ],
        'limits': ['English lexical candidates; not established incidents or quality scores.',
                   'No message text, paths, native IDs, or model analysis emitted.',
                   'Session metadata and source labels are claims, not proof of human authorship.',
                   'Native format coverage is limited; excluded inputs are listed by ordinal.'],
    }, incomplete


def main():
    parser = PrivateArgumentParser(description=__doc__)
    parser.add_argument('exports', nargs='*', help='Explicit UTF-8 JSONL files; omit with --repo.')
    parser.add_argument('--repo', help="Discover this repository's Claude Code, Codex, and Antigravity sessions.")
    parser.add_argument('--days', type=int, default=30, help='With --repo: sessions active in this many days.')
    args = parser.parse_args()
    if bool(args.exports) == bool(args.repo) or args.days < 1:
        parser.error('input_mode')
    discovery = None
    since = None
    if args.repo:
        since = time.time() - args.days * 86400
        sessions, discovery = discover(args.repo, since, include_subagents=False)
        discovery['sessions_found'] = len(sessions)
        discovery['sessions_capped'] = max(0, len(sessions) - MAX_REPO_INPUTS)
        paths = [s['path'] for s in reversed(sessions[-MAX_REPO_INPUTS:])]
    elif len(args.exports) > MAX_EXPLICIT_INPUTS:
        parser.error('input_limit')
    else:
        paths = args.exports
    report, incomplete = aggregate(paths, skip_oversized=bool(args.repo), since=since)
    if discovery is not None:
        report['discovery'] = discovery
        incomplete = (
            incomplete
            or discovery['sessions_capped'] > 0
            or bool(discovery['blocked'])
            or any(h.get('unreadable', 0) > 0 for h in discovery['harnesses'].values())
            or bool(discovery['uncovered_stores'].get('antigravity_store_unreadable'))
        )
        report['status'] = 'partial' if incomplete else report['status']
    print(json.dumps(report, indent=2, sort_keys=True))
    return 2 if incomplete else 0


if __name__ == '__main__':
    sys.exit(main())
