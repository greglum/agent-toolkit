# 0007: Deduplicate Claude Events Globally and Parse Codex Completed User Items Without Double-Counting

- Status: Accepted
- Date: 2026-11-20

## Context

Claude Code forked or resumed sessions replay earlier messages carrying the same global UUID across multiple JSONL files, while newer Codex rollouts emit user turns as item_completed UserMessage entries rather than legacy user events.

## Decision

Key Claude message deduplication globally by (harness, event_id) rather than per session file, and parse Codex item_completed UserMessage payloads alongside legacy user events because the two formats never coexist in the same rollout.

## Consequences

Forked Claude transcripts cannot inflate correction counts, and both legacy and current Codex rollout formats are parsed accurately without duplicate counting.

## Code References

- `skills/analyze-agent-history/scripts/analyze_history.py:68`
- `skills/analyze-agent-history/scripts/session_records.py:136`
- `skills/retro-agent-friction/scripts/session_records.py:136`
