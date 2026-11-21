# Profilers and data tests

Reported by research lane 2026-11-20; not rechecked against the current docs here. Recheck
trigger: a major release of a listed tool, or before relying on one of these facts for a
decision. Each row is labeled Reported unless it says otherwise.

| Tool | Reported fact (research lane 2026-11-20) | What to do here |
| --- | --- | --- |
| DuckDB `SUMMARIZE` | Distinct counts and quantiles are approximate | Use it as a lead; prove keys with an exact `GROUP BY` count |
| fg-data-profiling | Successor to ydata-profiling | Check which name and version the project pins before citing its output |
| Great Expectations Core 1.x | Profilers were removed | Do not plan on generating expectations from a profile; write claims from evidence |
| pandera `infer_schema` | Output is a draft schema | Review each inferred check against the dictionary before enforcing it |
| dbt data tests `unique`, `not_null`, `accepted_values`, `relationships` | They pass when the model has zero rows | Pair them with a row count test, as `check-claims` does with `vacuous` |

Analysis, not from tool docs: any profile built from a sample or a sketch can miss rare
duplicates, rare codes and late files. Use such output to choose what to count, then count it
exactly.
