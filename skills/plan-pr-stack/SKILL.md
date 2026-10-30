---
name: plan-pr-stack
description: Plan dependency waves for a set of pull requests from a revision-bound snapshot. Use for stack ordering, overlap decisions and unresolved dependencies. Produces a read-only plan; it does not assess merge readiness or land changes.
compatibility: The bundled offline planner requires Python 3.10+. Live collection needs an authorized read-only repository connector or GitHub CLI. Without live access, use a supplied snapshot and report its age and missing evidence. No installation, Git mutation or GitHub write is required.
---

# Plan a PR stack

Return dependency waves with evidence for every edge and visible gaps. Use this for a set
of PRs; a single-PR readiness check belongs to the repository's delivery workflow.

1. Bind the target repository, selected PR numbers, observation time and requested finish.
   Read the repository's stacking and delivery rules. Planning authorizes reads of the
   identified targets, without granting publication or merge authority.
2. Read [the snapshot contract](references/snapshot.md) before collecting input. Capture full
   head and base repository, branch and SHA identities. Resolve declared dependencies from
   source evidence, including PRs outside the selected set. Preserve missing values as null.
3. Run `python3 <skill-dir>/scripts/plan_stack.py snapshot.json`. Inspect unresolved external
   dependencies, unknown identity or file coverage, and cycle witnesses before using waves.
   Exit 1 means incomplete evidence or ordering; exit 2 means invalid input or a read failure.
4. Inspect shared contracts, migrations, generated artifacts and workflows beyond identical
   file paths. Add only evidenced `orderings` for required sequencing. File overlap alone
   has no direction. Explain the chosen order; never derive it from PR number. Re-run after
   changing the snapshot. Keep independent work independent.
5. Deliver the input snapshot and generated JSON, edge reasons, candidate waves, unresolved
   decisions and unknowns. A wave describes known dependency order, not safe parallel merges.
   Refresh identity and invalidated evidence after any head/base or dependency change. Hand
   off actual landing to the repository's live review, checks, protection and queue gates.

The bundled tool reads only its input file and writes JSON to stdout. It performs no Git or
network operations. It does not infer semantic coupling, parse PR prose, judge reviews,
validate test execution, restack branches, operate a merge queue or estimate savings.

Source context and intentional limits: [sources](references/sources.md).
