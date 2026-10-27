# 24. Uiverse

Observed: 2026-10-05. Depth: targeted web search, public homepage, contribution guidelines, one author-attributed loader, Galaxy repository license, and linked Terms viewer. Public gallery pages were readable; the Terms viewer returned an effectively empty text page. No element was executed, installed, or tested for accessibility or performance.

Research method: searched `site:uiverse.io license terms UI`, opened the official site, and followed the primary pages listed below.

## Purpose and useful evidence

[Uiverse](https://uiverse.io/) is a community collection of small UI elements, with browsing for buttons, cards, inputs, loaders, switches, tooltips, forms, and patterns. The homepage advertises HTML/CSS, Tailwind, React, and Figma copying options. This is useful for a bounded element treatment rather than planning a complete application layout.

The [submission guidelines](https://uiverse.io/guidelines) encourage hover/focus/active states, scoped CSS, proportional sizing, contrast, and sensible grouping. They prohibit JavaScript, global document styling, and external images/fonts/files in submissions. These constraints make the gallery different from a full-featured React widget library. A generated React export does not establish a complete state or accessibility contract.

The sampled [alexruix loader](https://uiverse.io/alexruix/tame-fly-42) identifies its creator, HTML/CSS format, date, tags, and an author-specific MIT notice. That is meaningful provenance to retain if the element is selected. Its visible view count is popularity evidence, not evidence that it improves a user's task.

## Patterns and application fit

Use the gallery for an isolated affordance: a clear press state, compact progress presentation, a restrained background, or a field treatment that supports labeling. Search by the element's function before a style label. Terms such as glassmorphism or neon can produce many interesting effects without narrowing the actual interaction problem.

For a working app, add the operational contract yourself. A CSS loader needs a real pending condition, useful status text, and a defined failure path. A styled checkbox needs a native input, a label, and correct state handling. A tooltip that only reacts to hover cannot carry essential instructions. Those are application design decisions beyond the gallery image.

Reference extraction should name what is useful about the treatment and what needs replacing. Keep the project token names, form primitive, and focus rules. Often only the spacing, border treatment, or interaction feedback should transfer. Avoid importing several unrelated elements with incompatible scales and palettes.

## Rights, access, and integration

The homepage says UI elements are MIT licensed and free for personal/commercial use. The sampled item carries its own creator notice, and the [Galaxy repository license](https://github.com/uiverse-io/galaxy/blob/main/LICENSE) is MIT. Preserve the correct author and permission notices for copied code. These grants concern the software/UI elements, not a blanket right to all site branding or unrelated assets.

The linked [Terms viewer](https://app.termly.io/policy-viewer/policy.html?policyUUID=bdc0e7cf-cb88-4f24-9cb5-13761e20dedb) could not be substantively inspected in text retrieval; current general service terms remain unverified. Public browsing was available, while commenting/creating variations exposed login links. Dependencies vary by chosen export. CSS-only reference adaptation may require none; inspect any framework export before adopting it.

## Skill use and checks

Route small element polish here after checking existing primitives. Store source links and original interpretation rather than building a mirrored gallery or generic style pack.

Analytical checks: native semantics, labels, focus/active contrast, disabled state, scalable dimensions, CSS leakage, loading announcements, and animation preferences. Moderation guidance does not certify every element.

Recheck the selected item's author/license, export format, service terms when needed, and actual rendered behavior before reuse.
