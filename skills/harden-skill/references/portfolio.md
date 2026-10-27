# Portfolio mode

Use this protocol only for an explicit `/harden-skill portfolio` request. It extends the
single-target workflow without creating a second hardening entrypoint.

## Scope and modes

Use the target repository's declared skill registry, meaning a manifest, catalog, or equivalent checked
scope file, as the default scope. When none exists, use every skill directory under the discovered
skill root and say which root was used. Accept `skills <comma-separated names>` to narrow the run,
and reject names outside that scope. Honor the parent skill's `audit only`, `full
benchmark`, and `keep eval artifacts` modifiers. Exclude a newly edited `harden-skill` from its
own unvalidated run; include it on later runs.

Order ordinary skills lexically and process skills that other skills depend on, such as
`harden-skill` last. Record repository rules, validators, dirty paths, exclusions, and the exact
ordered scope before candidate work.

## Isolate the portfolio

Create one external temporary workspace containing repo-shaped `baseline/` and `candidate/`
trees plus a disposition ledger. Snapshot every scoped canonical skill, referral wrapper,
sidecar, catalog, routing manifest, registry, contract test, and documentation path that a
passing revision could change. Hash shared files before any candidate work.

Run `scripts/inspect_skill.py <skill-directory> --profile auto` for every scoped skill and use
the parent workflow's bundle manifests and `scripts/apply_candidate.py` protections
([`apply.md`](apply.md)). Never let
parallel workers edit live repository paths. When agent coordination is available, give each
worker one isolated skill or tightly coupled trigger group; otherwise run the same isolated
passes sequentially.

## Triage and compare

Run structural and portfolio validators first. Audit adjacent descriptions together for trigger
collisions, then assign every scoped skill exactly one initial disposition: `blocked`,
`candidate needed`, or `no supported change`. In `audit only`, finish after proving live hashes
and repository diffs are unchanged.

Build candidates only in the external tree. Apply the parent skill's rubric, baseline comparison,
trigger evidence, and rejection rules to each candidate. Serialize candidates that share a
wrapper, catalog, manifest, script, or reference. A rejected or blocked candidate stays
byte-identical in the live repository and does not block unrelated passing candidates.

## Integrate and apply

Assemble all passing candidates and shared-file updates in one integration tree. Run global
frontmatter, registration, routing, resource, link, script, and portfolio checks there. Reject or
repair conflicting candidates before any live write.

Rehash every scoped live path, dry-run the complete bundle, and review its writes and explicit
deletions. Apply validated skills serially with dependency skills last. Retain rollback snapshots
until final reconciliation; if any application or shared-file write fails, stop and restore every
live path changed by the portfolio run before reporting failure.

## Reconcile

Rerun all global validators, bundled-script tests, `git diff --check`, and cross-skill trigger
checks on the live result. Remove temporary artifacts unless retention was requested. Report one
final disposition for every scoped skill, applied paths, comparison and trigger evidence,
validators, rejected or blocked candidates, unchanged hashes, and residual risks. Never claim
portfolio completion while any scoped skill is unaccounted for or a required validator failed.
