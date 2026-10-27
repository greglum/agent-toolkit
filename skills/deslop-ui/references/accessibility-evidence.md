# Accessibility evidence

For each accessibility claim in the scoped audit, record the surface, interaction state,
method, observation, and unresolved work. Reuse the existing UI matrix and evidence files.
A passing observation closes only the claim its method can establish in that state.

| Claim | Evidence that can support it | Still distinct |
| --- | --- | --- |
| Dialog has a programmatic name | DOM/accessibility tree and automated rule result while open | Focus containment, dismissal, and return |
| Keyboard can use and leave a widget | Keyboard actions and observed focus through its states | Assistive-technology announcements |
| Content fits and stays readable | DOM bounds and computed contrast at the tested viewport/theme | Reading order and zoom/reflow elsewhere |
| Screen reader announces a change | Observation with the named reader/browser in that state | Other reader/browser combinations |

A clean axe result is evidence for its executed rules, not every criterion. A closed dialog
scan says nothing about its open state. Driver calibration proves the driver; test the
product separately. Name unavailable manual checks and unvisited states instead of counting
those as passes. Preserve failed checks even when another method passes a different claim.
Recheck affected evidence after content, state, or revision changes.

Method labels are not certifications. Apply the repository's accessibility target and the
relevant standard; do not invent a universal tool-to-criterion mapping.

## Source

Informed by Microsoft HVE coverage at
[49dfb738](https://github.com/microsoft/hve-core/blob/49dfb73866f8c5f81bf734d6ca808dac25a2a330/.github/skills/accessibility/accessibility-coverage-matrix/SKILL.md),
observed October 10, 2026. Original local procedure; no HVE taxonomy or implementation copied.
HVE is MIT at root; its accessibility adequacy doctrine identifies CC BY 4.0. The narrower
local method keeps existing tools, state records, and manual limits. Recheck the source and
applicable standard before changing the method.
