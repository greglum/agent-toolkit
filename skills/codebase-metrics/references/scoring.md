# Frozen local score contract

The formula is local policy. It is not a score issued by any cited standards body.
Read measurement evidence before assigning statuses; the helper validates structure
and arithmetic, not whether tests are meaningful or evidence is sufficient.

For each applicable dimension, let T be total criterion weight, P verified PASS
weight, and U UNAVAILABLE plus NOT RUN weight. Report `10*P/T` and the possible
interval `[10*P/T, 10*(P+U)/T]`. FAIL and unknown weights remain in T. A critical
FAIL or unknown blocks attainment even if the conservative score reaches target.
Each applicable dimension must meet target independently. Required project gates
are an additional acceptance condition, regardless of the numeric result.

## Files and invocation

Use a project-owned assessment directory and retain baseline and final observations
separately. Evidence paths resolve from `--evidence-root`, never the skill directory.
Run from either Codex or Claude Code using the skill's installed path:

```sh
python3 <skill>/scripts/score.py freeze plan.json --evidence-root assessment > freeze.json
python3 <skill>/scripts/score.py score plan.json baseline.json --evidence-root assessment > baseline-score.json
python3 <skill>/scripts/score.py score plan.json final.json --evidence-root assessment > final-score.json
```

Exit codes: 0 means a valid freeze or all applicable dimensions met the target;
1 means valid observations with an unmet target; 2 means invalid input or evidence.
JSON score output on exit 1 is still the measurement result. Exit 2 writes an
error JSON to stderr and emits no score. Do not treat these codes as project gate
results. Keep the freeze output in the original assessment record before editing.
The helper cannot prevent somebody from deliberately replacing both plan and hash.

Hashes are lowercase SHA-256. JSON hashes use Python `json.dumps(value,
sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)` encoded
as UTF-8. `freeze` returns the canonical plan and scope hashes; formatting changes
alone do not change them. Duplicate JSON keys and nonfinite values are rejected.
Evidence hashes use the file's raw bytes. Every supplied evidence file must exist,
be a regular file within the evidence root after resolving symlinks, and match its
hash. No commands are executed and no files are written by the helper.

## Plan schema, version 1

The top-level object contains:

| Field | Value |
| --- | --- |
| `schema_version` | Integer `1` |
| `assessment_id` | Nonempty stable name |
| `frozen_at` | Nonempty UTC observation timestamp |
| `target` | Finite number from 0 through 10, typically `9.5` |
| `scope` | Nonempty object recording files/features/journeys, exclusions with reasons, execution profiles, baseline revision/diff, and mandatory gate owners/commands |
| `dimensions` | Exactly eight objects, one per ID in measurement selection |

Each dimension has `id`, `applicable` (boolean), and `criteria` (list). An applicable
dimension has at least one criterion. Every criterion has the following fields:

```json
{
  "id": "functional.import-roundtrip",
  "weight": 5,
  "critical": true,
  "pass_condition": "Existing export/import contract passes without losing supported fields",
  "evidence_level": "Existing contract suite plus observed running journey with fixture",
  "raw_measure": "Verified supported fields / frozen supported-field inventory; list losses"
}
```

IDs are globally unique. Weights are positive integers fixed by user harm before
improvement, not by how easy checks are to pass. The helper accepts additional
metadata and includes it in the plan hash. Put precise command/profile, thresholds,
state lists, exclusions and denominator definitions beside each obligation as needed.
The helper does not verify that these text fields define a sound assessment.

For an inapplicable dimension, use `applicable: false`, `criteria: []`, a nonempty
`reason`, and a nonempty `evidence` list supporting the decision. This yields N/A,
not 10. At least one dimension must be applicable. Do not use N/A for missing tools,
time, access, or operational data required by the frozen scope. Individual exclusions
belong in the frozen scope/criterion rationale, not in deleted observations.

## Observation schema, version 1

The top-level object contains `schema_version: 1`, the exact `assessment_id`,
`plan_sha256` and `scope_sha256` from freeze, nonempty `observed_at`, `source`, and
`criteria`. `source` contains nonempty `revision` and `diff_sha256`. Hash a retained
working diff artifact, including an inventory/content hashes of relevant untracked
files; SHA alone misses local edits. Observations must describe one assessed source
state. The helper validates hash syntax, not correspondence to an actual checkout.

Each observation contains:

```json
{
  "id": "functional.import-roundtrip",
  "status": "PASS",
  "reason": "Every frozen supported field survived the observed roundtrip",
  "raw": {"verified_fields": 12, "supported_fields": 12, "lost_fields": []},
  "evidence": [{"path": "roundtrip.log", "sha256": "replace-with-file-sha256"}]
}
```

Use exactly one observation for every frozen criterion, with no extra or missing
IDs. `status` is `PASS`, `FAIL`, `UNAVAILABLE`, or `NOT RUN`; `reason` is nonempty.
`raw` is a nonempty object preserving the declared measurements, units, denominators,
exclusions and uncertainty. When unavailable, use null values and a missing-data
reason, not invented zeros. For example:

```json
{
  "id": "performance.field-inp",
  "status": "UNAVAILABLE",
  "reason": "No eligible field dataset is accessible",
  "raw": {"p75_ms": null, "eligible_sessions": null, "missing": "field dataset"},
  "evidence": []
}
```

PASS and FAIL require at least one hashed evidence file. Unknown observations may
have empty evidence, since missing data is not proof; any supplied files are checked.
Keep UNAVAILABLE separate from NOT RUN and retain logs for failed attempts. Neither
an evidence hash nor a PASS label proves the asserted outcome. Read the files.

## Output

Each applicable dimension reports `score`, `possible_interval`, `total_weight`,
`pass_weight`, `unknown_weight`, `status_weights`, `critical_blockers`, `target_met`,
and `status` (`MET`/`UNMET`). N/A has a reason, null score and null `target_met`.
Top-level output retains assessment/hash/source identity and
`all_applicable_dimensions_met`. Target comparisons use exact weighted arithmetic,
not rounded displayed scores. The output deliberately has no average score.
Present raw observations beside it, plus independently tracked mandatory gates.
