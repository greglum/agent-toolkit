# 0015: Use Canonical Text UDF Comparisons, Finite-Number Guards, and 15-Digit Float Thresholds in Data Profiling

- Status: Accepted
- Date: 2026-11-20

## Context

SQLite's CAST(2.0 AS TEXT) yields '2.0' while Python's canonical as_text(2.0) yields '2'; IEEE-754 NaN compares false against all range bounds; and integers longer than 15 decimal digits exceed float64 exact precision.

## Decision

Register a deterministic SQLite UDF (map_data_accepted) using as_text() for set-membership claims, explicitly count non-finite values with math.isfinite() before low/high range checks, and treat digit strings exceeding MAX_DIGITS = 15 as identifiers rather than floats.

## Consequences

True claims on REAL columns do not spuriously fail, NaN cannot slip past range validation, and long numeric IDs are never silently rounded into floats.

## Code References

- `skills/map-data-source/scripts/claims.py:132`
- `skills/map-data-source/scripts/claims.py:133`
- `skills/map-data-source/scripts/claims.py:163`
- `skills/map-data-source/scripts/column_profile.py:20`
