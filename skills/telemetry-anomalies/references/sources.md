# Sources and departures

Observed 2026-11-20. All local prose and code are original. No upstream code, prompt, fixture
or license text was copied. Each entry gives the idea in our words and how this skill departs.
Papers are cited for ideas only; their text is under the publisher's terms.

## Papers

- Adams and MacKay, Bayesian online changepoint detection, <https://arxiv.org/abs/0710.3742>,
  2007. Idea: track a distribution over the run length since the last change, updated per
  sample. Departure: described in the chooser, not implemented here.
- Hundman et al., Detecting spacecraft anomalies using LSTMs and nonparametric dynamic
  thresholding, KDD 2018, <https://arxiv.org/abs/1802.04431>; code at
  <https://github.com/khundman/telemanom>. Idea: forecast each channel and threshold the
  smoothed error from its own distribution. License: `LICENSE.txt` on master, read 2026-11-20,
  is a custom Caltech BSD-style license, although GitHub metadata says Apache-2.0. Ideas
  only. Departure: no forecasting model ships here.
- von Schleinitz, Graf, Trutschnig and Schroeder, VASP, Engineering Applications of
  Artificial Intelligence 104 (2021) 104354, <https://doi.org/10.1016/j.engappai.2021.104354>.
  Idea: a variational autoencoder trained on normal race-car signals flags and replaces
  anomalous inputs before prediction; anomalies were simulated. Departure: cited as evidence
  the approach can work, not as a real-fault detection rate.
- Kim, Choi, Choi, Lee and Yoon, *Towards a Rigorous Evaluation of Time-series Anomaly
  Detection*, AAAI 2022, <https://arxiv.org/abs/2109.05257v2> (published 2021-09-11, v2
  2022-01-04, arXiv non-exclusive license). Idea: point adjustment lets random scores look
  strong. Departure: `score.py` never computes it, and the test shows the gap on synthetic data.
- Wu and Keogh, *Current Time Series Anomaly Detection Benchmarks are Flawed and are Creating
  the Illusion of Progress*, TKDE 2021, <https://arxiv.org/abs/2009.13807v5> (published
  2020-09-29, v5 2022-09-03, arXiv non-exclusive distribution license). Idea: trivial detectors
  solve many benchmark series, and labels can be wrong. Departure: a trivial baseline is always
  scored next to the detector.
- Qinghua Liu and John Paparrizos, *The Elephant in the Room: Towards A Reliable Time-Series
  Anomaly Detection Benchmark* (NeurIPS 2024), TSB-AD benchmark,
  <https://github.com/TheDatumOrg/TSB-AD>, revision
  `303dffbfc11612995b17b06633f8c9d0ea0e38e5` (2026-10-20), Apache-2.0. Idea: curated
  datasets and VUS-PR as the more reliable measure. Departure: not bundled; recommended for
  cross-dataset comparison.

## Libraries

- ruptures, <https://github.com/deepcharles/ruptures>, BSD-2-Clause, PyPI 1.1.10 observed
  2026-11-20. Idea: offline change-point search, including PELT, with pluggable costs.
  Departure: optional, never installed by this skill.
- STUMPY, <https://github.com/stumpy-dev/stumpy>, BSD-3-Clause, PyPI 1.14.1 observed
  2026-11-20. Idea: matrix profile discords for unusual shapes at a chosen window length.
  Departure: optional, never installed by this skill.

## Platform documentation

See the platform section of [methods](methods.md). BigQuery and Beam facts there were checked
against official documentation on 2026-11-20. Google documentation pages are living pages; no
text was copied.

## Agent skills

- google/skills, `bigquery-ai-ml` skill, <https://github.com/google/skills>, revision
  `bf80eb9187dc3479b27e6a14ec02eaa098045e12` (2026-11-20), Apache-2.0. Idea: the function
  chooser separates point anomalies from sustained shifts. Departure: the chooser here is by
  fault class and starts with physics residuals. Its usage-attribution instructions are not
  carried over.
- K-Dense-AI/scientific-agent-skills, `timesfm-forecasting` skill,
  <https://github.com/K-Dense-AI/scientific-agent-skills>, revision
  `ec59a29a03d5c40f73ab40878df04860bc00e876` (2026-11-16), MIT.
  Idea: a forecast interval miss is not an anomaly probability. Departure: stated in the
  chooser; no forecasting code ships here.

## Recheck triggers

Recheck an entry when its library publishes a major release or license change, when a
BigQuery or Beam release touches the listed functions, when TimesFM pricing or versions
change (a TimesFM 3.0 pricing change was announced for 2026-12-01), or when an upstream
skill revision moves. Read the telemanom license file again before any reuse beyond ideas.
