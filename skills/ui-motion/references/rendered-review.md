# Rendered motion review

Use this for the running application after reading its own verification contract.

1. Record source/build revision, browser, viewport, palette, motion preference, relevant data,
   and the action that reaches each changed state. Reuse existing fixtures for controlled
   comparison. Source inspection, fixtures, and live behavior are separate evidence.
2. Use a visible or headless browser and record the page's visibility state. Background pages
   can suspend animation frames and stall a timeline at its current position. Verify progress
   before treating a stalled reading as a product defect. Exercise the real action at normal
   speed. Check pending, success, error/retry, and long
   content where they exist. Repeat or reverse it before the transition completes. Inspect the
   actual handoff, including outgoing content; endpoint screenshots cannot expose a blank
   intermediate state, delayed action, or stranded layer.
   For gestures, exercise the pointer/touch input, cancellation, snap/inertia policy, scroll
   arbitration, drag-versus-tap cancellation, and linked-visual tracking defined in
   [reference to interaction](reference-to-motion.md). Record the input and engine used;
   viewport emulation alone is not touch or physical-device proof.
   Leave and return to the owning surface during motion where its lifecycle can change, and
   for continuous effects exercise hide, restore, and unmount against the suspension and
   teardown rules in [performance diagnosis](performance.md).
3. Measure relevant element bounds before and after the action. Check scroll anchoring,
   trigger origin, clipping, layout shifts, and whether the settled content fits its pending
   space. Use computed styles to confirm that the intended token and reduced-motion rule won
   the cascade. Slow playback is useful for diagnosis, followed by normal-speed acceptance.
4. Check visible focus and contrast in the rendered states. Run axe-core through the existing
   accessibility rig; inspect keyboard dismissal, focus return, and screen-reader semantics
   separately where the changed component requires them. Automatic accessibility checks do
   not prove every interaction.
5. If performance is the reported defect, compare a trace or frame measurements under the same
   conditions before and after. Reserve claims about latency, dropped frames, or device behavior
   for measurements that actually establish them.

Keep audit output bounded to actionable findings: location, observed behavior, expected
behavior or owner policy, evidence, and the smallest fitting fix. A source risk is a lead until
the relevant rendering or interaction confirms it. Label inaccessible states and unrun checks.
