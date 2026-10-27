# Integrate concurrent research changes

Use this procedure when another session or round may edit the same checkout, branch, catalog
index, or registry. Reuse the round's existing state record outside the repository.

## Bind one integration owner

Record the integrating session, repository, target branch and HEAD, its working-tree/index
state, and the paths each round owns. Inspect existing coordination records and active
worktrees before claiming ownership. A matching branch name or a clean index is not ownership.

Only the named integrator changes the shared checkout's files, index, or branch state.
Other writers use task-owned worktrees with separate branches or detached heads. Read-only
research lanes remain read-only. If the current integration owner cannot be reached, keep
the new round isolated and report integration pending; do not take over its checkout.

## Hand off exact work

Each writer returns its worktree, base and current HEAD, owned path/hunk allowlist, reviewed
patch and untracked artifacts, and checks bound to that content. Identify dependencies,
excluded dirty work, and unresolved decisions. Keep coordination state out of catalog commits.

The integrator inspects the original changes and combines them one round at a time. Shared
registry and index entries are reconciled against their current content, preserving entries
from other rounds. A stale whole-file copy is not a valid integration patch.

## Recheck before changing shared state

Before each integration, staging, commit, or push, compare current HEAD, selected file content,
and index with the reviewed snapshot. On a mismatch, stop the dependent write, inspect the
new state, and rebuild the affected patch. After one conflict-driven refresh of the same shared file or index, another mismatch
leaves that shared integration pending until ownership is settled. An independently merged
upstream PR is handled by the normal branch-update and review gates. Preserve existing exact-head and
compare-before-write safeguards; this procedure does not replace them with a model judgment.

Recheck the final diff and run required checks on integrated content. Reuse unaffected proof;
rerun invalidated checks. Report each round as integrated or pending with its exact revision
and blocker. Commit, push, PR creation, and merge retain their separate action authority.
