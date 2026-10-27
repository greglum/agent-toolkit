# Rendered checks

Run the checks that apply to the changed surface in its requested conditions. The surface
table in [design synthesis](design-synthesis.md#fit-the-surface-to-its-job) names what each
kind of surface needs beyond a tidy screenshot.

- **Comprehension.** From the rendered content, identify the current object, what needs
  attention, and the next action. Check whether truncation, competing emphasis, or a hidden
  explanation prevents that reading. Compare with the baseline under the same content and
  viewport; visual novelty alone does not establish improvement. Label agent judgment as
  such rather than claiming user-tested comprehension.
- **Geometry.** Measure wrapping, overflow, alignment, and sticky/overlay geometry from the
  DOM. Exercise long labels, realistic row counts, and narrow widths where supported.
- **Accessibility.** Measure the composited contrast of each surface and text pair in use, in
  every theme, and report any pair under 4.5:1 for body text, even one the design contract
  specifies. Check visible focus. Run axe-core through the existing UI test setup or available
  browser tooling. Exercise keyboard navigation, overlay dismissal and focus return, forms, and
  primary actions; automated accessibility checks do not prove usability.
- **Pinned states.** To review hover, focus, active, disabled, loading, and invalid states side
  by side, extend the project's state selectors to also match a preview attribute and render a
  variant by state matrix. A state the contract says does not change stays visibly identical.
  Real pointer and keyboard checks still decide behavior.
- **Load position.** A fresh load starts at the top (`scrollY` 0) unless the route restores
  position by design; an offset points to a component that scrolls itself into view.
- **Motion and input.** Exercise the applicable normal and reduced-motion paths. Check touch
  or pointer input when those interactions are in scope; a small viewport alone does not prove
  touch behavior.
- **Matching a supplied image.** When the task is to match an image or mockup, measure it
  first, then record reference value, rendered value, delta, and pass, fix, or uncertain for
  each feature.
- **Performance.** Measure relevant performance when the change affects it, including any
  costly effect; a screenshot or use of transform/opacity does not prove smoothness or speed.
