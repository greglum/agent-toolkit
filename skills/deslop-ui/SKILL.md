---
name: deslop-ui
description: >-
  Audit or fix a web UI that looks AI-generated: repeated visual, structural, and copy
  patterns. Use to deslop, de-AI, modernize, sharpen, or make a UI pop. Keeps the
  repository's design system; an audit changes nothing. For new visual direction use
  web-app-design; for width or overflow fit use fit-surface.
license: MIT
compatibility: Source review needs file access. Bundled scanner needs Bash, grep, find, xargs, sed, and Perl. Browser tooling and companion skills are optional; absent capabilities leave corresponding checks unrun.
metadata:
  version: "1.0.0"
---

# Deslop UI

Outcome: every screen in scope looks like a person chose it for these users and this data.
The repository's design system, tokens, and primitives stay the authority. With no
constraint, a generator reaches for the most common default: a gradient, a glow, six
identical cards. Replace each default with a decision grounded in this product's users, data,
and register, and verify it on the rendered page.

Two modes, like `deslop`. **Audit** changes nothing; use it when asked to check, review, or
audit, and as the first pass over any screen. **Edit** applies the fixes; use it when asked to
fix, deslop, modernize, or sharpen.

Use available `frontend-design` and repository UI audit skills for their matching concerns.
If absent, read the design owners and audit directly without installing helpers. Resolve
bundled scripts from this skill's directory and targets from the destination repository.

## Procedure

1. **Ground.** Read the repository's design authority before any screen: its DESIGN.md or
   equivalent, tokens, primitives, and any copy rules. Record the register (a working tool at a
   desk, a consumer app, a marketing site) and the supported viewports and themes. Reuse the
   repository's UI test setup or browser tools for rendering. Before declaring rendering
   unavailable, look for its no-login fixture harness or seeded entry and the dev server's
   actual port; a sign-in or configuration page is a setup state, not a finding. If nothing
   can render, say so and audit the source, marking every visual claim unverified.
2. **Scope.** List the routes, states, and components in scope and build a coverage matrix
   (route × viewport × theme, plus the empty, loading, error, and long-content states that
   exist, and every in-page tab, since a route sweep sees only the default one). Cover the
   entire requested matrix in bounded batches and name every uninspected cell. A missing
   DESIGN.md alone does not make the product greenfield; inspect its existing identity and
   implementation before judging.
3. **Mechanical pass.** Run `scripts/ui-tells.sh PATHS` over the source and keep the output as
   the before list. If unavailable or failed, continue manual source review and report that
   status. Verify every hit against the design owner, content, and user task; record justified
   brand choices and false positives separately from confirmed defects.
4. **Rendered pass.** Open every cell of the matrix and read it against
   [references/catalog.md](references/catalog.md), three layers in order: visual, structural,
   conceptual. For each finding record file:line, the evidence (a screenshot path, a measured
   value, a computed style), the layer, and the smallest fix that replaces the default with a
   decision.
   For accessibility claims, use [evidence by state and method](references/accessibility-evidence.md).
   Judge paint at rest from computed values: skip elements mid-transition or held at zero
   opacity, and exempt disabled controls from the text contrast minimum.
5. **Rank.** Order by what a user of this product would notice first, not by ease. Structural
   and conceptual findings usually outrank visual ones: recoloring a generic page leaves it
   generic.
6. **Fix (edit mode).** Take the highest-ranked finding, make the smallest change inside the
   repository's system (a token, a primitive variant, a layout decision, a rewritten string),
   render the affected cells again, and recheck against the
   [acceptance bar](references/catalog.md#acceptance-bar). Keep the best render, not the
   latest: revert a fix that makes the render worse rather than patching on top. Repeat until
   the bar passes or the remaining findings need a decision from the owner. Never add a
   dependency, a second token set, or a new visual idea to fix a slop finding; the fix is
   subtraction or specificity. If a tell lives in a primitive, fix the primitive once.
7. **Verify.** Run the repository's own checks (typecheck, lint, tests, its UI gates), rerun
   `scripts/ui-tells.sh` for the after list, and confirm contrast and focus on any element whose
   color or shape changed (the repository's accessibility checks, or measured computed colors).
   Then get unprimed eyes: first prove each fix reached the render (a computed-style or pixel
   difference on the changed element; a fix that changed nothing passes every static check),
   then give every after capture, plus 2-4x crops of the changed areas, to a fresh subagent with
   a neutral prompt that names no expected defect, when available. Parent-verify every candidate
   against the design owner and observed behavior; record it as accepted, rejected, or
   unverified. With no subagent available, write the strongest case that each changed screen is
   still broken before accepting it.
8. **Report.** Findings by layer with evidence and disposition (fixed, kept with reason, needs
   owner decision); requested/covered/uninspected cells; actual scanner counts and status
   (unavailable is not zero); the acceptance bar item by item; each check run with its result;
   anything unrendered or unverified, named. Mark counts from truncated scanner groups as lower
   bounds and inspect the omitted scope before claiming full coverage.

## Completion

Done when every acceptance-bar item passes on the rendered screens in scope or every remaining
item carries an owner decision, the repository's checks pass, and the report is delivered.
If rendering is unavailable, deliver a source audit with rendered acceptance explicitly
unverified. In audit mode, done when the report lists every finding with file, line, layer,
evidence, and the proposed fix, and offers the edit.

## Scripts

- `scripts/ui-tells.sh PATH...` greps source trees (tsx, jsx, vue, svelte, html, css) for the
  class-name and markup tells and prints file:line hits grouped by tell. Exit 1 on a strong hit,
  0 when scanning succeeds without a strong hit, and 2 on invalid targets, missing dependencies,
  or scan failure. Each group displays at most 200 matches and reports when more were omitted.
  Strong tells prioritize inspection.
