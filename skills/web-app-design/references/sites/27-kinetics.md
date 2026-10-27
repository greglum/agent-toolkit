# 27. Kinetics

**Observed:** 2026-10-05. **Research depth:** targeted searches including `site:kinetics.colorion.co React motion effects license`, official gallery and its embedded CSS/React samples, physics/about sections, and first-party GitHub README. Public text was accessible. No browser, accessibility, or performance testing was performed.

## What it offers

Kinetics is a motion-pattern library for developers. The observed gallery advertised 153 examples with live previews, CSS, React, and prompt views. Its controls expose stiffness and damping as a way to discuss motion. This makes it useful when a team knows which interaction needs polish but needs a concrete starting point. [Official gallery](https://kinetics.colorion.co/)

The repository describes a static Astro site whose effect markup, demo JavaScript, and styles are separate from the displayed React snippets. Studying the site's own implementation and adopting a displayed snippet are different workflows. Its README identifies external Google Fonts and suggests self-hosting them when external requests are unwanted. [Source and architecture](https://github.com/ckissi/kinetics)

## Useful patterns and fit

For working applications, inspect expansion feedback, toast arrival, progress transitions, focus cues, and changes in numeric values. For marketing pages, magnetic buttons, layered cards, text effects, and decorative depth can supply stronger visual character. Choose a pattern because it clarifies a state change, keeps context, or helps the next action feel responsive. Do not add every attractive effect to the same screen. [Pattern gallery](https://kinetics.colorion.co/)

The physics language needs care. Observed examples often use a fixed-duration cubic Bézier curve to approximate a spring. That does not establish velocity-preserving spring simulation. The card-resize sample animates `height`; that property can cause layout work even though the description emphasizes avoiding JavaScript measurement. Assess the actual implementation rather than adopting the site's performance wording. [Observed code and physics section](https://kinetics.colorion.co/#physics)

## Integration, access, and rights

The site describes copy-paste use without an animation-library dependency. Individual React samples still require the relevant React hooks and integration with the host app. No paid gate was observed for the public gallery. [About section](https://kinetics.colorion.co/#about)

The footer labels the patterns MIT licensed. However, the inspected repository listing did not expose a license file, and the expected `LICENSE` path returned 404. Treat this as an incomplete rights record: verify the actual notice and its scope before copying substantial code, and preserve the notice when reuse is permitted. A public GitHub repository alone does not settle that question. [License statement](https://kinetics.colorion.co/#about), [repository](https://github.com/ckissi/kinetics)

## Use in the design skill

Use Kinetics late in the design pass, after structure, typography, and states work. Record the selected effect, its purpose, the simplest implementation in the existing stack, and the reduced-motion alternative. Prefer an existing app motion primitive or CSS transition when it fits.

**Analytical checks, not measured findings:** clickable `div` or `span` snippets need native control semantics; hover behavior needs keyboard and touch equivalents; toasts need suitable announcements; animated progress must retain truthful values. Check interrupted interactions, timer cleanup, rapid input, focus visibility, reduced motion, and layout cost. Recheck the catalog, license record, and actual snippet whenever adopting code or changing motion dependencies.
