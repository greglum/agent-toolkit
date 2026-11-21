# Layers, miss modes and fixes

## Layers

Name the cheapest layer whose stated scope covers the failed behavior. Use the repository's own
names for its lanes and profiles; these are the classes.

| Layer | Covers | Evidence that it was in play |
| --- | --- | --- |
| Unit or behavior test | One module's contract | Tests added or changed near the defect |
| Integration or contract test | A boundary between layers or services | A contract, schema or wire test suite |
| Gate or lane | Lint, types, build, a named check profile, CI job | A gate config, a check command named in the change |
| Rig or harness scenario | Rendered UI, keyboard and focus, accessibility, end-to-end flows | A rig, harness or browser scenario named in the change or docs |
| Review | A human or agent reading the diff | Review threads, approvals, reviewer comments |
| Self-assessment | The author's own score, checklist or claim of done | A self-score or "verified" claim in the body |
| Spec or acceptance | The stated requirement for the change | An issue, spec or acceptance list the change links |

## Miss modes

- `absent`: no layer in the repository covers this behavior.
- `skipped`: the layer exists but this change did not run it, for example an optional lane or a
  profile that leaves the needed check out while still passing.
- `blind`: the layer ran and passed, but asserted nothing about the failed behavior.
- `self-assessed`: the only evidence was the author's own score or claim, and a later reader found
  the defect. A high self-score followed by review findings is this mode.
- `overridden`: the layer reported the problem and the change merged anyway.

A defect review caught before merge is an escape of the layers before review, not of review.

## Discount blame's false positives

Blame names the last change to a line, not the change that caused the defect. Discount, and say
why, when:

- the introducer only refactored, formatted, renamed or moved the code (`false_positive_hints`, a
  matching `.git-blame-ignore-revs` entry, or a diff that moves lines without changing them);
- the fix removed lines only to make room for new code, so the blamed lines were never wrong;
- the fix is a dependency bump, generated output, or a revert of a change in the same window;
- the "fix" is an improvement or polish round that raised quality without repairing a defect;
- the introducer is a root or bulk commit, such as an import of existing code;
- the introducer's `share` is small and another introducer holds most of the blamed lines;
- the defect came from an outside change, such as an upstream release or a platform change.

Read the fix diff with `--stat` first, then the hunks, before accepting an attribution.

## Fixes and handoffs

| Miss mode | Usual fix | Handoff |
| --- | --- | --- |
| `absent` at a test layer | A behavior or contract test at the nearest suite | The nearest test suite owner, or `encode-correction` (behavior test level) |
| `absent` or `blind` at a gate | Extend or add a gate check | `encode-correction` |
| `skipped` | Make the lane mandatory for the paths that need it, or make the default profile include it | `encode-correction`, at the gate owner |
| `blind` at a rig or harness | Add the missing scenario, such as keyboard, toast or focus states | The rig's owner file |
| `self-assessed` | Require independent review or a named check before a self-score counts | The instruction or review owner |
| `overridden` | Make the signal blocking, or record why it is advisory | The gate owner |
| Review missed it twice | One rubric item naming the defect class | The review rubric owner |

Prefer the fix that removes the miss mechanically over a new instruction line.
