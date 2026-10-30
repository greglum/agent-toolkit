# Snapshot contract, version 1

The script validates this contract at its input boundary. A supplied snapshot records
observations, not a live GitHub guarantee. Record dependency evidence with a source locator
and observation time. Include every known declared dependency and state what coverage was
not available in the handoff. No prose dependency parser is bundled.

```json
{
  "version": 1,
  "observed_at": "2026-10-30T00:00:00Z",
  "repository": "github.com/example/project",
  "default_branch": "main",
  "prs": [
    {
      "number": 10,
      "head": {"repository": "github.com/example/project", "branch": "feature", "sha": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"},
      "base": {"repository": "github.com/example/project", "branch": "main", "sha": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"},
      "files": ["src/feature.py"],
      "depends_on": [
        {"repository": "github.com/example/project", "number": 9, "state": "merged", "evidence": "PR 9 merged state observed at 2026-10-30T00:00:00Z; supplied fixture"}
      ]
    }
  ],
  "orderings": []
}
```

All displayed fields are required. Extra fields and duplicate JSON members at any object
level are rejected. Types and meaning:

| Field | Contract |
| --- | --- |
| `version` | Integer 1 |
| `observed_at` | ISO timestamp with timezone |
| `repository` | `host/owner/name`, no URL scheme; normalized to lowercase |
| `default_branch` | Nonempty branch name, case preserved |
| `prs` | Nonempty array of selected PR records in this target repository; unique positive integer numbers |
| `head`, `base` | Exactly `repository`, `branch`, `sha`; each nonempty string or null. SHA is a full 40/64-character hex object ID |
| `files` | Complete array of changed paths, including both old and new paths for a rename; null if completeness is unknown. An empty array asserts no changed paths |
| `depends_on` | Array of objects with repository, positive number, state and evidence. State is `open`, `closed`, `merged` or `unknown`; evidence is nonempty text |
| `orderings` | Array of `{ "before": 10, "after": 20, "reason": "producer precedes consumer; source locator" }`; selected endpoints and nonempty reason required |

Internal dependencies always create edges. An internal dependency also asserted merged is
flagged for snapshot reconciliation. An external dependency clears only when its supplied
state is merged. Closed is not merged. The tool does not verify that assertion remotely.

Stack inference matches base and head using repository plus branch, never branch alone.
An unmatched base other than the target's default branch blocks that PR and its descendants.
A mismatched parent-head/base SHA remains unknown even when branch order is known. Duplicate
head repository/branch identities are rejected as ambiguous. Full identities are retained.

Unordered same-path overlaps block both PRs and their descendants until an evidenced ordering
or existing dependency path resolves them. Unknown file lists make the plan incomplete;
candidate waves can still be shown. This is not proof that different files are independent.

Output includes source PR records, observation time, edge reasons, overlaps, unresolved
dependencies, unknowns, one cycle witness when present, blocked PRs and candidate waves for
unblocked components. Other cycles and their descendants remain blocked. Exit codes:
0 means a complete dependency plan under supplied evidence; 1 means incomplete; 2 means
invalid snapshot or input read failure. No exit code establishes merge readiness.

## Collect current GitHub evidence

Use an authorized read-only connector or the following GitHub CLI queries with explicit
hostname and target. These commands only read. Set `TARGET` to `HOST/OWNER/REPO` and `PR` to
the selected number. Repeat for every selected PR and each dependency outside the set.

```sh
gh repo view "$TARGET" --json nameWithOwner,defaultBranchRef
gh api --hostname "$HOST" "repos/$OWNER/$REPO/pulls/$PR"
gh api --hostname "$HOST" --paginate "repos/$OWNER/$REPO/pulls/$PR/files?per_page=100"
```

Map the PR response's `number`, `head.repo.full_name`, `head.ref`, `head.sha`, `base.repo.full_name`,
`base.ref` and `base.sha` into the snapshot. Prefix repositories with the response's host.
A deleted or unavailable repository maps to null. Collect every file page, then compare the
number of returned file records with the PR response's `changed_files` count. Do this before
adding `previous_filename` paths: one renamed file is one API record with two relevant paths.
The REST endpoint returns at most 3,000 files. A count mismatch, larger declared total,
API error or incomplete pagination means completeness is unknown: set files to null and
preserve the limitation. After this check, flatten `filename` and `previous_filename` paths.
Inspect
PR bodies and linked requirements manually for declared dependencies. Do not interpret an
issue number as a PR dependency without source evidence.

For external dependencies, record `merged_at` or verified PR state, not merely `closed`.
Check selected head/base identities again after collection; if they changed, refresh the
affected snapshot before planning. This tool supplies no live collection adapter or atomic
snapshot guarantee. Stacking systems that use synthetic bases, such as ghstack, may require
explicit dependency records rather than branch-name inference.
