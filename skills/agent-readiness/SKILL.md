---
name: agent-readiness
description: Analyze a repository for reliable agent work, make an evidence-backed improvement plan, and implement it with bounded parallel workers. Use to prepare or optimize a codebase for agents. Assessment-only requests produce a plan without repository edits.
compatibility: Needs repository read access and a shell for its native checks. Native subagents enable parallel discovery, disjoint implementation, and independent review; without them, work sequentially and mark independent review unavailable. Use the current harness, model, and settings. Installs no agent framework or external service.
---

# Agent readiness

Run `$agent-readiness` in Codex or `/agent-readiness` in Claude Code, optionally adding
`assessment-only` or a bounded surface.

Make the repository easier to change correctly and easier to verify. The deliverable is a
source-grounded plan with implemented, checked improvements, or an assessment when requested.
More instructions, tests, agents, or tools are not measures of success.

For an optimize request, write the plan and continue through local implementation in the same
run. An analyze, plan-only, or assessment-only request stays read-only: return the plan in the
response or its authorized output location. Repository rules and existing task authority govern
every action. This skill supplies no authority to publish, deploy, spend, change harness
permissions, send source to a new provider, delete tests, or clean up someone else's work.

## 1. Establish the working boundary

Read applicable agent instructions, contributor guidance, architecture, setup, review rules,
and required gates. Identify the repository's language, runtime, package manager, lockfiles,
generated outputs, external services, and local fixture paths from current source.

Record the base/head, dirty and untracked ownership, active worktrees or overlapping changes,
authorized targets, required proof, and material exclusions in the existing task record. Use
an isolated task worktree or the repository's equivalent when work overlaps. A clean checkout
on an old branch is not a current baseline; verify which revision the user intends. Preserve
existing work and credentials. Run no setup step whose writes or external effects are unclear.

Freeze the acceptance conditions before editing. Define observable outcomes for each selected
improvement using repository policy, not a generic score. Set the work and review bounds from
the task and repository. Keep the record resumable: stable item IDs, owner, inspected revision,
status, evidence, and next action. One integrator owns this shared record.

Done when the target revision, ownership, authority, and completion checks are explicit.

## 2. Discover in bounded parallel lanes

Use native subagents for independent questions that can reduce uncertainty. Give each scout
the original request, repository path and revision, applicable instructions, one question,
read-only scope, and a concise return contract: locations, observed behavior, missing proof,
and proposed disposition. Adapt the number of lanes to available slots and repository size;
use a small bounded swarm rather than recursive delegation. Inherit model and effort settings.

Useful lanes, combined when small:

- **Entry and feedback:** cold setup, local fixture access, focused checks, full gates,
  diagnostics, reproducibility, and documentation that disagrees with executable commands.
- **Ownership and invariants:** trace important flows, boundary validation, representable
  states, shared owners, generated artifacts, and dangerous operations. Use the
  [reliability reference](references/reliability.md) for this lane.
- **Coordination:** instruction routing across the requested harnesses, stale workflows,
  safe parallel edits, review independence, and evidence tied to the tested source.

Scouts do not edit or start another swarm. The parent checks their claims against original
source and actual commands before accepting them. A worker summary is a lead, not evidence.
Unavailable commands stay unavailable; record the observed error rather than inferring a
product defect. Distinguish source inspection, local execution, hosted checks, and live proof.

Done when every examined area has located evidence and a disposition: retain, improve,
blocked, or outside scope. List unexamined areas; do not imply whole-repository coverage.

## 3. Plan around existing owners

For each candidate, name the concrete failure or repeated cost, current owner, affected
callers, evidence, proposed change, preservation conditions, and smallest sufficient proof.
Rank by material impact and effort. Reject cosmetic process additions and fixes already
enforced by the current tree. State briefly what a fresh design would do differently; prefer
it only when correctness, ownership, and transition cost support the change.

Choose the first fitting option:

1. Reuse existing behavior and its checks.
2. Extend the responsible module, type, schema, generator, or repository workflow.
3. Use the standard library, native constraint, or installed dependency.
4. Add a small implementation where the invariant belongs.
5. Refactor coherently when existing ownership prevents the correct change.

Keep commands and feature recipes with the project. Use `app-verifier` when the missing
deliverable is a repeatable app verification record; use `encode-correction` for a known
recurring mistake; use `codebase-metrics` for a requested scored baseline. Those workflows
do not replace this repository-wide plan or its integration. Read an available skill only
when its branch is needed; otherwise perform the narrow work directly.

Record the plan in the task record before edits. Mark each item selected, retained, deferred
with reason, or blocked with the exact missing decision or access. Record discretionary choices
and confidence, least confident first. Continue selected authorized local work without an
extra plan-approval pause. Pause only the dependent operation when authority or a material
decision is missing; continue independent work.

Done when every selected item has an owner, bounded scope, acceptance, and proof command.

## 4. Implement through disjoint ownership

Give builders non-overlapping files or isolated worktrees, the original requirement,
accepted item IDs, invariants, and proof. The parent owns integration, shared manifests,
instruction indexes, and the task record. Workers return changed paths, exact checks and
statuses, unresolved decisions, and the revision or baseline they read. Do not let workers
edit a shared file concurrently or overwrite another lane's output.

Trace callers and trust boundaries before changing behavior. Keep valid examples close to
the owner so the next agent can copy the right pattern. Extend existing checks before adding
a second checker, hook, policy table, verification framework, or token system. Keep always-loaded
instructions short and route conditional procedures to their existing owner.

Preserve security, privacy, accessibility, error handling, rollback, concurrency, and public
contracts. Keep move-only refactors separate from behavior changes where the repository
requires it. Add tests only when they satisfy its test-value policy; retain existing tests
and gates. A proposed new dependency or external service needs a demonstrated gap and the
authority required by the repository.

Before integration, compare each worker's baseline with current owned files. On a conflict,
re-read and reconcile once against original requirements; if ownership remains unclear,
stop that item and ask. Never resolve by taking an entire worker version blindly.

Done when every selected item has an integrated change or an explicit blocked disposition.

## 5. Verify and review the resulting tree

For each mechanical correction, demonstrate that a representative bad input or forbidden
state fails for the intended reason and the valid case passes. Keep destructive or mutation
probes in task-owned scratch space. Then run the closest preservation checks and required
repository gates. Reuse results only while the tested source and environment remain valid.
Keep full logs locally when needed and return bounded results with producer exit statuses.

Use fresh independent reviewers, separate from implementers, against the resulting diff and
identified base. Supply the original request, sources, acceptance, repository review rules,
and proof locations, without the desired verdict. Include dedicated security coverage when
the repository's risk rules require it. Verify every finding, fix or answer it, and rerun
affected checks after changes. Follow repository review limits; if none exist, allow two
review-and-fix rounds, then report unresolved findings and the exact next decision. Never
claim an unavailable independent review passed.

Refresh the base as repository policy requires. A material base change invalidates affected
checks and review. Report PASS, FAIL, UNAVAILABLE, and NOT RUN separately, each tied to the
tested revision or dirty-tree fingerprint. Docs-only proof does not establish runtime behavior;
local fixtures do not establish production behavior or model quality.

Done when every acceptance condition has passing evidence or a named unresolved blocker,
and dependent delivery is held on any required failure or missing proof.

## Report and stop

Return the plan/record path, changed owners and why, retained or rejected ideas, check and
review results, unresolved limits, and delivery state. Account for every selected item and
identify any unexamined scope. Keep the user's external delivery boundaries intact.

A successful application shows checked improvements on this repository. Claims of faster
work, lower cost, better automatic skill selection, or general quality gains require a
separate comparable evaluation; file counts, shorter prompts, and swarm size prove none.
