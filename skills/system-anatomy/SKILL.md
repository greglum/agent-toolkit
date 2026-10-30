---
name: system-anatomy
description: Create a source-grounded interactive anatomy, cutaway, or isometric explainer of a system or mechanism. Use when parts, layers, and user-controlled state changes teach how it works. For ordinary architecture graphs use diagram-design; for timeline videos use motion-film.
compatibility: The optional offline slider-crank example builder needs Node.js 18+. Without Node, author the figure using the project's existing tools; the mechanism guidance does not require the bundled example or a graphics library.
---

# System anatomy

Build an explorable figure whose structure and behavior explain its subject. Deliver it
with source evidence, an understandable static view, and working controls. A visual metaphor
is an explanatory choice, not evidence that software has that physical structure.

## 1. Bind the subject and delivery

Read the destination's instructions, design tokens, documentation index, and existing work.
Identify the audience, the question they should be able to answer, and the output surface.
Inspect the current figure before changing it. Preserve unrelated edits. For an audit, report
findings and proposed fixes without editing the deliverables.

Trace the relevant implementation or supplied model before drawing. Record source revision,
material claims, owning paths/symbols, unknowns, and intentional simplifications beside the
artifact. Keep implementation, proposal, simulation and observed runtime evidence distinct.
Never obtain private records or call live systems merely to make the illustration realistic.
For a physical object, distinguish measured geometry from estimated proportions and unknown
interiors. A photograph or finish reference cannot establish hidden construction, dimensions
or tolerances. Label invented internals as illustrative. Keep fabrication deliverables with
a CAD/drafting workflow: identify missing authoritative dimensions, units, fits and standards
before handing off; never label this explanatory figure as fabrication-ready.

For a moving physical mechanism or calculated physical readouts, read
[mechanism modeling](references/mechanisms.md) before choosing inputs or drawing geometry.
It includes a runnable offline example; software metaphors do not need that branch.

Use the smallest fitting output: a standalone HTML figure with inline SVG and local controls,
or a component in an existing app when requested. Prefer native browser features and installed
project tools. New libraries, copied upstream kits and network resources are not prerequisites.
Keep ordinary architecture diagrams with `diagram-design`, and video delivery with `motion-film`.

**Ready:** the reader question, factual model, output and source owners are identified.

## 2. Make the subject determine the form

Read [craft and interaction](references/craft.md). Write a compact mapping: represented
entity, visible part, what the reader can do, and what the resulting change means. Include
where the metaphor stops being faithful. Choose a cutaway, exploded assembly, instrument,
workspace, or layered view only when it explains those relationships. If spatial treatment
adds no insight, use a simpler explainer and state that choice.

Derive materials, visual hierarchy and meaningful details from the content and project design
language. A queue might appear as a magazine of waiting items; an approval boundary must still
be identified as a human decision. Labels and callouts are welcome when they reduce guesswork.
A technical subject does not require an industrial machine, a medical subject does not require
a body illustration, and a large part count does not establish craft.

Give the main subject a coherent silhouette and one focal relationship. Use consistent
projection, thickness, light direction and support. Detail should reveal a role or behavior.
When a cutaway or isometric anatomy is requested, the figure must actually expose structure:
layers, connected parts, openings or a mechanism whose geometry explains the subject. A row
of cards with shadows and mechanical labels does not meet that brief. Keep the controls and
inspection panel outside the main illustration; judge the illustration before adding polish.
Separate explanatory parts from ornament; remove detail that obscures the mechanism. Keep
unchanged identities stable when switching layers or states. A lifted part remains associated
with its original place; separating it must not imply deletion, execution or a trust crossing.

**Ready:** the composition and interactions teach the question without inventing facts.

## 3. Implement one truthful state model

Define the meaningful states and transitions before wiring controls. Derive visible parts,
readouts, selected state and explanatory text from that same model. Distinguish user intent,
pending work, completed work and failure. Use clearly labeled synthetic scenarios when runtime
data is absent; never invent latency, completion percentages or throughput as factual readouts.

Start with the static assembled view, then add the smallest useful interaction: selecting a
part, exposing a layer, stepping a path, or changing a model input. Prefer native buttons,
radios, details and range inputs outside the drawing; support keyboard and touch as well as
pointer input. Provide selected-state and focus feedback. Descriptions must be available
without hover, motion, color recognition or reading tiny engraved text.

Keep the explanatory content available if script or graphics acceleration is unavailable.
The default standalone page works offline, without remote fonts, analytics or runtime fetches.
Use local, reviewed code for its controls; keep untrusted labels inert through textContent or
proper escaping, never executable HTML. Do not turn documentation controls into live actions.

For substantial animation, load `ui-motion` when available. Motion expresses a transition;
reduce it to immediate state changes under reduced motion. Make tours opt-in and pausable,
and stop loops when settled, hidden or offscreen. Use one time-based loop if a loop is needed.
Avoid frame-by-frame component rerenders. Use WebGL or true 3D only when the mechanism needs
it and the output scope supports it; retain a useful non-WebGL view.

**Ready:** every control produces its stated result and all displayed evidence agrees.

## 4. Finish and prove the artifact

Load and apply `deslop` to the language and `deslop-ui` to the actual rendered figure and
surrounding page, one skill invocation at a time. Keep the review limited to the requested
figure, states and sizes. Use available scanners on supported inputs; extract SVG text for
prose scans when necessary. A scanner skipping SVG proves nothing about its appearance.
If a skill/helper is unavailable, perform direct review and name that missing check.

Use `diagram-design` for any separate static architecture diagrams or presentation exports;
its source-fidelity and export rules apply to those artifacts, not as a ban on this figure's
local interactive controls. Use `frontend-design` and `web-design-guidelines` when building or
auditing a surrounding web surface. Do not copy their procedures into this skill.

Render the assembled view and every meaningful selected, expanded, failure and reset state.
Measure text bounds, overlap, page overflow, focus and contrast at the intended desktop size
and a narrow viewport. Run the available accessibility rig. Test actual keyboard/touch
controls, reduced motion, no-script content and offline requests. Verify evidence and labels
after each state change. A screenshot proves appearance, not interaction or accessibility.

Inspect the whole figure and close-ups of changed joints, edges and labels. Check occlusion
at both endpoints and intermediate poses of any exploded transition. For consequential work,
use a fresh reviewer with neutral questions: what does this teach, what is confusing, what
looks unsupported? Reconcile findings against source and pixels, then recheck affected states.
Keep the best version, not automatically the latest one. Do not award arbitrary quality scores.

Keep editable source, requested static exports and their build/capture instructions in the
repository's documentation location. A static export must include its subject, legend and
state; it cannot silently lose essential explanation that was only in a tooltip. Update the
source ledger, documentation links and actual verification record together. Run required
repository gates; no test suite or renderer migration is implied by this documentation work.

**Done:** deliver artifact links, meaningful design choices, source scope, and passed, failed,
unavailable and unrun checks. Report incomplete rendering or exports as incomplete. Local
creation does not authorize publication, deployment or live data access.

## Source

This is an original local workflow inspired by Anatomy and related explainer systems.
Read [provenance and boundaries](references/provenance.md) before importing or updating any
upstream implementation. No upstream geometry library, scripts or assets are bundled.
