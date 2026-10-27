---
name: review-integration
description: Review client-API integration for wire-contract mismatches, transformation costs, validation, and error handling. Audit a requested feature or integration scope; keep findings read-only unless fixes are authorized.
disable-model-invocation: true
arguments:
  - name: entity
    description: "Entity or feature to review (default: every integration point in the requested scope)"
  - name: layer
    description: "Focus areas to review: types, transforms, contract, errors, validation, naming (default: all)"
---

# Client-API Integration Review

Identify real problems in the client-API integration layer. Report only issues with
demonstrable impact on development velocity, type safety, data consistency, or
maintainability, and a reachable input or caller.

Keep this review read-only unless the user also authorizes fixes. Read applicable repository
instructions and bind the requested feature, paths, and revision before examining contracts.
`entity` narrows the scope to one entity or feature. `layer` narrows the assessment to the
named rows of [`references/focus-areas.md`](references/focus-areas.md).

## 1. Discover the stack

Read package, build, route, and schema metadata to identify the actual stack, then inventory
the requested paths with `rg --files` or the available equivalent. Map the integration points:
types and models, the API client (fetch and transform), handlers or controllers, and the
schema as source of truth.

Account for every integration point in scope as reviewed, excluded with a reason,
or blocked. Follow shared contracts and callers beyond a named file when needed
to understand it; keep any fixes within the authorized scope. Work in bounded
batches for a large request and keep remaining paths visible. A partial sample
cannot support a clean full-scope verdict.

## 2. Assess

1. Map data flow for key entities: Schema → Backend → API Response → Frontend Type → Component.
2. For each entity, verify actual route, serializer/naming policy, request validation, and
   consumer behavior at each boundary; declared types alone do not prove the wire contract.
   No statically found consumer means unknown external use, not unused API.
   Check that the client validates the reply at its boundary, that validating only
   the envelope does not prove the variant fields, and that test fixtures keep the
   real wire shape (serialized timestamps, omitted nulls). A serializer can omit null
   keys, so nullable and absent are different wire shapes; a schema that requires the
   key fails on a healthy reply.
3. Review the API client layer for consistent, necessary transformations.
4. Identify translation-layer code bridging misaligned contracts, and TODO comments or
   workarounds indicating friction.
5. Read the relevant contract tests and checks. Treat comments, declared types,
   and search matches as leads; confirm each candidate on the actual data path.
6. Apply each requested focus area from [`references/focus-areas.md`](references/focus-areas.md).

When the stack is unclear:

| Situation | Action |
|-----------|--------|
| Can't identify frontend framework | Ask user or note limitation |
| Can't identify backend framework | Focus on API response shapes from client perspective |
| No TypeScript types found | Inspect the actual contract mechanisms; report only a proven mismatch |
| Mixed stack (multiple backends) | Analyze each integration point separately |

## 3. Report

For each finding, provide:

| Field | Value |
|-------|-------|
| Location | [frontend file], [backend file] |
| Evidence | Source or observed result, reachable trigger, and violated contract |
| Category | The Category of the finding's row in the focus-areas table |
| Issue | Description of WHY this is an integration problem |
| Impact | What breaks, what's confusing, what slows down development |
| Fix | Which layer should change, or if both need coordination |
| Effort | Low, Medium, or High |
| Value | Why fixing this matters |

Constraints:

- Only suggest consolidation when it reduces complexity.
- Client validation gives feedback and server validation protects the trust boundary; keep
  both when they serve these distinct roles. Consolidation must preserve authorization,
  tenant scope, input validation, and backward compatibility for other API consumers.
- Some transformations are intentional.
- Account for other API consumers and compatibility before recommending a response change.

### Good Finding

| Field | Value |
|-------|-------|
| Location | src/services/userService.ts:45, api/controllers/UserController.java:120 |
| Evidence | UserController.java:118 serializes `role` as an int; userService.ts:45 maps it through a literal table with no default |
| Category | TRANSFORMATION |
| Issue | User role stored as integer in DB, returned as integer by API, mapped to string enum in service via hardcoded lookup |
| Impact | Mapping table in both backend and frontend. New role requires updating both or client shows "undefined" |
| Fix | Find the owner of the role contract and coordinate a correction that preserves other consumers and supported versions |
| Effort | Low |
| Value | Single source of truth for role values |

### Bad Finding (Don't Report)

The client uses camelCase and the database snake_case. A single transformation layer is the
standard convention.

## Completion

Finish when every integration point in scope has a disposition and each material
finding identifies its trigger, evidence, impact, and owning correction. State
reviewed and unresolved paths, schema/API versions when known, and checks run,
failed, unavailable, or unrun. Keep source, wire observations, and runtime results
separate. A source review does not prove live API behavior or deployment readiness.
