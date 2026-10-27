# 30. Anime.js

**Observed:** 2026-10-05. **Research depth:** explicit search for `site:animejs.com documentation license accessibility`, official homepage, current documentation index, scope/media-query and text documentation, easing editor, first-party source and license. Public pages were accessible. No library was installed or benchmarked.

## Purpose and capabilities

Anime.js is a JavaScript animation engine. Its official site presents timelines, staggering, SVG drawing/morphing/path tools, draggable interactions, scroll coordination, scopes, springs, and a Web Animations API lane. It can animate DOM/CSS properties, SVG, and JavaScript objects. This is an execution tool for deliberate motion, rather than a collection of finished product layouts. [Homepage](https://animejs.com/), [source README](https://github.com/juliangarnier/anime)

The current documentation is organized around individual APIs and includes layout, text, events, and adapters alongside the core animation tools. Read the documentation matching the installed version; the first-party repository points users migrating from v3 to a separate migration guide. Do not combine old tutorial syntax with a new package import. [Documentation index](https://animejs.com/documentation), [version guidance](https://github.com/juliangarnier/anime)

## Patterns worth borrowing

Working apps can use a short timeline to relate a user's action to a resulting state, animate an SVG diagram, or coordinate a compact guided transition. Marketing experiences can justify richer staged reveals, animated illustrations, or scroll-linked composition. The easing editor offers a way to preview and export easing choices rather than guessing from names. None of these capabilities prove that added motion improves task completion. [Easing editor](https://animejs.com/easing-editor)

Scopes accept media-query conditions and expose current matches, which creates an implementation point for responsive and reduced-motion alternatives. The text utility describes splitting and wrapping lines, words, and characters with accessibility options. Those facilities need correct application use; they do not eliminate the need to check the accessible reading order or user preference. [Scope media queries](https://animejs.com/documentation/scope/scope-parameters/mediaqueries), [text splitting](https://animejs.com/documentation/text/splittext/)

## Integration, access, and rights

Anime.js is publicly available through npm and first-party source. The site describes modular imports and lists bundle-size figures. Those figures are vendor-reported, without a target app's build or device context; measure the resulting application bundle and runtime if size matters. Public documentation and library access were free at observation. The separate Learn page was still a course waitlist, so do not assume a completed course is available. [Installation and modules](https://github.com/juliangarnier/anime), [Learn page](https://animejs.com/learn)

The repository declares MIT licensing and links its license file. Retain the required notices when copying substantial software. Example media, fonts, and independently hosted CodePen content can have separate rights. [First-party license](https://github.com/juliangarnier/anime/blob/master/LICENSE.md)

## Use in the design skill

Choose the existing app motion library or browser CSS/WAAPI first when it meets the need. Consider Anime.js for sequence, SVG, or interaction requirements that justify another dependency. Define the motion's purpose, interruption behavior, end state, and fallback before implementing it. Keep lifecycle ownership with the component that owns the visual state.

**Analytical checks:** stale timers/animations after unmount, rapid repeated input, animation cancellation, focus and text semantics, scroll behavior, reduced motion, and transform/opacity versus layout cost. Recheck versioned APIs, browser support, package/license notices, and measured app cost when adopting or upgrading.
