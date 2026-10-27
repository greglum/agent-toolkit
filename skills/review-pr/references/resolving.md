# Resolving review objects

Load from Step 1 when a recorded object is missing locally, `--base` is provided, or PR
metadata is unavailable, and from Step 6 for a PR freshness check.

## Missing recorded object

If either recorded OID is unavailable locally and remote reading is authorized, retrieve that exact object from the verified repository remote into an isolated scratch object store. Verify the full OID before review; preserve checkout and branch refs. If retrieval fails or access is missing, report the missing object and continue independent checks. Never substitute another commit.

## Explicit base

If `--base` is provided, resolve that explicit base to a commit and honor it even when the PR has a different base. Use the merge base of that custom base and selected head as the comparison base unless the user explicitly requests a historical two-endpoint comparison. Retain the PR base and PR merge base separately in the review metadata. Only an explicit historical request compares the two selected endpoints directly.

If the explicit base cannot resolve, stop and ask for a resolvable `--base`; do not substitute another base.

## Local review without PR metadata

If PR lookup fails because remote metadata, authentication, or the `gh` client is unavailable, continue with a named local review only when a local committed base can be resolved. Do not infer that no PR exists and do not fetch automatically. State the unavailable metadata and the local base and head used. If neither a PR nor a usable local base is available, stop and ask for an explicit `--pr` or `--base`.

For a local review with no explicit base, resolve a named local base supplied by repository context if it exists locally, then use its merge base with the selected head. Do not assume `dev` is present. Resolve every object with `git rev-parse --verify` and record full SHAs.

## Freshness

For an explicitly selected historical review, retain the pinned original endpoints and
reconcile survival at the separately pinned current revision. Report remote-state availability;
do not move the historical comparison to today's PR base or claim merge readiness.

Before issuing a current PR verdict or review output, requery the selected repository's PR for
`baseRefOid`, `headRefOid`, and state. Compare with the recorded values. Re-resolving the
same local SHA is not a remote freshness check. If an endpoint changed, repeat the full
review once against the new immutable endpoints. If it changes again, report the review
stale. If remote verification becomes unavailable, report freshness unverified and qualify
the result. A changed pushed head requires a fresh independent review and fresh required
gates before merge readiness can be claimed.
