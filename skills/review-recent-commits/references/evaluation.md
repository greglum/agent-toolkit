# Evaluation checklist and priorities

Evaluate both each commit and the selected series:

| Area | Required check |
|---|---|
| Correctness and safety | Logic, edge cases, data loss, security, concurrency, resource handling, and silent failures |
| Intent and value | The change solves an evidenced problem without speculative scope |
| Repository compliance | Applicable instructions, architecture, types, generated-file rules, and required test changes |
| Simplicity | No premature abstraction, duplication, dead compatibility layer, or unrelated refactor |
| History quality | Atomic scope, cross-commit interactions, reversibility, and a message that accurately describes the patch |
| Current state | Whether later commits or dirty work fixed, superseded, or obscured the original effect |

Do not trade away the problem being solved for superficial simplicity, and do not apply
rules from the wrong runtime.

Use these priorities:

- **P0**: immediate security, data-loss, or system-wide failure risk.
- **P1**: significant correctness or operational failure.
- **P2**: material design, scope, rule, test-evidence, or commit-history problem.
- **P3**: non-blocking maintainability or clarity issue.

P3 findings alone do not block approval. A materially misleading commit message may be
P2; minor wording preferences are P3 or omitted.
