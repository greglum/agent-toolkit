---
name: polish-animations
description: >-
  Run the whole animation loop on a web app with subagents: find opportunities, build each
  with animate, then review and fix in bounded rounds until no Block findings remain, and
  verify in the running app. Explicit only. Edits code in the current workspace; never
  commits. Arguments: scope path, max=N rows, rounds=N, or plan-only. Not for fixing one
  broken transition or stutter (ui-motion), building a single request (animate),
  discovery-only sweeps (find-animation-opportunities), or read-only audits
  (review-animations).
disable-model-invocation: true
compatibility: >-
  Requires find-animation-opportunities; building also requires animate and review-animations,
  source access, and the project's verification tools. Subagents and ui-motion are optional.
  Installing this bundle alone does not include companions. Report missing companions without
  installing them; deliver source-only planning when possible and mark the other phases
  blocked or unavailable.
---

# Polish animations

Explicit-only orchestrator (`/polish-animations` in Claude Code, `$polish-animations` in
Codex) for `find-animation-opportunities`, `animate`, and `review-animations`. You are the
parent: you bind scope, split work, recheck claims, and integrate. Workers execute the domain
work through those skills without duplicating their procedures here.

Before each phase, check companion availability:
- **Discover** requires `find-animation-opportunities` (`#procedure`, `#ledger-format`). If
  absent, name it, stop Discover, and mark Discover and downstream phases `unavailable` /
  `blocked`.
- **Build and Review** require `animate` (`#sequence`, `#output`) and `review-animations`
  (`#procedure`, `#output`). If either is absent, allow `plan-only` discovery when
  `find-animation-opportunities` is present, then stop before Build, name the missing
  companion(s), and mark Build and Review `unavailable` / `blocked`.
- **Verify** optionally uses `ui-motion` (`references/rendered-review.md`). If absent, run
  the project's verification workflow directly and record `ui-motion` as `unavailable`.

## Arguments and authority

- `scope`: a path or surface name; default is the app's interactive UI.
- `max=N`: rows to build, default `5`, integer `1` to `7`.
- `rounds=N`: review rounds per row, default `3`, integer `1` to `3`.
- `plan-only`: source-only discovery and report mode.

Stop with a clear error before preflight or discovery if `max` or `rounds` is out of range,
an unrecognized argument is passed, or a named `scope` path does not exist.

With `plan-only`, read applicable instructions, design owners, and scoped source directly
(read-only native Git inspection and task-owned scratch notes permitted), then run only
**Discover** and **Report**. Skip Implementation preflight, Settle shared decisions, Build,
Review rounds, Integrated review, Verify, checkouts, installs, gates, browser actions, and
product edits, and report implementation checks as `not run`.

Use the current task's authority for reading, scoped local edits, and local checks. Reuse
authority already given for an identified action and target; ask only for missing authority
or a material decision. This workflow leaves changes uncommitted. Publication, dependency
installation, deployment, and test removal retain their own task and repository requirements.

## State file

Keep run state in `polish-animations/<run-id>/state.md` under the directory that
`git rev-parse --git-dir` prints, so it is never committed. Give each task a distinct simple
run ID and create its directory exclusively; a collision requires another ID, never replacing
existing state. To resume, select the original run ID explicitly rather than the newest file.
Without Git, use a task-specific harness scratchpad and say so. It holds the base revision,
scope, preflight facts, source identity, the ledger with a status per row (`accepted`,
`building`, `reviewing`, `approved`, `blocked`, `unresolved`, `dropped`), finding
dispositions, round log, and check results. Update it at the end of each phase and each row
transition.

For a new or resumed run, follow [source identity and resume](references/resume.md) to
capture and reconcile the source manifest before reusing any row's approval or evidence.

## Workers

- Give each worker one self-contained task: the skill to invoke, the original evidence (the
  ledger row or finding text verbatim, file paths, preflight facts), the files it owns, and
  what to return. Never pass another worker's summary as evidence.
- Ask each worker to mark anything it could not confirm and say where it looked.
- A reviewer never reviews its own build. Use the available worker slots within the harness
  cap, counting the parent toward that cap.
- Use native subagents with isolated worktrees when the harness supports them; otherwise run
  each phase sequentially in order, re-reading the diff cold before each review, and report
  the review as same-agent, not independent.

## Phases

1. **Implementation preflight.**
   - **Workspace check:** confirm a web application workspace with interactive UI source for
     the scope (e.g., package manifest or static HTML/CSS/JS entrypoints); otherwise stop and
     say so.
   - **Checkout and owners:** resolve the requested branch and base within existing
     authority, preserving local work without substituting a different branch. Label remote
     state unverified when unchecked. Read repository instructions, design system, motion
     tokens and runtime, reduced-motion policy, verification workflow, and required gates.
   - **Baseline:** record files already dirty (never edit or revert them outside a row's
     owned lines), run the required gates once, and record pre-existing failures. Stop work
     that depends on a failed gate; independent diagnosis and planning may continue.
   - **Exit:** state file holds preflight facts, baseline gate results, and the source
     manifest from [source identity and resume](references/resume.md).
2. **Discover.** For one view or a small app, invoke `find-animation-opportunities`
   (`#procedure`, `#ledger-format`) yourself. Otherwise split the scope by app area across
   available read-only worker slots, each invoking that skill with the preflight facts and
   returning ledger rows only. Recheck every returned row at its `file:line`, merge
   duplicates and rows sharing an owner, and cap at `max`. Keep every rejected candidate.
   Write the ledger to the state file and show it to the user. In `plan-only`, continue to
   Report; otherwise proceed with the ranked rows (a present user may narrow them).
3. **Settle shared decisions.** Before any build, decide every new token the rows need and
   which file owns it. Record these in the state file and pass them to every builder, so no
   two workers invent the same token.
4. **Build.**
   - **Partition:** group rows whose owned files overlap to run serially in one worker; run
     disjoint groups in parallel isolated worktrees when supported, merged back one at a time,
     or sequentially in the current checkout otherwise.
   - **Isolate and verify base:** confirm every worktree starts at the run's base revision
     with identical uncommitted state and each worker verifies its row's cited code before
     editing. Pull each worker's diff manually if its sandbox blocks Git.
   - **Execute:** each builder invokes `animate` (`#rules`, `#sequence`, `#output`) with its
     row verbatim, preflight facts, shared decisions, and owned files (its inline
     `review-animations` call is a pre-check; Phase 5 decides). It returns the diff, choices
     ledger, and checks run.
   - **Exit:** every accepted row is `reviewing`, `dropped` (gate rejected it), or `blocked`
     with a stated reason.
5. **Review rounds.**
   - **Inspect:** for each row, a fresh worker invokes `review-animations` (`#procedure`,
     `#output`) on that row's diff with the row text. Recheck each Block and Fix finding at
     its location.
   - **Disposition:** assign every finding a stable ID and status: `accepted` with evidence,
     `refuted` with contrary evidence, or `unresolved` with the missing evidence or
     disagreement. Missing source or disputed interpretation never refutes a finding; keep feel
     questions visibly unverified.
   - **Iterate:** send accepted findings verbatim to a builder invoking `animate` (`#sequence`),
     then review again up to `rounds`. A verified finding that the motion should not exist
     drops the row and reverts only this run's edits for it.
   - **Exit:** mark a row `approved` at zero confirmed Block findings, no unresolved material
     finding, and Fix findings fixed or listed; mark `unresolved` if a material finding
     remains open; if Block findings remain after `rounds`, save the row's diff as a patch
     beside the state file, revert only this run's edits for that row, and mark it `blocked`.
6. **Integrated review.** One worker invokes `review-animations` (`#procedure`, `#output`) on
   the whole run's diff for cross-cutting problems: mixed timing families, simultaneous
   motions competing, reduced-motion gaps, token drift. Fix confirmed Block and Fix findings
   in one more round under the same rules, retaining unresolved findings. Reconcile affected
   rows against [source identity and resume](references/resume.md) before reusing approvals.
7. **Verify.** Run the required gates and compare with the preflight baseline. Run the app
   through `ui-motion` (`references/rendered-review.md`) when installed, or the project's
   verification workflow otherwise, and exercise every approved row: normal speed, rapid
   repeat and reversal, reduced motion, keyboard, and narrowest supported width. A failure
   reopens that row for one fix round. Record unrun checks distinctly.
8. **Report.** Put first what needs the user: blocked or unresolved rows, their saved patches
   where present, exact missing evidence, and feel checks only a person can make. Then report
   the ledger with final statuses, rejected candidates, files changed, rounds and findings
   fixed per row, the combined choices ledger (least confident first), finding dispositions,
   invalidated evidence, and the state file path. Report every check with command/exit
   status distinctly as `passed`, `failed`, `unavailable`, or `not run`. Leave changes
   uncommitted.

Finish with every accepted row and finding accounted for and the report delivered. Claim the
requested polish complete only when every retained row is `approved`, integrated review has no
Block or unresolved material finding, and required verification passes. Otherwise report the
remaining work as incomplete, with its saved state and next bounded action.
