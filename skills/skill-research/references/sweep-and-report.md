# Catalog sweep lanes, concurrent ownership, and round reports

## Integrate concurrent research changes

Use this procedure when another session or round may edit the same checkout, branch, catalog
index, or registry. Reuse the round's existing state record outside the repository.

### Bind one integration owner

Record the integrating session, repository, target branch and HEAD, its working-tree/index
state, and the paths each round owns. Inspect existing coordination records and active
worktrees before claiming ownership. A matching branch name or a clean index is not ownership.

Only the named integrator changes the shared checkout's files, index, or branch state.
Other writers use task-owned worktrees with separate branches or detached heads. Read-only
research lanes remain read-only. If the current integration owner cannot be reached, keep
the new round isolated and report integration pending; do not take over its checkout.

### Hand off exact work

Each writer returns its worktree, base and current HEAD, owned path/hunk allowlist, reviewed
patch and untracked artifacts, and checks bound to that content. Identify dependencies,
excluded dirty work, and unresolved decisions. Keep coordination state out of catalog commits.

The integrator inspects the original changes and combines them one round at a time. Shared
registry and index entries are reconciled against their current content, preserving entries
from other rounds. A stale whole-file copy is not a valid integration patch.

### Recheck before changing shared state

Before each integration, staging, commit, or push, compare current HEAD, selected file content,
and index with the reviewed snapshot. On a mismatch, stop the dependent write, inspect the
new state, and rebuild the affected patch. After one conflict-driven refresh of the same shared
file or index, another mismatch leaves that shared integration pending until ownership is
settled. An independently merged upstream PR is handled by the normal branch-update and review
gates.

Recheck the final diff and run required checks on integrated content. Reuse unaffected proof;
rerun invalidated checks. Report each round as integrated or pending with its exact revision
and blocker. Commit, push, PR creation, and merge retain their separate action authority.

## Catalog sweep lanes and source rules

### Source rules for every lane

- **Recency** comes from commit history, changelog entries, and dated posts. Stars, install
  counts, leaderboards, and push timestamps are discovery leads only.
- **Pin** every repository source to a commit SHA or tag with its date. Identify a paper,
  dataset, rule or living page by URL, author or publisher, publication and observation dates,
  and section or version. An installer folder hash is a Git tree hash and a file hash is a
  blob hash; neither is a commit. Find the commit whose `git rev-parse <commit>:<path>` equals it.
- **License** is read at that revision or on that page. Public access is not permission to copy.
  Restate ideas in your own words; never paste upstream prose or code into a skill.
- **Read cheaply.** Prefer `gh api` reads of commits and contents, or blobless clones
  (`git clone --filter=blob:none`) in a scratch directory with selected `git show` reads. Never
  run upstream scripts, hooks, or installers. List the pinned tree before reading files; a
  guessed path's 404 proves only that the path is absent. Cap each read, save long responses
  to scratch, and reread any clipped range before relying on it.
- **Blocked hosts.** When a host or API refuses, say so, use search excerpts only as secondary
  evidence, and mark the claim unverified until a primary source confirms it. A sandbox DNS,
  TLS or network refusal is a route restriction, not a dead host: try the available connector,
  fetch tool or an approved read before calling the source unavailable.
- **Privacy.** Search queries and fetches carry only public, generic terms: no repository
  content, private names, paths, or URLs.
- **Capability check.** For tools and artifacts, return source/local implementation evidence
  using [capability comparison](url-and-source-intake.md#compare-delivered-capability). A model's
  ability to build a feature on demand does not establish that our skill already supplies
  reusable machinery.
- **Base-model check.** For each procedural idea, say whether a capable model would do it
  unprompted. If yes, mark it "likely no-op". Still report it when a miss would be a mandatory
  failure (scope, preservation, destructive action, authority, security); the parent decides.

### Return format

Ask every lane for: a table of sources (URL, SHA, date, license, what changed, the idea in its
own words, candidate target skill and the line that would change, likely no-op or not,
confidence); the sources checked with no change; and what it could not confirm and where it
looked. Give a word cap and a finish line, for example "every registry author is listed as
changed or unchanged".

### Lane presets

- **Catalog sweep** (default without URLs): the four lane briefs below.
- **New domain** (the catalog has no owner for the area): skip known authors. Run vendor
  skills, community skills, domain methods (papers, rules, open data), and current tool
  versions, plus history. Start a registry section for the domain.
- **Topic lanes**: split by subject when one question per lane stays self-contained. Each
  topic lane still returns the format above and names its finish line.
- **Catalog structure** (only when the user asks to reconsider structure): one read-only
  lane audits overlap, granularity, orchestration, discovery cost and packaging across every
  skill, with file and line evidence and a proposal per finding.

### Lane briefs

Run the lanes the focus selects. Each brief is one self-contained question.

1. **Known authors.** For every author in the registry with a public repository, list commits
   after the recorded revision or date, new skill repositories, and the material changes. Finish
   line: every registry author with a public repository is marked changed or unchanged.
2. **New authors.** Survey skills published or substantially updated in the window by authors
   not in the registry: code and topic search for `SKILL.md`, official vendor skill repositories,
   curated lists, and posts about writing or evaluating skills. Start with any unread leads the
   previous report lists. Finish line: a set number of sources examined at a pinned revision, each
   with a disposition. Ask separately for meta-lessons about authoring, triggering, evaluating, or
   maintaining skills.
3. **Platforms.** Changes since the recorded versions in each supported harness's skill format,
   invocation, install locations, and evaluation tooling, and in the open skill standard. Name the
   consequence for the authoring guide, the checker, or a specific skill. Finish line: each
   platform marked changed, with items, or unchanged since the recorded version.
4. **History.** Read the catalog's past round reports for process lessons, failures, and open
   recheck items, with file and line evidence. It runs by default. Read the lessons ledger
   when one exists, so repeats across non-adjacent rounds count.

## Round report and upkeep

### Report

Write one dated file, `YYYY-MM-DD-<topic>.md`, beside the other round reports. A round with
long lane outputs may add a same-named folder of lane files linked from that report. Sections:

1. **Title and status.** Date, branch and base SHA, window, lanes run, and who chose the changes.
2. **Method and limits.** How sources were read, blocked hosts, what counts as recency, and what
   was not run.
3. **Sources.** One row each: URL, pinned SHA, date, license, idea in our words, disposition.
   For tools/artifacts, include the source/local capability matrix, implementation versus
   instruction-only coverage, functional advantages and actionable gaps. State which missing
   functions were built and which still need work; procedural edits do not imply feature parity.
4. **Applied changes.** Owner file, the change, the failure it prevents, the source, and the
   proof (checker, blind run with control, or untested). Include minor refinements and cleanup;
   for zero adoptions, name the owners checked and why no supported fix remained.
5. **Gaps, retained, and rejected.** Each with a reason or the owner that already covers it. This
   may live in the Sources disposition column instead of its own section.
6. **Validation.** Commands run and results. Single runs are labeled as single runs, never as
   pass rates.
7. **Process lessons.** What wasted effort, what a lane got wrong, what had to be rechecked, and
   any lesson seen in an earlier report too (cite it).
8. **Not done and recheck triggers.** Unread leads, unverified claims, owner decisions, and the
   event that should prompt each recheck.

### Upkeep in the same change

- Before appending to a registry, index or ledger, check its size against the repository's
  commit gates. When the next row would cross a limit, first move the oldest sections or rows
  verbatim into a dated archive file as its own move-only change, then append. Commit each only
  with the authority [Publish](../SKILL.md#7-publish) requires; otherwise report the move and
  the append as two changes, in that order.
- When a lessons ledger exists, add each process lesson with the report citation, or add the
  new citation to its existing row.
- Add or update one registry row per author reviewed, adopted or not, with the new "last
  reviewed" link and what was drawn on.
- Add a dated section to the source index that links the report.
- Update the README with the useful outcome or its bundled source note. If a public snapshot
  excludes the research directory, keep the report link in the private source index and point
  the README to a shipped resource. Add a workflow row for any new skill.
- Update vendored-skill pins separately from the review record, and only after the installer
  action they describe has run.
