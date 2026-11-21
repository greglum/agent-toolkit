# 0004: Maintain Python 3.10 Standard-Library Compatibility Across Catalog Scripts

- Status: Accepted
- Date: 2026-11-20

## Context

Catalog scripts declare Python 3.10+ compatibility using only the standard library. Certain stdlib behaviors changed in Python 3.11+ (such as datetime.fromisoformat accepting trailing 'Z') and 3.13+ (Path.resolve raising OSError instead of RuntimeError on symlink loops).

## Decision

Keep explicit Python 3.10 compatibility guards: catch both (OSError, RuntimeError) around Path.resolve() symlink-loop checks and normalize trailing 'Z' to '+00:00' before calling datetime.fromisoformat().

## Consequences

All scripts run identically on Python 3.10 through current Python 3.x releases without relying on newer stdlib additions.

## Code References

- `scripts/install.py:92`
- `skills/map-data-source/scripts/column_profile.py:52`
