# Concurrency boundaries

Read for async work, task groups, actor isolation or cancellation. Map each mutable value to
its isolation owner and each task to the component responsible for its result and lifetime.

- Actor isolation protects access, not a whole operation across suspension. Recheck state
  assumptions after `await`; use the existing identity/version check when an older result
  must not replace newer state.
- Keep UI-owned state on its required actor. `async` alone does not establish background
  execution. Check the target's isolation settings and actual work before moving it.
- Prefer structured children for scoped work. An unstructured `Task` needs explicit result,
  cancellation and lifetime ownership. A detached task is not a repair for an isolation error.
- Cancellation is cooperative. Check or propagate it at useful boundaries; retain required
  cleanup. A canceled result must not become successful empty data unless that is the contract.
- Use `withTaskGroup` for nonthrowing children; use `withThrowingTaskGroup` for throwing
  children. Observe errors while consuming results. Both scopes wait for children; cancellation
  cannot force an uncooperative child to stop. Returning the first result is not a hard timeout.

Treat `@unchecked Sendable`, unsafe isolation and `@preconcurrency` as claims needing a concrete
safety argument, not routine diagnostic fixes. Inspect captures and reference-typed fields;
a copied struct can still share mutable storage. Repair ownership or pass safe snapshots
before adding escape hatches. Preserve checked continuation single-resume and cancellation
behavior when bridging callbacks.

## Test boundaries

Check the test runner and framework supported by the target. Swift Testing and XCTest can
coexist, but shared helpers must use assertions the executing framework recognizes in that
version. Prove a deliberate failure is reported before relying on a migrated helper.
Preserve UI/performance coverage in the runner that supports it. Tests involving actor-owned
APIs need the appropriate isolation; replacing annotations to silence an error can change
what the test exercises. Keep existing worker defaults and avoid shared mutable fixtures
that depend on execution order.

## Sources and limits

Observed November 4, 2026. Original synthesis, not copied API recipes:

- [Swift language guide, Concurrency](https://github.com/swiftlang/swift-book/blob/main/TSPL.docc/LanguageGuide/Concurrency.md),
  Swift project: suspension, actors, task lifetime and cooperative cancellation.
- [Swift task-group implementation documentation](https://github.com/swiftlang/swift/blob/main/stdlib/public/Concurrency/TaskGroup.swift),
  Swift project: group lifetime, throwing results and cancellation semantics.
- [Swift Testing migration guide](https://github.com/swiftlang/swift-testing/blob/main/Sources/Testing/Testing.docc/MigratingFromXCTest.md),
  Swift project: coexistence and version-dependent assertion interoperability.
- [Emil Kowalski, write-swift](https://github.com/emilkowalski/skills/blob/c8a79627b59d72d764d6ab6f2c87c09a48169833/skills/write-swift/SKILL.md),
  MIT, copyright 2026 Emil Kowalski: discovery lead for a Swift-specific owner. No fixed
  toolchain table, build-setting mandate or upstream code adopted.

Official links above are living source pages. Their revision identity was not pinned and
reuse rights were not independently established; no prose or code is redistributed from
them. Context7 resolved `/swiftlang/swift/swift-6.1.2-RELEASE`, older than the observed local
toolchain, and returned compiler internals rather than a current user-facing contract. It
was not used to infer newer APIs. Check the destination's version before applying advice.
Recheck on toolchain, isolation, API or runner changes. Compiler fixtures establish bounded
language behavior only, not device behavior, automatic selection or benefit over no skill.
