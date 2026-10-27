---
name: graph-engineering
description: >-
  Use repository graphs to plan and verify a change: trace dependencies, test impact, and missing relationships before choosing what to rebuild. Use for cross-file change impact and architecture questions; graph visualization belongs to diagram-design.
compatibility: Use an existing authorized graph index when available, or scoped source reads. The optional evidence snapshot and impact tool needs Node.js 18+ and Git; it neither extracts code nor installs a graph backend.
---

# Graph engineering

Turn a repository question into a bounded, source-checked change. A graph narrows the
reading path; its missing edges do not establish that a dependency is absent.

## Bind the question

Read repository instructions, revision, dirty ownership, and required checks. Name the
user-visible result, affected entry points, contracts to preserve, and one question the
graph should answer. For a small known owner, read it directly; indexing is unnecessary.
Compare a fresh design with the current one before deciding what to change.

Use the repository's existing index first. Record its root, revision, indexed languages,
excluded/generated files, and freshness evidence. Refresh only through its authorized
workflow. An index from another branch or before a dirty edit is a lead until reconciled.
Do not install a backend, hook, provider, or always-on instruction block for this task.

**Ready:** the question, source boundary, graph identity and exclusions are recorded.

## Trace and check

Query the smallest neighborhood containing the entry point and responsible owner. Follow
callers and consumers in the direction the relation means. Imports, calls, data flow,
content registration and test coverage are different edges; label each precisely.
Retain source locators and distinguish observed relationships, resolver inference and
proposed relationships. A connection, community, or high degree is not a defect or a
proof of runtime reachability.

Read the source behind each edge that changes the plan. Check unresolved names, dynamic
imports, registries, generated output, configuration and other off-graph consumers by
scoped search and existing checks. Keep unknown edges visible instead of inventing them.
For a reusable evidence snapshot or directional impact query, read
[the local tool contract](references/evidence-graphs.md).

**Ready:** each consequential path has current source evidence or an explicit unknown,
and non-indexed consumers have been checked.

## Change the responsible owner

Choose the first fitting solution: reuse existing behavior, extend its owner, use the
native platform or an installed dependency, then build a small implementation. Refactor
when the current structure blocks clear ownership. A graph does not justify a rewrite.
For each changed owner, trace upstream consumers and attach the existing preservation
check to the invariant it verifies. Include removal and compatibility paths when relevant.
Keep the graph and any private source details out of public outputs unless authorized.

**Ready:** one reviewable change delivers the scoped outcome, with affected consumers
accounted for and checks selected from the actual dependency boundary.

## Verify and close

Exercise the changed path, required gates, and relevant consumers. Reconcile the evidence
graph after edits; retain the pre-change snapshot when comparing impact. Recheck only
invalidated evidence. Report proposed impact separately from measured behavior, and local
proof separately from deployment. Do not claim savings without a matched baseline including
indexing, maintenance, query, source verification and review cost.

Deliver the change, source-bound impact record, checks and unresolved coverage. Leave
publication and live changes at the repository's authorized boundary.

Source scope and intentional departures: [provenance](references/sources.md).
