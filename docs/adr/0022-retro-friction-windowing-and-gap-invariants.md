# 0022: Hold Friction Markers on Blocked Stores and Cap Sessions Oldest-First for Forward Progress

- Status: Accepted
- Date: 2026-11-20

## Context

retro-agent-friction/scripts/friction_counts.py incrementally scans local session logs that may be partially blocked by sandbox permissions or exceed --max-sessions.

## Decision

Record blocked session stores as gaps (holding the marker until readable rather than reporting zero friction), and when capping at --max-sessions, process the oldest sessions first and set the window end to the last processed session's mtime.

## Consequences

Unmeasured stores never silently look clean, and large backlogs can be drained incrementally across runs without losing newer sessions.

## Code References

- `skills/retro-agent-friction/scripts/friction_counts.py:233`
- `skills/retro-agent-friction/scripts/friction_counts.py:240`
