# Subtree publication

Load from step 1 when the repository publishes subtrees, and again at step 5.

## Discover mappings

Discover subtree prefixes and remote/branch mappings from repository guidance, maintained
configuration, or verified history. Record affected prefixes for step 5. An uncertain
mapping stays preserved and unpublished.

## Publish

Each remaining prefix needs verified remote URL, exact target branch, and user authority for
that publication. The main repository's push request supplies no authority for other
repositories. Reuse explicit authority already supplied; never infer `dev`, `main`, or
`master` from branch availability.

For an authorized mapping, use:

```bash
git subtree push --prefix=<verified-prefix> <authorized-remote> <authorized-branch>
```

Verify the published split commit at the destination. On failure, retain existing resources
and report the exact target. Do not pull, rewrite, force-push, add `--rejoin`, or publish
elsewhere as an automatic recovery. Report other independent authorized targets separately.
