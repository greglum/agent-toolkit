# 0017: Keep Raw GitHub Diagnostics and Comment Bodies Out of PR Watcher State and Pin GH_HOST

- Status: Accepted
- Date: 2026-11-20

## Context

monitor-pr/scripts/watch_pr.py polls GitHub PRs via `gh`, writes local state files keyed by owner/repo#number, and emits structured JSON events to agents.

## Decision

Omit raw gh stdout/stderr from failure exceptions; store SHA-256 digests of PR comment/review bodies rather than raw text; emit the initial snapshot without exiting so normal runs wait for a subsequent change; and pin GH_HOST='github.com' to match the state identity key.

## Consequences

Credentials, response bodies, and untrusted PR comment text are kept out of logs and state files, initial snapshots remain observable without terminating watches early, and ambient GH_HOST overrides cannot corrupt state matching.

## Code References

- `skills/monitor-pr/scripts/watch_pr.py:34`
- `skills/monitor-pr/scripts/watch_pr.py:71`
- `skills/monitor-pr/scripts/watch_pr.py:160`
- `skills/monitor-pr/scripts/watch_pr.py:185`
