# 0020: Require Independent Human Review for Confirmed Retro Evidence and Restrict Marker Advancement to Tracked Runs

- Status: Accepted
- Date: 2026-11-20

## Context

The shared retro history collector (collect_history.py across retro-guardrails, retro-agent-context, and retro-verification) computes evidence confidence caps and incremental tracking markers.

## Decision

Cap confidence at 'candidate' unless tier == 'git+github', there are no gaps, AND at least one PR has human review by someone other than the author; allow marker_advance only when there are no gaps and the run is either marker-based (since_sha) or explicitly started with --start-tracking.

## Consequences

Self-merged PRs on a reachable GitHub remote are never over-promoted to 'confirmed', and ad-hoc 'last week' retro runs never advance the tracking marker past unreviewed intermediate commits.

## Code References

- `skills/retro-agent-context/scripts/collect_history.py:100`
- `skills/retro-agent-context/scripts/collect_history.py:108`
- `skills/retro-agent-context/scripts/collect_history.py:109`
- `skills/retro-guardrails/scripts/collect_history.py:100`
- `skills/retro-guardrails/scripts/collect_history.py:108`
- `skills/retro-guardrails/scripts/collect_history.py:109`
- `skills/retro-verification/scripts/collect_history.py:100`
- `skills/retro-verification/scripts/collect_history.py:108`
- `skills/retro-verification/scripts/collect_history.py:109`
