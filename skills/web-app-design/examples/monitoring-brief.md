<!-- Synthetic example. No product, account or live data. -->
# Draft design brief

Query: incident monitoring dashboard

Status: matched

## Operational monitoring (monitoring)

Lead with exceptions, freshness and the next useful action.

Use when: People watch changing system states and investigate exceptions.
Avoid when: The screen is a periodic narrative report.
Reason: A stable visual structure helps readers distinguish new evidence from layout movement.

Composition:

- Show timestamp and units next to each current value.
- Group exceptions by action or affected system.
- Preserve historical context and provide a text/table view of charts.

Type roles:

- heading: Use concise status headings.
- body: Keep alert explanations readable.
- data: Align units and use tabular numbers; do not rely on color alone.

Candidate color roles:

- surface: #151A21
- text: #E8EDF4
- accent: #9DC7FA
- on_accent: #102238

Declared pair checks (unrounded ratios):

- text on surface: 14.8561048682098:1, threshold 4.5, PASS (normal)
- on_accent on accent: 9.16199945932376:1, threshold 4.5, PASS (normal)

Sources: wcag22-contrast, dtcg-2025-10

## Product mapping still required

- Map candidate roles onto accepted token names; keep existing decisions and exceptions.
- Select real content, supported widths/themes and required interaction states.
- Verify geometry, actual fonts, contrast, focus and meaningful actions in the running app.

## Limits

- Original design candidates, not measured usability or industry-optimal recommendations.
- Use existing accepted design rules and tokens before these candidates.
- Pair checks cover declared opaque sRGB colors only, not rendered accessibility.

## Sources

- wcag22-contrast: https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html (Success Criterion; contrast thresholds and relative luminance; observed 2026-10-26; Reference only; W3C document rights. No text or color dataset copied.)
- dtcg-2025-10: https://www.designtokens.org/tr/2025.10/format/ (Design token; aliases/references; observed 2026-10-26; Reference only; W3C Community Final Specification Agreement. No schema copied.)
