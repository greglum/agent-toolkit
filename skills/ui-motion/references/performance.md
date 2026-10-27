# Diagnose animation performance

Use for a reported performance defect. For a new continuous canvas or GPU effect without
a reported defect, inspect the lifecycle checks in step 3 and verify hide/restore/unmount
behavior; the diagnosis and before/after trace steps apply only to a reproduced problem.
Keep the requested audit or implementation mode.

1. **Capture the failing action.** Record browser and library versions, device, refresh
   rate, content size, and competing work such as navigation or hydration. Capture a trace
   or frame measurements before editing. A 60 Hz display allows about 16.7 ms per frame;
   120 Hz allows about 8.3 ms for all work. Desktop CPU throttling does not reproduce a
   phone's GPU or memory limits. Without reproduction, report hypotheses and missing evidence.
2. **Trace the driver and the cost.** Identify the actual animated properties and owner.
   Expand shorthands and `transition: all`; a library name does not establish its execution
   path. Use the recording to choose the next investigation:

   | Observation | Inspect |
   | --- | --- |
   | Stall during navigation or hydration | Long tasks and whether updates require a main-thread callback |
   | Cost grows with drawer or list content | Inherited custom-property updates, descendant style recalculation, and rendered node count |
   | Framework commits on each frame | State writes in pointer, scroll, or animation handlers; separate transient visual values from committed application state |
   | Frequent layout or paint | Affected subtree, animated dimensions, filters, shadows, and painted area |
   | Layer growth or visual jump at start | Layer allocation and promotion; a scoped hint is a candidate only after measurement |
   | Work continues while an effect is invisible | Offscreen/hidden-document suspension and whether a stopped frame loop can restart correctly |

   CSS and WAAPI can use the compositor for eligible animations; they do not guarantee it.
   Check installed-version behavior before replacing library shorthands with a transform
   string. Preserve every existing transform and percentage-based geometry.
3. **Preserve meaning when reducing cost.** Scaling changes the visual size of children,
   not document flow. It cannot replace an expanding panel when siblings must move.
   Opacity alone leaves invisible controls available to interaction; preserve the owning
   primitive's focus, hit-testing, accessibility, and mount/unmount lifecycle. Shadow and
   filter substitutions can change appearance. Keep layout animation when required and
   measured acceptable; optimize the demonstrated cost rather than banning a property.
   For effects that own a canvas or GPU resources, inspect both visibility suspension and
   teardown: cancel pending frames, disconnect observers, remove listeners, and release
   owned graphics resources. Suspend visual work only; hiding an effect must not cancel the
   underlying operation or prevent its authoritative completion. Unsupported rendering or
   a disabled effect must leave the meaningful content and actions usable.
4. **Prove the remedy.** Change the responsible layer, then repeat the same action, load,
   content size, and recording conditions. Keep hints such as `will-change` scoped and
   remove ones that do not help. Recheck interruption, reversal, reduced motion, and the
   semantic final state through [rendered review](rendered-review.md). Report the measured
   difference and remaining device coverage, not a universal frame-rate claim.

For attribution and browser/library references, see [sources](sources.md).
