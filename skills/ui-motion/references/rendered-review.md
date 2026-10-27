# Rendered motion review

Use this for the running application after reading its own verification contract.

1. Record source/build revision, browser, viewport, palette, motion preference, relevant data,
   and the action that reaches each changed state. Reuse existing fixtures for controlled
   comparison. Source inspection, fixtures, and live behavior are separate evidence.
2. Use a visible or headless browser: a hidden or background tab renders no frames, so
   transitions stay at time zero and timings read as stuck. Exercise the real action at normal speed. Check pending, success, error/retry, and long
   content where they exist. Repeat or reverse it before the transition completes. Inspect the
   actual handoff, including outgoing content; endpoint screenshots cannot expose a blank
   intermediate state, delayed action, or stranded layer.
   For gestures, exercise the relevant pointer/touch input and cancellation path. Check the
   declared threshold and snap behavior, page scrolling, drag-versus-tap cancellation, and
   equivalent actions without dragging. A deliberate position-only snap needs no inertia.
   Record the input and engine used; viewport emulation alone is not touch or physical-device proof.
   Leave and return to the owning surface during motion where its lifecycle can change.
   Check that callbacks and handlers do not duplicate or commit a stale result after return.
   For continuous effects, hide and restore the surface, then unmount it. Verify suspended
   visual work resumes once and teardown releases its resources; underlying operations must
   still complete independently of visual visibility.
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
