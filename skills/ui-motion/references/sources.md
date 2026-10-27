# Sources and adaptation

## October 23 studio and gesture review

The [studio round trip](visual-editors.md) records its Motion sources and limits.
[Motion's drag](https://motion.dev/docs/react-drag) and
[gesture guides](https://motion.dev/docs/react-gestures), plus
[Jakub Krehel's swipe example](https://jakub.kr/work/drag-gesture), support distinguishing
position-only snaps from inertia, preserving scroll ownership and checking tap cancellation.
Observed October 23, 2026; exact publication dates and redistribution rights not established.
No code, thresholds or prose copied. Generalize the interaction contract rather than imposing
a library or its defaults. Recheck when the gesture owner or installed runtime changes.

## Earlier reviews

Reviewed September 29, 2026. This skill is original guidance. No upstream prose, code, asset,
or design system is bundled. Read these sources when reviewing provenance or adapting an
upstream change; project design and accessibility policy remain the authority.

- [Emil Kowalski, animate](https://github.com/emilkowalski/skills/blob/d16ebe60d09a5ba2afcb7054ede9d0a10c9f6128/skills/animate/SKILL.md),
  [review-animations](https://github.com/emilkowalski/skills/blob/d16ebe60d09a5ba2afcb7054ede9d0a10c9f6128/skills/review-animations/SKILL.md),
  and [apple-design](https://github.com/emilkowalski/skills/blob/d16ebe60d09a5ba2afcb7054ede9d0a10c9f6128/skills/apple-design/SKILL.md).
  MIT. Adopt purpose, restraint, native-tool choice, token reuse, and interruption principles.
  Fixed curves, timing tables, universal spring use, and a mandatory reduced-motion fade are
  not portable product policies.
- Original working rules: settle geometry before motion, show truthful operation state, and
  reuse the tokens and primitives the project already owns. Repository paths, fixed
  durations, component libraries, and library bans stay with each project.

[Impeccable](https://github.com/pbakaus/impeccable) `d98b0be` (October 7, Apache-2.0) retired
a layout-transition rule after judges rated its findings harmless; the matching measurement
clause was cut here. Observed stutter is still profiled.

## October 11 performance review

Reviewed [Emil's animation-performance](https://github.com/emilkowalski/skills/blob/2d228630ba1446365f614a108cb8252f1feda202/skills/animation-performance/SKILL.md),
MIT, copyright 2026 Emil Kowalski. Adopted the diagnostic questions about concurrent work,
per-frame framework state, descendant style costs, and device evidence in original prose.
Kept them under this skill's existing performance owner, behind a conditional reference.

Cross-checked [Motion's performance guide](https://motion.dev/docs/performance) and
[MDN opacity](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/opacity)
on October 11, 2026. These are mutable technical references, not bundled text or code.
Departure: acceleration depends on the browser and actual driver; transforms cannot replace
required layout, and transparency cannot replace hiding semantics. No fixed blur budget,
universal property ban, runtime install, or blanket compositor guarantee was adopted.

Recheck when a source revision, project policy, rendering mechanism, or observed defect changes
the applicable rule. Source reading is not execution or proof of performance.

## October 7 UTC, October 6 Pacific, 2026 supplement

The [reference-to-motion guide](reference-to-motion.md) is original procedure. It draws on
[Emil Kowalski's comparison exercises](https://emilkowal.ski/ui/train-your-judgement),
[GSAP lifecycle guidance](https://github.com/greensock/gsap-skills/blob/aed9cfd3277740755f6bfc1155c7aa645403b760/skills/gsap-react/SKILL.md),
[scroll geometry guidance](https://github.com/greensock/gsap-skills/blob/aed9cfd3277740755f6bfc1155c7aa645403b760/skills/gsap-scrolltrigger/SKILL.md),
and [native transition fallback](https://developer.mozilla.org/en-US/docs/Web/API/Document/startViewTransition).
The named GSAP skill files are MIT; its runtime has separate terms. Generalize reference
measurement, lifecycle ownership, and functional fallback, while retaining the product's
engine, tokens, router, and accessibility policy.

[Motion Prompts](https://motionprompts.dev/developers/) informs the reference's mechanics
and conflict questions. Its [distribution license](https://github.com/VanguardiaAI/motionprompts-mcp/blob/main/LICENSE)
is PolyForm Noncommercial plus attribution. This skill links to the source without copying
its prompts, components, metadata, rules, or MCP. Gallery and asset links are optional discovery
routes with item-specific rights and access checks. No upstream bundle or installer was run.

## October 15 effect lifecycle review

[Paper Shaders shader mount](https://github.com/paper-design/shaders/blob/43cd68db79fa0b1759f72ffc941b3238e2a3954c/packages/shaders/src/shader-mount.ts)
(Apache-2.0) supplies concrete examples of offscreen/hidden-document suspension and explicit
frame, observer, listener, texture and program cleanup. Adapted the lifecycle questions in
original prose; no runtime or source copied. Local departure: visual suspension cannot stop
the application's durable operation, and rendering failure retains usable content. Recheck
on changes to the rendering owner or observed lifecycle defects; source reading is not a
performance benchmark.
