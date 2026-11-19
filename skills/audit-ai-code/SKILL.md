---
name: audit-ai-code
description: "Audit changed code for recurring AI-authoring defects: one-caller indirection, hand-rolled security, mirrored state, failure-path leaks, weak failure tests, dev-scale data handling, invented locking, races, premature config, reinvented helpers, and unverified symbols. Use after AI-assisted work. Prefer a repository's own audit. Not for whole-repo sweeps."
compatibility: Requires Git and read access to the target files and repository standards (such as AGENTS.md). Report mode is read-only; applying fixes with --fix requires write access and an explicitly authorized current-worktree target. Runs the repository's existing checks after edits; report missing checks as unavailable.
---

# Audit AI code

Find recurring structural defects that AI-assisted code introduces into a repository, report confirmed findings, and apply the smallest fix only when explicitly asked (`--fix`). Defer stack-specific rules, canonical helper lists, and verification gates to the repository's `AGENTS.md` and local standards.

If the repository has its own AI-authoring audit, use that instead; its catalog and authority take precedence.

Use this during or right after AI-assisted implementation, before committing, or as a focused pass inside a review. Do not use it for whole-repository sweeps, spec-conformance reviews, or as a substitute for repository build and lint gates.

## 1. Resolve the target

Run target probes as separate commands without hiding stderr:

```text
git status --short
git diff --stat
git diff --cached --stat
```

- Default target: uncommitted working tree plus staged changes. A path argument scopes to one file or directory.
- `--branch`: target `<resolved-base>...HEAD`, resolving the default base from the remote HEAD rather than hardcoding a branch name.
- `--base <sha> --head <sha>`: report-only pinned committed diff. Verify both commits, use them in every diff command, and read files with `git show <head-sha>:<path>`. Do not combine pinned mode with `--fix`.
- When a caller already resolved a target, accept it without re-resolving.

A non-zero Git exit or malformed output is an operational failure, not an empty diff: report the command and error and stop. An empty diff exits cleanly with `no changes in scope`.

Read changed hunks first, then read full files and relevant callers for any candidate before confirming it. A tendency is a property of the resulting code, not an isolated hunk.

## 2. Confirmation discipline

- Every finding names a tendency ID (`T1` through `T11`), `file:line`, and concrete evidence satisfying its **Confirmed when** clause.
- Verify every candidate directly against the target file (or pinned revision). Never report from a grep hit or summary alone.
- Score each candidate from 0 to 100 and report or fix only findings at or above `70/100`. Count omitted lower-confidence candidates in the summary.
- Never duplicate what an automated repository gate already enforces (typecheck, linter, formatter, secret scan, or custom validator).
- Leave pre-existing code outside the target alone unless the change lands directly beside it in the same file.
- For every confirmed finding, state the behavior that must stay intact and the focused check that proves it.

## 3. Tendency catalog

### T1: Indirection with one caller
- **Confirmed when:** A new interface, factory, provider, strategy, callback seam, or wrapper has one production implementation and one call site, and inlining it removes a layer without changing behavior.
- **Not this:** Required framework extension points, shared helpers with three or more real callers, or repository-sanctioned boundaries.
- **Fix:** Call the concrete implementation directly and remove the seam.

### T2: Hand-rolled security and platform primitives
- **Confirmed when:** The change implements custom crypto, hashing, token minting/comparison, session or auth checks, builds queries by concatenating caller input, skips server/boundary validation, renders raw untrusted HTML, or puts secrets in tracked files.
- **Not this:** Standard library, framework, or platform primitives used per repository standards.
- **Fix:** Use parameterized queries, validate at the authoritative boundary, and delegate auth, crypto, and sanitization to platform primitives.

### T3: State kept that nothing needs
- **Confirmed when:** Code stores a value already available elsewhere: local state mirroring props or server query results, a manual in-flight flag beside a query/mutation state, a derived value kept in state and synced via effects, or a collection accumulated and read once.
- **Not this:** An edit buffer or optimistic draft that must diverge from source state, or a cache backed by measured cost.
- **Fix:** Derive the value at point of use and delete the mirror and sync effect.

### T4: Swallowed failures and leaks on failure paths
- **Confirmed when:** A resource, subscription, timer, handle, or tracked entry is acquired and released only on the success path, or a catch block swallows an error and returns a misleading normal result.
- **Not this:** Lifecycle management already owned by the runtime or enforced by an automated gate.
- **Fix:** Release resources on every exit path (scoped cleanup, `finally`, `defer`, try-with-resources, or effect cleanup) and propagate or surface real failures.

### T5: Missing or weak failure-path tests
- **Confirmed when:** The change adds a meaningful failure path (rollback, conflict mapping, validation rejection, error response) with only happy-path tests, or adds a test that asserts mock call order, private internals, or broad snapshots instead of observable behavior.
- **Not this:** Low-value coverage chasing, impossible states, or framework behavior. Follow the repository's test value standard.
- **Fix:** Add or extend one focused test that triggers the failure and asserts the observable outcome. If no test clears the repository's value bar, state that explicitly.

### T6: Dev-scale data and file handling
- **Confirmed when:** Work the database or a stream should perform happens in memory: fetching unbounded rows to filter, sort, paginate, or aggregate in application code; issuing a query per row (N+1); or buffering large files whole when streaming or path handling is available.
- **Not this:** Bounded small lookups or computations that cannot be expressed safely in the data layer.
- **Fix:** Push filtering, sorting, pagination, and aggregation into one bounded query or stream.

### T7: Invented locking for a database or single-owner invariant
- **Confirmed when:** In-process locks, mutexes, atomics, or concurrent maps are added to protect request-local state or enforce uniqueness/ordering invariants that belong in the database or shared store.
- **Not this:** Synchronization around a genuinely shared, documented in-process resource.
- **Fix:** Remove the in-process lock and enforce the invariant in the data store (constraints, conditional updates, or transactions).

### T8: Check-then-act races
- **Confirmed when:** Code reads state in one step and acts on it in another without atomicity (select-then-insert, read-modify-write counters, delete-then-insert, or UI submits lacking an in-flight guard).
- **Not this:** Explicitly documented best-effort reads where staleness is harmless.
- **Fix:** Collapse into one atomic operation with conflict handling, or wrap genuinely multi-statement invariants in a transaction; disable duplicate UI submits while in flight.

### T9: Configuration ahead of a second value
- **Confirmed when:** A new config key, environment variable, or feature flag has one call site and one value across all environments.
- **Not this:** A real per-environment or deployment-time difference.
- **Fix:** Inline the constant now; introduce configuration when a second value is needed.

### T10: Bespoke helper beside a canonical one
- **Confirmed when:** The change reimplements behavior the repository or its standard dependencies already provide (custom mappers, query builders, formatters, UI primitives, or duplicate libraries).
- **Not this:** A genuinely new capability or a documented limitation of the canonical helper.
- **Fix:** Reuse the canonical helper, or extend it cleanly in place if it nearly fits.

### T11: Unverified symbols
- **Confirmed when:** The change references an identifier outside compiler or typechecker reach (SQL tables/columns, config keys, event names, RPC/API strings, or unchecked dynamic names) without verifying it against its source of truth.
- **Not this:** Symbols verified in this pass against schema, registry, config, or checked imports.
- **Fix:** Verify each identifier against its authoritative source and fix or remove any mismatch.

## 4. Report or apply (`--fix`)

Reporting is the default and makes no edits. With explicit `--fix` on an authorized current-worktree target, apply only findings at or above `70/100`, smallest fix each, one tendency at a time. Never bundle unrelated cleanup, never edit generated files, and touch test files only for `T5` or to preserve contracts affected by a fix.

After applying fixes, run the repository gates required for the touched layers. Report each gate's exact status (`passed`, `failed`, or `unavailable`) and never claim a pass you did not observe.

## 5. Output

```markdown
## LLM tendency pass: <target> (<N> files, mode: report|fix)
**Scope:** <files read> | **Gates run:** <commands, or none in report mode>

### [T<n>] <tendency> at <file:line> (confidence N/100)
- **Evidence:** <verified fact satisfying Confirmed when>
- **Fix:** <smallest correction> | **Applied:** yes | no
- **Acceptance preserved:** <behavior that stays intact>
- **Verification:** required, not run: <check> | passed | failed | unavailable: <reason>

### Summary
<per-tendency counts, or "no tendency confirmed">; omitted below 70/100: <count>
```

Omit tendencies with no confirmed findings. A clean result on a small diff is normal.
