---
name: temporal-validation
description: Plan and audit time-series, backtest, or walk-forward validation on grouped/time-ordered data with rolling-origin folds, purge, embargo, lookahead and label leaks, and naive baselines. Not for paired comparisons (compare-experiments), disputed totals (reconcile-metric), sensor checks (telemetry-contract), or anomalies (telemetry-anomalies).
compatibility: The planner, auditor and baseline scorer need Python 3.10+ and only its standard library. They read local CSV and JSON files and write JSON to stdout. No network, provider, database or installation is required. Model training and feature pipelines stay in the project's own tools.
---

# Temporal validation

Deliver a validation record that a reviewer can rerun: the temporal contract, the folds,
a clean audit, per-fold metrics beside a naive baseline, and stated limits. This skill
plans and checks evaluation. It does not train models, change data or pick a model for you.

Random splits on time-ordered data look better than the model will do in use. Rows from one
session or event leak through shared conditions. A feature joined on event time can carry values the
model would not have had yet. Fix these before reading any metric.

## 1. Write the temporal contract first

Before touching data, write `contract.json` in the task's record using the
[contract reference](references/contract.md) for all required fields and the
[example contract](assets/contract.json). Mark unknown feature availability as unknown; do not
guess it from a column name. If availability cannot be established, exclude the feature or
report the result as provisional.
Finish: `contract.json` defines the unit, prediction time, label horizon, group key,
embargo, regime breaks and every feature availability rule.

## 2. Plan folds

Prepare a rows CSV with `row_id`, `group`, `prediction_time`, `label_end_time`, and one
`<feature>__available_at` column per feature. Times are numbers or ISO 8601, never mixed.
If `label_end_time` is absent or empty, `plan` stops unless you pass `--label-horizon T`,
which sets it to prediction time plus `T`. Write the full horizon even where the session ends first.
Then run (if Python 3.10+ is unavailable, stop and report that scripted checks cannot run):

```sh
python3 <skill>/scripts/temporal.py plan rows.csv --out folds.csv --folds 3 --test-groups 1
```

Options: `--window sliding --max-train-groups N`, `--embargo-groups N`, `--embargo-time T`
(seconds for ISO times), and `--no-purge` only to demonstrate a leak. Groups are ordered by
their first prediction time. Each fold tests the next block of groups and trains only on
earlier ones. Purge drops train rows whose label window reaches into the test period. The
output keeps purged, embargoed and future rows with their split label so the audit sees them.

Choose fold count and test size from the decision the model supports, such as one session or event ahead.
Keep at least one full season cycle of history before the first test fold when seasonality matters.
Finish: `plan` exits `0` and `folds.csv` has non-empty `train` and `test` rows per fold.

## 3. Audit before modeling or metrics

```sh
python3 <skill>/scripts/temporal.py audit folds.csv contract.json
```

Exit 0 means no findings, 1 means findings, 2 means invalid input. Each finding names a
check, fold, row count and example row ids. Checks:

| Check | Meaning |
| --- | --- |
| `lookahead` | A feature becomes available after its row's prediction time |
| `availability_missing` | A declared feature has no availability column, or a cell is empty |
| `label_window_short` | A label window is shorter than `label_horizon_time`, so purge cannot see it |
| `group_leak` | One group appears in both train and test of a fold |
| `label_overlap` | A train label window overlaps the test period; purge is missing |
| `forward_order` | A train row is at or after the test start in a forward-only contract |
| `embargo` | A train row falls inside the test period widened by `embargo_time` |
| `fold_incomplete` | A fold lacks train or test rows |
| `shuffle_suspect` | Heuristic: train and test labels interleave in time like a random split |

Fix the data, the joins or the plan, then rerun until the audit passes. Never lower a
threshold, drop a declared feature, edit the contract or alter folds only to pass. If
`shuffle_suspect` fires on folds that are contiguous by design, such as concurrent cars,
keep the finding, show the evidence of the design, and report the result as provisional. A
`regime_notes` entry is not a failure. Report it, and check whether folds that span the break
behave differently.
Finish: `audit` exits `0` (or documented concurrent-design `shuffle_suspect` marked provisional).

## 4. Fix metrics, baseline, and fold-local preprocessing before training

Choose the task metric and naive/seasonal-naive baseline from the
[metrics reference](references/metrics.md) before seeing any test predictions.
Fit scalers, encoders, imputers, feature selection and inner-split hyperparameter tuning
strictly on each fold's `train` rows from `folds.csv`, refitting at every origin. Never
refit on `test` or validation rows before reporting. Read [library splitters](references/tools.md)
only when using an external library splitter, and export its assignments to `folds.csv` for
Step 3 audit.

Generate per-fold predictions on each fold's `test` rows and export `forecasts.json`
matching [example forecasts](assets/forecasts.json) (`schema_version`, `season_length`,
`quantiles`, and `folds` keyed by the same `fold` IDs from `folds.csv`, with each fold's
`train` target series, `actual` test values, `point` predictions, and optional
`quantile_forecasts`).
Finish: models are trained per fold without test leakage and `forecasts.json` aligns with `folds.csv`.

## 5. Score forecasts against the naive baseline

For point and quantile forecasts, run:

```sh
python3 <skill>/scripts/baseline.py forecasts.json
```

It reports per-fold MASE for the model and naive/seasonal-naive baseline, pinball loss per
quantile, and interval coverage. Exit `0` means every fold was evaluated. Exit `1` means at
least one fold failed (such as a constant training series or `len(train) <= season_length`);
report failed folds without averaging them away. Exit `2` means invalid `forecasts.json`
(schema mismatch, crossed quantiles, or length mismatch); fix export formatting without
altering predictions and rerun. If Python 3.10+ is unavailable, report scoring as not run.
Finish: `baseline.py` completes (exit `0` or accounted-for exit `1`) with per-fold metrics recorded.

## 6. Report

Give, per fold: train and test groups, row counts, purged and embargoed counts, the model metric,
and the baseline metric. Then give counts of evaluated, failed and skipped folds, exact commands
and exit codes for `temporal.py plan`, `temporal.py audit`, and `baseline.py`, the audit result,
`regime_notes`, and limits. Spread across folds matters more than the mean. State what the audit
cannot prove: it trusts the supplied availability times, and a synthetic fixture pass does not
show that a real pipeline joins on availability time.
Done when: every fold is accounted for with clean audit evidence, per-fold baseline comparisons,
and command/exit-code receipts.

Read [sources and departures](references/sources.md) only when checking provenance or design
departures.
