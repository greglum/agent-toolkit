# 0019: Delegate Git Alternates Resolution to count-objects and Refuse Untrusted Clean Filters or Submodule Recursion

- Status: Accepted
- Date: 2026-11-20

## Context

repository-cleanup/scripts/inventory.py inspects potentially untrusted Git repositories before cleanup. Manual alternates parsing misses chained/env lenders, count-objects can exit 0 while printing missing-lender stderr diagnostics, core.quotePath=true emits C-octal escapes, and `git status` can execute clean filters or enter child submodule configs.

## Decision

Discover alternates via `git -c core.quotePath=true count-objects -v` with require_no_diagnostics=True and unquote C-octal paths via latin-1/os.fsdecode; inspect git config and check-attr before git status and refuse when active clean/process filters are configured; and pass `--ignore-submodules=dirty` to report gitlink changes without descending into child Git configurations.

## Consequences

Inventory stays safe and read-only on untrusted repositories while catching missing object lenders and preserving exact non-ASCII/newline alternate paths.

## Code References

- `skills/repository-cleanup/scripts/inventory.py:34`
- `skills/repository-cleanup/scripts/inventory.py:35`
- `skills/repository-cleanup/scripts/inventory.py:42`
- `skills/repository-cleanup/scripts/inventory.py:63`
- `skills/repository-cleanup/scripts/inventory.py:85`
