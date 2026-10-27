# Performance evidence

State the claim and read what the measurement script times, counts, and omits. Keep the
existing interleaved run protocol; extra runs need unresolved variance or a changed input.

- Confirm useful work happened inside the timed region. Record failures, retries, skipped
  cases, discovery counts, and completed assertions or outputs. Equal test counts alone do
  not establish equal work when a helper early-returns or a mock removes the behavior.
- Compare the same versions, build mode, data, cache state, concurrency, and relevant settings.
  Label an intentional out-of-box comparison; do not silently tune away the user's question.
- Locate the limiting resource or code path in a separate profiling run so profiling overhead
  is outside reported timings. If the cause remains unknown, report the measured difference
  and uncertainty without claiming a causal improvement.
- Check the end-to-end share. Removing a small phase cannot save more time than that phase
  consumed on the critical path. A result past that bound needs a work, cache, or error check.
- Report median and range with the run count and conditions. A difference inside run-to-run
  noise is inconclusive. No speed claim survives lost failure detection.

## Source

Informed by pstack's
[benchmark checklist](https://github.com/cursor/plugins/blob/9d76bcab133aefcccb16121d7be874e6aa823729/pstack/skills/benchmark-checklist/SKILL.md),
MIT, Lauren Tan, observed October 10, 2026. Original local procedure. Keeps this skill's
run count and test-preservation contract, and permits honestly labeled out-of-box comparisons.
Recheck when the runner, workload, or measurement harness changes.
