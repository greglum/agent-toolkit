---
name: repository-cleanup
description: Audit remote branches, local branches, worktrees and stashes; recover useful unfinished work before removing verified completed resources. Use for repository cleanup and stale-work sweeps, rather than a routine worktree refresh.
compatibility: Requires Git and Python 3.10+. Current branch protection and PR evidence need remote access plus a forge connector or CLI. Delegated recovery needs authorized subagents; without them, preserve uncertain work and report that review as unavailable. Mutations follow task authority and repository gates.
---

# Clean a repository without losing useful work

Account for every branch, worktree and stash. Age, branch names, a clean status and
closed PRs do not establish that work is disposable. Preserve even small useful changes.
A fresh design uses one evidence ledger and the repository's existing delivery process,
rather than a parallel backlog or a new release system.

## Establish scope and a complete inventory

Read `AGENTS.md` and the repository's delivery and cleanup rules. Resolve the Git common
directory, every configured remote, verified default branch, protected branches and the
user's requested targets. Record authority separately for local cleanup, remote deletion,
recovery implementation, push, merge and deployment. Reuse existing session authority;
this skill does not grant those actions or schedule future runs.

Fetch authorized remotes and freeze full base and tip SHAs. Keep the user's dirty checkout
in place. Run this bundle's read-only inventory helper from any checkout or bare repository:

```sh
python3 scripts/inventory.py --repo /path/to/repository --base refs/remotes/origin/main
```

Resolve that script relative to this skill bundle, not the target repository. Its JSON
contains local evidence only. It does not fetch, inspect hosted PRs, identify active chats,
prove squash equivalence or approve deletion. Keep its output private: paths and filenames
can disclose local details. Exit 2 means incomplete inventory and blocks affected deletions.

Reconcile the output with live remote refs and all pages of open, merged and closed PRs.
Verify listing coverage includes drafts and automated authors; connector defaults may omit
bot PRs. Cross-check listed PR heads against live branch heads and investigate omissions.
Include remotes without tracking refs, refspec exclusions, branches without upstreams,
detached heads, locks, prunable entries, registered nested worktrees, harness-owned trees,
recovery refs, stashes and ignored assets. Check repository-owned hidden worktree directories
for unregistered checkouts; inspect those directories, not unrelated projects or sessions.
Inventory submodules and nested repositories separately before deleting any parent directory.
Inspect Git object dependencies: common and effective `objects/info/alternates`, resolved
alternate object stores and environment-provided alternates. The helper uses native
`git count-objects -v` and retains unavailable-path diagnostics, including exit-zero errors.
[Git documents these alternate paths](https://git-scm.com/docs/git-count-objects).
Its evidence describes this repository's lenders, not every borrower of its objects. A
lender cannot prove that no outside shared or reference clone depends on it; record that
uncertainty and check known related clones without a global filesystem crawl. Inspect the
common store separately if an environment object-directory override hides its dependencies.
Remote-tracking refs without a configured matching remote are local snapshots, not live
remote branches. Unavailable remote, activity or filesystem evidence means unknown, never absent.

Keep one private ledger keyed by repository identity plus full ref/path and frozen SHA.
For each item record ownership, dirty/untracked/ignored resources, current PR and base,
unique work, proposed disposition, worker, proof and final state. Map multiple refs and
worktrees for the same changes to one recovery job while accounting for every resource.

## Vet everything that has not demonstrably landed

For each stash inspect the tracked worktree snapshot, its staged index in the second
parent, and any untracked or ignored files in the third parent. Compare each tree with
current source and preserve its unique content. Default `git stash show` omits third-parent
files; a small or empty displayed diff cannot prove that a stash has no remaining value.

Index merged PR evidence by repository identity and full PR head SHA across all branch
names. Match local aliases and detached heads to that index before creating recovery jobs;
a branch-name-only PR search misses integrated aliases. Also trace source tips into later,
differently named merged PR heads. That ancestry groups evidence; inspect the final diff
and dispositions before declaring source changes landed, since later work may revise or
remove them. Map aliases to the same landed change, while reviewing each worktree's dirty
files and later commits separately.

For ancestry-merged work, verify the exact tip is reachable from the current base. For
squash or rebased work, verify the actual PR head and landed merge, inspect the complete
source change against current source, and account for later commits. Patch IDs and
`git cherry` are leads: they do not prove that a squash contains all work or that later
base edits retained it. A merged PR does not cover dirty files or post-PR commits.

Dispatch subagents for every unmerged, detached, dirty or uncertain change set when
available and authorized. Fill useful independent slots within the harness limit. Batch
related candidates when the inventory is large; every candidate still needs a disposition.
The parent owns shared Git mutations and integration. Assign one writer per recovery;
reviewers work read-only. Workers inherit the current model and effort unless instructed
otherwise. Give them frozen source/base identities, original intent, complete diffs and
ownership limits, without a predetermined verdict.

Require source-grounded answers to these questions:

- What behavior or artifact was intended, and what unique work remains today?
- Does current main already provide it, or does any part still offer value?
- What is the smallest useful completion that fits current owners and contracts?
- What tests, review, contributor credit and delivery gates are required?

Use dispositions: **landed**, **useful: complete**, **superseded with proof**, or
**preserve: unresolved**. Disagreement gets an independent review of the disputed evidence.
Minimal value qualifies for preservation and completion; age or unfinished state does not
justify rejection. Keep active or paused work intact and coordinate through authorized
channels. Missing ownership evidence is a preservation reason. If delegation is unavailable,
record that limit and preserve unvetted candidates instead of labeling them reviewed.

## Finish useful work through the existing owners

When authorized, continue each useful item in an isolated checkout from the current base.
Reuse an installed continuation skill if appropriate; otherwise recover original intent,
check competing work, implement at the responsible layer, and preserve contracts and human
contributor credit. Resolve overlaps before parallel implementation. Do not modify an
active source checkout or rewrite a shared branch to simplify integration.

Run the repository's required checks and independent review against the exact final head.
After rebasing or resolving conflicts, refresh affected proof. Push, create a PR, merge with
an expected-head guard, and verify the landed result only within the user's authorization.
Serialize conflicting integrations and recheck current base after each merge. Never bypass
branch protection or replace failed required checks with a worker's assurance. Deployment,
paid services, production data and external messages retain their own authority boundaries.
Close a superseded source PR only after proving its useful changes landed and accounting
for outstanding review findings. Record blocked access or decisions with a concrete next
step; keep their original refs and worktrees. A recovery backlog is unfinished work, not
successful cleanup.

## Preserve, recheck, then remove verified completed resources

Build an exact-target action list from the ledger. Preserve default, protected, shared,
active, locked and uncertain resources. Prefer the harness's archive/restore lifecycle for
managed worktrees; absence from the current chat's attachment list does not prove unmanaged
ownership. Follow the existing refresh-worktree procedure when only updating a checkout.

Preserve lender repositories while any known borrower still depends on their object
stores. Before authorized lender removal, dissociate each known borrower through native Git,
then verify its effective/default alternates, `git fsck --full` and required history/files
independently of that lender. Preserve active or unresolved borrowers and lenders in place.
A verified complete bundle is recovery coverage only; it never authorizes breaking a
borrower. Account for object dependencies before archiving or deleting temporary clones too;
[Git explains the shared-clone risk](https://git-scm.com/docs/git-clone).

Before deletion, retain each removed tip and verify a recovery bundle or equivalent archive
outside every removal target. A Git bundle does not include dirty files, untracked files,
ignored assets, submodule data or local settings: preserve and verify those separately when
needed, without exposing credentials. Record restoration commands and the artifact owner.
Retain backups and preservation refs until separately authorized to remove them.

Immediately recheck each target's tip, status, locks, activity, important ignored resources,
PR state and current base. A changed source invalidates that target's decision. Use
non-force worktree removal for clean verified-done ordinary trees. Use safe local branch
deletion; a squash-only branch needs explicit coverage for its exact ref before a stronger
delete. Never use broad pruning or filesystem deletion as a fallback after a failed gate.
Preserve the actual error and exit status: a sandbox write denial, filesystem permission
error, lock or remote outage is not evidence of unmerged work. For an already authorized
safe deletion blocked by the sandbox, request the supported escalation for that same
operation; do not substitute a force delete or relabel the branch as unmerged.

For authorized remote cleanup, verify the exact repository and branch, current protections,
open PR use and worktree ownership. Delete only the frozen completed tip with an
expected-tip lease, for example:

```sh
git push --force-with-lease=refs/heads/BRANCH:EXPECTED_SHA REMOTE :refs/heads/BRANCH
```

Substitute reviewed arguments safely; this is a conditional deletion, not permission to
force update history. A moved tip or rejected lease stops that target. Verify the ref's
absence with the remote, then prune stale tracking refs if authorized. Local tracking-ref
pruning alone does not delete remote branches. Keep stashes until independently recovered
and their deletion is authorized; a merged branch does not prove a stash is redundant.

## Prove closure

Repeat the inventory and reconcile every original item plus newly discovered resources.
Record exact removed refs/paths, recovery artifacts, landed PRs and revisions, preserved
items with reasons, failed actions, unavailable evidence and unrun checks. Verify retained
checkouts and dirty state were preserved. Run the same assessment again: completed items
must need no further mutation. Do not report a clean repository while recoveries, required
checks, ownership decisions or remote verification remain open. A recurring invocation
starts from fresh evidence and verified current task authority. Reuse still-valid
authorization; reassess its scope rather than requiring a new grant on every run. Build
a new action list from that evidence.
