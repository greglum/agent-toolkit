# 0002: Enforce Public Export Snapshot Boundaries via Isolated Bare Clones and Preflight Checks

- Status: Accepted
- Date: 2026-11-20

## Context

The private source repository exports snapshots to the public greglum/agent-toolkit checkout. The public repo carries hosted GitHub Actions workflows absent from the private source, while local checkout attributes or target symlinks could otherwise leak internal docs or overwrite unmanaged files.

## Decision

Keep PUBLIC_ONLY files (such as .github/workflows/check.yml) intact when syncing snapshots, build snapshots from a temporary bare shared clone with scrubbed GIT_* env and core.attributesFile=/dev/null, and preflight-check every target ancestor for symlinks and unmanaged/ignored collisions before performing any write or deletion.

## Consequences

Local checkout attributes cannot alter exported trees, public-only CI workflows survive syncs, and invalid or symlinked targets abort cleanly before any public file is modified or removed.

## Code References

- `docs/maintainers/sync_public.py:21`
- `docs/maintainers/sync_public.py:22`
- `docs/maintainers/sync_public.py:31`
- `docs/maintainers/sync_public.py:78`
