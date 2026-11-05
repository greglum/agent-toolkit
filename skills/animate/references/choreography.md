# Coordinate a group

Read when one event moves several elements, including a stagger, a list removal, or a view
swap. Keep the existing purpose, frequency gate, tokens, state owner, and runtime.

1. Identify the element carrying the change, what supports it, and what can remain still.
   Check whether moving the container already communicates the change before also animating
   its contents. A second entrance needs a distinct purpose.
2. Choose the relationship: start together for one event; overlap when order helps explain
   the change; wait only when simultaneous content would conflict or obscure cause and effect.
   For shared-layout children, moving their existing container can supply the relationship.
   Neither a crossfade nor a sequential exit is the right default for every view swap.
3. Record element, trigger, start, duration, and dependency in a small timeline. The group's
   finish is the maximum of start plus duration across all elements, including finite repeats
   and child delays inside a moving parent. Assess continuing idle loops separately.
   Keep required actions available while supporting content arrives. Check
   the whole timeline against the project's budget, not each animation in isolation.
4. Reuse one timing family. Sync supporting effects to the event they explain, such as a
   click or arrival, rather than an unrelated earlier hover. A stagger's order should aid
   reading; variable delays are an optional treatment, not a correctness requirement.
5. Verify rapid repeat, reversal, and leaving mid-sequence. Superseded continuations must
   neither restart idle work nor commit stale state. Under reduced motion, remove nonessential
   group delays as well as travel, following the product's policy. Essential explanatory
   order can remain as static steps. Check normal speed after frame-by-frame diagnosis.

Done when the relationship explains the change, the group reaches the authoritative state,
and controls remain usable on normal, interrupted, and reduced-motion paths.

## Sources and limits

Original synthesis informed by [Emil Kowalski's choreograph](https://github.com/emilkowalski/skills/blob/c8a79627b59d72d764d6ab6f2c87c09a48169833/skills/choreograph/SKILL.md)
(MIT, copyright 2026 Emil Kowalski), observed November 4, 2026. No source recipe copied.
[Motion's presence modes](https://motion.dev/docs/react-animate-presence#mode) independently
document simultaneous, sequential, and layout-removal options. They are alternatives whose
applicability depends on geometry and the installed version, not a required dependency.
[W3C's interaction-animation guidance](https://www.w3.org/WAI/WCAG22/Understanding/animation-from-interactions)
supports disabling nonessential movement. These living references were read November 4,
2026; publication dates and redistribution rights were not established.

Departure: no universal ban on uniform stagger, no mandatory fade, fixed duration, duplicated
interactive view, or action gated by decorative completion. Recheck when the source, product
motion policy, lifecycle, or supported runtime changes. Static checks do not prove visual
quality or that this guidance improves agent outcomes.
