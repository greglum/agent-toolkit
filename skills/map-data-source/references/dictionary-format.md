# Dictionary format

Use these fields for the source map, the data dictionary, open questions and the claims file.
Markdown tables suit people; a CSV or YAML copy suits tools. Keep one owner for each fact.

## Table entry (source map)

| Field | What to write |
| --- | --- |
| table | Name as the tools report it, plus the file pattern or database object |
| grain | One sentence: "One row is one ___ per ___." Add its status: proven (with the `keys` result), unproven, or contradicted |
| keys | Proven unique column sets, with row count and the date checked |
| event time | Column that says when the thing happened, or "none found" |
| load time | Column that says when the row arrived or was loaded, or "none found" |
| freshness | Latest event time and latest load time seen, and the snapshot date |
| coverage | Files, rows, and the time range covered; gaps you saw |
| drift | Columns added, missing or changing type across files, by file |
| relationships | Kept joins: child, parent, containment, orphans, parent unique, fan-out, and whether confirmed |
| caveats | Anything that would mislead a reader: vacuous tables, duplicates, late rows |

## Column entry (data dictionary)

| Field | What to write |
| --- | --- |
| table | Table name |
| column | Column name exactly as in the source |
| type | Inferred type from `survey`; add the declared type when the source has one |
| unit | Unit of measure, or "none" for codes and text, or "unknown" |
| meaning | One plain sentence in the glossary's terms when one exists, or the literal marker "no description in source" |
| meaning status | `documented`, `sme-confirmed`, `inferred` or `unknown` |
| source or evidence | For documented: the document and section. For sme-confirmed: who and when. For inferred: the counts, values or joins that support it. For unknown: what was checked |
| sentinel codes | Each code and what it stands for, with status, for example `9999 = not weighed (inferred)` |
| missingness | Null, empty, token and absent counts, and the assumed mechanism (see below) |
| example values | Allowed only when the scope permits quoting; else "suppressed" |

Meaning status rules:

- `documented` needs a citation a reader can open.
- `sme-confirmed` needs a person or role and a date. Record the answer, not just the name.
- `inferred` needs evidence beyond the column name. Values, joins and counts qualify.
- `unknown` uses the literal marker "no description in source". Do not leave it blank.

Missingness mechanism: write `MCAR`, `MAR (given ___)`, `MNAR (because ___)` or
`unknown`, and add "assumed" unless a document or an owner states it. See
[methods](methods.md#missing-values) for why data alone cannot settle it.

## Open questions

One entry per question. When prior open questions exist, add to them instead of repeating
one; when a glossary exists, use its terms in the question.

| Field | What to write |
| --- | --- |
| id | `Q-<table>-NN`, for example `Q-orders-03`; never reuse or renumber an ID |
| question | One question that a person can answer |
| target | Table and column, or join |
| evidence | Starts with `data:`, then the counts or values that raised it, for example `data: 2 rows hold 9999` |
| why it matters | The decision or claim that depends on it |
| ask | Role or skill to ask, for example the data owner or learn-domain |
| status | open, answered (with answer, who, date), or dropped (why) |

## Claims file

A JSON object with a `claims` list. Each claim has a unique `id`, a `type` and a `table`.
Extra fields such as `evidence` or `source` are kept for readers and ignored by the checker.

| Type | Fields | Fails when |
| --- | --- | --- |
| `unique` | `columns` (list) | any value combination repeats; rows with a null in the set are counted, not tested |
| `not_null` | `column` | any null; empty cells in files count as null |
| `accepted_values` | `column`, `values` | any non-null value outside the list |
| `range` | `column`, `min` and or `max` | a value is outside, or cannot be read; numbers or ISO times |
| `relationship` | `column`, `to_table`, `to_column`, optional `min_containment` (default 1.0) | distinct child values found in the parent fall below the threshold |
| `row_count` | `min` and or `max` | the row count is outside |

Any claim whose table or column is missing fails. Any claim except `row_count` on a table
with no rows, and a `unique`, `accepted_values` or `range` claim on a column with no non-null
values, reports `vacuous`, which also exits 1. An empty `values` list is invalid input. Pair important claims with a `row_count`
claim so an empty refresh is visible.
