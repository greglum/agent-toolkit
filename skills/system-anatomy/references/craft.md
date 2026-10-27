# Craft and interaction

Use this when designing an interactive anatomy. The drawing should explain a mechanism at
normal size; close-up detail should reward inspection without becoming a completion quota.

## Translate content into a figure

Write a short mapping before geometry:

| Question | Useful visible relationship | Useful control |
| --- | --- | --- |
| What belongs to each responsibility? | Contained parts or labeled layers | Select a part to reveal its owner and contract |
| What changes an outcome? | Mechanism with a visible input and output | Change one input; update drawing and readout together |
| What blocks progress? | Explicit gate with waiting and rejected paths | Step through a synthetic scenario including a blocked state |
| How do parts fit together? | Assembled and separated views with stable identities | Expand, inspect, restore without losing the selected part |

Do not imply software runs in physical order merely because parts sit left to right. Use
labels to explain direction, ownership, concurrency and delayed completion. A pipe can imply
transport; a shared axle can imply coupling. Reject the metaphor if these implications conflict
with source. Unknown or absent evidence must remain visually distinct from success.

For a broad application, begin with an overview and a focused inspection panel. Do not put
every file or class into one mechanical scene. Reuse an existing architecture ledger and
link to technical detail; preserve the actual system and entity names across both views.

## Draw coherent volume

Use the destination's palette and type. Separate background, structural surfaces, main
subject, selection and actual status. A selected part is not automatically a healthy part.
Pair color with labels or shape. Keep explanatory text in readable screen space when a
perspective face would distort it.

For an isometric view, use one projection for geometry, connectors and anchor points. A
simple orthographic construction is sufficient for many figures: project horizontal world
axes diagonally in opposite directions, and vertical height upward. Compute shared corners
once. Changing camera or scale must transform every part and anchor consistently.

For a physical assembly, derive assembled, exploded and section views from the same part
inventory and model-space anchors. Zero explosion must restore mating contacts; intermediate
poses preserve insertion axes and quantities. Hatching represents cut solid material, not
empty passages. Explosion spacing is a display choice, never a measured dimension. Verify
corresponding features across views before polishing linework.

Paint far surfaces before near surfaces; split a wraparound shape if it straddles another
part. Transparent panels expose a chosen layer, not arbitrary hidden edges. Check the
assembled, separated and in-between poses because correct order at rest can fail in motion.
If many objects interlock, simplify the composition or use a fitting installed geometry tool
instead of growing an ad hoc 3D engine.

Use bevels, seams, supports, document edges, guide rails or instrument markings where they
help the reader recognize the subject. Connectors terminate on actual ports or marked anchors;
separate crossings from junctions. Consistent light direction and a restrained tone range
make volume legible. Glows, screws and texture are optional, never a substitute for structure.

## Keep interaction explanatory

For each control, specify input, changed state, visible result, accompanying text, reset
behavior and fallback. A good interaction resolves a question; moving parts for their own
sake do not. A part-selection panel can carry responsibility, source evidence and an honest
limitation. Give native controls accessible names and avoid a focus target for every decorative
part. Announce a concise changed result only when helpful; do not narrate every animation frame.

State is the authority. Animation interpolates its presentation; it does not independently
advance approvals, counters or calculated outcomes. Allow direct state selection under reduced
motion. Pause/resume and reset must not duplicate work, retain an old readout or lose focus.
When animation carries essential order, offer manual steps or an equivalent written sequence.

Keep the initial SVG and explanation in the document so blocked JavaScript still teaches
something. Disable or hide controls that cannot work without script. If the scene is too dense
at narrow widths, use a legible overview with a separately accessible detail view, or contain
necessary scrolling within the figure. Never shrink every label into illegibility.

## Acceptance examples

- A readout that says "ready" while a required derivative is pending is a semantic failure,
  even if the animation and screenshot look polished.
- A cutaway that hides an access guard behind a lifted layer loses meaning. Keep the guard
  in the explanation and any static export where that relationship matters.
- A rich surface with no meaningful control can be a valid static figure. Do not label it
  interactive or add an arbitrary slider to satisfy the word.
- A screenshot of a button does not establish its behavior. Exercise it and inspect the
  changed geometry, text, selected state and keyboard focus.
