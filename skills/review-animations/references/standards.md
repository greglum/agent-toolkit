# Ten standards

Each standard states what is judged and how to recognize a miss. The project's motion system
outranks any number here; where it has none, the `animate` skill's fallback defaults are the
reference.

1. **Justified.** Every motion names one purpose: feedback, spatial continuity, state
   legibility, bridging a jarring change, explanation, or delight on a rare moment. A miss:
   motion whose only effect is to look busy, often on a surface seen many times a day.
2. **Frequency-appropriate.** Constant-tier actions and keyboard shortcuts do not animate.
   Frequent actions get near-instant feedback or nothing. A miss: a command palette, shortcut,
   or tab switch that makes the user wait on a transition they trigger all day.
3. **Responsive curve.** Entrances and responses to input decelerate and start fast. A miss:
   `ease-in` or a weak built-in curve on a deliberate entrance, so the first frames barely
   move.
4. **Short.** Input feedback, menus, and tooltips finish under about 300 ms; dialogs, sheets,
   drawers, and toasts under about 500 ms. Longer needs a stated reason. A miss: a 400 ms
   dropdown that makes every menu feel heavy.
5. **Physical origin.** Anchored overlays grow from their trigger; dialogs stay centered;
   nothing grows from a point. A miss: a menu scaling from its own center, or a `scale(0)`
   entrance that appears out of nowhere.
6. **Interruptible.** Rapidly triggered and gesture-driven motion retargets from the value on
   screen. A miss: keyframes on toasts or toggles, so a second trigger snaps back to the start;
   a release that violates its declared snap or inertia policy, or a canceled drag that
   commits an action. A position-only snap can deliberately ignore release velocity.
7. **Cheap to render.** Prefer `transform` and `opacity`. They are eligible for compositing,
   not guaranteed it; the actual driver and browser decide. Layout animation is a measured
   exception, never a substitute removed by scaling, because scale does not move siblings. A
   miss: animating `top`, `left`, `width`, or `margin` where a transform would do; updating an
   inherited custom property each frame to move many children; a runtime shorthand whose
   installed version runs every frame on the main thread while the page is busy (check the
   version before claiming it).
8. **Accessible.** Reduced motion follows the project's contract; absent one, travel and
   scale go and short opacity or color changes that carry meaning stay. Hover motion is gated
   to fine pointers. Focus stays visible and correct through the motion. Opacity alone does
   not hide: transparent controls still receive clicks and focus. A miss: a sheet that still
   slides with reduced motion on; a faded-out menu whose items remain tabbable.
9. **Asymmetric where someone decides.** A deliberate phase (press and hold, a destructive
   confirm) is slow; the system's answer is fast. A miss: a hold-to-confirm whose release
   takes as long as the hold.
10. **Cohesive and owned.** Motion uses the product's tokens, matches its character (a dense
    tool stays crisp; a playful product can bounce more), shares one timing family, and lives
    in the component that owns the state. Its animations and listeners end with that owner.
    A miss: one-off curves scattered through components; two simultaneous motions fighting
    for attention; a completion callback that fires after unmount.

When unsure whether motion feels right, the strongest recommendation is often to delete it.
When feel cannot be judged from source, say so and name the check: slow playback, frame
stepping, or a real device.

## Provenance

The standards adapt the review bar in Emil Kowalski's `review-animations` (MIT,
`emilkowalski/skills` at `2d22863`) in original prose. Local departures: acceleration is
conditional on driver and browser; scale cannot replace layout; opacity cannot replace hiding
semantics; the project's motion system outranks fixed values; lifecycle ownership is a
standard of its own.

The gesture distinction was checked against [Motion's drag guide](https://motion.dev/docs/react-drag)
and [Jakub Krehel's swipe example](https://jakub.kr/work/drag-gesture), observed October 23,
2026. No upstream code, thresholds or article prose copied. Publication dates and article
redistribution rights were not established. Review the product's gesture contract rather than
imposing either example's physics.
