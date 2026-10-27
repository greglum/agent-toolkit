---
name: docs-sync
description: Audit or update project documentation against current code and commands. Use when a change leaves README, AGENTS, or linked docs stale. Audit, review, check, and dry-run requests report findings without edits; sync, fix, and update requests apply scoped corrections.
disable-model-invocation: true
arguments:
  - name: files
    description: "Specific documentation files (default: docs affected by the requested change)"
  - name: dry-run
    description: Report findings without editing
---

# Documentation sync

Make documentation claims true against current source. Keep principles, constraints,
decisions, and useful pointers. Replace volatile inventories with their owner when
that preserves what the reader needs.

## 1. Choose the mode and scope

- **Audit:** `--dry-run`, audit, review, check, or an unclear request. Report evidence
  and proposed corrections; edit nothing and create no files.
- **Edit:** an instruction to sync, fix, refresh, or update docs. Apply corrections
  within that requested scope. Existing authorization remains valid; routine local
  edits do not need another approval.
- **Change review:** given a diff or commit range, check the docs that describe the changed
  behavior and their inbound links. Report only drift this change introduced; a dated
  measurement remains evidence for its revision, not stale. Edit nothing unless asked.

Read repository instructions and record dirty paths. Respect canonical sources,
generated projections, and file ownership. Do not overwrite unrelated changes or
edit generated documentation directly.

Use named files when supplied. Otherwise inspect root README/AGENTS/CLAUDE files
and follow task-relevant links to find docs affected by the change. History locates
possible staleness; current code establishes the claim. Inventory the entire requested
scope and keep a coverage list. Do not expand a small correction into an unrelated
documentation rewrite.

## 2. Verify claims against their owner

For each target doc, read its content and the source that owns its claims. Verify:

- paths, links, and heading anchors;
- commands, prerequisites, and version constraints: CI workflows show which commands really
  run, and the lockfile, package manifest, and version files own package-manager and version
  claims;
- loading: an agent instruction file that no harness the project uses will load, checked
  against each harness's current documentation, is a finding;
- configuration, public contracts, architecture, and applicable rules;
- consistency with linked documentation and canonical sources.

Run a command only when its side effects are known and authorized. An install,
deployment, migration, external request, or production write is not a documentation
check merely because it appears in a README. Use source/help evidence where possible
and label execution unverified when the command was not run.

Do not erase an ADR, historical explanation, planned item, or policy solely because
today's code differs. Determine whether the text describes current behavior, history,
intent, or a binding requirement. Report unresolved contradictions instead of silently
rewriting requirements to bless the code.

## 3. Correct only supported problems

In audit mode, record each stale claim, its source evidence, and the proposed change.
Stop before the edit step.

In edit mode:

1. Correct false current claims, broken paths, commands, and links.
2. Give each fact one canonical home; replace redundant copies with useful links.
3. Remove text that mirrors source without explaining why, when, or what must hold.
4. Preserve required phrases, anchors, code, data, and deliberate historical records.
5. Add only knowledge needed to prevent a wrong reader decision.

Preserve the writer's register and formatting. Create missing docs only when the
request includes creation. If no target docs exist, report that fact. A missing source
is an unresolved claim, not evidence that its documentation should be deleted.

## 4. Verify and finish

Recheck modified links, anchors, required phrases, and claims. Run the repository's
required documentation gates within the authorized scope and inspect the final diff
for unrelated changes. Preserve stronger repository gates.

Report mode, coverage, findings and dispositions, edited paths, and checks passed,
failed, unavailable, or unrun. Audit completes with evidence and proposed corrections;
edit completes with verified scoped corrections or plainly reported blockers. Do not
claim that a command works because its spelling matches source.
