# Methods

Why each step exists, and the SQL behind each check so it can run in a warehouse or DuckDB
when the data is too large for the bundled scripts. These are Analysis notes built on the
ideas listed in [sources](sources.md).

## Grain first

Grain is what one row stands for. Every later fact depends on it: a key is only a key for a
stated grain, a sum is only right if rows do not repeat the thing summed, and a join is only
safe if its grain on each side is known. Dimensional modeling practice declares the grain
before choosing columns for the same reason. Write the grain sentence first, then let the
counts accept or reject it. If the counts reject it, the sentence was wrong, not the data.

## Exact and approximate counts

Analysis: profilers often use sketches such as HyperLogLog for distinct counts. They are
fast and close, but not exact. A key needs zero duplicates, so a count that is close is no
proof. The scripts count exactly. In `survey` the distinct set is capped per column, and
past the cap the result is `"exceeds cap"`, never an estimate. `keys`, `joins` and
`check-claims` count in SQL on the whole table.

Exact uniqueness check:

```sql
SELECT COUNT(*) AS duplicate_groups
FROM (SELECT 1 FROM t GROUP BY a, b HAVING COUNT(*) > 1);
SELECT COUNT(*) AS null_rows FROM t WHERE a IS NULL OR b IS NULL;
```

`GROUP BY` puts all nulls in one group. Report null rows apart from duplicates, and never
call a nullable set a clean key. A table with no rows passes every uniqueness test, so it
proves nothing.

## Joins: inclusion is necessary, not sufficient

If `child.x` is a foreign key to `parent.y`, every child value appears in the parent. The
reverse does not hold. Small integers, status codes and dates overlap by chance. Research
on foreign key discovery treats value inclusion as a filter and leaves the decision to a
person, using names, documents and data types as further evidence. The scripts do the same:
they rank candidates and never confirm one.

```sql
-- containment of distinct child values in the parent
SELECT COUNT(DISTINCT x) FROM child WHERE x IN (SELECT y FROM parent WHERE y IS NOT NULL);
-- orphan rows an inner join would drop
SELECT COUNT(*) FROM child WHERE x IS NOT NULL AND x NOT IN (SELECT y FROM parent WHERE y IS NOT NULL);
-- rows a join would produce, to compare with matched child rows
SELECT SUM(m) FROM child JOIN (SELECT y, COUNT(*) AS m FROM parent GROUP BY y) p ON child.x = p.y;
```

## Fan-out and chasm traps

Fan-out: joining to a parent side that is not unique repeats each child row once per parent
match. A `fan_out` of 1.5 inflates any sum of child measures by half. Price histories,
slowly changing dimensions and many-to-many bridges are common causes. Pick one parent row
per key first (for example the version valid at the event time), or aggregate before the
join.

Chasm trap: two child tables that both join to one parent, joined together through it,
multiply each other's rows per parent key. Sums from either child are then wrong. Aggregate
each child to the parent grain first, then join the aggregates.

## Missing values

Keep four counts apart: null, empty, null-like tokens (`N/A`, `unknown`), and absent (the
file lacks the column). A sentinel code such as `-1` or `9999` is a fifth kind: a value that
stands for missing or special. Record what each code means and how sure you are.

The mechanism matters for any analysis:

- MCAR, missing completely at random: missingness depends on nothing. Dropping rows loses
  precision but adds no bias.
- MAR, missing at random: missingness depends only on observed columns. Methods that
  condition on those columns can correct for it.
- MNAR, missing not at random: missingness depends on the missing value itself, such as
  heavy parcels that were never weighed.

Data can show that missingness relates to observed columns, which rules out MCAR. It cannot
separate MAR from MNAR, because the deciding values are the missing ones. That needs domain
knowledge or a study design. Record the mechanism as an assumption with its basis.

## Event time and load time

Event time says when something happened. Load time, also called processing or ingest time,
says when the system recorded it. They differ by lag, and the lag varies: late rows arrive
in later files, and backfills rewrite the past. Filtering by load time when the question is
about events miscounts both ends of a window. Name both columns in the dictionary. If only
one exists, say which, and say what that rules out. In a file drop, compare each file's
event-time range with its load time to spot late rows.

## Schema drift

A drop of many files can change shape: columns added, dropped, renamed or retyped. Profiling
one file misses this. `survey` compares each file with the first. A column missing from some
files is absent there, not null; a rename shows as one missing and one added column, which
only a person can pair. Record drift by file date so readers know which rows can hold a column.

## Column meanings

Column descriptions generated from names and sample values help, but ambiguous columns still
need a person who knows the data. Treat every generated meaning as `inferred` until a
document or an owner confirms it, and keep the literal marker "no description in source"
when nothing supports a meaning.
