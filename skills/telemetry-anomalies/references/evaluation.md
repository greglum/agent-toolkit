# Evaluating anomaly detectors

## Event-level scoring

Faults are ranges in time, so score ranges. The bundled `score.py` counts a label as
detected when a detection on the same channel overlaps it, optionally widened by a stated
tolerance. A detection is true when it overlaps any label. It reports:

- precision: true detections over all detections;
- recall: detected labels over all labels;
- detection delay: first overlapping detection start minus label start, per label;
- counts: detections, true and false detections, labels detected and missed;
- false alarms per hour of session;
- alarm time: seconds flagged and flagged share per channel and overall, next to the
  labeled share.

Event overlap has its own loophole. One detection per channel that spans the whole session
overlaps every label and is never false, so its precision and recall look perfect. Always read
the flagged share. `score.py` warns when a channel is flagged for more than 20% of the session.
A detector flagged far longer than the labeled share is not useful, whatever its F1.

Report counts next to every ratio. With 4 labels, recall moves in steps of 0.25.

Always score a trivial baseline on the same data. The bundled baseline is a static robust
threshold: one median and MAD per channel over the whole session or a clean reference, with
modes ignored. A detector that does not beat it on counts has not earned its complexity.

## Why point adjustment inflates scores

Point adjustment marks every point of a labeled range as detected when any single point
inside it is flagged. Long labels then reward random flags. Kim et al. (AAAI 2022) showed a
random scorer can match or beat published methods under this protocol. Wu and Keogh (TKDE
2021) showed that many popular benchmarks are flawed: trivial one-line detectors solve many
of them, and some labels are wrong or anomalies sit near the series end. The bundled test
shows the effect on the synthetic session: random flags score far higher point-adjusted F1
than event F1. Never report point-adjusted metrics, and say so in the report.

## Stronger references

VUS-PR is a volume under the precision-recall surface across label-buffer widths and
thresholds. It is less sensitive to label edges and to one chosen threshold. The TSB-AD
benchmark recommends it and curates datasets to reduce the flaws above. Use it when comparing
methods across many datasets. For one deployment, the calibrated event counts above are what
the user lives with.

## Single runs and best-of-N

Report one run with fixed settings chosen before seeing the test labels. If several seeds,
windows or thresholds were tried and the best is shown, say "best of N" and show the spread.
Tune on one labeled session and report on another.

## Family-wise false-alarm budget

Per-channel thresholds hide the total. If each of 200 channels alarms once per 10 hours on
clean data, a 2-hour session expects 40 false alarms. Set the budget for the whole
session across all channels, then calibrate thresholds to fit it on clean reference data.
`calibrate.py` does this with one shared threshold or equal per-channel shares. Rare true
faults on a long clean reference still count against the budget, so check the reference.

## Mixed-rate channels

Channels at 10 Hz and 1 kHz cannot share one timeline without care. Downsampling by picking
every Nth sample folds high-frequency energy into false low-frequency content (aliasing).
Low-pass filter below the new Nyquist frequency first, or use block mean, min and max over
each output interval, which also keeps short spikes visible. Upsampling by interpolation
invents smooth values between samples. Prefer scoring each channel at its native rate and
aligning events, not samples. Leave cells blank where a channel has no sample; the bundled
tools treat blanks as missing and skip them.
