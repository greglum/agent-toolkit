---
name: polish-animations
description: >-
  Run the whole animation loop on a web app with parallel subagents: find opportunities,
  build each with animate, then review and fix in bounded rounds until no Block findings
  remain, and verify in the running app. Explicit only. Edits code in the current workspace;
  never commits. Arguments: an optional scope path, max=N rows, rounds=N, or plan-only.
disable-model-invocation: true
compatibility: Requires find-animation-opportunities; building also requires animate and review-animations, source access, and the project's verification tools. Subagents and ui-motion are optional. Installing this bundle alone does not include companions. Report missing companions without installing them; deliver source-only planning when possible and mark the other phases blocked.
---

# Polish animations

Orchestrate `find-animation-opportunities`, `animate`, and `review-animations` across an
application. You are the parent: you bind scope, split work, recheck claims, and integrate.
Workers do the domain work by invoking those skills. Planning needs
`find-animation-opportunities`; building also needs `animate` and `review-animations`.
Check availability before each required phase. If a companion is missing, name it and the
blocked phase; do not replace its missing result with approval. `ui-motion` is optional and
supplies the rendered review method; otherwise use the project's verification workflow.

## Arguments and authority

- `scope`: a path or surface name; default is the app's interactive UI.
- `max=N`: rows to build, default 5, at most 7.
- `rounds=N`: review rounds per row, default 3, at most 3.
- `plan-only`: source-only discovery and a ledger; no implementation preflight.

Use the current task's authority for reading, scoped local edits, and local checks. Reuse
authority already given for an identified action and target; ask only for missing authority
or a material decision. This workflow ends with uncommitted changes. Publication, dependency
installation, deployment, and test removal retain their own task and repository requirements.

With `plan-only`, read current source and applicable instructions, then perform Discover and
Report. Read-only native Git inspection and task-owned scratch notes are permitted. Skip
fetch, checkout/worktree changes, installs, gates, tests, browser actions, and product edits.
Report those checks as not run. Do not enter the implementation preflight below.

## State file

Keep run state in `polish-animations/state.md` under the directory that
`git rev-parse --git-dir` prints, so it is never committed. Without Git, use the harness
scratchpad and say so. It holds the base revision, scope, preflight facts, source identity,
the ledger with a status per row (`accepted`, `building`, `reviewing`, `approved`, `blocked`,
`unresolved`, `dropped`), finding dispositions, round log, and check results. Update it at
the end of each phase and each row transition.

For a new or resumed run, follow [source identity and resume](references/resume.md). Bind
each row's evidence to its owned source and relevant shared inputs, including dirty tracked
and untracked content, dependencies, configuration, tokens, and primitives. A matching base
and scope alone never preserves approval. Recheck identity before reusing a row's evidence
and after integrating a change that can affect other rows.

## Workers

- Give each worker one self-contained task: the skill to invoke, the original evidence (the
  ledger row or finding text verbatim, file paths, preflight facts), the files it owns, and
  what to return. Never pass another worker's summary as evidence.
- Ask each worker to mark anything it could not confirm and say where it looked.
- A reviewer never reviews its own build. Keep at most four workers running at once.
- In Claude Code use subagents, with worktree isolation for parallel builders when offered.
  In Codex use its subagent support. With no subagent capability, run each phase yourself in
  order, re-reading the diff cold before each review, and report the review as same-agent,
  not independent.

## Phases

1. **Implementation preflight.** Skip this phase in `plan-only`. Confirm this is an application
   workspace: a package manifest with a UI framework and source for the scope. If not, stop
   and say so. Resolve the requested branch and base. Refresh or isolate the checkout within
   the task's existing authority, preserving local work; never substitute a different branch
   for one the user selected. Label remote state unverified when it cannot be checked. Read
   the repository instructions, design system, motion tokens and runtime, reduced-motion policy, the
   verification workflow, and the required gates. Record files already dirty; never edit or
   revert them outside a row's owned lines. Run the required gates once and record existing
   failures so they are not attributed to this run. Stop work that depends on a failed gate;
   independent diagnosis and planning may continue. Done when the state file holds these facts
   and the source manifest.
2. **Discover.** For one view or a small app, invoke `find-animation-opportunities` yourself.
   Otherwise split the scope by app area across up to four read-only workers, each invoking
   that skill on its area with the preflight facts and returning ledger rows only. Recheck
   every returned row at its `file:line`, merge duplicates and rows that share an owner, and
   cap at `max`. Keep every rejected candidate. In `plan-only`, first read the applicable
   instructions, design owners, and scoped source directly; use those facts instead of
   implementation preflight results. Write the ledger to the state file and show it to the
   user. With `plan-only`, report and stop. Otherwise continue with the ranked rows; a
   user who is present may narrow them.
3. **Settle shared decisions.** Before any build, decide every new token the rows need and
   which file owns it. Record these in the state file and pass them to every builder, so no
   two workers invent the same token.
4. **Build.** Group rows whose owned files overlap; a group runs serially in one worker.
   Disjoint groups may run in parallel workers in isolated worktrees, merged back one at a
   time. An isolated worktree must start at the run's base revision with the same
   uncommitted state; harness isolation often cuts from the default branch, so have each
   worker confirm its row's cited code before building. Take each worker's diff yourself when
   its sandbox blocks Git. Without that, build one group at a
   time in the current checkout. Each builder invokes `animate` with its
   row verbatim, the preflight facts, the shared decisions, and its owned files. Its own
   `review-animations` call in `animate` is a pre-check; the independent review in phase 5
   decides. It returns the diff, its choices ledger, and checks run. Done when every accepted row is `reviewing`,
   `dropped` (the gate rejected it), or `blocked` with a stated reason.
5. **Review rounds.** For each row, a fresh worker invokes `review-animations` on that row's
   diff with the row text. Recheck each Block and Fix finding at its location. Give every
   finding a stable ID and a disposition: accepted with evidence, refuted with contrary
   evidence, or unresolved with the missing evidence or disagreement. Missing source or a
   disputed interpretation never refutes a finding. Keep feel questions visibly unverified.
   A row with an unresolved material finding remains `unresolved`, not approved. Send accepted
   findings verbatim to a builder invoking `animate`, then review again. A row is `approved` at zero
   confirmed Block findings, no unresolved material finding, and Fix findings fixed or listed.
   A verified finding that says the motion should not exist drops the row and removes its
   edits. If Block findings remain after
   `rounds`, save the row's diff as a patch beside the state file, revert only this run's
   edits for that row, and mark it `blocked`.
6. **Integrated review.** One worker invokes `review-animations` on the whole run's diff for
   cross-cutting problems: mixed timing families, simultaneous motions competing, reduced-motion
   gaps, token drift. Fix confirmed Block and Fix findings in one more round under the same
   rules, retaining unresolved findings. Reconcile affected rows against the source manifest
   before reusing approvals; a shared change can invalidate rows outside its edited files.
7. **Verify.** Run the required gates and compare with the preflight baseline. Run the app
   through its verification workflow, or `ui-motion`'s rendered review, and exercise every
   approved row: normal speed, rapid repeat and reversal, reduced motion, keyboard, and the
   narrowest supported width. A failure reopens that row for one fix round. Anything you
   cannot run is listed as unverified.
8. **Report.** Put first what needs the user: blocked or unresolved rows, their saved patches
   where present, the exact missing evidence, and feel checks only a person can make. Then
   the ledger with final statuses, rejected
   candidates, files changed, rounds and findings fixed per row, the combined choices ledger
   (least confident first), and every check as passed, failed, or not run. Name the state file.
   Include every finding's disposition and any invalidated evidence. For `plan-only`, state
   source-only coverage and the implementation checks not run. Leave changes uncommitted.

Finish with every accepted row and finding accounted for and the report delivered. Claim the
requested polish complete only when every retained row is approved, integrated review has no
Block or unresolved material finding, and required verification passes. Otherwise report the
remaining work as incomplete, with its saved state and next bounded action.
