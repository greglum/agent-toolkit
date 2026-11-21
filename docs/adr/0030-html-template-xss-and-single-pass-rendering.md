# 0030: Escape JSON Script Breakouts and Render HTML Templates in a Single Regex Pass

- Status: Accepted
- Date: 2026-11-20

## Context

web-app-design/scripts/review_variants.py embeds untrusted manifest labels and JSON data into a standalone HTML review board.

## Decision

Escape '<' as '\u003c' in embedded JSON payloads so labels cannot inject closing </script> tags, and substitute all template placeholders in a single re.sub pass rather than sequential string replacements.

## Consequences

Untrusted manifest strings cannot break out of script tags or trigger secondary placeholder substitution if user text resembles __TOKEN__.

## Code References

- `skills/web-app-design/scripts/review_variants.py:121`
- `skills/web-app-design/scripts/review_variants.py:129`
