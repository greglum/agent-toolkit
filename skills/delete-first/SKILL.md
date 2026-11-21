---
name: delete-first
description: Remove dead code or overbuilt layers via blind refutation in a requested module, PR, or repo; propose only unless edits are asked. Never run during normal feature/bug work. Not for refactors (simplify-code), bugs (review-source), AI diffs (audit-ai-code), standards (global-code-review), tests (tune-tests), or git cleanup (repository-cleanup).
compatibility: Needs Git, source access and the repository's own checks. Independent read-only subagents are needed to clear cuts; without them the audit still runs, but refutation is reported as unavailable and nothing is applied. Removing live-code tests, features, contracts, security checks, data or migrations needs explicit approval. `simplify-code` and a harness advisor are optional; without `simplify-code`, the lead does the post-cut pass by hand.
---

# Delete first

Scope the pass strictly to the target the user named (a module, directory, PR, or whole
repository). Never run this pass during ordinary feature or bug work. When the requested scope
is a small module, directory, or PR, keep it single-partition without fanning out across the
rest of the repository; partition and fan out only when the requested target spans a whole
repository or large subtree.

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

0. Verify the named target path exists and matches in-scope files; if not, report the gap and
   stop. If the directory has no Git metadata or history, record `non-Git directory` instead of
   HEAD, branch, and status, skip Git-history checks, and inspect the filesystem directly while
   keeping refutation and proof rules intact.
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

For a small touched scope (one module, directory, or PR), use a single partition and skip
multi-partition fan-out. Otherwise, inventory tracked files once, map every tracked path to
exactly one partition, and keep totals so the report shows nothing was missed. Size large
non-code trees (docs, evidence, generated output, vendored code) before deciding how to cover
them. Give each partition one status: reviewed, skimmed, excluded because it is out of scope,
not run, or blocked.

Before spawning finders, write the shared brief verbatim using
[the brief and record shape](references/briefs.md). If independent read-only subagents are
unavailable, inspect the scoped partition as Lead instead (refutation will be unavailable at
step 4).

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

If independent read-only subagents are unavailable, report refutation as unavailable, classify
every candidate as `Decide`, and apply nothing. Otherwise, send every candidate that could be
applied to a refuter. It searches for dynamic references,
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
- an edit that deletes or rewrites a test, assertion or fixture covering still-live code. Tests and
  fixtures that only exercise the dead code may go with it, unless repository policy requires
  approval to remove tests.
- a security check or other guardrail
- data, a migration, or retained records and evidence
- a surface shared with another repository, a template or published components
- live cloud or Infrastructure-as-Code resource definitions (`*.tf`, DNS records, storage buckets,
  queues, databases, IAM or email policies): static repo call-graph refutation cannot prove a cloud
  resource has no live external consumer; route to live-state ownership checks (and `iac-teardown`
  when retiring IaC)

Before cutting, the lead checks each Cut's claim, paths and every required edit against this list.
Any match moves the whole candidate to Decide. The lead may downgrade a verdict, never upgrade one.

A user's approval settles only the decision it names. The item still needs a refuter's evidence,
edit list and proof before it is applied. Without refutation, report it and apply nothing.

## 5. Cut

Apply cuts only if the user asked for changes. Otherwise stop here and report Cut items as
proposals whose proofs have not run.

Apply Cut items smallest blast radius first, one coherent change per commit-sized group, working
from the refuter's edit list. Order dependent cuts. Before a parallel apply, intersect the cuts'
`required_edits` file sets and give each file one owner. Edit canonical sources, not generated
copies; regenerate them with their script, again after merging the base, and never hand-merge
them. Hold cuts in files that other active work is changing until it lands. Never bypass a gate
that blocks a correct cut. If a size gate blocks an already oversized file, a move-only split in
its own commit may go first; otherwise keep the patch and report the cut as deferred.

For each group of deletions, show its check can fail: leave or add one reference to a deleted name,
see the check fail on that reference, remove the reference and see that failure clear. If this
cannot be shown, revert the group and mark it Decide.

If HEAD moved after refutation, re-run each cut's search and proof at the new HEAD and record it
as already applied (name the commit), still dead or now live. Apply only still-dead cuts; report
the rest as Drop with that reason. When the user has approved retiring a command that callers may
still use, leave a short message that exits nonzero, so an old invocation cannot appear to
succeed. Do not commit, push or open a PR unless the user asked.

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
