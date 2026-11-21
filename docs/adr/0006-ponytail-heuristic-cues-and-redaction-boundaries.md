# 0006: Use Ordered Regex Heuristics as Verifiable Leads and Ordered Deny-by-Default Redaction

- Status: Accepted
- Date: 2026-11-20

## Context

Session history and friction analyzers run offline with Python's standard library only and process untrusted local logs that may contain credentials or markup-glued secrets.

## Decision

Follow the Ponytail principle by using explicit, ordered English regex cues whose matches are treated as candidate leads for verification rather than semantic ground truth. For --locate redaction views, split JSON/markup punctuation into word boundaries first and apply ordered redaction patterns (URLs and keyed secrets before generic paths) before token-level deny-by-default rules.

## Consequences

The analyzers stay small, fast, deterministic, and dependency-free while making their epistemic limits explicit and avoiding path-regex clobbering of credential URLs.

## Code References

- `skills/analyze-agent-history/scripts/analyze_history.py:16`
- `skills/retro-agent-friction/scripts/friction_counts.py:31`
- `skills/retro-agent-friction/scripts/record_view.py:20`
- `skills/retro-agent-friction/scripts/record_view.py:62`
