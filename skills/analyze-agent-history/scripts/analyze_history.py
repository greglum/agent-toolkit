#!/usr/bin/env python3
"""Aggregate candidate correction signals from explicit native JSONL exports."""

import argparse
from collections import Counter, defaultdict
import hashlib
import json
import re
import sys

from history_records import native_messages, read_export

# ponytail: fixed English cues are candidates, not semantic correction detection.
CUES = {
    'repeated_request': re.compile(r'\b(?:i (?:already|previously) (?:asked|told)|still (?:broken|wrong|failing)|once again)\b', re.I),
    'scope_correction': re.compile(r'\b(?:not what i asked|i asked (?:you )?(?:for|to)|you (?:missed|ignored)|out of scope)\b', re.I),
    'verification_request': re.compile(r'\b(?:you (?:did not|didn.t|haven.t) (?:test|verify|check)|verify before|run the (?:tests|checks) first)\b', re.I),
    'preservation_request': re.compile(r'\b(?:preserve (?:my|the|unrelated|existing)|do not (?:delete|overwrite|reset)|don.t (?:delete|overwrite|reset))\b', re.I),
}
ENVELOPES = ('# AGENTS.md instructions', '<environment_context>', '<INSTRUCTIONS>',
             '<skill>', '<system-reminder>', '<developer', '<user_instructions>',
             '<subagent', 'Message Type:', 'You are a newly spawned',
             'You are an agent in a team')


class PrivateArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        self.exit(2, 'Invalid arguments. Use --help for the accepted form.\n')


def aggregate(paths):
    totals = Counter()
    inputs = []
    file_digests = set()
    event_versions = {}
    sessions = set()
    categories = Counter()
    category_sessions = defaultdict(set)
    for number, path in enumerate(paths, 1):
        records, counts, digest, issue = read_export(path)
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
            identity, messages, issue = native_messages(records, counts)
        summary['status'] = issue or ('partial' if counts['malformed_records'] or
                                     counts['unsupported_records'] else 'parsed')
        summary['coverage'] = dict(sorted(counts.items()))
        inputs.append(summary)
        totals.update(counts)
        if issue:
            totals['unparsed_or_excluded_inputs'] += 1
            continue
        for event_id, text in messages:
            key = (identity, str(event_id))
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
            # Exclude quoted/code lines from cue matching, retaining no snippets.
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
                     'delegated_or_inherited_session') for item in inputs)
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
    parser.add_argument('exports', nargs='+', help='Explicit UTF-8 JSONL files; no directory discovery.')
    args = parser.parse_args()
    if len(args.exports) > 128:
        parser.error('input_limit')
    report, incomplete = aggregate(args.exports)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 2 if incomplete else 0


if __name__ == '__main__':
    sys.exit(main())
