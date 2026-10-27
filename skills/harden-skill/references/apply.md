# Snapshot and apply mechanics

Load at step 2 to build the workspace and baseline snapshot, and at step 7 to apply a passing
candidate.

## Snapshot

Select a unique workspace outside the target and every repository from the harness's approved
writable temporary roots. Prefer the host language's system-temporary-directory API only when
both command and file-edit tools can write there; otherwise use another approved OS temp root.
When file editing is scoped to the session's working directory, start the candidate-editing
session in that external workspace.

Use `baseline/` and `candidate/` as repo-shaped bundle roots: copy every selected path to
`baseline/<repo-relative-path>`, preserving the canonical skill directory name. Include the
canonical skill, referral wrapper, invocation sidecar, catalogs, routing manifests, and tests
or documentation that a passing revision could require.

Baseline snapshot command:

```bash
python3 scripts/apply_candidate.py snapshot-bundle <repo-root> <baseline-manifest.json> --path <repo-relative-path> [...]
```

A body-only revision may use the existing single-target `snapshot` command.

## Apply

Snapshot `candidate/` with the same selected path set:

```bash
python3 scripts/apply_candidate.py snapshot-bundle <workspace>/candidate <candidate-manifest.json> --path <repo-relative-path> [...]
```

If intentionally removing a whole selected path, add `--delete-path <repo-relative-path>` while
creating that manifest; an absent selected candidate path without this explicit intent is
rejected.

Then run, without `--apply`:

```bash
python3 scripts/apply_candidate.py apply-bundle <repo-root> <workspace>/candidate <baseline-manifest.json> --candidate-manifest <candidate-manifest.json>
```

A body-only revision may use the existing single-target commands.

The helper verifies content and Git-relevant executable state at the write boundary, rejects
symbolic links and modified or missing baseline files, never overwrites post-snapshot
additions, and retains one rollback snapshot. If any canonical or shared-file write fails, it
restores the complete selected path set; never leave a wrapper, catalog, routing case, or test
partially updated.
