# 29. Liquid Glass by Sam Asante

**Observed:** 2026-10-05. **Research depth:** targeted searches including `site:glass.samasante.com glass components code`, demo/docs/examples URLs, first-party README, browser support document, package metadata, and public API comments. The demo's direct text extraction was empty; indexed official text and repository content supplied the details. No visual or runtime tests were run.

## Purpose and fit

This resource provides a headless React `Glass` primitive for optical refraction, plus source examples for a slider, switch, notification, context menu, and video controls. It is a material effect and interaction implementation resource, not a full design system. The README says finished examples are code users can own and restyle. [Project README](https://github.com/samasante/liquid-glass), [examples page](https://glass.samasante.com/?view=examples)

Its strongest fit is a small, branded media control or a restrained floating surface over imagery. A normal settings form, dense table, or critical status message often needs a stable opaque surface instead. That is a design judgment: the glass appearance should support a chosen visual direction without compromising legibility or implying that every control needs an optical effect.

## Browser behavior and integration

The implementation has materially different modes. Source comments say a bare material wrap can bend arbitrary live content behind it in Chrome/Edge, while other engines receive frost, tint, and highlights. Explicit geometry can refract wrapped content across engines. A `refract` node supplies a copy to bend; video/canvas modes use one WebGL renderer for multiple lenses. These distinctions narrow the broad cross-browser language on the landing page. [Public API comments](https://github.com/samasante/liquid-glass/blob/main/src/index.ts)

The browser document describes SVG displacement filters, Safari-specific handling, content-size limits, and GPU cost for many or large lenses. It reports upstream Playwright checks in Chromium and WebKit, and lists Firefox support. Those are maintainer statements, not verification performed for this research or for a future app. It recommends frost-only treatment for very wide panels. [Browser support and limitations](https://github.com/samasante/liquid-glass/blob/main/BROWSERS.md)

Package metadata identifies `@samasante/liquid-glass`, React as the peer, and no runtime dependencies. The docs describe React 18+ and no required provider or stylesheet. A future adoption should check the installed React version, current package release, server/client boundary, and use of WebGL before adding it. No paid access requirement was observed in the public package/docs. [Package metadata](https://github.com/samasante/liquid-glass/blob/main/package.json), [official docs](https://glass.samasante.com/?view=docs)

## Rights and future skill use

The project declares MIT licensing. Preserve its copyright and permission notice for substantial copied code. Review image/video rights separately; the component license does not license a wallpaper or a brand mark. The project credits earlier glass techniques and disclaims affiliation with Apple. [License and acknowledgements](https://github.com/samasante/liquid-glass)

Use this resource when the chosen brief calls for a glass treatment. Prototype one content-sized instance with an opaque fallback. Preserve real input semantics and crisp foreground text, then inspect the exact modes across required browsers.

**Analytical checks:** contrast over variable backgrounds, duplicate accessible content from copied nodes, focus rings, keyboard drag alternatives, touch targets, reduced motion, GPU/context failure, and low-end device frame cost. Recheck browser documentation, source-mode behavior, example accessibility, asset rights, and package compatibility before shipping. A screenshot alone cannot confirm these conditions.
