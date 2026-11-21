# Sources and departures

Observed October 25, 2026, Pacific/Honolulu. Original procedure; no upstream prompt,
implementation, benchmark dataset or media copied.

- [Building effective agents](https://www.anthropic.com/research/building-effective-agents),
  Erik Schluntz and Barry Zhang, December 19, 2024. Evaluator-optimizer and agent stopping
  sections, living page read October 25, 2026. Reuse rights not established; original
  paraphrase only. Clear criteria and actionable feedback support a bounded loop.

Departure: preserve existing repository tools, task records and gates, separate deterministic
checks from judgment, and keep generated feedback attributed until independently verified. Do
not install an external loop scheduler or agent framework, change providers, save unverified
model outputs as facts, or claim speed or cost savings without a controlled comparison.

Recheck when repository check tooling, stopping criteria, or evaluation isolation requirements
change, or when a controlled trial contradicts the procedure.

## Noisy measurements and confirmation

Observed October 29, 2026, Pacific/Honolulu. Original synthesis; no upstream text or code adapted.

- [Lever](https://github.com/github/lever/tree/f859d0aa2be96981157ee0480655c84877e3cd98),
  GitHub, Inc., MIT, revision dated October 28, 2026. `find-the-loop` steps 3-7,
  `templates/loop-card.md` and `experiment-arms` steps 8-12 inform unchanged-run
  variation, matched work, visible failures and confirmation of combined changes.
- [NIST confirmation runs](https://itl.nist.gov/div898/handbook/pri/section4/pri46.htm),
  NIST/SEMATECH e-Handbook, section 5.4.6, living page. Supports confirming selected
  settings in comparable conditions. Reuse rights unassessed; no copied content.
- [NIST multiple comparisons](https://www.itl.nist.gov/div898/handbook/prc/section4/prc47.htm),
  section 7.4.7, living page. Separate per-comparison confidence does not establish
  confidence in a selected winner. Fresh confirmation reduces reuse of selection evidence;
  it is not a substitute for a statistical method suited to the design.

Departures: sample size and summary statistics depend on the instrument and intended effect.
No fixed repeat count, automatic KEEP verdict, provider roster, CI-writing driver, saved
permission dial or scheduler is adopted. Deterministic decisive checks keep the one-pass path.
Recheck when the measurement design changes or a matched trial contradicts the procedure.

## Recursive harness trials

Observed November 3, 2026, America/Los_Angeles. Original synthesis; no upstream prompt or
implementation copied.

- [Harness2](https://github.com/google-research/harness2/tree/6868817518876de8fd170c6a8354daca273b6191),
  Google Research, Apache-2.0 core code, revision dated November 1, 2026.
  `core/recursion.py`, `core/prompts.py`, `core/ledger.py`, `core/library.py`,
  `core/selection.py` and `docs/EXPERIMENTS.md` inform scoped candidates, executed
  contrasts, composition, experiment identity and evidence-supported lessons.
- [Harness2 paper](https://arxiv.org/html/2610.14224v1), Xu and colleagues, October 2026,
  sections 2-4. Its benchmark and ablation findings support trials, not a promise of
  gains for another repository. Paper reuse rights unassessed; original paraphrase only.
- [Harness-Delta Attribution](https://arxiv.org/html/2610.22466v1), Ding and colleagues,
  October 15, 2026, sections 3-5, CC BY 4.0. Compute matching, shortcut inspection and
  held-out transfer inform limits on benefit claims. The study tests other frameworks;
  its findings do not establish that Harness2 itself overfits.

Departures: baseline remains eligible; no automatic adoption, model launcher, persistent
harness library or benchmark datasets are added. Execution remains inside the permissions
already selected for the task. Trials and lessons stay in the responsible project's records.
Recheck when a controlled trial contradicts this procedure or experiment isolation changes.
The linked research was checked once, in a dated earlier round, and has not been rechecked since.
