# 0011: Restore Keyboard Focus After DOM Rebuilds and Record Hidden Shadow/Frame Omissions Before Render Filtering

- Status: Accepted
- Date: 2026-11-20

## Context

Interactive graph viewers rebuild component lists on selection, which drops browser keyboard focus if unhandled, and DOM surface collectors skip unrendered nodes while needing accurate omission reporting for unvisited subtrees.

## Decision

Explicitly re-focus the replacement button in graph-viewer.js after chooseNode() rebuilds #components, and record shadowRoot and iframe boundaries as omissions in collect-surface.mjs before skipping unrendered host elements.

## Consequences

Keyboard navigation stays unbroken across node selection, and surface audits never hide uninspected shadow DOM or iframe subtrees hosted inside currently hidden elements.

## Code References

- `skills/diagram-design/assets/graph-viewer.js:146`
- `skills/fit-surface/scripts/collect-surface.mjs:74`
