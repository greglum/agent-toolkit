---
name: review-source
description: Review named source files, a feature, or a codebase for reachable defects, contract failures, and maintenance problems with concrete impact, including unchanged code. Read-only source audit; not a PR verdict or commit-history assessment. Discover the stack and apply only relevant runtime checks.
compatibility: Requires source access and native read-only file or Git tools. Exact-version framework documentation is needed for claims that depend on it; missing contracts remain unverified. No package, server, credentials, or model provider is required.
disable-model-invocation: true
---

# Review source

Deliver evidenced findings for the requested current source, including code with no diff.
Preserve files, the index, and refs. Source review does not authorize edits, fetches, builds,
tests, project scripts, browser actions, or external comments. Separately authorized checks
retain their own scope and evidence. For a PR or history verdict, use the repository's
matching review procedure instead; this audit does not attribute defects to commits.

## 1. Bind the source and its contracts

Read applicable instructions and resolve the named files, feature, or codebase. Honor path
and focus limits; follow callers for context without widening the audit. Inventory the
complete requested scope, excluding generated code and dependencies unless requested.
Record source revision, relevant dirty paths, runtime and framework versions, existing
checks, and authoritative standards. For a current-tree audit, read current scoped files,
including in-scope untracked files; an empty Git diff does not end the audit. For an explicit
snapshot, read that snapshot and label it rather than substituting today's checkout.

Discover the actual stack, state and resource owners, and framework lifecycle contracts
from source and version metadata. Read matching checked-out framework source or exact-version
documentation when a conclusion depends on it. Missing contracts limit that conclusion;
continue independent review. Repository conventions decide local design choices, subject
to the user's instructions.

Load [Java contracts](references/java.md) for Java source and
[React contracts](references/react.md) for React surfaces. Read only applicable references;
other stacks use their discovered contracts, not Java or React conventions.

Complete when every requested path has a review batch or an explicit exclusion, and the
relevant source, version, and contract gaps are recorded.

## 2. Trace candidates through their owners

Read each included file and follow the entry point through callers, shared types, helpers,
persistence, response construction, consumers, and relevant tests. For each candidate,
establish the triggering input or event order, violated invariant, owning layer, and impact.
Check failure handling, resource lifetime, authorization, data integrity, concurrency,
compatibility, and performance where the path makes them relevant. A cost mechanism is an
unmeasured inference until measured. Source accessibility evidence does not prove rendering.

Try to refute the candidate using surrounding guards, framework behavior, tests, and actual
consumers. A documented API contract does not prove every shipped runtime implements it.
When that difference decides a finding, identify the affected runtime and keep its behavior
unverified until matching implementation evidence or an observation supports the claim.
Separate defects from intentional tradeoffs and style preferences. A syntax
pattern, line count, duplicate count, or unfamiliar abstraction alone is not a finding.
Unknown external use does not prove an API is unused. A proposed correction must preserve
the original goal, validation, authorization, data-loss safeguards, errors, accessibility,
and existing tests. Reuse the responsible owner or fitting native API before proposing a
new layer; respect borrowed-resource ownership.

Complete when every inspected candidate is confirmed, refuted with evidence, or unresolved
with the missing evidence named. Batch a large scope without silently sampling it. Report
urgent security, data-loss, or credential findings immediately.

## 3. Reconcile and report

Recheck scoped source fingerprints and relevant metadata before delivery. Refresh evidence
for concurrent changes, or identify the changed snapshot and limit the result. Account for
every requested path as reviewed, excluded, or incomplete.

For each actionable finding give location, governing contract, trigger, impact, evidence,
priority, and the smallest correction at its owner. Distinguish source proof, measured or
reproduced behavior, unresolved leads, and non-blocking judgment calls. Include framework
citations where the finding depends on them.

Finish with findings, covered and unresolved paths, resolved versions, and passed, failed,
unavailable, or unrun checks. No findings means no confirmed problems in the examined scope.
It does not establish runtime behavior, CI success, deployment, or merge readiness.
