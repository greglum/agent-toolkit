# Visual composition

Use for diagrams that must communicate in a presentation or stand alone in documentation.
The design should make relationships easier to understand before it makes the page attractive.

## Choose the visual argument

Write one sentence the audience should remember. Identify the object, boundary or relationship
that carries it, then choose a structure that makes that meaning visible:

| Reader's question | Useful structure | What the geometry should explain |
| --- | --- | --- |
| How does input become a useful result? | Transformation spine with outcome branches | Order, the important transformation and different outputs |
| Who owns each responsibility? | Responsibility lanes or nested domains | Ownership and allowed crossings, not an arbitrary component grid |
| What waits, retries or needs a person? | State/process flow with exception routes | Conditions, pause points and where execution resumes |
| What permits protected access? | Request path with explicit gates and stop paths | The guard at each crossing and the outcome of rejection |
| What changed? | Aligned before/after or a focused delta | Stable identities and changed relationships |

These are choices, not templates. A small graph may need only labels and lines. Do not force
a tiny diagram into lanes, invent a boundary to fill space, or use storage and actor symbols
for components that do not have those roles.

## Establish hierarchy before detail

- Give the visual argument one focal point. Use scale, position, surrounding space or a
  stronger surface for the important decision. Several equal accents cancel the hierarchy.
- Preserve the system or capability name alongside a takeaway headline so the detached
  export retains its scope.
- Use a clear type ladder: takeaway, group/role, node name, short supporting annotation.
  Judge legibility at the actual projected or embedded size, not only the source canvas.
- Size regions by their information and importance. Align related elements and share
  spacing intervals, but do not make unlike roles look equivalent just to complete a grid.
- Start with a sparse main path. Move implementation explanations to the companion text
  or a detail view instead of shrinking all labels to fit more copy.
  Keep a condition that changes whether an edge can be followed on that edge or its gate;
  a supporting card cannot qualify an otherwise unconditional path.
- Use negative space for grouping and connector routing. Empty space should reveal structure;
  a large unused middle with cramped perimeter labels usually indicates a weak layout.

## Encode meaning consistently

Position and grouping are the strongest encodings. Use restrained supporting distinctions:

- A document silhouette can identify a source artifact; a storage primitive can distinguish
  durable state; an explicit gate can emphasize a decision. Ordinary services can remain
  simple labeled regions. Choose a small vocabulary and provide a key if it is unfamiliar.
- Use icons only when they shorten recognition or replace repeated labels. Match their
  stroke, scale and alignment. Do not decorate every node with unrelated pictograms.
- Assign color to a role, such as a control boundary or active path. Keep state text or shape
  cues so the meaning survives grayscale. Do not invent a second product palette.
- Reserve connector corridors before placing labels. Show arrow direction clearly; keep
  labels near the edge they describe and avoid long detours, tangencies and accidental joins.
  A junction means a relationship. Use a visible junction only when that relationship exists.
- Distinguish containment, flow and dependency. A background region should not look like a
  process node. Repeated card borders can obscure grouping and make an architecture diagram
  read like a dashboard; remove borders that do no semantic work.

Keep the executive view focused on responsibilities and consequences. Technical views can
carry contracts and failure paths, using the same identities and semantic encodings. Shared
branding does not require every view to have the same layout.

## Review the rendered composition

Check these against the pixels and the source ledger, not the author's description:

1. **Takeaway:** at a reduced overview size, can a reader locate the main idea and start point?
   A page of equal boxes with no primary relationship fails this check even if every label fits.
2. **Structure:** do grouping, position and size explain responsibility, sequence or hierarchy?
   Removing color should preserve the essential relationships.
3. **Reading effort:** can the main route be followed without backtracking through unrelated
   edges? Do supporting labels stay subordinate and legible at the intended viewing size?
4. **Finish:** inspect optical alignment, padding, type rhythm, icon consistency, arrowheads,
   junctions and connector clearance. Geometric checks catch collisions; visual inspection
   catches awkward near-misses and misleading emphasis.
5. **Fidelity:** did simplification or emphasis hide an exception, imply an unsupported
   guarantee, or turn an implementation detail into the main message? Restore the meaning.

For consequential presentation work, use a fresh visual critique when available. Ask what the
viewer understands first, what is confusing and which specific changes would help; do not
prime the reviewer with the intended praise or a self-assigned quality score. Resolve material
findings and inspect the revised export. Record unavailable checks and subjective limits.

Do not claim professional quality from file generation, a clean linter, added color or an
arbitrary numerical score. Report the design decisions, observed improvements and actual
verification. No single style is professional for every audience.

## Basis

This original local guidance extends the source-grounded procedure using the
[Diagram Design reference](fidelity.md#provenance), the source systems linked in the
[visual profile](visual-profile.md), and a user review of the first clinical
application diagrams. This reference owns visual composition and critique; interactive graph
machinery lives in its own reference. No upstream templates or assets were copied. Recheck when a different
diagram type or audience exposes a concrete readability or semantic failure.
