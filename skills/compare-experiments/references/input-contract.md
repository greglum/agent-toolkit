# Input contract and commands

Use explicit task-owned JSON files. The analyzer never searches histories or discovers files.
Every object accepts only the documented fields. Duplicate JSON keys, duplicate observations,
reused run IDs, unplanned rounds, metadata mismatches and nonfinite values are input errors.

## Plan, version 1

See the runnable [plan](../assets/plan.json). Its exact fields are:

| Field | Meaning |
| --- | --- |
| `schema_version` | Integer `1` |
| `experiment` | Nonempty task identity |
| `metric`, `unit` | One scalar metric and its original unit; no automatic conversion |
| `direction` | `lower` or `higher` |
| `workload`, `profile` | Nonempty identities for equal work and measurement conditions, including cache state and scheduling where relevant |
| `guard_contract` | Nonempty preservation-check content or content hash of a separately retained check definition; changing checks changes the plan identity |
| `control`, `unchanged` | Distinct arm names for repeated unchanged code |
| `arms` | At least three names mapped to nonempty exact revision/diff identities; the two controls share a revision; treatments differ from control |
| `rounds` | Object with `unchanged`, `discovery`, `confirmation` arrays of globally unique round strings |
| `minimum_pairs` | Integer at least two, chosen before observation; every phase reserves at least that many rounds |
| `minimum_improvement` | Positive finite absolute difference in the metric's unit |
| `maximum_unchanged_delta` | Nonnegative finite permitted absolute paired variation between unchanged controls |

Use a revision plus dirty-diff identity when commits alone do not describe the measured code.
Choose a representative workload and instrument. A fixed number of pairs does not guarantee
adequate sensitivity. The unchanged-control phase can expose drift but does not prove all
noise sources are controlled. There is no automatic power analysis or confidence interval.
A change to a plan creates a different digest and analysis; retain the previous record.

## Observations

The [complete synthetic samples](../assets/samples.json) and their
[discovery-only subset](../assets/discovery.json) are JSON arrays, not JSONL.
Each array element has exactly these fields:

| Field | Meaning |
| --- | --- |
| `round`, `arm` | Planned pair and arm identity; exactly one observation per arm/round |
| `run_id` | Globally unique execution identity across phases; retries need their own planned round |
| `revision` | Exact revision identity from the plan's arm map |
| `metric`, `unit`, `direction`, `workload`, `profile`, `guard_contract` | Must equal the plan |
| `status` | `success`, `failure`, `skipped` or `timeout` |
| `value` | Finite number for success, otherwise `null`; booleans are invalid |
| `guards` | `pass`, `fail` or `unknown` for the task's previously declared preservation checks |

The unchanged phase expects control and unchanged arms. Discovery expects control and every
treatment in each planned round. Confirmation expects only control and the recorded selected
treatment. Missing observations remain visible. A sample with any unverified or failed guard
is unusable for a paired improvement. Counts include both sides of a pair; inspect raw samples
to distinguish control and treatment failures. Keep underlying logs and guard evidence in the
existing task record, outside this portable bundle.

## Runnable example

The two-pair fixture has zero unchanged-control difference and a ten-second candidate
improvement on both discovery and confirmation pairs. Its small size is for CLI verification.
From this skill's directory:

```sh
python3 scripts/compare.py freeze assets/plan.json
python3 scripts/compare.py analyze assets/plan.json assets/discovery.json --plan-sha DIGEST
python3 scripts/compare.py select assets/plan.json assets/discovery.json --plan-sha DIGEST --arm candidate > selection.json
python3 scripts/compare.py analyze assets/plan.json assets/samples.json --plan-sha DIGEST --selection selection.json
```

Replace `DIGEST` with the retained `plan_sha256` from `freeze`. Put actual result and selection
files in the task record. The bundled confirmation rows are prewritten demonstration data;
for real decisions, collect confirmation only after preserving the selection. No hash can
prove that chronology from caller-supplied labels alone.

`freeze` returns the plan digest. `select` refuses confirmation observations and candidates
that do not meet the discovery rule. It returns `plan_sha256`, `discovery_sha256` and `arm`.
The discovery digest binds unchanged-control and discovery content independently of input
array order. Changing, adding or removing those observations invalidates the selection.
`analyze` refuses confirmation observations without a matching selection artifact and rejects
confirmation observations for unselected treatments.

Exit `0` means valid inputs were analyzed, including `INCONCLUSIVE` or
`DOES_NOT_MEET_BAR`. Exit `2` means invalid/unreadable input or invalid command arguments.
A malformed dataset does not produce a partial success report. JSON reports go to stdout;
input errors go to stderr without echoing input file paths or offending data. The analyzer
reads only the named files and does not write them. Redirect stdout if a saved artifact is needed.

## Reading the result

Each arm reports planned/complete pairs, missing/status/guard counts, each paired difference,
its median/range, positive-pair count, issues and a verdict:

- `INCONCLUSIVE`: incomplete data, unverified guards or unstable unchanged controls. Mixed-sign
  candidate results are also inconclusive when the median clears the bar; otherwise they fail it.
- `DOES_NOT_MEET_BAR`: usable observations fail the frozen practical/spread rule.
- `NEEDS_CONFIRMATION`: discovery meets the rule; a fresh selected-candidate check is pending.
- `CONFIRMED_OBSERVATION`: a selected candidate's fresh supplied identities meet the same rule.

The tool does not suppress other arms, rank winners, calculate significance, infer causality,
validate external provenance or establish generalization. Treat many-arm discovery as selection,
not independent confirmation. Report a failed confirmation rather than selecting a different
candidate after seeing it. New selection or changed criteria starts a new recorded experiment.
