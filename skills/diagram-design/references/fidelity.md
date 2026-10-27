# Redraws and topology changes

Read for imported diagrams, before/after views, graph exploration checks, or changes to
this skill's upstream basis.

## Redraw a supplied figure

Retain the original source. Assign stable identities to its entities and relationships.
Record source and output node/edge counts, then reconcile the identities; equal counts alone
do not prove fidelity. In a small ledger, account for every rename, merge, split, collapse,
removal, and added inference. Preserve guards, cardinality, sequence, direction, and boundary
membership. Mark uncertain source meaning rather than resolving it through appearance.

A dense slide may omit implementation detail when a linked detail figure and its ledger
retain that meaning. It may not silently remove a rejected outcome or turn conditional
access into unconditional access. Keep uncertainty visible in the overview itself.

## Compare versions

Separate identity from display name. Keep unchanged components in stable positions when
possible. Distinguish a rename from a new component, a move from a rewire, and an absent
component from one outside the view. Label added, removed, changed, and rewired elements;
provide an explicit before-to-after mapping where identity could be ambiguous.

Check each changed edge against both source versions. The ledger must account for every
scoped topology change and every intentional omission. A delta diagram explains design;
it does not establish safe migration order, rollback correctness, or data preservation.

## Check graph exploration

When an existing viewer promises search or tracing, check results against stable node and
edge identities in the source ledger. Exercise search, both traversal directions, a disconnected
target and reset. Distinguish all reachable components from one selected route. A highlighted
path establishes connectivity in the authored graph; execution order, conditional feasibility
and live impact need separate evidence. Verify which selected state survives the requested
export, including its legend and scope, rather than assuming the image matches the viewer.

This original refinement draws on Archify's
[Focus implementation](https://github.com/tt-a1i/archify/blob/25cf37080fc8b1dbe758a4efc3935b55f3327083/viewer/focus.js#L57-L119)
and [viewer contract](https://github.com/tt-a1i/archify/blob/25cf37080fc8b1dbe758a4efc3935b55f3327083/viewer/README.md#export-contract),
observed October 25, 2026, under its
[MIT license](https://github.com/tt-a1i/archify/blob/25cf37080fc8b1dbe758a4efc3935b55f3327083/LICENSE).
The local implementation is documented in [interactive graphs](interactive-graphs.md).
Recheck a viewer's actual contracts before relying on different selection or export behavior.

## Provenance

This skill uses original prose and no upstream scripts, templates, fonts, or icons.
Its reference is [cathrynlavery/diagram-design](https://github.com/cathrynlavery/diagram-design),
observed October 10, 2026 at
[`7a2e22170ee838e859d8142ba825d83f8b6375e6`](https://github.com/cathrynlavery/diagram-design/tree/7a2e22170ee838e859d8142ba825d83f8b6375e6).
The upstream [MIT license](https://github.com/cathrynlavery/diagram-design/blob/7a2e22170ee838e859d8142ba825d83f8b6375e6/LICENSE)
names copyright 2025 Cathryn Lavery.

Adopted ideas: semantic fidelity, overview/detail splits, transformation ledgers, stable
identities, and verification of the delivered export. Local departures: compact procedures,
project-owned design choices, offline defaults, no shared profiles and an original local graph
renderer rather than imported upstream runtime. Recheck source and dependency licenses before copying upstream
material or adding imports, motion, remote assets, or executable helpers. Popularity and the
upstream pin are provenance, not evidence that a generated artifact passed validation.
