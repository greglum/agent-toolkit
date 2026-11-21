# Guide format

Omit empty sections and shorten small changes; delivery and freshness rules stay in `SKILL.md`.

## Opening

Lead with one sentence explaining the problem and resulting behavior. Include:

- repository and PR/range link;
- observed date, comparison method, full base/head SHAs;
- original PR head and landed revision separately when they differ;
- size and changed artifact kinds;
- intent source and any inference;
- source-only, author-reported, or independently run evidence;
- current, historical, stale, or freshness-unavailable status.

## Reading map

| Order | Chapter | Why here | Attention |
|---|---|---|---|
| 1 | Contract or central behavior | Consumers depend on it | Boundary/invariant to verify |
| 2 | Consumers and observable result | Shows where the contract matters | Compatibility or state change |
| 3 | Supporting artifacts | Documents or enforces the change | Actual enforcement limits |

Use as many chapters as the behavior requires. These rows are examples, not a fixed count.
Put the change's risk concentration in plain words near the map. Do not invent scores,
review durations, or a confidence percentage for an explanation.

## Chapter

**Purpose:** The trigger, owning layer, and why the reader should care. Distinguish behavior
changes from mechanical moves and intended preservation.

| Before | After |
|---|---|
| Source-backed old flow or result | Source-backed new flow or result |

**Read in order:** Owner, callers, related test assertions. Use base links for deleted or
replaced behavior, head links for new behavior, and cite unchanged context separately.
Prefer commit-pinned permalinks with verified paths and line numbers; for local-only
history, give the SHA, path, symbol, and a native read command rather than a link to the
mutable checkout. Escape unusual filenames and validate link hosts. Explain the connections
between those anchors; a file list alone is not a walkthrough.

**Checkpoint:** A specific question about an invariant, failure path, or design choice, plus
the source or check that answers it and any evidence still needed. Distinguish a proven
defect from an open question, avoid invented bugs or urgency, and retain the applicable
defect-review workflow's finding identifiers for confirmed defects.

**Evidence/limits:** Source examined; checks actually run with revision and result;
author-reported results; unrun, failed, or unavailable checks. Tests present in a diff did
not thereby run. Label illustrative examples or diagrams that are not observed runtime behavior.

## Coverage and handoff

| Changed path or hunk | Chapter | Disposition |
|---|---|---|
| Exact path; old -> new for a rename | Owning chapter | Explained / inventory only / unresolved with reason |

Keep this complete even when an appendix is needed. For a file in several chapters,
identify its hunk ranges. Separate relevant unchanged context from changed coverage.
Totals must reconcile with the original diff, not with a renderer's normalized output.

Close with remaining questions, the next review action, and optional unchecked chapter boxes
tied to the full head SHA per `SKILL.md`.
