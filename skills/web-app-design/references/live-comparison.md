# Compare live variants

Use when the question depends on interaction, timing or state changes. A screenshot board
cannot answer those questions. Use an available prototype skill for its UI variant workflow;
otherwise build the smallest experiment directly in the destination's existing framework.
This fallback is self-contained and does not require another installed bundle.

1. Freeze one question, the current baseline, content, viewport, theme, initial state and
   synthetic operation results. Change only the decision being compared. Reuse the real
   component and primitive owners so the comparison retains actual density and semantics.
2. Gate variants and controls behind the project's development-only mechanism. An unknown
   variant selects the baseline. Preserve unrelated URL parameters, router/history behavior
   and native widget keys; keyboard switching belongs only to the comparison control.
3. Provide an explicit replay action for a timing comparison. Reset only the experiment's
   owned state, pending callbacks and visual sequence to the same fixture. Keep replay focus
   on its control. Remount only a disposable isolated subtree with no unsaved user work or
   durable operation. Use inert synthetic mutations; replay must not repeat a real write.
4. Run each variant from that same starting state. Exercise primary actions, keyboard and
   touch paths where applicable, interruption and reduced motion. Compare at normal speed;
   use slow playback to diagnose a specific handoff. Measure geometry and run the existing
   accessibility checks for the comparison controls as well as the candidate surface.
5. Record the choice, fixture/source identities, observations and unrun conditions. Confirm
   the production build exposes neither the variants nor the comparison controls. Preserve
   the prototype until its recovery value is settled; implementing or publishing a preferred
   variant still follows the task's authority and production gates.

Done when the question has an evidence-backed answer or an explicit unresolved observation,
with repeatable replay and no production exposure. This is a procedural recipe, not a
bundled live-app generator or proof of skill effectiveness.

## Provenance

Original synthesis, observed November 4, 2026. Compared with [Emil Kowalski's prototype](https://github.com/emilkowalski/skills/blob/c8a79627b59d72d764d6ab6f2c87c09a48169833/skills/prototype/SKILL.md)
(MIT, copyright 2026 Emil Kowalski) and the available prototype skill's project-native UI
workflow. No picker code copied. Departure: no global arrow listeners, unbounded URL index,
mandatory variant count or production experimental route. Recheck on changes to the target
router, state owner, build gating or replay lifecycle; app/browser evidence remains task-specific.
