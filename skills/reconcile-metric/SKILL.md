---
name: reconcile-metric
description: Trace a disputed dashboard number or aggregate to its definition and source records, then reconcile it independently. Use for conflicting totals, join inflation, rate denominators, weighted averages, or time-window mismatches; not general chart styling or database tuning.
---

# Reconcile a metric

Deliver an evidence record that explains the observed value and any remaining difference.
An audit permits inspection and calculation, not changes to product code, stored data, or
business definitions. Use the destination's access rules, query limits, and data-handling
requirements. Keep sensitive rows out of reports; use redacted identifiers or aggregates.

## 1. Bind the comparison

Identify the disputed value, where and when it was observed, and the comparison value.
Read the project's metric definitions and owning code. Record units, entity grain, eligible
population, numerator and denominator, aggregation, time window, timezone, filters, and
freshness for each side. Mark missing definitions as unknown; do not choose business meaning
from a label alone. Finish with comparable definitions or an explicit mismatch to investigate.

## 2. Trace the value

Follow displayed value -> API field -> calculation -> query -> source records, skipping only
layers the system does not have. Cite each hop and its source revision or observation time.
Track transformations, cached results, rounding, exclusions, and permission-dependent filters.
For every aggregate, establish:

- The grain before and after each join, the join keys, and whether multiplicity changes the
  contribution of an entity. Extra rows can be intentional; distinct counts do not repair sums.
- Whether null means unknown, absent, ineligible, or zero. Keep asserted totals distinct from
  recorded sums. Preserve missing observations rather than silently filling them.
- Whether a rate uses a shared denominator, a weighted aggregate, or an average of group rates.
  Preserve numerator and denominator through regrouping; verify the handling of zero weights.
- Whether both sides cover the same complete or partial period, timezone boundaries, source
  snapshot, units, and included population.

Finish when every transformation affecting the discrepancy has evidence or a named gap.
Judge plausible ranges against the actual metric contract: negatives and percentages above
100 can be valid for returns, growth, or variance.

## 3. Recalculate independently

Use authorized source records at the intended grain to calculate the contractual value without
reusing the suspect aggregation path. A repeated API call or the same query in a new wrapper
is not an independent check. Prefer the smallest read-only calculation that can distinguish
the competing explanations. Verify that extracted records are complete enough for the claim.

Compare observed and recomputed values at full precision, then account for presentation
rounding separately. Define the residual as observed minus recomputed, with units; report a
relative difference only when its denominator is meaningful. Account for each supported cause
and leave the unexplained remainder visible. Derive any tolerance from the contract or known
numeric precision, not from the difference you want to dismiss.

If source records or definitions are unavailable, report the trace and missing evidence.
Do not replace a live-data check with fabricated rows or claim reconciliation from source
inspection alone. Synthetic examples can illustrate a hypothesis if labeled as such.

## 4. Deliver the evidence record

Include the definitions and scope, linked trace, independent method and inputs, observed and
recomputed values, explained difference, remaining residual, and unknowns. Separate confirmed
causes from hypotheses and unavailable or unrun checks. Recommend a change at the owning layer
only when the evidence supports it. Apply fixes only within the user's authorized scope and
preserve the project's required verification gates.

For provenance or future revisions of this method, read [sources](references/sources.md).
