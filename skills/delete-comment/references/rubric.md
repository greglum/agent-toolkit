# Comment Classification Rubric

Classify every non-directive comment into exactly one of four categories before deciding edits.
Never invent a fifth bucket. If a comment mixes categories, assign the highest-consequence category
(`Decision Record` > `Excuse` > `Stale` > `Tautology`). See `SKILL.md` Step 3 for deletion, ADR
writing, shared-copy propagation, and syntax rules.

## 1. Tautology

**Definition:** Repeats what identifiers, types, signatures, control flow, or assertions already
show.

**Examples:**
- `# increment counter` above `count += 1`
- `// loop through users` above `for (const user of users)`
- `# Arrange`, `# Act`, `# Assert` inside short unit tests
- Ornamental banners such as `# ---- Helpers ----` or `// === Exports ===`

**Classification note:** No ADR or issue is needed.

## 2. Stale

**Definition:** Refers to removed code, old parameter names, retired behavior, fixed issues, or
claims that contradict the current implementation. Also includes commented-out dead code.

**Examples:**
- `// Fallback for IE11` when IE11 support was removed
- `# Returns None on timeout` when the function now raises `TimeoutError`
- `# old_v1_handler(req)` left commented out

**Classification note:** Verify against current source and history. If an active caller still
depends on the described behavior, reclassify as `Decision Record` or `Excuse`.

## 3. Excuse

**Definition:** Explains away a hack, fragile assumption, race condition, unfixed defect, missing
validation, or suppressed failure (`TODO`, `FIXME`, `HACK`, `XXX`, `WORKAROUND`).

**Examples:**
- `// Sleep 200ms so the DOM settles before clicking`
- `# Skip validation here because upstream sometimes sends strings`
- `# TODO: handle pagination when results exceed 100`

**Classification note:** Pair with the draft issue template below; do not reclassify a workaround as
a `Decision Record` unless it documents an intentional, permanent constraint.

## 4. Decision Record

**Definition:** Captures a non-obvious architectural, security, privacy, concurrency, protocol,
compatibility, or legal constraint that code alone cannot communicate and that a future reader
could accidentally break.

**Examples:**
- `# Constant-time compare prevents timing oracle on HMAC tags`
- `// Must drain stream before closing socket or kernel sends RST`
- `# Sorted insertion keeps binary search O(log n) in lookup_span`

**Classification note:** Check the enclosing module docstring, function docstring, and companion
documentation first. If they already capture the invariant accurately, classify the inline comment
as `Tautology` (or `Stale` if it drifted) instead of `Decision Record`.

## Edge-case rules

- **Contiguous blocks and mixed headers:** Evaluate consecutive comment lines (including blank `#`
  spacer lines) as one logical block, and split mixed headers cleanly: classify usage banners as
  `Tautology` while routing legal or licensing blocks through the license rule below.
- **License and attribution headers:** Check `LICENSE`, `THIRD_PARTY_NOTICES.md`, and whether the
  file ships as a standalone bundle. Classify required copyright lines, SPDX tags, or third-party
  attributions as preserved `Decision Record` legal notices rather than `Tautology`; if attribution
  is already recorded centrally and the license permits omitting inline repeats in every
  distribution form, classify it as a `Decision Record` reference.
- **Tool directives with trailing prose:** Bare tool directives (`# noqa: F401`,
  `# type: ignore[arg-type]`, `// eslint-disable-next-line`, `// @ts-expect-error`,
  `# shellcheck disable=SC2086`) are exempted so build and lint gates remain green. When an
  exempted directive carries trailing prose (for example `# shellcheck disable=SC2016 # ...`),
  classify only the trailing prose (`Excuse`, `Decision Record`, `Stale`, or `Tautology`) while
  leaving the bare directive outside deletion scope.
- **Intentional heuristics vs true excuses:** Separate documented simplicity caveats or design
  tradeoffs from real `Excuse` hacks such as workarounds that split strings to evade overbroad
  secret or leak scanners, suppress errors, or bypass validation.
- **Shared copies and templates:** Identify mirrored helper scripts, configs, or template copies
  (for example, via parity tests or `diff`) before classifying, and classify identical copies
  identically.
- **Test fixtures and string-embedded code:** Comments inside string literals, heredocs, or fixture
  blobs used to test parsers, linters, or formatters are code data, not comments to classify. For
  real comments in test files, classify setup narration (`# create user`) as `Tautology`, misplaced
  post-refactor history as `Stale`, non-obvious platform-emulation choices (such as file-mode
  emulation of sandbox failures) as `Decision Record`, and regression thresholds
  (`# fails when payload > 64KB`) as `Decision Record` unless captured in the test name or docstring.
- **Public docstrings and API doc comments:** Python docstrings (`"""..."""`) are string tokens
  and are not scanned as comments. JSDoc/TSDoc (`/** ... */`), Javadoc, and Rust doc comments
  (`///`, `//!`) use comment syntax and appear in inventory: classify redundant internal blocks as
  `Tautology`, and classify verified public API contracts read by tooling or external callers as
  retained `Decision Record` contracts.

## Lightweight ADR template

Save as `docs/adr/NNNN-<slug>.md` (use the repository's existing numbering and naming scheme if
one exists).

```markdown
# NNNN. <Short decision title>

- Status: Accepted
- Date: YYYY-MM-DD
- Sources removed: `<path>:<line>`, `<path>:<line>`

## Context

What constraint, failure mode, or external requirement forced this design?

## Decision

What invariant, ordering, or boundary the code enforces today.

## Consequences

What maintainers must preserve when changing this area, and when to revisit the decision.
```

## Draft issue template (for Excuses)

```markdown
### [<slug>] <Short problem title>

- Locations: `<path>:<line>`, `<path>:<line>`
- Problem: What hacky assumption, suppressed check, or missing edge case exists today.
- Proposed fix: Narrowest clean remediation and how to verify it.
```
