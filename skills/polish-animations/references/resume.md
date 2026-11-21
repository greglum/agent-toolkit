# Source identity and resume

Use this record to resume work without treating an old approval as evidence about new source.
Keep it in the existing run state; no new service or repository artifact is needed.

## Capture the inputs

Record the run ID, repository/worktree identity, scope, and manifest snapshot using standard
CLI primitives:

1. **Git revision and dirty tree:** run `git rev-parse HEAD` and `git status --porcelain`
   (without refreshing the index) to capture the base commit plus modified, added, deleted,
   renamed, and untracked paths in scope.
2. **File digests:** run `shasum -a 256` (or `sha256sum`) on each row's owned paths and
   relevant shared inputs: package manifests/lockfiles, build and verification config,
   applicable instructions, design and motion tokens, and shared primitives. Record symlink
   targets via `readlink` without following them outside the authorized source. Omit
   dependency folders and credential values.
3. **Row bindings:** for each row, record its owned paths, relevant shared inputs, and known
   consumers when a shared primitive affects them, tied to the digests from its last review
   and checks. If a required input cannot be inspected, mark its identity unknown and keep the
   affected evidence unverified.

## Reconcile before reuse

1. Select this task's recorded run ID and compare a fresh snapshot against its saved manifest
   before resuming a phase. Never reuse another task's state because its scope looks similar.
   A different repository, scope, or base starts a fresh run; preserve the old state with a
   timestamp.
2. With the same base and scope, compare `git status --porcelain` and `shasum` digests. Mark
   every `approved` or `reviewing` row affected by drift as `reviewing`, and invalidate its
   affected checks. Recheck its opportunity and ownership before building or approving it
   again. Keep unrelated rows only with an explicit reason.
3. Follow shared inputs to their dependent rows. A token, primitive, helper, runtime, or
   verification-config change may invalidate an unchanged component's approval. If the
   dependency set cannot be established, mark all potentially affected rows `unresolved`
   rather than assume independence. Refresh build assumptions for unfinished rows too.
4. Recover outstanding findings under their existing IDs. Keep `accepted`, `refuted` with
   evidence, and `unresolved` findings distinct. A missing reviewer response or inaccessible
   location leaves an `unresolved` finding, not a clean review.
5. After each owned edit or integration, record the new observation. Replace a row's reviewed
   identity only after its review and affected checks have run again. Updating the manifest
   alone cannot renew an approval. Report external changes separately from this run's edits;
   preserve them when saving or reverting a blocked row's work.

Resume is complete when every reused approval names unchanged supporting inputs, every
invalidated row has a next check, and the current state retains all unresolved findings.
