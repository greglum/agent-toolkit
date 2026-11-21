---
name: cloud-ops-audit
description: >-
  Audit recurring cloud alerts, reconcile live AWS or GCP spend and free-tier cliffs against IaC
  and docs, and check cross-cloud cost-bound parity. Read-only by default. Not for IaC teardown
  (iac-teardown), threat modeling (security-audit), or BI metrics (reconcile-metric).
compatibility: >-
  Works with repository source and read-only cloud CLI access (aws, gcloud). Without cloud CLI
  credentials, audits IaC and docs statically and reports live billing, metrics, and account
  checks unavailable. Never mutates cloud state.
---

# Cloud operations and cost audit

Investigate recurring cloud alarms, reconcile actual and forecast spend against tagged project
budgets, and expose upcoming cost cliffs or live-vs-doc drift before making infrastructure
changes. Stay strictly read-only until the user authorizes specific remediation.

## 1. Bind scope, account boundaries, and read-only guard

Read the repository's agent, infrastructure, runbook, and cost-guard instructions first.

- Separate in-scope project resources from sibling projects sharing the same cloud account so
  out-of-scope account findings are surfaced clearly without touching them.
- Pass privileged or read-only cloud profiles strictly to read-only inspection commands; never
  export cloud admin credentials into build or test shells.
- Note per-call billing API charges (for example AWS Cost Explorer API calls) and batch reads
  rather than polling repeatedly.
- When `aws` or `gcloud` CLI access, billing APIs, or account permissions fail, are denied, or
  return partial data, continue the static IaC and doc audit, report each failed or unavailable
  live check separately, and never infer live spend or alarm state from missing calls.

Done when project scope, sibling exclusions, and credential boundaries are established.

## 2. Reconcile live spend against tagged budgets and upcoming cliffs

Load [cost and alarm traps](references/cost-and-alarm-traps.md) and reconcile account-level
billing against tag-filtered project budgets and live resource inventories:

- Compare ungrouped account totals and 30-day forecasts against tagged project budgets to surface
  untagged charges (public IPv4 addresses, extra budget actions past free tiers, active custom
  metrics, stopped-instance storage, orphaned snapshots, and unused secrets).
- Check free-tier and promotional trial expiration dates on active compute or database resources,
  and distinguish stopping an instance from releasing its billed IP or volume.
- Verify whether disabled or retired functions still emit logs into log metric filters with a
  non-null `default_value` that keeps custom metric billing active.

Done when every cost line item is mapped to an owner and classified as measured or estimated.

## 3. Trace recurring alerts to root cause

Correlate alarm states, notification logs, audit trails, runtime metrics, and application or IaC
source before assuming traffic spikes or abuse:

- Inspect serverless database auto-pause windows against alarm periods and statistics for sliding
  1-hour boundary spill, and check whether managed secret rotation schedules wake paused DBs.
- Inspect low-memory regional functions calling cross-region global endpoints (such as IAM) for
  short single-attempt timeouts without client reuse across warm invocations.
- Check whether nested exception wrappers (such as Python `ExceptionGroup`) hide the real timeout
  or error cause from structured JSON logs.

Done when each recurring alert is tied to source configuration, runtime logs, and measured spend.

## 4. Cross-check live account state against docs and migration plans

Compare live cloud account state against repository assumptions and any proposed cloud moves:

- Check account-level or regional capabilities (such as email sandbox vs production access) so a
  grant requested for a sibling project does not silently expose an idle endpoint in this repo.
- Before recommending or starting a cross-cloud migration, audit whether target managed services
  preserve hard overage/spend caps and true scale-to-zero behavior or require an edge cap first.

Done when live-vs-doc drift and migration cost-bound prerequisites are explicitly recorded.

## 5. Deliver a prioritized ledger

Group findings cleanly without applying unapproved edits:

1. **Immediate false-alarm fixes:** root cause, smallest change, and impact on any rate/cost
   flood envelope.
2. **Zero-regression cleanups:** dead schedules, disabled functions, orphaned snapshots, or
   unused parameters with confirmed zero live callers.
3. **Strategic retirements and migrations:** runtime savings now vs post-trial cliffs. When
   stack retirement is requested, hand off a structured packet (source revision, retiring stack,
   surviving dependencies, live findings, and teardown traps) to the explicit `iac-teardown`
   workflow (if available; otherwise note `iac-teardown` is not installed and leave teardown
   unexecuted). Hand off discovered security boundary drift (such as sibling privilege bleed) to
   `security-audit` and living-doc drift to `docs-sync` when those workflows are available, or
   flag those gaps explicitly when running standalone.
4. **Out-of-scope shared-account items:** listed separately for the owner without mutation.

Label every cost and traffic figure as measured, projected, or estimated.
