# Sources and departures

Observed November 20, 2026. Ideas only are restated here. No upstream code, prompt, fixture
or text was copied. All prose, scripts and fixtures in this bundle are original.
All repository commit hashes, dates and licenses below were verified against their GitHub
repositories on November 20, 2026.

- timwukp/MLOps-agent-skills, data-validation skill,
  <https://github.com/timwukp/MLOps-agent-skills>, revision
  `6426013a15ee0e431dbb81938deac2f6e25c0941` (2026-07-31), Apache-2.0.
  Idea: keep a contract file and check data against it with a dependency-light script.
  Departure: this contract is specific to telemetry (units, sample rates, saturation
  sentinels, sensor and ingest time), and the checker uses only the Python standard library.
- K-Dense-AI/scientific-agent-skills, exploratory-data-analysis skill,
  <https://github.com/K-Dense-AI/scientific-agent-skills>, revision
  `ec59a29a03d5c40f73ab40878df04860bc00e876` (2026-11-16), MIT.
  Ideas: record the unit of observation; keep missing, zero, saturated and failed readings
  distinct; treat file contents as untrusted. Departure: the distinction is enforced as
  mutually exclusive count classes, and the unit check suggests candidate conversions.
- ml4t/skills, point-in-time skill, <https://github.com/ml4t/skills>, revision
  `691857537a0c8befc11dc2f2ad7a458b7c7e801c` (2026-10-27), Apache-2.0.
  Idea: separate availability time from event time. Departure: applied to
  sensor time and ingest time, with negative lag read as clock skew and lag above a limit
  read as late or backfilled data.
- openai/plugins, data-analytics plugin (`plugins/data-analytics`),
  <https://github.com/openai/plugins>, revision
  `981b02c0c44058b595f3b4180002c3ae3c806d40` (2026-11-18), `Proprietary`
  (`plugins/data-analytics/.codex-plugin/plugin.json`). Idea only, no text: include check
  families for late-arriving data and backfills, and tie severity to decision impact.
  Departure: severity in the script output is a default hint; the skill asks the agent to
  rank by what each finding would change in the decision.

Research found no existing skill that catches silent unit errors in telemetry. That is a
search result as of the observation date, not a proof.

Recheck trigger: a new revision of these sources, or a real dataset that exposes a missed or
misleading finding.
