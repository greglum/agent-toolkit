---
name: docs-sync
description: Audit or update README, AGENTS.md, plans, and docs/ when code, CLI flags, commands, links, or navigation drift. Audit/dry-run reports only; sync/fix/update edits in scope. Not for prose-only cleanup (deslop), context retros (retro-agent-context), repo agent-setup (agent-readiness), external library docs (find-docs), or chat specs (to-spec).
compatibility: Needs access to the selected documentation and its owning source. Git is optional for history and change comparisons. Without command execution, assess source claims and mark commands and gates unrun. Installs no tools.
---

# Documentation sync

Make documentation claims true against current source, easy to find, and free of obsolete task
scaffolding. Keep principles, constraints, decisions, and useful pointers. Replace volatile
inventories with their owner when that preserves what the reader needs.

## 1. Choose the mode and scope

**Mode:**

- **Audit:** `--dry-run`, audit, review, check, or an unclear request. Report evidence,
  file dispositions, and proposed corrections; edit nothing and create no files.
- **Edit:** an instruction to sync, fix, refresh, or update docs. Apply corrections within
  the requested scope. Existing authorization remains valid; routine local edits do not need
  another approval.

**Scope:**

- **Named files or handoff packet:** use supplied file paths, or inspect root
  `README`/`AGENTS`/`CLAUDE` files, section indexes, and task-relevant links. Accepts
  repeated-drift handoff packets from `retro-agent-context` (`files`, stale claim class,
  `coverage.head`, and unresolved items) and other callers.
- **Change review:** given a diff, PR, or commit range:
  - Inspect only docs describing the changed behavior, section indexes, and inbound links
    (a source-only change can invalidate a guide).
  - Use the caller's exact target revisions, including Git tree reads for a frozen review;
    never substitute a dirty checkout for committed target evidence.
  - Report only drift introduced or left unresolved by this change. Keep dated measurements
    tied to their revision; do not expand into a full-tree audit.
- **Full-tree audit:** when asked to review or organize a docs tree:
  - Inventory every file under the requested directory using `git ls-files` plus a filesystem
    scan to separate tracked, untracked, and ignored files (never follow symlinks outside).
  - Read every prose file in scope and inspect structured evidence for purpose, validity,
    provenance, and consumers; report unread or unsupported files explicitly.
  - A path listing, heading scan, or passing link gate is not a content review.

Selection alone permits no deletion, publication, deployment, or global harness change. Read
repository instructions, record the revision and dirty-file ownership, and respect canonical
sources, generated projections, and unrelated work. Do not expand a small correction into an
unrelated rewrite.

Done when mode, scope, revision, and coverage list are recorded.

## 2. Verify claims, ownership, and navigation

Read each target doc against its stated role (contract, how-to, reference, deferred work, ADR,
dated plan, or evidence) and check current claims against owning source. Trace implemented
behavior rather than copying source comments. Verify:

- paths, section index registration, relative links, and heading anchors;
- commands, prerequisites, and version constraints (CI workflows show real commands; lockfiles
  and manifests own package-manager and version claims);
- loading (flag agent instruction files that no project harness loads per current harness docs);
- ownership and duplication (competing canonical homes, template examples shown as shipped
  behavior, moved owners, instructions duplicated across rules, skills, and guides);
- navigation gaps (orphaned docs, broken indexes, folder layouts hiding the canonical home);
- configuration, public contracts, architecture, rules, and consistency across linked docs.

Search repository-wide callers before recommending a move or removal, including prompt or skill
dependencies, code, checks, tests, and evidence manifests. No inbound Markdown link alone does
not prove a file is unused.

Run a command only when its side effects are known and authorized. An install, deployment,
migration, external request, or production write is not a documentation check merely because
it appears in a README. Label execution unverified when a command was not run.

For full-tree audits, dated plans, or corpora with repeated claims, read
[dated plans and claim ledger](references/dated-plans-and-ledger.md).

Done when every in-scope file and claim has source evidence or an explicit unverified/unread note.

## 3. Correct only supported problems

Give each reviewed file a disposition: **keep**, **refine**, **move/consolidate**, or
**removal candidate**. Group files only when every member and the shared reason are named.
Prefer existing audience or task folders; add a folder only for a concrete navigation problem,
and keep a plan's evidence beside its narrative.

In **Audit** mode, record each finding, disposition, source evidence, and proposed change, then
skip to step 4 without editing.

In **Edit** mode:

1. Correct false current claims, broken paths, commands, section indexes, and links.
2. Refine current guidance at its canonical home and remove repeated instructions; keep a
   pointer only when it helps the intended reader find the owner. Label examples clearly.
3. Remove text that mirrors source without explaining why, when, or what must hold.
4. Preserve required phrases, anchors, code, data, and deliberate historical records.
5. Add only knowledge needed to prevent a wrong reader decision.

A removal recommendation names exact paths, the obsolete content, the surviving source of
truth, callers to update, and any unresolved retention decision. Apply removals only when the
request explicitly authorizes those targets; a general cleanup request is an audit, not
blanket deletion authority. Moves update inbound links and indexes in the same change. Never
erase another task's untracked files or rewrite immutable evidence to pass checks.

Preserve the writer's register and formatting. Create missing docs only when requested. If no
target docs exist, report that fact; a missing source is an unresolved claim, not deletion
evidence.

Done when Audit proposals are listed, or Edit corrections and inbound index updates are applied.

## 4. Verify and finish

In **Edit** mode, recheck modified links, anchors, required phrases, and claims (inspect
untracked Markdown links separately without staging unrelated work). Run repository
documentation gates within the authorized scope and inspect the final diff for unrelated
changes. If a post-edit link check or required documentation gate fails, fix the broken
reference within scope or revert incomplete moves and report the failure before stopping.

Report mode, scope, coverage, findings and dispositions, edited paths, removal candidates,
and checks separated into **passed**, **failed**, **unavailable**, and **unrun** with exact
command and exit-code receipts for every gate executed. Include per-file or named-group
coverage and any proposed directory map for full-tree audits, and stay within the Section 1
scope rules. Never claim a command works because its spelling matches source.
