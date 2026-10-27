---
name: encode-correction
description: "Prevent repeated agent mistakes by finding their source in history or user corrections, then changing the owning architecture, types, or checks. Use for recurring review findings, correction sweeps, or requests inspired by pstack /correct. A single incident needs evidence of a recurring rule."
---

# Encode a correction

Make the correct change the natural change for an agent that reads one file and copies its
nearest example. Fix the environment that permits the mistake, rather than accumulating
instructions about it. Use the repository's own development and review workflow.

## 1. Establish the evidence

Read the repository instructions, current branch/worktrees, dirty paths, and existing gates.
Preserve unrelated work. Name the authorized scope, targets, and completion checks. Audit-only
requests stay read-only. A request to implement this workflow authorizes local corrections
within its scope; publication, deployment, destructive changes, and harness configuration
still need their own authority. Reuse authority already given.

For a sweep, inspect recent commits, reverts, available review findings, and existing rule
owners. Record the revision range and unavailable sources. Group concrete incidents by the
same failed invariant, not by similar wording. A recurring class needs two distinct incidents;
a re-review of one incident is still one. An explicit user rule can also establish the class.
Treat an instruction without a check as a lead, not proof the mistake happened.

For each class, record source locations, a real bad example, the intended behavior, its current
owner, and whether today's code already prevents recurrence. Prioritize material impact and
frequency. Fix a one-off locally when requested; do not invent a permanent rule for it.

Done when each candidate has evidence and a disposition: already prevented, actionable,
one-off, outside scope, or uncertain. Missing evidence stays uncertain.

## 2. Remove the opportunity at its owner

Trace the affected callers and trust boundaries before editing. Compare the smallest fitting
options in order, stopping at the first that preserves the repository's contracts:

1. **Architecture:** put state and decisions with one responsible owner; derive repeated lists
   from that owner, narrow an unsafe public boundary, or migrate callers off an obsolete path.
2. **Types and native constraints:** express valid states or enforce the invariant with the
   existing type system, schema, database, or installed tool.
3. **Existing gate:** extend a lint rule or focused check. Its diagnostic should identify the
   offending location and the supported replacement. Wire it into the actual required gate.
4. **Behavior test:** extend the nearest suite only when it meets the repository's test-value
   policy and detects a material failure beyond existing checks.
5. **Judgment guidance:** one line at the existing instruction owner only when a mechanical
   boundary cannot express the decision. Report that this remains unenforced.

Explain why higher levels do not fit. Reuse the existing owner; a second policy table, hook,
framework, or CI job needs a concrete gap. Apply coherent caller migrations when architecture
is the fix. Preserve authorization, privacy, concurrency, error handling, and accessibility.
Test removal or weakening requires the repository's explicit approval, even when upstream
guidance suggests deleting weak tests.

Done when each selected class has one enforcement owner and a reviewable change or an
evidence-backed reason to leave it alone.

## 3. Prove prevention and preservation

For every new or changed mechanical check, run the real bad example in an isolated scratch
copy. The check must fail for the intended reason. Run the corrected example and the current
scoped tree; both must pass. Confirm it examined the affected files. A synthetic variant may
extend proof but cannot be reported as a historical incident.

For a behavior test, try the two edits separately: breaking the promised behavior must turn
it red; a behavior-preserving internal change should leave it green. Keep probes isolated.
For an architecture or type correction, demonstrate that the old unsupported path is gone or
rejected, and run the existing behavior checks for migrated callers.

Count existing violations before broad changes. Within authorized scope, fix them or use the
repository's existing ratchet convention. Baselines must prevent trading a fixed violation
for a new one elsewhere and reject stale entries. Each exception needs an owner and rationale
under repository policy. Do not introduce a new waiver system just for this run.

Run affected checks and the required delivery gates. Keep failed, unavailable, and unrun
checks distinct. Stop dependent delivery on a failure; continue safe diagnosis. Report the
actual local or CI wiring, without inventing CI where none exists.

Done when the old mistake is rejected, the correction passes, and required preservation
checks pass, or the unresolved limit is explicit and dependent delivery is stopped.

## 4. Review and repeat within the requested bound

Review the complete change against evidence, repository rules, and task intent. Use an
independent reviewer when authorized and available; otherwise disclose self-review. Resolve
confirmed findings, rerun affected checks after edits, and review the revised head. Do not
repeat unchanged checks just to count a pass.

When the user requests several runs, keep one worktree and record each run's base/head,
examined evidence, classes, changes or no-change result, proof, and review outcome in the
existing task record. Each run reassesses current evidence. A clean run is a valid result;
neither a quota of edits nor repeated speculation establishes a new class. Stop at the
requested bound and report any unfinished work.

Keep rule-to-enforcement links at the existing rule owner when they help future changes.
Avoid duplicating instructions in a new always-loaded ledger. Publish or merge only under
the user's target authority and the repository's final-head delivery rules.

## Report

Return each class's incidents, owner, selected level, reasons higher levels did not fit,
change or disposition, bad/good proof, existing violations, and remaining judgment calls.
State the reviewed revision, required check results, completed run count, and delivery state.

Source and intentional departures: [pstack /correct adaptation](references/provenance.md).
