---
name: postgres-investigate
description: Diagnose PostgreSQL query slowness, estimate errors, lock or connection bottlenecks, and row-security surprises. Produce evidence and a bounded remedy; use the project's migration workflow for schema or policy changes.
compatibility: Use an existing authorized PostgreSQL connection or supplied plans and schema. Without database access, produce an evidence-based diagnosis with explicit missing checks. Requires version-matched PostgreSQL documentation for engine-specific conclusions; no installer or database changes are included.
---

# Investigate PostgreSQL

Deliver a diagnosis record with reproducible evidence, semantic constraints, a proposed
remedy, and measured comparison where execution is authorized. Keep source-only hypotheses
separate from observed database behavior.

## 1. Bind the investigation

Identify the affected query or operation, database target, PostgreSQL version, actual
application role, and authorized observation scope. Read the project's database guidance
and identify the existing owner of SQL, migrations, and connection configuration. A platform
connection does not prove the underlying engine is PostgreSQL or authorize tuning it.
Record expected results, tenant boundaries, and the symptom before choosing a remedy.

## 2. Collect the smallest discriminating evidence

Choose the relevant branch and account for its missing evidence:

- **Query plan:** capture SQL shape, representative parameters, indexes, table sizes,
  statistics freshness, and a nonexecuting plan where safe. Compare estimated rows,
  selectivity, joins, loops, and work done. A sequential scan may be the right plan;
  a read-to-hit ratio alone does not diagnose memory pressure.
- **Connections or locks:** correlate the incident time with active versus idle sessions,
  waiting queries, blocking relationships, transaction age, and pool limits. Identify the
  pooler, version, mode, and application concurrency. Distinguish waiting for a connection
  from waiting inside a query before proposing a setting change.
- **Row security:** inspect grants, policies, function execution rights, table ownership,
  bypass privileges, and session identity as the actual caller. Check version-matched
  PostgreSQL documentation for policy combination and UPDATE new-row checks. When
  `WITH CHECK` is omitted, determine the applicable `USING` fallback; omission alone is
  not evidence of unrestricted reassignment. Inspect any security-definer helper's owner,
  search path, and caller execution rights.

Use supplied artifacts if live observation is unavailable. Redact secrets and sensitive
values from retained plans and records; preserve parameter shape and relevant selectivity.

## 3. Test a cause before recommending a change

State the leading cause and an observation that could disprove it. Choose the smallest
comparison that separates it from competing causes. Verify the execution target and scope
before running SQL. `EXPLAIN ANALYZE` executes the statement, including writes and functions
inside reads. Plain `EXPLAIN` is not an unconditional safety boundary either: planning may
invoke functions. Check side effects, workload, time limits, and target-specific authority;
a rollback does not undo every external effect. Use an authorized disposable fixture when
live execution is outside scope, preserving representative data shape and cardinality.

Compare equivalent result sets and access behavior, then plans and latency under stated
parameters, cache state, concurrency, and repetitions. For a row-security remedy, exercise
allowed and denied operations as the real application role and at least two tenant identities,
including attempted ownership reassignment where applicable. A privileged admin run cannot
prove tenant isolation. Mark absent runtime evidence as unrun.

## 4. Deliver the diagnosis

Save the record in the project's existing investigation location or the requested destination.
Include:

- Target, observation date, source revision, engine and pooler versions, caller identity,
  expected semantics, and the evidence needed to reproduce the symptom.
- Supported cause, rejected alternatives, remaining uncertainty, and proposed SQL or
  configuration diff where justified.
- Before/after results with execution conditions, access checks, and failed, unavailable,
  or unrun checks kept distinct.
- The change owner, rollout and rollback considerations, and the next bounded verification.

Hand schema, policy, or configuration changes to the existing project workflow. Diagnosis
alone does not authorize applying them. Finish with this record even if the result is a
supported no-change recommendation or a precise list of missing evidence.

For source attribution and recheck triggers, see [provenance](references/provenance.md).
