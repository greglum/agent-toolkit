# Dated plans, historical records, and claim ledgers

Load this reference when auditing a full documentation tree, reviewing dated plans or
historical records, or tracking repeated claims across a multi-file corpus.

## Dated plans and historical records

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

## Corpus claim ledger

For a corpus with repeated claims, reuse the coverage list as a claim ledger: doc locator,
claim, owning source/revision, evidence, and disposition. Keep unresolved or historical claims
separate from false current claims. This is a view of the existing audit record, not a new
index, documentation format, or requirement for a small correction.
