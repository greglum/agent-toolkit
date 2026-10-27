# Source identity and resume

Use this record to resume work without treating an old approval as evidence about new source.
Keep it in the existing run state; no new service or repository artifact is needed.

## Capture the inputs

Record the repository/worktree identity, scope, base and current commit, then a path manifest:

- For scoped tracked files, retain status, index identity, and current content hashes, with
  explicit deletion and rename entries. A tracked diff alone misses untracked source.
- For scoped untracked files, record paths and content hashes, including additions and
  removals since the last observation. Record symlink targets without following them outside
  the authorized source. Use read-only native Git inspection without refreshing the index.
- Include relevant manifests and lockfiles, installed runtime/library versions used by the
  implementation, build and verification configuration, applicable instructions, design and
  motion tokens, shared primitives, and source helpers. Record only relevant inputs, not
  dependency folders or credential values. If a required input cannot be inspected, mark its
  identity unknown and keep the affected evidence unverified.

For each row, list owned paths and relevant shared inputs, with the identities used by its
last review and checks. Include known consumers when a shared primitive's behavior affects
them. An approved row needs its own evidence identity, not only the run's latest manifest.

## Reconcile before reuse

1. Compare the new observation with the saved manifest before resuming a phase. A different
   repository, scope, or base starts a fresh run; preserve the old state with a timestamp.
2. With the same base and scope, compare content, index, path inventory, dependency, and
   configuration identity. Mark every `approved` or `reviewing` row affected by drift as
   `reviewing`, and invalidate its affected checks. Recheck its opportunity and ownership
   before building or approving it again. Keep unrelated rows only with an explicit reason.
3. Follow shared inputs to their dependent rows. A token, primitive, helper, runtime, or
   verification-config change may invalidate an unchanged component's approval. If the
   dependency set cannot be established, mark all potentially affected rows `unresolved`
   rather than assume independence. Refresh build assumptions for unfinished rows too.
4. Recover outstanding findings under their existing IDs. Keep accepted, refuted with
   evidence, and unresolved findings distinct. A missing reviewer response or inaccessible
   location leaves an unresolved finding, not a clean review.
5. After each owned edit or integration, record the new observation. Replace a row's reviewed
   identity only after its review and affected checks have run again. Updating the manifest
   alone cannot renew an approval. Report external changes separately from this run's edits;
   preserve them when saving or reverting a blocked row's work.

Resume is complete when every reused approval names unchanged supporting inputs, every
invalidated row has a next check, and the current state retains all unresolved findings.
