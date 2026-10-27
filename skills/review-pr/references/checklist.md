# Review checklist

Load from Step 4 for the guideline and bug questions and the confidence scale.

## Guideline compliance

If AGENTS.md or project-specific guidelines exist:
- Verify changes follow documented conventions
- Check naming patterns, file organization, import style
- Verify test requirements are met
- Only flag violations when the guideline **explicitly** addresses the issue

If no committed instructions apply, skip guideline compliance and note it.

## Bug detection

Attribute a regression only when the PR introduced it. Separately report an incomplete repair
of a requirement the PR promises to satisfy, even if the underlying defect predates it. Keep
unrelated pre-existing issues outside the PR verdict. Flag missing error handling only when
the failure has a real cost where the code runs: a crash, a caller acting on a wrong result,
or partial work a rerun will not repair.

For conflict markers in committed content, verify whether they are intentional text or an introduced defect; unresolved code conflicts block approval.

Check each suggested fix against the original problem so it does not reintroduce it, and apply
rules that fit the changed layer: backend, frontend, CI, and scripts have different constraints.

For a planner or evaluator that mirrors production, trace the same boundary inputs through both
owners. Compare acceptance and size limits with the payload actually emitted; a conservative
estimate or a matching happy path alone does not prove equivalence.

Treat scanner output as a candidate. Check the pinned dependency contract and reproduce the
user impact before changing semantics. Verify that the proposed repair improves that behavior
rather than merely changing the warning.

## Confidence scale

| Score | Meaning |
|-------|---------|
| 0-25 | Probably a false positive |
| 26-50 | Might be real, likely a nit |
| 51-75 | Likely real, worth noting |
| 76-90 | Confident this is a real issue |
| 91-100 | Certain this is a real issue |
