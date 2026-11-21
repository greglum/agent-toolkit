# 0008: Probe Blocked Directories via scandir() Because macOS Sandboxes Permit stat()

- Status: Accepted
- Date: 2026-11-20

## Context

Under macOS Seatbelt sandboxes, os.stat() can succeed on a blocked session-store directory while directory listing fails with PermissionError. Treating an unreadable directory as empty would silently report zero sessions.

## Decision

Follow os.stat() with os.scandir() to confirm readability before classifying a store directory as accessible, and test this path using mode 0o111 (execute-only) directories to reproduce stat-allowed/scandir-denied behavior portably on POSIX.

## Consequences

Sandbox-blocked session stores are accurately reported as blocked coverage gaps rather than empty histories.

## Code References

- `skills/analyze-agent-history/scripts/session_records.py:253`
- `skills/analyze-agent-history/scripts/test_analyze_history.py:225`
- `skills/retro-agent-friction/scripts/session_records.py:253`
