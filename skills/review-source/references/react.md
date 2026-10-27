# React contracts

Use for React surfaces after identifying the React version, build environment, client/server
boundaries, design authority, and installed state and UI libraries. Trace components through
their hooks, services, shared primitives, consumers, and relevant tests.

| Boundary | Required evidence |
| --- | --- |
| Component identity | A reachable remount or key change that resets state, focus, or effects. Nested component definitions and unstable keys are leads. |
| State ownership | Inputs or event order that cause competing truth, stale derived state, or an effect race. Intentional editable drafts and captured snapshots can be correct. |
| Async work | A reachable stale response, cancellation gap, or pending/error transition and its user-visible result. |
| Native subscriptions | Trace actual element or resource identity and readiness through mounting, hydration, deferred rendering, replacement, and cleanup. Stable IDs or keys do not prove a native observer subscribed to the current target. |
| Accessibility | Names, semantics, keyboard operation, focus, contrast, and reduced motion; label source evidence separately from observed browser behavior. |
| Performance | Measured cost where available, or a concrete unmeasured mechanism involving work, subscriptions, renders, or requests. |
| Contracts | Both sides of a prop, service, or server/client boundary and a failing input or state. |
| Maintenance | A shared rule that can drift or a change requiring coordinated edits, rather than line count or superficial similarity. |

Repository decisions outrank generic React preferences within the user's instructions.
Do not impose a state library, server components, barrel policy, prop typing style, or
arbitrary size threshold without an applicable rule or an evidenced failure.

Memoization, callbacks, refs, context, manual fetching, and class components can be valid.
Verify their behavior. Deriving values during render fits a single authoritative source;
an editable draft or intentionally retained snapshot has a different contract. Similar
components can represent distinct domain concepts. Share code only when it owns a shared
invariant and reduces actual maintenance cost.

Preserve authorization, validation, error handling, accessibility, and existing tests when
proposing simplification. A source-only audit leaves rendering, live async ordering, focus,
contrast, and runtime performance unverified where no observed evidence exists.

## Origin

Consolidates this catalog's React source-review checks, including the evidence required to
reject common false positives. No state library, rendering mode, or UI framework is imposed.
