# 0013: Model Evidence Graph Edges as Consumer-to-Dependency and Surface Non-Observed Paths as Leads

- Status: Accepted
- Date: 2026-11-20

## Context

graph-engineering/scripts/evidence-graph.mjs seals and queries authored source-evidence graphs without claiming automated static extraction or runtime reachability.

## Decision

Define edges strictly as consumer -> dependency (so impact analysis traverses incoming edges from edge.to to edge.from) and include inferred and proposed edges visibly in impact output as leads rather than silently dropping them.

## Consequences

Impact queries surface all authored dependency leads with explicit status tags while keeping the tool's non-runtime epistemic scope transparent.

## Code References

- `skills/graph-engineering/scripts/evidence-graph.mjs:2`
- `skills/graph-engineering/scripts/evidence-graph.mjs:71`
