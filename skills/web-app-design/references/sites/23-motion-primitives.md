# 23. Motion Primitives

Observed: 2026-10-05. Depth: targeted web search and direct official-site attempts, followed by first-party GitHub README, installation source, Morphing Dialog docs source, and licence. Homepage returned 403 and other site/doc requests failed. Public repository files were readable without authentication. No site access bypass, package install, code execution, or runtime measurement occurred.

Research method: searched `site:motion-primitives.com docs license installation`, attempted the official site, then used its official public GitHub repository for the blocked pages.

## Purpose and useful evidence

The official [README](https://github.com/ibelick/motion-primitives/blob/main/README.md) describes motion components for engineers and designers built with Motion and Tailwind CSS. It also labels the project beta and warns of substantial updates. That is an explicit maintenance consideration, not proof the current code is unstable in every use.

The readable [installation source](https://github.com/ibelick/motion-primitives/blob/main/app/docs/installation/page.mdx) specifies Tailwind, Motion, a class helper, and Lucide React icons, with CLI or manual component addition. Repository source is a useful public fallback when the documentation host is unavailable, but it may not match the currently deployed site revision. Keep that distinction visible.

The first-party [Morphing Dialog docs](https://github.com/ibelick/motion-primitives/blob/main/app/docs/morphing-dialog/page.mdx) describe a layout transition into a focused view, Escape/click-outside dismissal, trigger references, transition settings, and a description layout-animation switch. These are documented behaviors. They do not establish complete focus trapping, screen-reader behavior, or reduced-motion support in a receiving app.

## Patterns and application fit

The central useful idea is continuity between a compact object and its expanded detail. For a working app, motion can help users recognize that the opened panel belongs to the item they selected. Apply that idea when it reduces uncertainty about context. A standard dialog or drawer may be simpler when the starting element, focus target, and return path are already obvious.

Before choosing a morphing transition, define what happens when content is long, data loads late, an error occurs, or a user switches items quickly. Motion must not obscure those state changes. Preserve the repository's established dialog semantics rather than replacing them only to obtain a visual effect.

A reference note should capture the before/after layout, which element maintains identity, the user action that begins the transition, and the instant alternative for reduced motion. That supplies a design hypothesis without requiring a new library. If the existing Motion dependency can express it clearly, reuse that responsible layer.

## Reuse and access

The official [LICENCE.md](https://github.com/ibelick/motion-primitives/blob/main/LICENCE.md) contains MIT terms, including preservation of copyright and permission notices. The README's license link uses a different spelling from the file located through search; retain the verified path rather than assuming every link works. Third-party packages and assets have separate rights.

A Pro license page appeared in search results but direct retrieval failed. Its current paid plans, code access, and terms were not verified. Do not extend the public repository's MIT license to Pro material. Official-site access failures limit this page's coverage of current hosted demos and pricing.

## Skill use and checks

Route purposeful layout continuity and compact-to-detail transitions here. Read exact current source before adoption, especially given the beta notice. Prefer an original adaptation using established primitives over a second overlay framework.

Analytical checks: initial focus, focus containment/return, Escape, scroll locking, interrupted transitions, keyboard activation, reduced motion, and layout work under load. No passing audit is claimed.

Recheck hosted docs when access returns, deployed-versus-repository revision, beta changes, license paths, and Pro terms before implementation.
