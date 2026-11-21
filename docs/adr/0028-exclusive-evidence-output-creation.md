# 0028: Use Exclusive File and Directory Creation So Prior Evidence Is Never Silently Overwritten

- Status: Accepted
- Date: 2026-11-20

## Context

web-app-design verification and reference scripts write evidence directories and output artifacts that may be compared across runs or written concurrently.

## Decision

Create evidence directories with mkdir(output) without { recursive: true } and open output files with exclusive mode 'x' rather than truncating existing paths.

## Consequences

Re-running against an existing output path or colliding with a concurrent writer fails cleanly instead of silently clobbering accepted evidence.

## Code References

- `skills/web-app-design/scripts/check-variant-browser.mjs:31`
- `skills/web-app-design/scripts/design_reference.py:190`
