# Ten standards

Each standard states what is judged, how to recognize a miss, and whether that miss is
**Block** or **Fix**. **Polish** covers non-blocking cohesion, crossfade masking, stagger
tuning, and token consolidation.

The project's own motion system outranks every value here. Where a project has no tokens,
grade against these self-contained fallback bands:

- **Duration bands:** press feedback 100 to 160 ms; tooltip or small popover 125 to 200 ms;
  menu, select, or dropdown 150 to 250 ms (under ~300 ms); dialog, sheet, drawer, or toast
  200 to 400 ms (up to ~500 ms for large travel).
- **Curve bands:** entrance, exit, or input response uses strong decelerate
  (`cubic-bezier(0.23, 1, 0.32, 1)`); on-screen move or morph uses strong symmetric
  (`cubic-bezier(0.77, 0, 0.175, 1)`); sheet or drawer travel (`cubic-bezier(0.32, 0.72, 0, 1)`);
  color or hover (`ease`); constant motion (`linear`). Never use `ease-in` on an entrance or
  response.
- **Stagger:** 30 to 80 ms per item, capped so total duration does not delay content or block
  input.

## Standards and miss severity

1. **Justified.** Every motion names one purpose: feedback, spatial continuity, state
   legibility, bridging a jarring change, explanation, or delight on a rare moment. **Block**
   miss: motion with no valid purpose whose only effect is looking busy.
2. **Frequency-appropriate.** Constant-tier actions and keyboard shortcuts do not animate;
   frequent actions get near-instant feedback or nothing. **Block** miss: motion on a
   keyboard-shortcut or constant-tier action, or a frequent transition that delays repeated
   work.
3. **Responsive curve.** Entrances and responses to input decelerate and start fast. **Block**
   miss: `ease-in` or a slow-start curve on a deliberate entrance or input response.
4. **Short.** Input feedback, menus, and tooltips finish under about 300 ms; dialogs, sheets,
   drawers, and toasts under about 500 ms unless a deliberate reason is stated. **Block** miss:
   unjustified motion exceeding those thresholds.
5. **Physical origin.** Anchored overlays grow from their trigger; dialogs stay centered;
   nothing grows from a point. **Block** miss: `scale(0)` entrance, or a trigger-anchored
   overlay scaling from the wrong origin.
6. **Interruptible.** Rapidly triggered and gesture-driven motion retargets from the value on
   screen. **Block** miss: rapid-trigger motion that restarts (such as keyframes on toasts or
   toggles) or cannot be interrupted, a release violating its declared snap or inertia policy,
   or a canceled drag that commits an action. A position-only snap can deliberately ignore
   release velocity.
7. **Cheap to render.** Prefer `transform` and `opacity` (eligible for compositing, though the
   actual driver and browser decide). Layout animation is a measured exception, never replaced
   by scaling because scale does not move siblings. **Block** miss: `transition: all`;
   animating `top`, `left`, `width`, or `margin` with a simple transform equivalent and no
   measured need; updating an inherited custom property per frame to move many children; or a
   runtime shorthand whose installed version runs every frame on the main thread while busy
   (verify the version before claiming it). **Fix** miss: an animated transform that
   overwrites a layout transform.
8. **Accessible.** Reduced motion follows the project's contract; absent one, travel and
   scale go while short opacity or color changes carrying meaning stay. Hover motion is gated
   to `(hover: hover) and (pointer: fine)`. Focus stays visible and correct; opacity alone
   does not hide. **Block** miss: travel with no reduced-motion handling; motion that delays a
   semantic action, leaves hidden controls tabbable/clickable, or breaks focus; or persistent
   automatic motion (>5 s alongside other content) lacking its WCAG 2.2.2 pause, stop, or
   hide control ([W3C criterion and examples](https://www.w3.org/WAI/WCAG22/Understanding/pause-stop-hide.html),
   tested independently of reduced motion). **Fix** miss: ungated hover motion.
9. **Asymmetric where someone decides.** A deliberate phase (press and hold, destructive
   confirm) is slow; the system's answer is fast. **Fix** miss: symmetric timing on a
   press-and-hold, or a release as slow as the hold.
10. **Cohesive and owned.** Motion uses the product's tokens, matches its character (dense
    tool stays crisp; playful product can bounce more), shares one timing family, and lives
    in the component that owns the state. Its animations and listeners end with that owner.
    **Block** miss: an animation, listener, or completion that outlives its owner or
    overwrites newer state. **Fix** miss: hard-coded values where tokens exist, a parallel
    token set, an exit leaving by a different path than its entrance, or a stagger whose total
    time delays the last item noticeably. **Polish** opportunity: cohesion with character,
    crossfade masking, stagger tuning, or token consolidation.

When unsure whether motion feels right, the strongest recommendation is often to delete it.
When feel cannot be judged from source, say so and name the check: slow playback, frame
stepping, or a real device.

## Provenance

The standards adapt the review bar in Emil Kowalski's `review-animations`
([emilkowalski/skills](https://github.com/emilkowalski/skills/blob/2d228630ba1446365f614a108cb8252f1feda202/skills/review-animations/SKILL.md),
MIT License, Copyright 2026 Emil Kowalski; observed October 11, 2026, verified against the
catalog notice on November 20, 2026) in original prose, with fallback bands aligned to the
same revision. Local departures: acceleration is conditional on driver and browser; scale
cannot replace layout; opacity cannot replace hiding semantics; the project's motion system
outranks fixed values; lifecycle ownership is a standard of its own. Recheck when the
project's motion standards or upstream skill revisions change.

The gesture distinction was checked against [Motion's drag guide](https://motion.dev/docs/react-drag)
and [Jakub Krehel's swipe example](https://jakub.kr/work/drag-gesture), observed October 23,
2026. No upstream code, thresholds or article prose copied. Publication dates and article
redistribution rights were not established. Local departure: review the product's gesture
contract rather than imposing either example's physics. Recheck when the gesture primitive
or upstream drag guides change.
