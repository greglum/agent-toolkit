---
name: docs-sync
description: Audit or update project documentation against current code, commands, ownership, and navigation. Use when changes leave README, AGENTS, plans, or linked docs stale, duplicated, or obsolete. Audit, review, check, and dry-run requests report findings without edits; sync, fix, and update requests apply scoped corrections.
compatibility: Needs access to the selected documentation and its owning source. Git is optional for history and change comparisons. Without command execution, assess source claims and mark commands and gates unrun. Installs no tools.
arguments:
  - name: files
    description: "Specific documentation files (default: docs affected by the requested change)"
  - name: dry-run
    description: Report findings without editing
---

# Documentation sync

Make documentation claims true against current source, easy to find, and free of obsolete task
scaffolding. Keep principles, constraints, decisions, and useful pointers. Replace volatile
inventories with their owner when that preserves what the reader needs.

## 1. Choose the mode and scope

- **Audit:** `--dry-run`, audit, review, check, or an unclear request. Report evidence,
  file dispositions, and proposed corrections; edit nothing and create no files.
- **Edit:** an instruction to sync, fix, refresh, or update docs. Apply corrections
  within that requested scope. Existing authorization remains valid; routine local
  edits do not need another approval.
- **Change review:** given a diff, PR, or commit range, inspect only documentation describing
  the changed behavior, its section indexes, and inbound references. A source-only change can
  invalidate a guide. Use the caller's exact target revisions, including Git tree reads for a
  frozen review; never substitute a dirty checkout for committed target evidence. Report only
  drift introduced or left unresolved by this change; a dated measurement remains evidence for
  its revision, not stale. Do not turn a PR into a full-tree audit. Edit nothing unless asked.
- **Full-tree audit:** when asked to review or organize a docs tree, inventory every file under
  the requested directory using `git ls-files` plus a filesystem inventory to distinguish tracked,
  untracked, and ignored material (do not follow symlinks outside the tree). Read every prose
  file in scope and inspect structured evidence for purpose, validity, provenance, and
  consumers; report unread or unsupported files explicitly. A path listing, heading scan, or
  passing link gate is not a content review.

This skill is automatically discoverable and inherits the caller's authority: a review stays
read-only, while an implementation task may update affected docs. Selection alone permits no
deletion, publication, deployment, or global harness change.

Read repository instructions, record the revision and dirty-file ownership, and respect
canonical sources, generated projections, and file ownership. Do not overwrite unrelated
changes or edit generated documentation directly.

Use named files when supplied. Otherwise inspect root README/AGENTS/CLAUDE files, section
indexes, and task-relevant links to find docs affected by the change. History locates
possible staleness; current code establishes the claim. Inventory the entire requested
scope and keep a coverage list. Do not expand a small correction into an unrelated
documentation rewrite.

## 2. Verify claims, ownership, and navigation

For each target doc, read its content against its stated role (current contract, how-to,
reference, deferred work, decision record, dated plan, or supporting evidence) and check
current claims against the owning source. Trace implemented behavior rather than copying
source comments. Verify:

- paths, section index registration, relative links, and heading anchors;
- commands, prerequisites, and version constraints: CI workflows show which commands really
  run, and the lockfile, package manifest, and version files own package-manager and version
  claims;
- loading: an agent instruction file that no harness the project uses will load, checked
  against each harness's current documentation, is a finding;
- ownership and duplication: competing canonical homes, inherited template examples presented
  as shipped behavior, moved ownership, and instructions duplicated across rules, skills, and
  guides;
- navigation gaps: orphaned or unregistered docs, broken indexes, or folder layouts that hide
  the canonical home;
- configuration, public contracts, architecture, and applicable rules;
- consistency with linked documentation and canonical sources.

Search repository-wide callers before recommending a move or removal, including prompt or skill
dependencies, code, checks, tests, and evidence manifests. No inbound Markdown link alone does
not prove a file is unused.

Run a command only when its side effects are known and authorized. An install,
deployment, migration, external request, or production write is not a documentation
check merely because it appears in a README. Use source/help evidence where possible
and label execution unverified when the command was not run.

For dated plans and historical records:

- Verify whether a dated plan's recommendations landed, remain open, or were rejected.
  Distinguish source evidence from remote issue or PR state; offline evidence cannot establish
  today's tracker state.
- Require a concrete reader or agent-facing reason to retain each file: current contract,
  supported how-to or reference, active or explicitly deferred work, or evidence still used for
  an approval, incident, decision, or reproducible measurement. A dated title or unique wording
  alone does not earn retention.
- Completed ticket graphs, continuation prompts, routine check logs, and superseded
  implementation recipes can be flagged as removal candidates once surviving owners cover their
  useful content. Git history preserves obsolete task narrative; record the recovery revision
  when helpful instead of creating archive folders or wrappers to avoid deciding.
- A completed plan may still own useful measurements, approvals, incident evidence, or an ADR's
  rationale. Trace active use and keep that evidence at its owner or name a verified surviving
  home. Historical measurements stay tied to their revision, never rewritten as current results.
- Preserve ADR numbers, historical decisions (mark supersession instead of deleting or
  renumbering), and test-deletion approval ledgers. Never erase a policy or binding requirement
  solely because today's code differs; report unresolved contradictions instead of silently
  rewriting requirements to bless the code.

For a corpus with repeated claims, reuse the coverage list as a claim ledger: doc locator,
claim, owning source/revision, evidence, and disposition. Keep unresolved or historical claims
separate from false current claims. This is a view of the existing audit record, not a new
index, documentation format, or requirement for a small correction.

## 3. Correct only supported problems

Give each reviewed file a disposition: **keep**, **refine**, **move/consolidate**, or
**removal candidate**. Group files only when every member and the shared reason are named.
Prefer existing audience or task folders; add a folder only when it resolves a concrete
navigation problem, and keep a plan's evidence beside its narrative.

In audit mode, record each stale claim, ownership or navigation issue, its source evidence,
and the proposed change. Stop before the edit step.

In edit mode:

1. Correct false current claims, broken paths, commands, section indexes, and links.
2. Refine current guidance at its canonical home and remove repeated instructions; keep a
   pointer only when it helps the intended reader find the owner. Label examples clearly.
3. Remove text that mirrors source without explaining why, when, or what must hold.
4. Preserve required phrases, anchors, code, data, and deliberate historical records.
5. Add only knowledge needed to prevent a wrong reader decision.

A removal recommendation names exact paths, the obsolete content, the surviving source of
truth, callers to update, and any unresolved retention decision. Apply removals only when the
request explicitly authorizes those targets; a general request to identify cleanup is an audit,
not blanket deletion authority. Moves update inbound links and indexes in the same change. Do
not erase another task's untracked files or rewrite immutable evidence to make checks pass.

Preserve the writer's register and formatting. Create missing docs only when the
request includes creation. If no target docs exist, report that fact. A missing source
is an unresolved claim, not evidence that its documentation should be deleted.

## 4. Verify and finish

Recheck modified links, anchors, required phrases, and claims. New untracked Markdown may fall
outside tracked-link gates; inspect its links separately without staging unrelated work. Run
the repository's required documentation gates within the authorized scope and inspect the final
diff for unrelated changes. Preserve stronger repository gates.

Report mode, coverage, findings and dispositions, edited paths, removal candidates, and checks
passed, failed, unavailable, or unrun. For a full-tree audit, include a per-file or exhaustive
named-group coverage record and a proposed directory map when structure changes. For change
review, return only defects introduced or left unresolved by the target change. Audit completes
with evidence and proposed corrections; edit completes with verified scoped corrections or
plainly reported blockers. Do not claim that a command works because its spelling matches
source.
