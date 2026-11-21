# Git storage and checkout edge cases

Read this reference only when `inventory.py` reports object-store alternates, configured
Git filters, initialized submodules, stashes, or missing/unregistered checkout paths.

## Submodules and Git filters

- **Initialized submodules:** `inventory.py` uses `--ignore-submodules=dirty` and reports
  gitlinks plus `submodule status` without inspecting child repositories. When `inventory.py`
  flags initialized submodules, inspect each submodule's own worktree status, unpushed
  commits, and stashes separately before deleting any parent checkout.
- **Configured clean/process filters:** When a tracked path has a configured `.clean`,
  `.process`, or `.required` filter driver (or partial-clone promisor with filter drivers),
  `inventory.py` withholds worktree `changes` instead of triggering configured filter
  programs. Preserve the affected worktree unless separate trusted inspection resolves its
  dirty state.

## Stashes with third-parent untracked files

- A Git stash commit can carry three parents: first parent (base `HEAD` commit), second
  parent (staged index tree), and third parent (untracked and sometimes ignored files).
- Default `git stash show` inspects only the tracked worktree diff and omits third-parent
  files; an empty diff never proves a stash is safe to drop.
- Inspect all parents (`git rev-parse --verify <stash>^1`, `^2`, and optional `^3`) and
  compare each tree against current source before dropping any stash.

## Hidden and unregistered worktree directories

- Check repository-owned hidden worktree directories (such as `.worktrees/` or tool-owned
  checkout folders inside the repository) for unregistered checkouts not listed by
  `git worktree list`.
- Inspect only repository-owned directories; never crawl unrelated projects or unrelated
  agent sessions.

## Object-store alternates, lenders, and borrowers

- `inventory.py` runs `git count-objects -v` (with `core.quotePath=true`) and inspects
  `common_alternates_file`, `effective_alternates_file`, `GIT_ALTERNATE_OBJECT_DIRECTORIES`,
  and `GIT_OBJECT_DIRECTORY`, retaining unavailable-path diagnostics even on exit zero.
- **Lender vs. borrower asymmetry:** Alternates evidence describes this repository's
  lenders, not outside clones or worktrees borrowing from it. Never assume a repository has
  no external borrowers; check known related clones without a global filesystem crawl and
  record uncertainty.
- **Dissociating before lender removal:** Preserve lender repositories while any known
  borrower depends on their object stores. Before authorized removal of a lender,
  dissociate each known borrower through native Git (for example `git repack -a -d` and
  removing its alternates entry), then verify the borrower's effective/default alternates,
  `git fsck --full`, and required history/files independently of that lender. Keep active
  or unresolved borrowers and lenders in place. A verified Git bundle provides recovery
  coverage only and never authorizes breaking an active borrower. Account for object
  dependencies before archiving or deleting temporary clones as well.
