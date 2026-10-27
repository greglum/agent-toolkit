# Lanes and source rules

## Source rules for every lane

- **Recency** comes from commit history, changelog entries, and dated posts. Stars, install
  counts, leaderboards, and push timestamps are discovery leads only.
- **Pin** every source to a commit SHA or tag with its date. An installer folder hash is a Git
  tree hash; find the commit whose `git rev-parse <commit>:<folder>` equals it.
- **License** is read at that revision. Public access is not permission to copy. Restate ideas in
  your own words; never paste upstream prose or code into a skill.
- **Read cheaply.** Prefer `gh api` reads of commits and contents, or blobless clones
  (`git clone --filter=blob:none`) in a scratch directory with selected `git show` reads. Never
  run upstream scripts, hooks, or installers.
- **Blocked hosts.** When a host or API refuses, say so, use search excerpts only as secondary
  evidence, and mark the claim unverified until a primary source confirms it.
- **Privacy.** Search queries and fetches carry only public, generic terms: no repository
  content, private names, paths, or URLs.
- **Capability check.** For tools and artifacts, return source/local implementation evidence
  using [capability comparison](capability-comparison.md). A model's ability to build a feature
  on demand does not establish that our skill already supplies reusable machinery.
- **Base-model check.** For each procedural idea, say whether a capable model would do it unprompted. If
  yes, mark it "likely no-op". Still report it when a miss would be a mandatory failure (scope,
  preservation, destructive action, authority, security); the parent decides.

## Return format

Ask every lane for: a table of sources (URL, SHA, date, license, what changed, the idea in its
own words, candidate target skill and the line that would change, likely no-op or not,
confidence); the sources checked with no change; and what it could not confirm and where it
looked. Give a word cap and a finish line, for example "every registry author is listed as
changed or unchanged".

## Lane briefs

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
   recheck items, with file and line evidence. It runs by default; it can be short when the
   previous report's process lessons are already in this skill.
