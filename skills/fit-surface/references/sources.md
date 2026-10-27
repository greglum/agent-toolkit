# Sources and adaptation

Reviewed October 7, 2026. This skill is original guidance. No upstream prose, code, or asset is
bundled. Read these sources only when reviewing provenance or adapting a later change; the
target repository's design owner remains the authority.

Original working rules, written October 7, 2026:

- Derive the supported range, design target, floor, and height budget from the design owner.
  Chrome changes the box without changing the viewport. Reserve the scrollbar gutter.
- Use a state matrix, reach states without touching real data, report each state as covered,
  skipped, or unreachable, and watch for the observation traps.
- Common failures these rules prevent: declared column widths that sum to a floor a few
  pixels wider than a laptop box; columns that give way below a container width, so each
  hidden fact must stay reachable elsewhere; a width budget that forgets the page scrollbar;
  a scrollbar and a result-sized panel that move the page on each keystroke; and fixed
  trailing columns that push totals off screen.

Local departures: no viewport numbers, paths, commands, harness names, component names, or
library recipes. The skill discovers each value from the target repository.

## October 11 mobile review

Reviewed [mobile-native](https://github.com/emilkowalski/skills/blob/2d228630ba1446365f614a108cb8252f1feda202/skills/mobile-native/SKILL.md)
and [break-ui](https://github.com/emilkowalski/skills/blob/2d228630ba1446365f614a108cb8252f1feda202/skills/break-ui/SKILL.md),
MIT, copyright 2026 Emil Kowalski. The worst-case content method was already covered by
the state matrix. Added original guidance for browser chrome, keyboard, safe areas, and
physical-device evidence to the existing box-measurement workflow.

Cross-checked [MDN VisualViewport](https://developer.mozilla.org/en-US/docs/Web/API/VisualViewport)
and [touch-action](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/touch-action)
on October 11, 2026. These are mutable technical references, not bundled text or code.
Departures: no mandatory fixture toggle, global mobile CSS reset, zoom suppression, or
claim that dynamic viewport units alone solve keyboard occlusion. An unknown field limit
is an evidence gap; a supported value causing a rendered failure establishes the UI defect.

October 25, 2026 refinement: re-read the same pinned mobile-native source's hover and input
focus sections. Added explicit tap/hover and viewport-scale probes to mobile fit. Cross-checked
[MDN hover](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/At-rules/@media/hover)
and [WAI Resize Text](https://www.w3.org/WAI/WCAG21/Understanding/resize-text).
These mutable references support capability-based checks and preserving zoom, not a universal
input font size, global reset, or proof of mobile behavior from desktop emulation.

Recheck when a source revision changes these rules, when a target repository reports a
false finding the traps should have caught, or when browser scrollbar behavior changes.

## October 11 component stress review

Reviewed Jakub Krehel's [break](https://github.com/jakubkrehel/skills/blob/c0588bb6d654eb725046f0bf9deec338c34891ab/skills/break/SKILL.md),
[scenario axes](https://github.com/jakubkrehel/skills/blob/c0588bb6d654eb725046f0bf9deec338c34891ab/skills/break/scenarios.md),
and [state-machine](https://github.com/jakubkrehel/skills/blob/c0588bb6d654eb725046f0bf9deec338c34891ab/skills/state-machine/SKILL.md).
MIT, copyright 2026 Jakub Krehel. Original local guidance adopts applicability-based case
selection, sibling pressure, fixture-delivery verification, and stable pending states. No
upstream text or implementation is bundled.

Departures: use an existing harness first, retain DOM measurements and affected-state rechecks,
and follow the requested audit or edit scope. No mandatory scratch route, full suite import,
fixed 320px product floor, or one-look limit. Recheck if fixture plumbing hides failures or
upstream changes the scenario method.
