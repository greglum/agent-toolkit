---
name: global-code-review
description: "Review a diff against a coding standards file the user names plus any standards the repo documents. Use when asked for a global code review, a review against their own standards, an over-engineering or unnecessary-complexity check, or a standards review in a repo that documents none."
compatibility: Requires Git. Reads the user's standards file when one is named; without one, says so and continues with the repository's documented standards only, without inventing rules.
arguments:
  - name: standards
    description: Path to the user's own coding standards file (optional)
---

Review the changes between `HEAD` and a fixed point against a standards set
assembled from two layers:

1. **User** (when named): the user's own standards file. Applies everywhere.
2. **Repo** (when present): whatever this repository documents about how its
   code should be written.

Make two passes: standards first, then simplicity. This review only asks whether
the code is written well. To check the diff against an originating issue or spec,
use the repository's spec-conformance review.

## Process

### 1. Pin the fixed point

Choose the requested comparison first. For uncommitted work, pin `HEAD` and use
`git diff HEAD` for all tracked changes, or `git diff --staged` for a staged-only
request. Account for untracked files when the requested scope includes them.
Skip the committed-range steps below and report which working-tree snapshot you
inspected. Recheck that diff before reporting if the files changed during review.

The fixed point is whatever the user gave: a commit SHA, branch, tag, `main`,
`HEAD~5`. Resolve it and `HEAD` to immutable commit SHAs. If they gave none,
default to the merge base with the repository's default branch and say so. Use
the merge base for an explicitly requested branch or PR comparison too. If the
intended base cannot be resolved, ask.

Confirm before going further:

```bash
git rev-parse --verify <fixed-point>^{commit}
git rev-parse --verify HEAD^{commit}
git diff --stat <base-sha> <head-sha>
```

Compare the pinned endpoints directly. Taking a merge base again can hide
changes when the user named a specific commit. A bad ref or an empty diff stops
here, with a clear message.

Capture the commit list too: `git log <base-sha>..<head-sha> --oneline`.

### 2. Load the user standards

Find the user's standards file: the `standards` argument, a path named in the
request, or a file the user's global agent instructions name as their coding
standards. Read it in full.

If no file is named, or the named file is missing, say so plainly and continue
with the repo layer only. Do not invent a substitute set of rules.

### 3. Load the repo standards

Search the repository for everything that documents how its code should be
written, and do not stop at the first hit. Read whatever exists:

- `CODING_STANDARDS.md`
- `CONTRIBUTING.md`, `REVIEW.md`
- `CLAUDE.md`, `AGENTS.md`
- `docs/adr/` and `CONTEXT.md`, for decisions that bind the code you are
  reviewing
- a `docs/standards/` or `docs/style/` directory, or any other standards file the
  repo documents

Read only the parts that could bear on this diff. Do not read an entire
handbook to review a ten line change.

### 4. Resolve precedence

The repo wins. Where a repo standard contradicts or endorses something the
user file would flag, follow the repo and suppress the user rule. Note the
override in one line in the report, so the user can see which rule yielded and
why.

Where the repo is silent, the user standards apply in full.

### 5. Review the diff

Pass 1: for each hunk, ask whether it breaches a loaded standard.

Pass 2: simplicity. Most rules read as "is this line wrong". Simplicity reads
as "should this exist at all", which is easy to skip. Go through the diff again
asking only: what here could be deleted, flattened, or never written? Look for
abstractions with one caller, layers that only forward, options and flags
nothing sets, defensive checks between the code's own functions, and comments
restating the line below them or narrating the change instead of explaining the code.
Also check as a future agent contributor would: a second way to do an existing task,
a second writer of the same state, a hand-synced list, internals newly reachable
past their module. Over-engineering is the finding this review
most often exists to catch, so do not let a clean standards pass end it.

A one-caller abstraction is not excess when it lands with the lint rule, check,
or type that bans going around it and migrates the existing callers (a closed
door). This exemption never overrides a loaded standard; it only answers the
default over-engineering question when no loaded rule decides it. Repetition
that every future change must reproduce correctly is a cost, not clarity.

If the diff touches checks, lint config, hooks, baselines, suppressions, CI, or
dependency manifests or lockfiles, also read `references/gates.md`.

In both passes, use actual check evidence. Avoid repeating current tooling
results as separate manual findings. When required results are missing, stale,
or failed, report that limitation; do not assume a configured check ran or passed.

For a mechanical violation, name the lint or CI check that would prevent
recurrence. Classify each finding:

- **Violation**: it breaches a documented rule in the user file or the repo.
- **Simplicity**: pass 2 found code that does no work.
- **Judgement**: it matches a smell or a heuristic and is worth a look, but a
  reasonable person could leave it. Every smell from the user standards file lands
  here.

### 6. Report

Group by classification in the order below. Within a group, order by file.

```markdown
## Global code review

`<base-sha>..<head-sha>` · N commits · M files changed
Standards: <user file, or "no user file"> + <repo sources, or "no repo standards found">

### Violations
- `path/to/file.ts:42` · <standard> · <what is wrong>. Fix: <what to write>.

### Simplicity
- `path/to/thing.go:15` · <what is doing no work>. Delete/collapse to: <what>.

### Judgement calls
- `path/to/other.py:88` · <smell> · <what it looks like>. Consider: <fix>.

### Overrides applied
- <repo rule> overrode <user rule> in <where>.
```

End with the count per group, the single worst finding, and a verdict: REVISE
while any Violation or Simplicity finding stands, or required checks or coverage
are missing; otherwise APPROVE. State scope or check gaps,
including any drift after the pinned review. If there is nothing to report, say
so in one sentence and retain material limitations. A standards review does not
establish CI or merge readiness.

## Scope

Stay on how the code is written. Out of scope here:

- Whether the change implements what an issue asked for. Use the repository's
  spec-conformance review.
- Diagnosing a bug the change introduced. Use a debugging workflow.
- Rewriting the code. Report findings; applying fixes is a separate step.
