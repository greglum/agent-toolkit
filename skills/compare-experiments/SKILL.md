---
name: compare-experiments
description: Analyze supplied paired A/B or benchmark experiment samples against a frozen practical rule, auditing noisy timing, cost, or quality effects, missing/failed runs, and candidate confirmation. Does not collect runs; not for codebase baselines (codebase-metrics), disputed totals (reconcile-metric), or time-split validation (temporal-validation).
compatibility: The offline analyzer needs Python 3.10+ and only its standard library. It reads explicit local JSON files and writes JSON to stdout; no network, provider, collector or installation is required.
---

# Compare experiments

Return an inspectable comparison, including an inconclusive result when the samples do not
support the planned decision. This skill analyzes existing observations. It does not launch
experiments, create PRs, schedule jobs or choose a model.

1. Read the supplied experiment record and [input contract](references/input-contract.md).
   If supplied data is unstructured raw logs rather than JSON matching the contract, or if
   Python 3.10+ is unavailable, stop and report the missing contract fields or unavailable
   runtime instead of inventing values to satisfy the schema. Identify the user outcome,
   measured proxy, workload, execution profile, revisions, units, direction, practical bar,
   sampling plan and preservation checks. Reuse an existing plan. If no plan was fixed before
   measurements, construct a retrospective plan JSON matching the schema, label the analysis
   exploratory, and omit pre-registration claims. A digest binds content; it cannot establish
   when the plan was written or whether observations are true.
   Finish: contract-valid `plan.json` and exploratory vs. pre-registered status recorded.
2. Run `python3 <skill>/scripts/compare.py freeze plan.json` before collecting discovery
   observations (or before analyzing a retrospective exploratory plan). Keep its `plan_sha256`
   with the task's existing record. Freeze the number and identities of planned rounds,
   practical improvement, acceptable unchanged-control variation, and `guard_contract` before
   examining results. Bind the preservation-check content or a content hash of its retained
   definition, not a mutable label. Choose sampling for the task; the bundled tiny fixture
   demonstrates plumbing, not adequate statistical power.
   Finish: `freeze` exits `0` and `plan_sha256` is saved.
3. Analyze the explicit samples with `--plan-sha`. Check missing, unsuccessful, skipped and
   guard-unknown observations before comparing effect sizes. Inspect the raw evidence behind
   `guards: pass`, revision, workload and profile claims. The tool checks matching labels, not
   their truth, complete CI pagination, billing accuracy or equivalent work.
   Finish: `analyze` exits `0` with all missing/failed/guard counts inspected.
4. Read the complete result. Positive differences mean improvement in either direction.
   A candidate needs every planned pair usable, each paired difference positive, a median
   difference at least the practical bar and greater than observed unchanged-control spread.
   These are conservative descriptive rules, not significance tests. Keep the supplied raw
   observations, rejects and unknowns. Do not remove an outlier or failed run to obtain a win.
   Finish: verdict verified against all planned pairs, spread and positive-pair count.
5. If selecting a candidate, run `select` on discovery-only data and preserve its output
   **before** fresh confirmation collection. The selection binds the chosen arm, plan and
   discovery content. Reserve confirmation round/run identities and keep selection fixed.
   Analyze the combined data with `--selection`. A changed plan or discovery record requires
   a new explicit analysis; keep the original result. Multiple candidates are exploration,
   with no automatic winner ranking or correction for multiple comparisons.
   Finish: `select` exits `0` (when confirming) and combined `analyze --selection` exits `0`.
6. Deliver the executed `compare.py` command(s) and exit code(s), content digests
   (`plan_sha256`, `discovery_sha256`), pair counts, observed spread, differences in original
   units, failed/missing/guard counts, selected confirmation result and remaining limits.
   `CONFIRMED_OBSERVATION` means supplied fresh identities met the same descriptive rule.
   It establishes neither causality, population significance nor behavior on other workloads.
   If chronology, equivalence or the outcome proxy cannot be verified, say so even when the
   arithmetic passes.
   Done when: the supplied evidence has an accounted-for disposition backed by command and
   exit-code receipts.

Read [sources and departures](references/sources.md) only when checking provenance or design
departures.
