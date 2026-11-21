# Method chooser

Pick a method per fault class. Start at the top. Move down only when the earlier option does
not fit. Each method has a blind spot; state it in the report.

## Order of preference

1. **Rule or physics residual.** When a model predicts the channel (oil temperature from
   load and coolant flow, brake pressure from pedal travel, wheel speed from vehicle speed),
   score the residual: measured minus predicted. A residual removes expected behavior, such
   as a mode change or a gear shift, before any statistics. Then apply the robust z-score
   below to the residual. A hard rule (pressure below a floor while the engine runs) needs no
   statistics at all. Blind spot: faults the model also explains, and model drift.
2. **Robust z-score (bundled).** (x minus rolling median) divided by (1.4826 times the
   rolling MAD), against the trailing window of the same mode. Good for spikes, dropouts and
   fast steps. Median and MAD resist the outliers they are meant to find. Blind spot: a drift
   slower than the window is absorbed into the baseline. A step is flagged only until the
   window fills with the new level.
3. **Change-point detection.** For sustained shifts and slow drift.
   Bayesian online change point detection (Adams and MacKay, arXiv 0710.3742) keeps a
   distribution over the time since the last change and works sample by sample.
   PELT finds an offline segmentation under a penalty; the `ruptures` library
   (BSD-2-Clause) implements it with several cost functions. Blind spot: the penalty or
   hazard rate sets the false-alarm rate, so calibrate it on clean data like a threshold.
4. **Matrix profile discords.** For an unusual shape, such as one odd oscillation burst.
   `STUMPY` (BSD-3-Clause) computes it. You must choose a window length near the shape's
   duration. A discord is the subsequence farthest from its nearest neighbor, so a fault that
   repeats has a near neighbor and is not a discord.
5. **Forecast residual detectors.** Forecast each channel and flag large errors, with a
   threshold set from the error distribution. Telemanom (Hundman et al., KDD 2018) used LSTM
   forecasts with a nonparametric dynamic threshold on spacecraft telemetry. Its license is
   unsettled (see [sources](sources.md)), so borrow ideas only. A forecast interval miss is not an anomaly
   probability. A 95% interval misses about 5% of normal points by design, and more when the
   model is miscalibrated.
6. **Reconstruction error.** A variational autoencoder trained on normal multichannel
   windows flags windows it reconstructs poorly. von Schleinitz et al. (2021) applied this
   to race-car signals, evaluated on simulated faults. Treat that as evidence the idea can
   work, not as a measured detection rate on real faults.

## Methods to avoid for this job

- **Isolation forest on raw samples.** It treats rows as independent points and ignores time
  order. A stuck sensor or slow drift stays inside the normal range of values and is not
  isolated. Use it only on engineered window features, and still calibrate it.
- **Point-wise global thresholds across modes.** Pit limiter, caution laps, gear shifts and
  hybrid deploy change the normal level. Keep baselines per mode, or exclude those modes.
- **High-rate claims from low-rate public data.** A method validated on 1 Hz or slower
  benchmarks has not seen 1 kHz vibration or pressure transients. Validate on data at the
  target rate, even synthetic data with planted faults, and say which it was.

## Platform options

Verified against official BigQuery and Apache Beam documentation on 2026-11-20. Recheck the
official docs for the version in use. Recheck triggers: a BigQuery release note touching these
functions, a Beam release, or a TimesFM pricing or version change (including the TimesFM 3.0
pricing change announced for 2026-12-01).

- **BigQuery `AI.DETECT_ANOMALIES`.** Checked 2026-11-20,
  <https://docs.cloud.google.com/bigquery/docs/reference/standard-sql/bigqueryml-syntax-ai-detect-anomalies>
  (page cached 2026-11-01). Zero-shot detection with TimesFM, no training step. One data
  column, so univariate point anomalies. TimesFM 2.5 is the default and TimesFM 3.0 is in
  Preview. `anomaly_prob_threshold` defaults to 0.95. Only the most recent 1,024 time points
  are evaluated, which is under 2 seconds of a 1 kHz channel. Treat its anomaly probability
  with the caution in item 5 until you confirm how it is derived.
- **BigQuery `ML.DETECT_CHANGE_POINTS`.** Checked 2026-11-20,
  <https://docs.cloud.google.com/bigquery/docs/reference/standard-sql/bigqueryml-syntax-detect-change-points>.
  Returns begin and end timestamp intervals for sustained shifts. It is Preview (Pre-GA),
  under the Pre-GA Offerings Terms. Use it for shifts, not spikes.
- **BigQuery `ML.DETECT_ANOMALIES`.** Checked 2026-11-20 against BigQuery ML docs. Works with
  a trained `ARIMA_PLUS` / `ARIMA_PLUS_XREG` model for time series, or k-means, PCA, or
  autoencoder models for feature rows (with `contamination` threshold option). Training,
  storage, and query costs apply.
- **Apache Beam `apache_beam.ml.anomaly`.** Checked 2026-11-20 in the Beam Python docs
  (<https://beam.apache.org/releases/pydoc/>, observed at 2.76.0). `AnomalyDetection` in
  `apache_beam.ml.anomaly.transforms` applies detectors from `apache_beam.ml.anomaly.detectors`,
  including `IQR`, `ZScore`, `RobustZScore`, `OfflineDetector`, and `PyODFactory` (with
  `FixedThreshold` / `QuantileThreshold` and aggregation strategies). Detectors are univariate
  and keep state per key; streaming scores use online statistics, so they will not match a
  batch run of the bundled tools on the same data. Calibrate a streaming job on its own output.

Platform choices are the user's. They carry cost, data residency and access decisions this
skill does not make.
