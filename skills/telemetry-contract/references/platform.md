# Enforcing the contract in a pipeline

Observed against official documentation on 2026-11-20. Recheck these notes after a major
release of BigQuery, Apache Beam, polars, DuckDB, pandera or Great Expectations.

The local checker is for a sample or one file. When the same data flows through a pipeline,
enforce the same contract where the data lands. Keep one contract file as the owner and
generate or review pipeline rules from it, so units and limits do not drift between copies.
Use a tool the project already uses. Do not add a validation framework for this alone.

## Where each check can live

- **BigQuery.** A table schema enforces column names and types, not units or ranges. Put the
  unit in each column's description and in the column name suffix. Express ranges,
  saturation counts, missing fractions, duplicate times and lag limits as SQL assertions
  (for example, Dataform assertions or scheduled queries that fail on violating rows).
  Store sensor time and ingest time as separate columns. Partition by one of them and say
  which in the contract.
- **Apache Beam in Dataflow** (version unconfirmed; the current pydoc showed 2.76.0 when checked on 2026-11-20). Schema-aware transforms give named, typed fields. Add a
  validation step that routes violating elements to a dead-letter output with the reason,
  rather than dropping them. Use event time from the sensor timestamp, and set allowed
  lateness from `max_lag_s`. Late data beyond it should be counted, not silently discarded.
- **pandera or Great Expectations.** If the project already uses one, translate each channel
  into column checks: range, allowed sentinel set, null fraction, and monotonic time within a
  sorted frame. Keep saturation counts as their own check so they are not merged with nulls.

## Engine notes

Observed against official Polars and DuckDB documentation on 2026-11-20; verify against the
version in use.

- **Polars (`join` and `group_by`).** By default (`maintain_order=False` on `group_by` and
  `maintain_order="none"` on `join`), Polars does not guarantee output row order. Sort by
  sensor time before any rate, gap or monotonic check, and before export to the local checker.
  When a session or car key is present, export one file per key. Otherwise the checker reports
  false regressions.
- **DuckDB storage versions.** DuckDB does not guarantee forward compatibility for database
  files written by newer major releases (such as v2.0 files opened by 1.x). Export the checked
  slice to CSV or Parquet with explicit column types, or use `EXPORT DATABASE` / `IMPORT DATABASE`
  or `storage_compatibility_version` when sharing across versions.

Verify version-specific behavior in the official documentation before relying on it.
