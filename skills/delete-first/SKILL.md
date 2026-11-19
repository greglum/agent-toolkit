---
name: delete-first
description: Find and remove dead code or overbuilt layers, with independent refutation before any edit. Use when asked to clean up, delete from, or simplify a module, directory, PR, or repository. Reports proposals unless changes were requested. For behavior-preserving cleanup use simplify-code; for defects use review-source.
compatibility: Needs Git, source access and the repository's own checks. Independent read-only subagents are needed to clear cuts; without them the audit still runs, but refutation is reported as unavailable and nothing is applied. Removing live-code tests, features, contracts, security checks, data or migrations needs explicit approval. `simplify-code` and a harness advisor are optional; without `simplify-code`, the lead does the post-cut pass by hand.
---

# Delete first

Scope the pass to match how it was triggered:

- **Touched scope (automatic):** When the user asks to clean up, delete from, or simplify a
  module, directory, or PR, work only there, without fanning out across the whole repository.
  Do not start this pass during ordinary feature or bug work.
- **Whole-repo sweep (explicit or scheduled):** Run full repository partitioning and parallel
  finder fan-out only when explicitly requested for a whole repository or named subtree, or on
  an approved scheduled sweep.

Ask what the product would need if it were built today, then find the rest. Work down the ladder:
**delete**, then **simplify what remains**, then **simplify what should have been simple from the
start**. Report optimization and automation ideas, but do not build them in this run. Live users
depend on the result, so every cut carries proof, not confidence.

## Roles

- **Lead:** the main session. It owns scope, the ledger, every decision and every write. It never
  accepts a worker claim it has not checked. If the harness offers a stronger model as an advisor,
  consult it when freezing the contracts and before applying cuts.
- **Finders:** read-only subagents, one per partition. They return candidates, never edits.
- **Refuters:** read-only subagents in fresh context. Each gets claims and paths, not the
  finder's reasoning, and tries to prove each cut unsafe.

Inherit the user's model settings unless the user or the harness routing rules say otherwise, and
record which model each role ran on. Without independent workers, the lead may do the finding
itself, but it cannot refute its own findings: report refutation as unavailable and classify every
candidate as Decide.

## 1. Freeze the target and the baseline

If the user did not ask for changes, run no project script or check unless it is known not to
write, report the rest as not run, and keep the ledger outside the checkout.

1. Record the HEAD SHA, branch and `git status --short`. Exclude dirty paths you did not create,
   and paths that active branches or other sessions are changing.
2. Read the repository's agent instructions, product and architecture docs, test policy and
   any ownership or "do not touch" rules. These are contracts, not candidates.
3. Find what lives outside this tree's call graph: other repositories that copy these paths, a
   template it syncs with, published components, generated files and their generators.
4. Read recent history for earlier cleanup or audit work, so you do not redo it.
5. Run the repository's standard checks before editing, and record each as passed, failed,
   unavailable (it cannot run here) or not run (withheld for an audit-only request). A failing baseline is a finding; it is not something the cuts may hide. A cut that
   depends on an unavailable check is Decide.
6. Keep a ledger file in the scratch or temp area the repository already ignores. Write the
   target, partitions, each worker's result as it returns, decisions and check results to it. An
   interrupted run resumes from the ledger.
7. Check remaining usage if the harness shows it. Reduce concurrency to fit, never coverage.

## 2. Partition and brief

Inventory tracked files once. Map every tracked path to exactly one partition, and keep the
totals so the report can show nothing was missed. Size large non-code trees (docs, evidence,
generated output, vendored code) before deciding how to cover them. Give each partition one
status: reviewed, skimmed, excluded because it is out of scope, not run, or blocked.

Before spawning, write the shared brief that every finder receives verbatim. Use
[the brief and record shape](references/briefs.md).

## 3. Find

Spawn one finder per partition in parallel. Each asks two questions of its partition:

1. **What can be deleted entirely?** Dead code, unused exports and scripts, retired features,
   stale docs, duplicated owners, configuration nobody sets.
2. **What should have been simple from the start?** Abstractions with one caller, wrappers that
   only delegate, hand-rolled versions of platform or library features, and assumptions that no
   current requirement supports.

For each assumption a design rests on, ask what evidence supports it today. "We might need it",
age, or effort already spent is not evidence. If a finder withheld candidates at the record cap,
split its partition and run the parts.

## 4. Refute

Send every candidate that could be applied to a refuter. It searches for dynamic references,
external consumers, and the tests or incidents that explain the code. It reads the closest
regression tests, failure paths and state transitions, including leaving and returning to a prior
state. It also lists every edit the change really needs, because a finder's path list is usually
short. Classify each candidate once:

- **Cut:** the candidate's own refuter returned `cut`, with evidence, the full edit list, a proof,
  and nothing unverified that touches it. For a deletion, the proof is a reference search shown to
  find a known use of the same kind, plus a build, type, import, link or test check that should
  fail if a reference remains. Without such a check, it is Decide.
- **Decide:** any item on the list below, split evidence, a missing verdict on an applicable
  candidate, or anything still unclear after one refutation pass. The user decides.
- **Drop:** unsafe, intentional, generated, already handled, untrue or preference only.

These are always Decide:

- user-visible behavior, or a public, wire, URL or command contract
- a test file, case or assertion covering still-live code, or a fixture still-live tests depend on (deleting dead production code together with tests or fixtures that exclusively exercise that dead code is eligible for Cut once refuted, provided every assertion covering still-live code is preserved and repository policy does not require approval for test removal)
- a security check or other guardrail
- data, a migration, or retained records and evidence
- a surface shared with another repository, a template or published components

Before cutting, the lead checks each Cut's claim, paths and every required edit against this list.
Any match moves the whole candidate to Decide. The lead may downgrade a verdict, never upgrade one.

A user's approval settles only the decision it names. The item still needs a refuter's evidence,
edit list and proof before it is applied. Without refutation, report it and apply nothing.

## 5. Cut

Apply cuts only if the user asked for changes. Otherwise stop here and report Cut items as
proposals whose proofs have not run.

Apply Cut items smallest blast radius first, one coherent change per commit-sized group, working
from the refuter's edit list. Order dependent cuts. Edit canonical sources, not generated copies,
and regenerate them. Hold cuts in files that other active work is changing until it lands. If a
repository gate blocks a correct cut, do not bypass it: keep the patch and report the cut as deferred.

For each group of deletions, show its check can fail: leave or add one reference to a deleted name,
see the check fail on that reference, remove the reference and see that failure clear. If this
cannot be shown, revert the group and mark it Decide.

If HEAD moved after refutation, re-run each cut's search and proof at the new HEAD before applying
it. When the user has approved retiring a command that callers may still use, leave a short message
that exits nonzero, so an old invocation cannot appear to succeed. Do not commit, push or open a PR
unless the user asked.

## 6. Simplify what remains

Now that the cuts exist, look once more at the paths they touched for indirection, flags, branches
and parameters that only served the deleted parts. Use `simplify-code` in dry-run mode when it is
available; otherwise do this pass by hand, preserving behavior. Each result is a new
candidate: send it through step 4 before applying it. Then stop.

## 7. Prove

Rerun the baseline checks and each cut's proof. A check that ran no tests, was cached or skipped,
or hid its exit code did not run. Read the full diff. If a cut breaks a check, revert that cut
rather than patching around it.

## Report

Start with **Complete** or **Incomplete**. The run is incomplete if any partition is not run or
blocked, a split did not recover a finder's withheld candidates, or any candidate other than an
`idea` lacks a verdict; name the resume point.
Then lead with what was removed and the net change, or with the proposed cuts if none were applied.
Group Decide items by the question that settles them, so the user answers a few questions rather
than dozens, with the largest first. Then give candidate, Cut, Decide and Drop counts, Drop totals
by reason, optimization and automation ideas, checks that passed, failed, were unavailable or did
not run, partition totals with their statuses, and whether refutation ran. If little survived refutation, say so;
never pad the result.
