# 0016: Anonymize Data-Like Headers Under --no-values and Always Clean Up Temporary SQLite Staging Files

- Status: Accepted
- Date: 2026-11-20

## Context

map-data-source supports a --no-values privacy mode that must never echo cell values, yet headerless CSVs or value-keyed JSONL records can place sensitive values in header/key positions. Staging files also copy user data into a temporary SQLite database.

## Decision

Under --no-values (show=False), replace data-like CSV headers and JSONL keys with synthetic col_N names instead of echoing them, and wrap Workspace.__init__ staging in `except BaseException: self.close(); raise` so temporary SQLite files are always deleted even on KeyboardInterrupt.

## Consequences

Sensitive cell values cannot leak through schema headers in --no-values reports, and interrupted runs leave no staged copies of user data on disk.

## Code References

- `skills/map-data-source/scripts/sources.py:161`
- `skills/map-data-source/scripts/sources.py:197`
- `skills/map-data-source/scripts/sources.py:253`
