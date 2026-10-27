---
name: review-pr
description: Review a pull request for code quality, bugs, over-engineering, and guideline compliance. Analyzes the full PR diff with confidence-scored findings and APPROVE/REVISE/REJECT verdict. Read-only assessment.
compatibility: Requires Git with the PR's base and head commits available locally, or an authorized read to fetch them. The GitHub CLI or an equivalent read-only API is optional for PR metadata and for posting a comment. Without it, review a named local base and head and report the PR metadata as unavailable.
disable-model-invocation: true
allowed-tools: Bash(git diff *), Bash(git log *), Bash(git show *), Bash(git rev-parse *), Bash(git status *), Bash(git merge-base *), Bash(git ls-files *), Bash(git branch --show-current), Bash(git remote -v), Bash(gh pr view *), Bash(gh pr diff *), Read, Glob, Grep
arguments:
  - name: pr
    description: "PR number to review (default: current branch's open PR)"
  - name: base
    description: Base ref to compare against, or historical endpoint when explicitly requested
  - name: comment
    description: Post review as a PR comment instead of outputting to terminal
  - name: threshold
    description: "Minimum confidence score to report (default: 70)"
---

# Pull Request Review

Review a pull request for code quality, bugs, over-engineering, and guideline compliance. Output actionable findings with confidence scores.

Preserve files, the index, and refs. Do not execute target-controlled builds, tests, hooks,
or scripts as part of this assessment. Native read-only Git checks are permitted. Separate
required gates that remain unrun from the source-review result. A separately authorized
runtime check has its own scope and evidence; it does not make this review a code-edit task.
Use equivalent read-only GitHub APIs when available; the `gh` examples name the required
metadata and do not require installing that client.

## Scope

**This skill reviews:** An open pull request (or branch diff against base)

**Use instead:** `review-pending-changes` for uncommitted work, `review-recent-commits` for already-committed work

Order governs presentation, never disclosure. Report a security, data-loss, or credential finding as soon as it is found, even before the freshness gate in Step 6. A credential-shaped literal counts even when it looks fake; in a single final reply, lead with it.

## Step 1: Resolve immutable review objects

Record the current branch, remotes, and full `HEAD` SHA. `git status --short` is only a preservation check. Never read, diff, format, stage, or otherwise use working-tree or sibling-worktree content for this review.

If `--pr` is provided, query that exact PR. Otherwise, try to identify the current branch's PR:

```bash
gh pr view <pr-if-provided> --json number,title,baseRefName,baseRefOid,headRefName,headRefOid,state,isDraft,url,body,additions,deletions,changedFiles
```

If remote metadata is available, record `baseRefOid` and `headRefOid`, then resolve those exact OIDs with `git rev-parse --verify <oid>^{commit}` before reading the change. Do not substitute mutable named refs. A named PR head may be any locally available committed object and need not equal the current local `HEAD`. The PR merge base is the default comparison base. The PR base remains metadata and must not be lost.

If a recorded object is missing locally, `--base` is provided, or PR lookup fails, follow [`references/resolving.md`](references/resolving.md) before reading the change; it holds the retrieval, custom-base, and local-review rules.

Bind the base and head repository identities too, especially for forks. Attach the selected
PR to the current task when the harness supports PR artifacts. A PR number alone is not a
repository identity.

Review drafts when selected and state draft status. Closed or merged PRs may be reviewed only when explicitly selected for historical review. Pin
the original comparison and its provenance; report a missing historical endpoint instead of
substituting today's base. Assess whether historical findings survive at a separately pinned
current revision, without replacing original attribution. A historical verdict is not merge
readiness. Stop if the selected committed comparison has zero changes. Do not treat a dirty
worktree as PR changes.

## Step 2: Gather committed context

Use the resolved base and head SHAs for every read: the patch, renames, and commit log. Diff the two commits directly (`git diff <base-sha> <head-sha>`); that form matters for safety, because it never reads the working tree or touches the index.

Read applicable instructions from committed blobs, never from the working tree. Identify repository-level and nested `AGENTS.md`, `CLAUDE.md`, or harness equivalents that govern each changed path, then read the governing blob from the head or base endpoint as relevant. If a required instruction exists only in the working tree, report that it could not be part of this immutable review. When the change edits `AGENTS.md`, `CLAUDE.md`, `REVIEW.md`, or other review instructions, judge it by the base version, and review the edit itself as part of the change.

Read the PR body when remote metadata is available. For local-only review, state that intent is inferred from the committed diff and history unless the user supplied it.

## Step 3: Understand the change

Before evaluating quality:

1. Record the resolved base, head, comparison method, PR base and merge base when available, and whether each endpoint came from local or remote metadata.
2. Read the complete committed diff and commit history.
3. For every added or modified text file, read the complete selected-head blob with `git show <head-sha>:<path>`. For a deleted file, read its base blob; do not request an impossible head blob. Read the base blob when needed to decide whether a concern is newly introduced. A repeat review may reuse inspection only under the evidence conditions below.
4. Identify and document the problem the change solves.
5. When the PR has earlier review threads, read them. Keep the wording of a finding that still
   applies. Reopen a human-resolved or dismissed point only with new evidence or a change
   that makes it worse.

For a repeat review after fixes, with or without earlier threads, follow
[re-review evidence](references/re-review.md) to reconcile prior findings and scope the new
inspection without losing full PR coverage.

Keep a coverage ledger for every changed path and its status. Include renamed/deleted
originals, type and executable-mode changes, symlinks, submodules, generated sources,
lockfiles, and binary artifacts. Record the depth for each path: diff only, complete file and
relevant owners, artifact consistency, or not inspected. An inventory, matching blob hashes or
clean diff check does not establish semantic review. Where line review does not fit the
artifact, inspect its source-of-truth or contract impact and state the limitation. Do not
silently sample a large diff; review a very large PR in bounded batches. Missing objects,
truncated content, or unresolved artifact coverage prevent an
unqualified approval; report the exact gap while completing independent checks.

## Step 4: Multi-Perspective Review

Evaluate the PR from each perspective independently: guideline compliance, bugs introduced
by this PR, over-engineering, and spec conformance. For each finding, assign a confidence
score (0-100). Load [`references/checklist.md`](references/checklist.md) for the guideline
and bug questions and the score scale.

A single-caller abstraction is not over-engineering when it lands with the lint rule, check, or type that bans going around it and migrates existing callers. Repetition that every future change must reproduce correctly is a cost.

Spec conformance and docs drift:

- Against the linked spec or issue, report requirements that are missing, partial, wrong, or
  unrequested, citing the requirement. An incomplete promised repair can block approval even
  when the defect predates the PR; label it incomplete repair, not introduced regression. Check
  equivalent boundaries covered by that requirement, not only the supplied reproducer. A fix
  must satisfy the full requested contract at its existing owner. A decision the spec records
  is a requirement. With no spec, say "no spec available" and continue correctness review.
- Check docs that describe the changed behavior and report only the drift this change introduced.

## Step 5: Score and filter

**Filter:** Validate the threshold as a number from 0 through 100. Merge findings about the same defect into one that lists every location. Score every candidate
before filtering. Report findings at or above the threshold (default: 70), and give the
number below it in the summary. Confidence measures evidence, not impact. Use `bug`,
`design`, or `nit` for severity; a credential, or an edit that weakens the rules, tests, or
gates the PR is judged by, is a `bug`. A nit alone does not block approval. Missing evidence is a
coverage limitation, not a low-confidence finding to discard. If a raised threshold hides
a material candidate, disclose that the filtered output cannot establish an unconditional
approval rather than treating silence as proof of correctness.

## Step 6: Freshness and output

Before any verdict or output, check freshness: for a PR, follow [`references/resolving.md`](references/resolving.md#freshness); for a named local review, re-resolve the selected refs and report a changed endpoint as stale.

Write the terminal output (the default) in the layout of
[`references/report-format.md`](references/report-format.md), which also lists the coverage
facts the report must state.

An `APPROVE` verdict is a local review result. It does not claim merge readiness, CI success, required-gate completion, approval authority, or permission to merge.

| Verdict | When to Use |
|---------|-------------|
| APPROVE | Requested coverage is complete and fresh, with no unresolved material concern. Nits alone do not block. |
| REVISE | A material issue needs correction, or coverage/freshness prevents unconditional approval. |
| REJECT | Critical bugs, security issues, or fundamental design problems. Needs significant rework. |

### PR Comment Output (with `--comment`)

Posting is an external mutation. Do it only with explicit authority to comment on the resolved PR. Write the exact review content to a temporary file and use:

```bash
gh pr comment <number> --body-file <review-file>
```

Read the posted comment back and confirm its body matches the review file. Report its URL. Without that check, report the review as delivered to the terminal only.

Done when the verdict, coverage, and freshness status are delivered, and any requested comment is verified.
