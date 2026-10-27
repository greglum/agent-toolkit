# 25. SmoothUI

Observed: 2026-10-05. Depth: targeted web search, official homepage, Getting Started, Accessibility matrix, GitHub repository, and MIT license. Public docs were readable. No CLI/API request beyond browsing, component install, code execution, purchase, or independent accessibility/performance measurement occurred.

Research method: searched `site:smoothui.dev docs installation license`, opened the official site, and followed the primary pages listed below.

## Purpose and useful evidence

[SmoothUI](https://smoothui.dev/) provides animated React components, blocks, and starter pages in the shadcn ecosystem. Its homepage names Motion and GSAP and includes functional UI such as tabs, popovers, inputs, buttons, and expandable cards alongside decorative orbs and landing sections.

The observed [Getting Started guide](https://smoothui.dev/docs/guides/getting-started), updated September 19, 2026, requires Node 18.17+, React 19+, and Tailwind 4+. It describes initializing shadcn, adding components through its own CLI or the shadcn registry, and copying components into the project with required dependencies. This is a strong compatibility filter for existing apps on older versions.

The [Accessibility guide](https://smoothui.dev/docs/guides/accessibility) publishes a component matrix for keyboard behavior, semantics, announcements, and reduced motion, including overlays, controls, navigation, forms, and decorative content. It describes using Motion's reduced-motion hook and names VoiceOver/NVDA testing. These are first-party claims and documented expectations. This research did not reproduce their tests or verify every source component against that matrix.

## Patterns and application fit

The most useful area for working apps is state-linked motion: tab indicators, expandable detail, copy feedback, and instant reduced-motion alternatives. Those patterns can make state changes easier to track without requiring a new visual theme. Decorative Siri-style orbs or a Dynamic Island presentation should have a defined purpose before becoming permanent UI.

Use the matrix as a review plan. If adopting a popover, write down the expected trigger announcement, dismissal, focus route, and reduced-motion behavior. Then verify the adapted component in our app. A published matrix is useful because it makes promises explicit; it does not transfer acceptance evidence across themes, content, wrappers, or versions.

Consider ownership before installing. Copied source gives control but requires deliberate maintenance. A second set of buttons or form inputs may be less coherent than extending the current primitives with a modest transition. Check whether existing Motion or CSS already expresses the desired effect.

## Rights, tools, and access

The official [repository license](https://github.com/educlopez/smoothui/blob/main/LICENSE) is MIT and requires notice preservation. Third-party code, icons, fonts, images, and separate products still require their own rights check. The homepage calls some blocks premium while also positioning the project as free/open source; entitlement for any particular block or template should be verified rather than inferred from a general label.

The homepage advertises MCP support, a public search/source API, machine-readable catalog formats, and a separate UI Craft product. Availability does not authorize installing these tools, replacing the current design system, transmitting project source, or importing their skills. No such action occurred here. Review any registry manifest and file/dependency changes before adopting a component.

## Skill use and checks

Route a compatible React/shadcn app here for purposeful motion references. Preserve repository tokens and primitives. Treat its accessibility matrix as a set of claims to validate, and compare the current implementation with an instant/static equivalent.

Analytical checks: React/Tailwind version fit, focus restoration, long-content layout, disabled/pending behavior, reduced motion, overlapping animation engines, and sustained frame cost. No passing runtime audit is claimed.

Recheck version prerequisites, exact component source, matrix revision, API/registry behavior, and rights before installation or updates.
