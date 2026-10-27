# Staging edge cases

## Clean worktree

Load from step 1 when the worktree is clean.

A clean worktree means there is nothing new to commit. It does not mean there is nothing
to push. Inspect committed differences against the identified remote branch and account
for all commits publication would expose. Report a complete no-op only when neither local
commit work nor authorized publication remains. Label cached remote evidence as cached.

## Unrelated staged content

Load from step 3 when unrelated staged content exists.

`git commit --only -- <paths>` reads those paths from the worktree, so it fits only when
their entire worktree content belongs in this commit. It cannot preserve a deliberate
staged/unstaged split within those same paths.

## Failed hook or command

Load from step 3 when a hook or command fails.

Inspect HEAD and the index before retrying: a failed post-commit action may already have
created the commit. Report completed and remaining groups. Repair only authorized work.
