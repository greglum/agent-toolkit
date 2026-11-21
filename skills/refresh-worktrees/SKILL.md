---
name: refresh-worktrees
description: Assess Git worktrees against a current base and update authorized active worktrees in place while keeping them. Use after merges to sync local worktrees without losing dirty or unmerged work. Not for unmerged-work recovery or deleting finished local/remote branches, PRs, and worktrees (repository-cleanup).
compatibility: Requires Git 2.x with worktree support and Python 3.10+ for the bundled read-only inventory helper. Updating bases needs remote access when authorized; without it, assess locally cached bases and label stale evidence. PR-state checks need a PR connector (such as gh) or remain unverified; full PR and branch cleanup hands off to repository-cleanup.
---

# Refresh worktrees

Preserve local work first. Prefer updating an existing clean worktree in place over
removing and recreating it. A clean Git status does not prove a worktree is disposable.

Use this skill to sync active local worktrees onto a current base while keeping them. When
invoked from `repository-cleanup`, accept its repository path, verified base ref/SHA,
target worktree paths, and preservation/ownership notes. Hand off stale-work sweeps,
unmerged recovery, completed-PR checks, and remote branch deletions to `repository-cleanup`.

## 1. Resolve the repository, base, and authority

1. Read applicable repository rules and the user's requested targets. Stop and report
   without mutating anything if the target path is not a Git repository, if requested
   worktree paths do not exist, or if no valid base ref/SHA can be resolved.
2. Resolve the base from an explicit request, repository convention, or verified remote
   default, in that order. Resolve the intended remote from configuration and the request.
   Do not use the current branch as the base merely because it is checked out somewhere.
   Record the full base SHA and whether remote state was checked or is locally cached.
   Ask only if evidence cannot settle the destination or required authority.
3. Run this bundle's read-only inventory helper from any checkout or bare repository,
   resolving the script path relative to this skill bundle rather than the target repository:

   ```sh
   python3 scripts/inventory.py --repo /path/to/repository --base <verified-base-ref-or-sha>
   ```

   The script runs with `GIT_NO_LAZY_FETCH=1`, `GIT_ALLOW_PROTOCOL=""`, and
   `core.fsmonitor=false`. It handles bare repositories, linked worktrees, detached HEADs,
   and locks without requiring the user to switch directories, and it withholds status when
   partial-clone filters, active clean/process filters, or initialized submodules would hide
   dirtiness or run configured programs. Exit `2` means incomplete inventory; preserve the
   affected worktree unless separate trusted inspection resolves that gap.
4. Fetch or update the base only when the refresh request authorizes it. If updating a base
   checkout, require it to be clean and use fast-forward-only update (`merge --ff-only`).
   Preserve a dirty or divergent base and continue assessing from the available committed
   object, labeling remote evidence as stale.

Done when: the repository, verified base SHA, inventory JSON (with exit code), and target
worktree list are recorded, or a missing-repo/missing-path stop is reported.

## 2. Assess each requested worktree

1. From the inventory output and local inspection, record each target's path, branch or
   detached SHA, upstream, lock/managed ownership, staged/unstaged/untracked changes,
   important ignored files (local data, credentials, artifacts), active processes or chats,
   commits unreachable from the selected base, and whether the base is contained in `HEAD`.
2. Use locks, processes, and harness sessions tied to these paths to verify ownership and
   active use; do not survey unrelated sessions. Missing access, no visible process, or a
   clean status does not prove inactivity. Mark unavailable activity evidence as unknown and
   preserve that target unless ownership and exact authorized action are established. Avoid
   reading ignored credentials merely to inventory preservation needs; record paths and
   owners instead.
3. Commit reachability alone does not prove a squash-merged branch is safe to discard, and a
   closed-unmerged PR is not completed work. If PR-hosting access (such as `gh`) is
   unavailable, mark PR state unavailable and preserve the branch and worktree. Hand off
   completed-PR reconciliation and stale local/remote branch cleanup to `repository-cleanup`
   (passing repository path, verified base ref/SHA, target paths/refs, PR IDs, and
   preservation notes). If `repository-cleanup` is unavailable, keep finished PR branches
   and remote refs intact and report them for explicit cleanup.
4. Classify each target:

| State | Default action |
|---|---|
| Base already contained, no requested rebuild | No change |
| Clean, inactive branch that can fast-forward to the base | Update in place when authorized |
| Dirty, active, locked, or containing unique/uncertain work | Preserve; report the needed decision |
| Explicitly selected for removal or recreation | Prepare an exact-target preservation and replacement plan |

Done when: every requested worktree is classified with preserved paths, activity status,
and any `repository-cleanup` handoff or missing-access limits noted.

## 3. Make the concrete plan

1. Report the selected remote, base ref/SHA, and one planned action per target with its
   supporting evidence. Reuse session authority already granted for identified targets
   rather than asking again.
2. Separate worktree removal from branch deletion:
   - Requesting cleanup of a finished worktree covers a non-force `git worktree remove` only
     when that exact target is clean, unlocked, inactive, verified done, and free of
     important ignored files (since removal deletes them).
   - Safe deletion (`git branch -d`) applies only to verified merged local branches. Keep a
     squash-only branch ref unless the user explicitly authorized deleting that exact
     branch, and retain its tip SHA first.
   - Any other removal, branch reset, or replacement of uncertain work needs explicit
     target authority. Local cleanup authority never authorizes remote deletion.
3. Before any approved recreation, back up tracked changes, untracked files, unpushed
   commits, and important ignored files in a recoverable location and verify the backup.
   Resolve branch/path reuse and the replacement base before removing anything. Keep
   protected, shared, or active worktrees. Use harness lifecycle tools for managed
   worktrees when available instead of raw removal.

Done when: every target action, backup path, and required authorization is confirmed before
any write starts.

## 4. Execute authorized actions

1. Recheck each target's `HEAD`, status, active use, locks, and base SHA immediately before
   writing. Changed evidence invalidates only that target's plan; reassess it without
   disturbing other targets.
2. For an approved clean branch whose `HEAD` is an ancestor of the selected base, run:

   ```sh
   git -C <path> merge --ff-only <base-sha>
   ```

   Keep the checkout and branch. If it cannot fast-forward, stop that target and never fall
   back to `reset` or `rebase`.
3. Recreate or remove only exact approved local targets after verifying backups. Never use
   `--force`, `git branch -D`, `reset --hard`, or broad pruning before or after a failure
   unless the user explicitly confirmed that exact command. Hand off completed-PR or remote
   branch cleanup to `repository-cleanup`; if `repository-cleanup` is unavailable and remote
   deletion was separately authorized for an exact verified tip, never delete without an
   explicit lease (`git push --force-with-lease=refs/heads/<branch>:<expected-sha> <remote> :<branch>`)
   and post-delete verification (a fetch prune only removes local tracking refs).
4. On any failure, report the error and exit status and preserve remaining resources. Run
   dependency setup only when requested or required by the repository's refresh workflow,
   using that repository's own command; a setup failure leaves only that target incomplete.

Done when: all planned updates/recreations ran or stopped cleanly on changed/failed checks.

## 5. Verify and finish

Confirm every target's final `HEAD` and status, preserved resources, backup paths, setup
results, and final base SHA versus the planned SHA. Include command and exit-code receipts
for inventory, Git, and setup steps. Report changed, unchanged, preserved, failed,
unavailable, and unrun actions separately.

Complete only when every requested target is accounted for and any `repository-cleanup`
handoff or absent-companion limit is stated. Repeating a refresh with the same base and no
requested rebuild must leave current worktrees unchanged.
