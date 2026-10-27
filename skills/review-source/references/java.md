# Java contracts

Use for Java source after identifying the repository's language target, runtime, framework,
dependency versions, and threading model. Unknown or conflicting versions remain a gap.
Recommend newer syntax only when the actual target supports it.

| Boundary | Establish before reporting a defect |
| --- | --- |
| Correctness | Reachable inputs, nullability, bounds, state transitions, error propagation, and data integrity. |
| Resources | Who creates, borrows, and closes each connection, statement, stream, executor, and lock; the platform's lifecycle contract. |
| Transactions | Atomic operations, isolation, rollback ownership, and uncertain write outcomes. Identify the database engine/version, driver, transaction manager, autocommit mode, failure class, and savepoints before prescribing recovery. |
| Concurrency | Shared-state ownership, lock scope, safe publication, cancellation, and ordering races under the actual framework. |
| Security | Authorization at its owner, query construction, validation, sensitive logging, and resolved file paths confined to their permitted root. |
| APIs | Request/response types, serializer behavior, backward compatibility, and version constraints at both ends. |
| Performance | Query count, blocking work, allocation, and data volume on a real path; label inferred cost separately from measurements. |
| Maintenance | Shared invariants, duplicated decisions, unclear ownership, and layers that add no behavior. |

A failed SQL statement does not imply one universal transaction state. Some engines or
failure classes roll back a statement; others abort or roll back the transaction. Determine
what later callers observe and how the owning transaction protocol restores valid state.
An empty catch is a lead, not proof that the whole transaction needs rollback. A borrower
must not close a shared connection or roll back its owner's transaction merely to satisfy
a generic cleanup rule. Preserve savepoint and transaction-manager boundaries.

When source extends a platform, consult its matching implementation or exact-version
documentation for resource, lifecycle, transaction, and threading claims. Without that
evidence, keep those claims unresolved and continue the independently supported review.

A loop, record, stream, Optional, base class, or dependency-injection pattern is not a
defect by itself. Apply the repository's rules and concrete impact rather than imposing
modern syntax, file-size targets, or an abstraction because a duplicate count was reached.

## Origin

Consolidates this catalog's Java source-review checks. Transaction recovery is qualified by
engine and ownership rather than inferred from Java or connection sharing alone. No SQL
recipe or external framework implementation is bundled.
