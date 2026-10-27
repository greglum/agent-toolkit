---
name: tune-tests
description: "Audit, prune, or speed up an existing test suite without losing failure detection. Audit mode scores every in-scope test and returns a ledger without edits. Speed mode makes behavior-preserving speedups with measured before and after timings. Prune mode proposes removals and deletes only ledger items the user approves. Use when a suite is slow, flaky, bloated, or due for a value review."
disable-model-invocation: true
arguments:
  - name: mode
    description: "audit, speed, or prune (default: audit when unclear)"
  - name: scope
    description: "Test files or directories (default: the suite the request names)"
---

# Tune tests

Keep every realistic failure the suite catches today. Only then aim for fewer or faster
tests. Load [references/ledger.md](references/ledger.md) before step 3.

## 1. Ground the run

Pick the mode:

- **Audit:** audit, review, check, or an unclear request. Write the ledger. Edit nothing.
- **Speed:** "make it faster", "too slow". Edit tests without changing what they assert.
  Delete nothing.
- **Prune:** remove, trim, or consolidate tests. Propose removals, then stop for approval.

Read repository instructions, test policy, runner configuration, and CI scripts. Record the
test command, any value score or threshold the repository defines, its removal rules, branch,
HEAD, and dirty paths. A project skill or policy that owns test cleanup takes precedence.

Done when mode, scope, command, and policy (or "none found") are recorded.

## 2. Measure the baseline

Run the narrowest command that owns the scope. Record exit code, test count, wall time, and CPU
time (the runner's report, or a time wrapper). Collect per-file or per-test durations to rank
where time goes. When the runner runs files in parallel, wall time follows the slowest file, not
the sum. Collect coverage, or mutation results where the repository has them.

Record baseline failures apart. A flaky or failing test is a defect to root-cause at its
owner. It is not evidence for removal, skip, or quarantine.

Done when the baseline numbers, their machine and load conditions, and failures are written.

## 3. Build the ledger

Read every in-scope test in full and judge its assertions, not its name. Score a disabled or
skipped test only after running it enabled in a scratch copy outside the repository. Give each test or
coherent group a stable ID. Score it on regression likelihood, impact, unique detection, and
reliability or maintenance cost, using the repository's threshold when it has one. Name the
check that would catch the same regression if this test were gone.

Never propose removing the only check for a reachable harmful failure. Removal needs named
overlap evidence.

In speed mode the ledger covers the slow items you inspect, so a slow low-value test can be
proposed for removal instead of tuned; there, the inspected items are the scope. Done when every
in-scope test has an ID, a score, and a candidate disposition. In audit mode, report the ledger
and stop.

## 4. Speed up (speed mode)

Work from the slowest measured items down. Apply only changes that keep the assertion intact:

- **Timing matches the assertion.** When the assertion reads a resulting value or payload,
  drop per-keystroke delays and paste or fill instead of typing. Keep the default yield when
  the assertion depends on a render between two events, like a double press or a filter that
  narrows per keystroke.
- **Scoped queries.** Query within the nearest stable container (row, toolbar, dialog)
  instead of sweeping the whole page by accessible name. Keep absence and uniqueness checks
  page-wide.
- **Wait on the outcome.** Replace a sleep or a race with a wait on the observable result,
  then re-query rather than hold a stale node.
- **Lightest environment.** Run a test in the cheapest environment its assertions need.

When a change could let a test pass vacuously, break the behavior in a scratch copy, confirm
the test still fails for the intended reason, and restore it.

Measure before and after interleaved (A, B, A, B) on the same machine under the same load,
at least three runs each. Report wall and CPU ranges with those conditions. A change inside the
measured noise range is not a speedup, and the faster run must execute the same number of tests
as the baseline.

Use [performance evidence](references/performance-evidence.md) before calling a timing
difference a speedup. Done when each change has comparable before and after numbers,
verified work counts and outcomes, and the scoped suite passes.

## 5. Prune (prune mode)

Present the ledger's removal candidates as a short list with IDs, exact cases, overlap
evidence, and coverage tradeoffs. Then stop. Removal is its own approval boundary.

The user may approve in plain English ("all except the parser ones"). Map that to IDs
yourself and echo the mapping. Approving the skill, a directory, a goal, or a quota approves
no item. New candidates and unresolved items stay unapproved. Ask when the selection is
ambiguous.

Before applying, recheck HEAD and the evidence. Changed evidence needs a revised proposal.
Apply only approved IDs. Re-run the suite and coverage or mutation, and compare test discovery
before and after.

Done when every removal carries an approval ID and the before and after evidence is recorded.

## Never

Never weaken an assertion, broaden a mock, add a retry or sleep, skip, quarantine, disable,
or update a snapshot to get green or fast. This skill authorizes no commit or push.

## Finish

Report the ledger with every in-scope test dispositioned: kept, sped up, proposed for
removal, or removed with its approval ID. Include measured timings with conditions, coverage
or mutation before and after, suite pass evidence, and checks that were not run.
