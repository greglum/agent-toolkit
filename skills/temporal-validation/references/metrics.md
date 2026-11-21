# Metrics by task type

Fix the metric and the baseline before scoring. Report every fold, not only the mean.

## Baseline rule

Score a naive baseline on the same folds, with the same rows, horizon and preprocessing
boundary as the model. For a seasonal series, also score seasonal naive, which repeats the
value from one season earlier. For classification, report the base rate and a simple rule,
such as "pit when tyre age passes the median stint length". A model that does not beat the
baseline on most folds has not shown value.

## Point forecasts

**MASE** (mean absolute scaled error) divides the test mean absolute error by the in-sample
mean absolute error of the seasonal-naive forecast on that fold's train values:

    MASE = mean(|y_t - f_t|) / mean(|y_t - y_(t-m)| for train t > m)

A value below 1 beats the one-step in-sample naive error. Compare model MASE with the
multi-step baseline MASE on the same fold. MASE is undefined when the train series is
constant; `baseline.py` reports that fold as failed. Avoid MAPE near zero values.

## Probabilistic forecasts

**Pinball (quantile) loss** for quantile `q`, actual `y` and forecast `f`:

    loss = max(q * (y - f), (q - 1) * (y - f))

Average over rows per quantile, then over quantiles. Lower is better.

**CRPS** (continuous ranked probability score) scores a whole predictive distribution.
Averaging pinball loss over many evenly spaced quantiles approximates it. Use a library
implementation for parametric or sample forecasts.

**Interval coverage and width**: for a central interval such as 10% to 90%, report the share
of actuals inside it beside the nominal 80%, and the mean width. Report both by horizon step,
because coverage often degrades with lead time. Narrow intervals with low coverage are worse
than they look.

## Rare events

Pit stops are irregular and rare among laps (Peng et al., arXiv:2010.01707v2). For example,
at a 3% base rate, a model that never predicts a stop scores 97% accuracy. Report instead:

- precision and recall at the operating threshold, chosen on train folds only;
- PR-AUC (average precision) beside the base rate, which is its no-skill value;
- event-level recall: a stop counts as caught if any alert falls within the agreed lead window;
- false alerts per race, which is what a strategist experiences.

Keep the threshold fixed across test folds. Report the count of positive rows per fold.
A fold with very few positives gives an unstable estimate; say so.

## Forecast export contract

When exporting fold results from `folds.csv` to `forecasts.json` for `scripts/baseline.py`
(see [example forecasts](../assets/forecasts.json)):

- Set `schema_version: 1`, `season_length` (`1` for naive, `m > 1` for seasonal naive), and `quantiles` (`[]` or distinct values in `(0, 1)`).
- Emit one entry in `folds` per evaluated fold using the same `fold` identifier string from `folds.csv`.
- Supply that fold's `train` target values, `actual` test target values, `point` forecasts (matching `actual` length), and optional `quantile_forecasts` keyed by stringified quantile.

## Across folds

Report per-fold values, the spread, and the count of evaluated, failed and skipped folds.
Do not average a failed fold away. Rows are not independent: laps within a race repeat
conditions, so the effective sample size is closer to the number of races than laps.
