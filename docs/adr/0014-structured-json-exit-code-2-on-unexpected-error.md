# 0014: Emit Structured JSON and Exit 2 on Unexpected Errors Across Audit CLIs

- Status: Accepted
- Date: 2026-11-20

## Context

Machine-consumed audit scripts (check_domain_notes.py and map_data.py) use exit 0 for clean, exit 1 for findings, and exit 2 for invalid input or tool errors.

## Decision

Catch unexpected top-level Exceptions, print a structured JSON {"error": ...} object without a raw Python traceback, and exit 2 so callers never confuse a crash with exit 1 ('findings').

## Consequences

Downstream agents and pipelines always receive parseable JSON and a clear exit-code distinction between findings (1) and invalid input or crashes (2).

## Code References

- `skills/learn-domain/scripts/check_domain_notes.py:326`
- `skills/map-data-source/scripts/map_data.py:99`
