# Mobile fit

Use when the supported surface runs on phones, tablets, or an installed web app. Extend the
existing fit matrix only with applicable mobile conditions; preserve audit mode and real data.

1. **Record the environment.** Identify browser/OS, orientation, browser or standalone
   display mode, and touch or mixed input. Separate desktop viewport emulation, simulator,
   and physical-device evidence. Keep unsupported or unavailable conditions explicit.
2. **Measure visible space.** Exercise browser chrome expanded and collapsed, then focus a
   fixture input to open the software keyboard. Record layout viewport size plus visual
   viewport width, height, offsets, and scale where available. The keyboard can shrink what
   is visible without resizing layout. Compare control bounds in the same coordinate space
   as the visible viewport; a passing document overflow check alone is insufficient.
   Check focused inputs, validation messages, fixed actions, sheets, and dismissal controls.
3. **Choose the height policy.** Use the product's existing viewport and safe-area owner.
   Decide whether the surface should track changing browser chrome or retain a stable
   height before choosing dynamic or small viewport units. Treat keyboard resizing as a
   separate browser-dependent behavior; changing `vh` to `dvh` is not proof of keyboard fit.
   For edge-to-edge layouts, inspect the viewport metadata and computed safe-area padding
   in each supported orientation. Preserve content spacing as well as the inset.
4. **Check input behavior.** Tap controls, then scroll and tap elsewhere to expose sticky
   hover styling. Confirm essential actions work without hover and press feedback remains
   visible. On mixed-input devices, check keyboard and pointer use too; a hover media query
   describes an input capability, not a device identity. Focus fixture inputs and record any
   unexpected viewport scale change and whether the view recovers on blur. Correct the
   responsible control styling rather than disabling user zoom.
5. **Check reachability.** Scroll focused content and bottom actions into view, dismiss the
   keyboard, and rotate where supported. Verify scroll position and usable space recover.
   Preserve zoom, text selection for content, and native scrolling. Scope touch and
   overscroll changes to the responsible gesture or scroll owner; test browser panning,
   pinch zoom, and cancellation when that policy changes. Visual press feedback must not
   move a semantic or destructive action from normal activation onto pointer-down.
6. **Report the actual proof.** Include viewport mode and keyboard/chrome state with each
   measurement. Restore the initial view state. Desktop resizing can establish responsive
   geometry; it cannot establish physical keyboard, safe-area, or touch behavior. If hardware
   is unavailable, finish source and emulated checks and leave those conditions unverified.

Read [sources](sources.md) for provenance and platform references when updating this method.
