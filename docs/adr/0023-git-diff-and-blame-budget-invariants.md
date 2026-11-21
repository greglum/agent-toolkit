# 0023: Strip Git Trailing Tab on Spaced Diff Headers and Blame Smallest Files First Within Line Budget

- Status: Accepted
- Date: 2026-11-20

## Context

retro-verification/scripts/find_escapes.py parses unified git diffs and blames changed lines under a fixed line budget.

## Decision

Strip a trailing tab from ---/+++ header paths before unquoting (because Git appends a tab when an unquoted path contains spaces), and sort blameable files by smallest changed-line count first before consuming the blame budget.

## Consequences

Paths with spaces parse cleanly without mangled filenames, and one oversized file cannot exhaust the blame budget and starve smaller files in the same fix commit.

## Code References

- `skills/retro-verification/scripts/find_escapes.py:61`
- `skills/retro-verification/scripts/find_escapes.py:224`
