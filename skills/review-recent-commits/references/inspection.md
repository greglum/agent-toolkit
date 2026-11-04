# Commit inspection commands

## Scope commands

Capture repository and worktree state before reviewing:

~~~bash
git rev-parse --show-toplevel
git -c core.fsmonitor=false --no-optional-locks status --short --branch
git branch --show-current
git rev-parse --verify HEAD
git --no-pager log --format='%H%x09%h%x09%an%x09%aI%x09%s' -n 5
~~~

For a count, select with git --no-pager log --format=%H -n <count>. For each named revision, resolve it with:

~~~bash
git rev-parse --verify --end-of-options '<revision>^{commit}'
~~~

When an upstream exists, inspect it without fetching:

~~~bash
git rev-parse --abbrev-ref --symbolic-full-name '@{upstream}'
git rev-list --left-right --count 'HEAD...@{upstream}'
git branch -r --contains <sha>
~~~

## Per-commit inspection

For each selected SHA, establish its parents, metadata, complete path inventory, and
patch:

~~~bash
git rev-list --parents -n 1 <sha>
git --no-pager show --no-ext-diff --no-textconv --format=fuller --stat --summary <sha>
git --no-pager show --no-ext-diff --no-textconv --format=fuller --find-renames --find-copies <sha> --
git --no-pager diff-tree --no-ext-diff --no-textconv --root --no-commit-id --name-status -r -M -C <sha>
~~~

- For a root commit, use the --root view.
- For a normal commit, review the parent-to-commit diff and run
  git --no-pager diff --no-ext-diff --no-textconv --check <parent>..<sha>.
- For a merge, do not skip the merge. Review the first-parent integration diff,
  git --no-pager show --no-ext-diff --no-textconv --cc <sha>, and each parent-to-merge diff so conflict resolutions and
  merge-only changes are visible.

Use these pager and driver controls for every patch-producing Git read, including
series and parent comparisons. Configured pagers, external drivers and text converters
can execute programs. Read complete blobs with raw `git --no-pager show <sha>:<path>`;
do not enable conversion or filters.
For index or working-tree reads, also set `-c core.fsmonitor=false` to suppress
configured monitor hooks, and use `--no-optional-locks` to avoid optional index writes.

## Path coverage

For every changed path:

1. Inspect its exact patch and status, including renames, deletions, mode changes,
   submodules, and symlinks.
2. Read the complete post-commit blob with git --no-pager show '<sha>:<path>'; for a deletion,
   read the parent blob.
3. Read the complete committed version at the final HEAD, when it still exists.
4. Read the worktree file, when present, only to reconcile current state. Keep
   uncommitted or later changes separate from the reviewed commit.

Inventory generated, lock, vendored, and binary files, but skip line-level review only
when repository rules or file evidence supports that classification. Review their
source-of-truth or invariant impact instead.
