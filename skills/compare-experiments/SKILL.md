---
name: compare-experiments
description: Analyze supplied paired experiment samples against a frozen practical improvement rule. Use to compare noisy timing, cost or quality measurements, audit missing or failed runs, and confirm a selected candidate on fresh observations; this does not collect measurements or run CI.
compatibility: The offline analyzer needs Python 3.10+ and only its standard library. It reads explicit local JSON files and writes JSON to stdout; no network, provider, collector or installation is required.
---

# Compare experiments

Return an inspectable comparison, including an inconclusive result when the samples do not
support the planned decision. This skill analyzes existing observations. It does not launch
experiments, create PRs, schedule jobs or choose a model.

1. Read the supplied experiment record and [input contract](references/input-contract.md).
   Identify the user outcome, measured proxy, workload, execution profile, revisions, units,
   direction, practical bar, sampling plan and preservation checks. Reuse an existing plan.
   If no plan was fixed before the measurements, label the analysis exploratory. A digest
   binds content; it cannot establish when the plan was written or whether observations are true.
2. Run `python3 <skill>/scripts/compare.py freeze plan.json` before collecting discovery
   observations. Keep its `plan_sha256` with the task's existing record. Freeze the number
   and identities of planned rounds, practical improvement, acceptable unchanged-control
   variation, and `guard_contract` before examining results. Bind the preservation-check content
   or a content hash of its retained definition, not a mutable label. Choose sampling for the task;
   the bundled tiny fixture demonstrates plumbing, not adequate statistical power.
3. Analyze the explicit samples with the retained digest. Check missing, unsuccessful,
   skipped and guard-unknown observations before comparing effect sizes. Inspect the raw
   evidence behind `guards: pass`, revision, workload and profile claims. The tool checks
   matching labels, not their truth, complete CI pagination, billing accuracy or equivalent work.
4. Read the complete result. Positive differences mean improvement in either direction.
   A candidate needs every planned pair usable, each paired difference positive, a median
   difference at least the practical bar and greater than observed unchanged-control spread.
   These are conservative descriptive rules, not significance tests. Keep the supplied raw
   observations, rejects and unknowns. Do not remove an outlier or failed run to obtain a win.
5. If selecting a candidate, run `select` on discovery-only data and preserve its output
   **before** fresh confirmation collection. The selection binds the chosen arm, plan and
   discovery content. Reserve confirmation round/run identities and keep selection fixed.
   Analyze the combined data with `--selection`. A changed plan or discovery record requires
   a new explicit analysis; keep the original result. Multiple candidates are exploration,
   with no automatic winner ranking or correction for multiple comparisons.
6. Deliver the content identities, pair counts, observed spread, differences in original
   units, failed/missing/guard counts, selected confirmation result and remaining limits.
   `CONFIRMED_OBSERVATION` means supplied fresh identities met the same descriptive rule.
   It establishes neither causality, population significance nor behavior on other workloads.
   If chronology, equivalence or the outcome proxy cannot be verified, say so even when the
   arithmetic passes. Stop when the supplied evidence has an accounted-for disposition.

The [input contract](references/input-contract.md) includes the runnable synthetic example,
command exit semantics and exact fields. [Sources and departures](references/sources.md)
record the evidence for this deliberately limited analyzer.
