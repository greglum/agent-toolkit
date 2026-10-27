# 21. Aceternity UI

Observed: 2026-10-05. Depth: targeted web search, official homepage, Sidebar component, 3D Card Effect route, Pricing, Installation, and Licence. Public docs were readable; the guessed `/components/3d-card` route failed and the actual linked route was located. No installation, paid access, runtime audit, or performance test occurred.

Research method: searched `site:ui.aceternity.com components license pricing`, opened the official site, and followed the primary pages listed below.

## Purpose and useful evidence

[Aceternity UI](https://ui.aceternity.com/) offers React/Tailwind effects, animated components, marketing blocks, and templates. Its categories span parallax, backgrounds, cards, navigation, inputs, overlays, and some data display. It is useful for studying specific visual or motion treatments, especially on public-facing sections.

The sampled [Sidebar docs](https://ui.aceternity.com/components/sidebar) describe hover expansion, a mobile variant, dark-mode support, controlled open state, and an `animate` flag. They expose a shadcn registry installation route and component APIs. These concrete controls are more informative than the homepage's general polish claims. The [3D Card Effect](https://ui.aceternity.com/components/3d-card-effect) is another example of a targeted effect rather than a complete application design.

The [Pricing page](https://ui.aceternity.com/pricing) separates free components from annual, lifetime, and team access to premium blocks/templates. Prices, counts, and offers can change. Public preview access does not establish entitlement to premium source.

## Patterns and application fit

Consider Aceternity after deciding what an effect communicates. A stateful button can reinforce pending/success feedback; a subtle card emphasis can support selection; a sidebar transition can preserve spatial continuity. A parallax stack or pointer-following decoration often serves marketing personality rather than frequent data work.

For an operational app, first protect speed of understanding and input stability. Navigation should stay usable by keyboard and touch, and repeated actions should not wait for an animation. Hover expansion is a behavior to inspect carefully, not a default replacement for persistent labels. A small source adaptation to the existing sidebar may be simpler to own than importing a second navigation system.

Reference extraction should specify the trigger, affected property, duration or spring behavior, final state, and reduced-motion alternative. Also identify a static version that communicates the same information. If the visual treatment becomes unclear without animation, resolve the hierarchy before adding the effect.

## Reuse and integration

The [Licence page](https://ui.aceternity.com/licence) permits repeated use and modification for end products while prohibiting source/item redistribution, marketplace derivatives, and template resale. Third-party material can carry separate licenses. Its page is labeled for Pro while its overview refers broadly to items purchased or downloaded; this research does not infer a blanket MIT grant for all free snippets. Check the exact selected item's accompanying license before copying it into a project or redistributing it.

The [generic installation guide](https://ui.aceternity.com/installation) contains Tailwind initialization commands and suggests bypassing peer dependency checks. Meanwhile sampled component pages advertise newer Tailwind-based templates. Treat that as a version-sensitive area: follow the actual item's current package requirements, inspect registry dependencies, and diagnose conflicts rather than adopting bypass flags automatically. React/Next.js, Tailwind, and Motion assumptions must fit the repository.

## Skill use and checks

Route here for a justified effect or a compatible implementation candidate. Prefer adapting its visual idea to existing primitives. Purchases, new libraries, and design-system replacements need the applicable authority.

Analytical checks: hover-only access, focus visibility, motion preference, text clarity, GPU-heavy blur or canvas work, layout movement, and mobile touch behavior. “Responsive” and “production-ready” marketing does not substitute for local DOM, axe, or manual verification.

Recheck item licensing, dependency versions, premium entitlements, and animation behavior before adoption or updates.
