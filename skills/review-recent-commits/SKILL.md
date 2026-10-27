---
name: review-recent-commits
description: >-
  Review recent or named Git commits against repository rules and current file
  state. Use for an evidence-based, read-only APPROVE/REVISE/REVERT verdict on
  committed work. Use review-pending-changes for uncommitted work and review-pr
  for a PR or branch diff.
disable-model-invocation: true
allowed-tools: Bash(git diff *), Bash(git log *), Bash(git show *), Bash(git rev-parse *), Bash(git rev-list *), Bash(git diff-tree *), Bash(git status *), Bash(git branch --show-current), Bash(git branch -r *), Read, Glob, Grep
arguments:
  - name: count
    description: "Number of newest commits to review (default: 2)"
  - name: hash
    description: "One or more commit hashes or revisions to review instead"
---

# Recent Commits Assessment

Review immutable commit snapshots and their net effect in the current repository.
Edit nothing.

## Input and boundaries

- With no argument, review the newest two commits reachable from HEAD.
- A positive integer selects that many newest commits. One or more explicit Git
  revisions select those commits instead. Resolve every selection to a full SHA and
  keep that immutable list in the report.
- Review committed history only. Use review-pending-changes for uncommitted work
  and review-pr for a PR or branch-wide diff. For a persisted multi-axis audit of
  merged work, use a repository's own audit of merged work, when one exists.
- This workflow is assessment-only. Do not edit files, change the index or refs,
  fetch, checkout, reset, amend, revert, commit, push, or post review comments.
  Do not run build or test commands unless the user separately authorizes them;
  they may mutate caches or generated files.
- Order governs presentation, never disclosure. Report a security, data-loss, or credential
  finding as soon as it is found, even though later steps are unfinished. A credential-shaped
  literal counts even when it looks fake; in a single final reply, lead with it.

## 1. Establish immutable scope

Capture repository and worktree state before reviewing, and resolve the selection, with the
commands in [`references/inspection.md`](references/inspection.md#scope-commands). If HEAD
does not exist, report an empty repository and stop. Reject an invalid revision or
non-positive count instead of guessing. Record the initial HEAD, selected full SHAs,
branch, dirty paths, and locally observed upstream state. Local remote-tracking refs may be
stale; label them as local observations.

Discover and read the repository instruction files that apply to every changed path,
including root and nested AGENTS.md, CLAUDE.md, or harness equivalents. If dirty paths
overlap the review, preserve them and use committed blobs, not the worktree, as the
attribution source. When a commit edits `AGENTS.md`, `CLAUDE.md`, `REVIEW.md`, or other
review instructions, judge it by the parent version of those instructions.

## 2. Inspect every commit and the series

For each selected SHA, establish its parents, metadata, complete path inventory, and patch
as [`references/inspection.md`](references/inspection.md#per-commit-inspection) describes
for root, normal, and merge commits. Cover every changed path as
[`references/inspection.md`](references/inspection.md#path-coverage) lists.

Infer intent from the commit message, neighboring selected commits, changed tests and
docs, and local history. Do not invent an unstated requirement.

Do not silently sample large commits: batch the paths and finish all material source,
config, migration, test, and documentation coverage before issuing APPROVE. If coverage
cannot be completed, report the exact gap and issue REVISE with that gap as the reason.
Never APPROVE.

For a linear commit window, also inspect the net diff from the oldest commit's first
parent through the newest commit. For unrelated named commits, assess them separately
and state that there is no single series diff.

## 3. Evaluate and attribute

Evaluate each commit and the selected series with the checks and priorities in
[`references/evaluation.md`](references/evaluation.md).

A finding must cite evidence that the reviewed commit introduced the problem. Compare
the parent snapshot before attributing it. If a later commit fixed the problem, mark
it resolved and do not let it block the series verdict. List important pre-existing or
out-of-scope current issues separately; they do not drive the verdict.

## 4. Reconcile a moving worktree

Immediately before the verdict, rerun `git rev-parse HEAD` and
`git status --short --branch`.

If HEAD changed and the user requested the newest commits by count, recompute that
window, review commits that entered it, and refresh current-file evidence until the
reported window matches the final HEAD. For explicit revisions, retain the original
SHAs but refresh current-state notes. If overlapping dirty paths changed, refresh their
reconciliation. Report initial and final state rather than hiding concurrent movement.

## 5. Verdict and output

- **APPROVE**: coverage is complete, no unresolved material finding is attributable
  to the selected commits, and messages are materially accurate.
- **REVISE**: the net change has value but has an unresolved P1/P2 defect, a
  material scope/history/message problem, or incomplete review coverage. Recommend an amend only when history is
  private; otherwise recommend a follow-up commit and note coordination needs.
- **REVERT**: the net effect is unsafe or harmful and reverting is safer than
  incremental repair. Severity alone does not require a revert. Never recommend
  rewriting or reverting shared history without coordination.

Write the output in the layout of [`references/output-template.md`](references/output-template.md).
Do not claim test, CI, or runtime evidence that was not observed.
