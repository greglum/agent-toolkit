---
name: acp
description: Review task-owned changes, stage and commit them in cohesive groups, then push to the authorized Git destination. Use for add/commit/push requests; preserve unrelated staged and working-tree changes.
compatibility: Requires Git and, to publish, authorized access to the target remote. Subtree publication also needs git subtree. Without publish access, finish the authorized local commits and report publication pending.
disable-model-invocation: true
arguments:
  - name: message
    description: Optional commit message override (single commit mode)
  - name: files
    description: "Specific files to stage (default: reviewed task-owned changes)"
  - name: no-push
    description: Commit without pushing
  - name: split
    description: Analyze multiple commit groups, even for a small changeset
  - name: no-split
    description: Use a single cohesive commit
  - name: no-subtree-push
    description: Skip subtree publication; retain the identified main repository destination
---

# Add, Commit, Push

Deliver the requested commits and publication for the identified repository and target.
Reuse authority already supplied by the user. A skill invocation does not authorize
publishing to another repository, rewriting history, bypassing hooks, or staging others' work.

## 1. Bind the state, ownership, and destination

Read repository instructions and required gates. Record the repository, branch, HEAD,
upstream, remotes, staged patch, unstaged patch, and untracked paths. Inspect every selected
change, including deletions, renames, executable modes, generated artifacts, and lockfiles.
Record which paths and hunks belong to this task; preserve unrelated work and the existing
index. Conflicts or an operation in progress block committing until safely resolved.

Resolve the publication remote URL and branch from the request and current configuration.
Do not silently choose `origin` or infer a destination from a matching directory name.
Respect repository branch protections. A detached HEAD needs an identified branch before
publication. Ask only when evidence cannot settle ownership, target, or missing authority.

A clean worktree may still leave commits to publish:
[`references/staging.md`](references/staging.md#clean-worktree). Subtree prefixes need mapping:
[`references/subtrees.md`](references/subtrees.md#discover-mappings).

## 2. Review and plan cohesive commits

Read recent history for the repository's commit format and issue-reference conventions.
Keep implementation, its tests, required configuration, and docs together when they solve
one problem. Split independent concerns into commits that each leave a coherent state;
different file types or commit labels alone are not reasons to split.

Present the paths, branch, ordered groups, and complete messages. Continue under existing
authority when this is a routine grouping choice; seek input only for an unresolved scope
decision. For grouping flags, message format, and Markdown audit advice, apply
[`references/grouping.md`](references/grouping.md). Add attribution trailers only when the
user's or harness's current instructions call for them; never add one on your own initiative.

## 3. Stage and commit the exact reviewed content

Inspect selected content for credentials, private keys, tokens, and accidental local data.
Sensitive-looking filenames are clues; verify content before excluding a legitimate source
file. Example environment files also need inspection. Apply the repository's secret checks,
large-file policy, generated-file rules, and required gates. A failed gate stops dependent
publication; do not bypass hooks or silently delete tests.

For each group:

1. Recheck HEAD and selected working-tree/index content against the reviewed snapshot.
   Reconcile concurrent changes before staging. Stage named paths or reviewed hunks;
   use broad staging only when explicitly requested and all resulting content is owned.
2. Inspect the full proposed commit patch, not only its stat. The commit must contain
   exactly this group's reviewed changes. Ordinary `git commit` includes every staged
   path, including unrelated work left in the index.
3. When unrelated staged content exists, use a verified Git path-scoped or isolated-index
   procedure that preserves it
   ([`references/staging.md`](references/staging.md#unrelated-staged-content) covers `--only`).
   If exact content cannot be isolated safely, report the ownership blocker rather than
   reset the index.
4. Write the message to a temporary file and pass `git commit --file <message-file>`.
   Preserve literal text and actual newlines. Inspect the new commit's full patch and SHA,
   then verify unrelated staged and working-tree content remains intact.

A check that selected zero tests, was skipped or cached, or masked its exit code did not run;
a forced failure counts only after confirming the forcing edit applied.

Execute groups sequentially and confirm each success before the next. If a hook or command
fails, follow [`references/staging.md`](references/staging.md#failed-hook-or-command) before
retrying; do not automatically roll back or amend completed/shared commits.

## 4. Push the identified branch

Respect `--no-push`. Otherwise recheck HEAD, completed gates, the destination URL and
branch, and every outgoing commit before pushing with an explicit destination refspec.
If target authority is missing, finish authorized local commits and report publication
pending. A rejected push does not authorize force-push, pull/rebase, reset, or another target.

Verify the remote branch's observed SHA after success. Compare it with the pushed SHA and
report any concurrent movement or unavailable verification. Local tracking refs and a local
commit alone do not prove publication. Do not push a concurrently changed, unreviewed HEAD.

## 5. Publish authorized subtrees

Skip unchanged subtrees, `--no-push`, and `--no-subtree-push`. Publish each remaining prefix
only as [`references/subtrees.md`](references/subtrees.md#publish) allows.

## 6. Verify and finish

Report each created or reused commit with its full SHA and message, covered paths, final
branch/status, preserved unrelated work, required checks, and each publication destination
and observed SHA. Account for completed, unchanged, skipped, pending, failed, unavailable,
and unrun actions, including subtrees. `--no-push` completes with verified local commits.
Otherwise finish only when every requested commit and publication has a supported outcome;
state any remaining blocker without claiming completion for it.
