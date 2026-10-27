---
name: continue-pr
description: Resume a PR, branch or agent handoff, or reassess an old PR before rebasing. Recover intent, preserve contributors and local work, and check whether the goal is still useful against the current architecture.
compatibility: Requires Git and access to the selected source commits. GitHub metadata needs gh or an equivalent connector. Without remote access, assess local evidence only and mark current PR state unavailable. Rebase, push, publication and closure require authority for the identified target.
---

# Continue existing work

Finish the requested goal from verified current work. A handoff is context, not proof.
Read [source and continuation checks](references/continuation.md) when updating history or
changing where the work will be delivered.

## Recover intent and ownership

Read the original request, later user corrections, source PR/thread, linked requirements,
commits, complete diff and outstanding findings. Resolve the actual source head/base and
repositories, plus any uncommitted work and its owner. Record immutable SHAs and missing
access. Preserve unrelated files and active worktrees; use an isolated checkout for overlapping
work. Do not stash, reset or overwrite inherited work to make a checkout convenient.

Identify the requested continuation: assessment, local repair, update in place, or replacement.
Reuse existing authority for the named target. A replacement PR, changed base, rewrite of a
shared branch, merge or closure is a separate decision unless already requested.

## Reassess the goal before the branch

Inspect base changes since divergence and current callers, APIs, schemas and ownership.
Look for merged replacements or competing open work when the changed behavior suggests one.
Ask what you would build today for the same goal. A clean rebase establishes only textual
compatibility. Choose with evidence:

- **Continue:** the goal and implementation still fit; apply the authorized update.
- **Rework:** the goal remains useful but needs a different implementation. Do that work when
  the request covers it; otherwise report the concrete change and missing decision.
- **Superseded:** current behavior already meets the goal or the goal no longer fits. Recommend
  retiring the old work, with source evidence; close or delete only when authorized.

Age and sunk effort do not settle the disposition. Report an urgent defect immediately.

## Continue and verify

Carry forward intended behavior, contracts, accessibility and required tests. Preserve verified
human contributor credit when importing or squashing work; do not invent identities or add AI
co-author trailers. Keep your corrections distinct from inherited changes where practical.
Recheck the original source before delivery in case its owner advanced it.

Verify the original failure and representative workflows independently, using the repository's
gates. Rebase/conflict fixes invalidate affected proof. Keep unresolved findings and unavailable
checks visible. For a requested PR, use the repository's publication workflow; this skill does
not invoke explicit-only skills. For requested monitoring, `monitor-pr` owns event handling.

Deliver the inherited source and chosen disposition, exact final head/base, what changed,
contributor treatment, checks, excluded work, publication state and remaining decision.

Source context and recheck triggers: [sources](references/sources.md).
