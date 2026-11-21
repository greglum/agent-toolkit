# Library splitters and evaluators

API names and versions below were checked against official documentation and PyPI on
2026-11-20. Recheck trigger: a major version release of any listed library or BigQuery syntax update.

The "Gap to cover" column states the temporal validation requirement to check when using each tool.

| Tool (observed 2026-11-20) | Documented API | Gap to cover |
| --- | --- | --- |
| scikit-learn 1.9.1 | `TimeSeriesSplit(n_splits, max_train_size, test_size, gap=0)`; no group key | Assign whole groups to folds first, as `plan` does, or a group (such as a race) can straddle a split |
| statsforecast 2.1.1 | `cross_validation(df, h, step_size, n_windows)` | Check feature availability and fold-local preprocessing boundaries yourself |
| sktime 1.3.0 | `ExpandingWindowSplitter`, `SlidingWindowSplitter` (`fh`, `initial_window`/`window_length`, `step_length`) | Confirm how groups and label horizons are handled across splits |
| skfolio 1.14.3 | `CombinatorialPurgedCV(purged_size, embargo_size)` | Train can follow test; audit with `forward_only: false` and a matching `embargo_time` |
| skfolio 1.14.3 | `WalkForward(purged_size=0)` | Confirm observation/time unit mapping before converting contract horizons |
| BigQuery ML | `ML.ARIMA_EVALUATE(MODEL ...)` | Extracts in-sample model diagnostics without evaluation data; do not treat as an out-of-sample backtest |
| BigQuery | `AI.EVALUATE(history, actual, ...)` | Confirm evaluated history/actual windows and hold out by time yourself |

Common gaps to check in any tool:

- A splitter does not know when a feature became available. Join features as-of
  availability time before splitting.
- Preprocessing leaks unless it is fit inside each fold, for example by passing the whole
  pipeline to the cross-validation call.
- Fold counts and sizes may be in rows. Convert the contract's group and time terms first.

Whatever splitter you use, export its fold assignments to the audit CSV and run `temporal.py audit`.
