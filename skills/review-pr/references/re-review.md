# Re-review evidence

Use when reviewing the same PR after fixes. One invocation delivers one review; it does not
start an author/reviewer loop or authorize fixes, thread resolution, or further passes.

1. Recover the prior report's repository identity, comparison base, head, path coverage and
   findings. Without that evidence, perform the complete initial review. Prior approval alone
   is not coverage evidence.
2. Pin the current endpoints using Step 1. Keep the full base-to-head comparison as the
   verdict's scope. Compare the prior head with the current head to locate fixes and new
   changes. Read complete current blobs for new or changed text paths and base blobs for
   deletions. Recheck affected callers, contracts and instructions. Reuse
   prior inspection only for identical blobs whose relevant context and requirements remain
   unchanged; name that evidence in the coverage ledger. A changed base or merge base needs
   reconciliation too. If reuse cannot be justified, inspect the affected scope again.
3. Reconcile each prior finding as unresolved, fixed, dismissed with a reason, or unverifiable.
   Verify fixes in the current committed code. A resolved thread alone does not prove a fix.
   Keep unresolved findings visible under the same identity. Reopen a dismissed finding only
   with new evidence or a change that worsens it; explain the difference. Report new defects
   separately and group equivalent instances by their failed invariant.
4. Apply the normal coverage, instruction, threshold and freshness gates to the current PR.
   State reused and newly inspected evidence separately. Missing coverage, unresolved material
   findings or stale endpoints still prevent unconditional approval. Reaching a round limit
   never clears a finding. If an authorized surrounding workflow has a review-round budget,
   report its remaining blockers when that budget is exhausted rather than continuing it.

This is a procedure for manual agent review, not a hosted reviewer or enforcement mechanism.
