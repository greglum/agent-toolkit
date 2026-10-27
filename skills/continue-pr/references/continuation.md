# Preserve intent across a continuation

Fetch the identified source head and actual base, including fork identities. Record their
full SHAs and merge base. Read the original series separately from changes newly landed on
the base. Avoid assuming that the default branch is this PR's target.

For a rebase, retain the old head and base objects. Compare the old and new commit series with
`git range-diff <old-base>..<old-head> <new-base>..<new-head>`, then inspect the final diff and
current behavior. Range-diff aids human inspection; it is not a semantic equivalence proof.
Reconsider the disposition when conflicts expose product or architectural disagreement.
Preserve newer base invariants and avoid resurrecting behavior already removed deliberately.

Publish a rewritten branch only with authority for that target and a lease tied to the remote
head observed before the rewrite: `--force-with-lease=refs/heads/<branch>:<observed-head>`.
A lease rejection means another writer advanced it; fetch and reconcile rather than replacing
the expected SHA merely to make the next push pass. A rewrite is never the fallback for a
routine push rejection. Respect stronger repository restrictions on force pushes.

For a replacement, preserve original human authorship when importing commits, link the source,
and explain which goal carries forward. Follow an explicitly requested stacked or in-place
continuation. Verify squash credit using actual human identities and repository policy.
Do not close the original, edit its metadata, or post on it without that action's authority.
A replacement that exists does not establish that the original is obsolete.
