---
name: refresh-worktrees
description: Assess Git worktrees against an identified base and refresh authorized clean worktrees without losing local work. Use after merges or when asked to refresh worktrees. Preserve dirty, active, or unmerged work; removal, recreation, and branch reset require authority for the exact targets.
compatibility: Requires Git 2.x with worktree support. Updating the base needs remote access and runs only when the request authorizes it; without it, assess against the locally cached base and label that evidence stale.
---

# Refresh worktrees

Preserve work first. Prefer updating an existing clean worktree in place over
removing and recreating it. A clean Git status does not prove a worktree is disposable.

## 1. Resolve the repository, base, and authority

Read applicable repository rules and the user's requested targets. Inventory with
`git worktree list --porcelain`; support bare repositories, linked worktrees, detached
HEADs, locks, and managed checkouts. Do not assume the first entry is a usable main
checkout or require the user to switch directories.

Resolve the base from an explicit request, repository convention, or verified remote
default, in that order. Resolve the intended remote from configuration and the request.
Do not use the current branch as the base merely because it is checked out somewhere.
Record the full base SHA and whether its remote state was checked or is locally cached.
Ask only if the evidence cannot settle the destination or required authority.

Assessment is read-only. Fetch or update the base only when the refresh request
authorizes that operation. If updating a base checkout, require it to be clean and
use a fast-forward-only update. Preserve a dirty or divergent base and continue the
assessment from the available committed object, labeling stale remote evidence.

## 2. Assess each requested worktree

Record path, branch or detached SHA, upstream, lock/managed ownership, and:

- staged, unstaged, and untracked files;
- ignored files that matter, including local data, credentials, and artifacts;
- processes or other active chats using the worktree;
- commits not reachable from the selected base;
- whether the selected base is already contained in the worktree's HEAD.

Use locks, processes, and harness sessions tied to these paths to establish ownership and active
use; do not survey unrelated sessions. Missing access, no visible process, or a clean status
does not establish inactivity. Mark unavailable activity evidence as unknown and preserve that
target unless its exact authorized action and ownership can be established. Avoid reading
ignored credentials merely to inventory preservation needs; record their paths and owners
instead.

Commit reachability alone cannot prove a squash-merged branch is unmerged or safe to
discard. For completed-PR cleanup, verify the identified repository/PR is merged and its merge
is on the selected base. Compare the worktree tip with the recorded PR head and check the
landed diff; preserve later commits or uncertain equivalence. A closed-unmerged PR is not
completed work. Do not infer disposability from branch naming or a local environment name.

Classify each target:

| State | Default action |
|---|---|
| Base already contained, no requested rebuild | No change |
| Clean, inactive branch that can fast-forward to the base | Update in place when authorized |
| Dirty, active, locked, or containing unique/uncertain work | Preserve; report the needed decision |
| Explicitly selected for removal or recreation | Prepare an exact-target preservation and replacement plan |

## 3. Make the concrete plan

Report the selected base/remote/SHA and one action per requested worktree, with the evidence for
preservation or update. Reuse authorization already given for identified targets. A request to
clean up finished worktrees covers a non-force `git worktree remove` of each clean, unlocked,
inactive, verified-done target with no ignored files that matter, since removal deletes them,
and `git branch -d` of its branch. A squash-only branch keeps its ref unless the user has
authorized deletion of that exact branch; retain its tip SHA before an authorized deletion.
Reuse that session authority instead of asking again. Other removal, branch deletion or reset,
or replacing uncertain work needs explicit target authority. Local cleanup authority does not
authorize deleting a remote branch.

Before any approved recreation, preserve tracked and untracked work, unpushed commits,
and important ignored files in a recoverable location. Verify the backup. Resolve
branch/path reuse and the replacement base before removing anything. Keep protected,
shared, or active worktrees. A managed worktree belongs to its harness's lifecycle
tools when available; use their archive/restore contracts rather than raw removal.

## 4. Execute authorized actions

Recheck the target HEAD, status, active use, and base SHA immediately before each write.
Changed evidence invalidates that target's plan; reassess it without disturbing others.

For an approved clean branch whose HEAD is an ancestor of the selected base, use
`git -C <path> merge --ff-only <base-sha>`. Preserve the checkout and branch. If it
cannot fast-forward, stop that operation; do not reset or rebase as a fallback.

Recreate only the exact approved targets with the verified preservation plan. Before completed-PR
cleanup, recheck the PR identity/state, worktree tip, ownership and preservation evidence. Changed
evidence invalidates the cleanup plan too. Never use `--force`, `git branch -D`, `reset --hard`,
or broad pruning, before or after a failure, unless the user confirmed that exact action.
When remote cleanup is authorized, verify the repository and exact branch against the merged
PR head, landed merge, and local activity inventory. Preserve protected/shared branches and any
branch whose tip moved. Delete with an expected-tip lease, then verify the remote ref is absent.
A fetch prune only removes tracking refs and does not delete remote branches.

Report the failure and preserve remaining resources. Do not delete unrelated branches.

Run dependency setup only when requested or required by the repository's refresh workflow,
using that repository's own command. A setup failure leaves only that target incomplete.

## 5. Verify and finish

Confirm every target's final HEAD and status, preserved resources, backup paths, and
setup results. Compare the final base to the planned SHA. Report changed, unchanged,
preserved, failed, unavailable, and unrun actions separately.

Complete only when every requested target is accounted for. Repeating a refresh with
the same base and no requested rebuild must leave current worktrees unchanged.
