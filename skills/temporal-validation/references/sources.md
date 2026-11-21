# Sources and departures

Observation date 2026-11-20. All repository revisions, commit dates, licenses and paper
versions below were verified against their primary sources on 2026-11-20. All local prose,
code and fixtures are original; no upstream text, code or fixture was copied.
Recheck trigger: a new revision of a listed source, or a real audit that misses a leak.

| Source | Revision | License | Idea restated | Local departure |
| --- | --- | --- | --- | --- |
| [mospira/walkforward-audit](https://github.com/mospira/walkforward-audit) | `ef3e1f19785553ba3782bf7f250c4b94169669ab`, 2026-06-13 | MIT | Write temporal contract fields first; keep a fixture that must fail on a leak | Contract fields cover hierarchy, group key, a numeric horizon and regime breaks; fixtures include a planted lookahead and an unpurged overlap |
| [ml4t/skills](https://github.com/ml4t/skills) | `691857537a0c8befc11dc2f2ad7a458b7c7e801c`, 2026-10-27 | Apache-2.0 | Join features on the time a value became available | Availability is a per-feature column that the audit checks row by row |
| [sreedhararolla/enterprise-data-science-skill](https://github.com/sreedhararolla/enterprise-data-science-skill) | `1915698a58052ef70720dc52678869b139be1dea`, 2026-09-29 | MIT | Scan single features for out-of-fold leakage; keep a change only if it beats seed noise | The audit checks availability times, not model scores; fold spread is reported instead of a single mean |
| [K-Dense-AI/scientific-agent-skills](https://github.com/K-Dense-AI/scientific-agent-skills), timesfm-forecasting and experimental-design | `ec59a29a03d5c40f73ab40878df04860bc00e876`, 2026-11-16 | MIT | Rolling origins with preprocessing refit at each origin; repeated measures are not independent | Rolling origin is by group; the metrics note treats races, not laps, as the effective sample |
| Peng et al., *Rank Position Forecasting in Car Racing*, [arXiv:2010.01707v2](https://arxiv.org/abs/2010.01707v2) | `v2` (published 2020-10-04, updated 2020-10-23) | arXiv non-exclusive distribution license | Pit stops are irregular, rare events needing event-aware evaluation | Metrics reference uses precision, recall, PR-AUC and false alerts per race, not accuracy |

## Rejected source

[GoogleCloudPlatform/data-agent-kit-plugin](https://github.com/GoogleCloudPlatform/data-agent-kit-plugin),
`skills/ml-best-practices/SKILL.md` at `83c53b5f129cdeecabe149ff4ba82645d3e51745`
(2026-09-29, Apache-2.0). Checked directly on 2026-11-20: line 77 instructs retraining the
selected model on the test and validation sets before predicting test values, and lines
204-207 instruct fitting preprocessing pipelines on training and test data independently.
Read literally, both are evaluation errors: the first leaves no untouched test result to
report, and the second scales test rows with statistics the model never saw in training.
This bundle requires a final score on untouched test folds and preprocessing fit on train
rows only. Refitting on all data after reporting is a separate deployment choice.
