---
name: deslop-ui
description: >-
  Audit or fix AI-looking web UI (de-AI, modernize, sharpen): visual, structural, and copy
  tells inside the design system. Audits edit nothing. Not for prose/i18n alone (deslop),
  new direction (web-app-design), width fit (fit-surface), motion (find-animation-opportunities),
  model-chosen UI (bounded-generative-ui), or launch harnesses (app-verifier).
license: MIT
compatibility: Source review needs file access. Bundled scanner needs Bash, grep, find, sed, and Perl. Browser tooling and companion skills are optional; absent capabilities leave corresponding checks unrun.
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

Optional companion skills (`fit-surface` for geometry collection, `deslop` for copy rewrites,
and `frontend-design` or repository UI audit skills) help when available; when absent,
read the design owners and audit geometry, copy, and UI directly without installing helpers.
Resolve bundled scripts from this skill's directory and targets from the destination repository.

## Procedure

1. **Ground.** Read the repository's design authority before any screen: its DESIGN.md or
   equivalent, tokens, primitives, and any copy rules. Record the register (a working tool at a
   desk, a consumer app, a marketing site) and the supported viewports and themes. Reuse the
   repository's UI test setup or browser tools for rendering. Before declaring rendering
   unavailable, look for its no-login fixture harness or seeded entry and the dev server's
   actual port; a sign-in or configuration page is a setup state, not a finding. If nothing
   can render, say so and audit the source, marking every visual claim unverified.
2. **Scope.** If requested paths are missing, empty, or contain no web UI surfaces, stop and
   report the gap before running scanners. Otherwise, list the routes, states, and components
   in scope and build a coverage matrix (route × viewport × theme, plus the empty, loading,
   error, and long-content states that exist, and every in-page tab, since a route sweep sees
   only the default one). Never submit forms, mutate real data, or change permissions when
   exercising routes and states. Cover the entire requested matrix in bounded batches and name
   every uninspected cell. A missing DESIGN.md alone does not make the product greenfield;
   inspect its existing identity and implementation before judging.
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
   When `fit-surface` is available, its browser collector supplies structured geometry
   observations; review them against the design owner rather than treating them as defects.
   Judge paint at rest from computed values: skip elements mid-transition or held at zero
   opacity, and exempt disabled controls from the text contrast minimum.
5. **Rank.** Separate findings into two tiers before ordering: **Floor** (non-waivable
   correctness, contrast, focus, reduced motion, overflow, broken wiring, or invented/fake
   content) and **Reflex** (stylistic AI defaults that a project may keep with a recorded
   product or brand reason; flag stale waivers whose target no longer triggers). Order by what
   a user of this product would notice first, not by ease. Structural and conceptual findings
   usually outrank visual ones: recoloring a generic page leaves it generic. Audit mode stops
   after this step, skips Steps 6 and 7, and proceeds directly to Step 8.
6. **Fix (edit mode).** Before editing an existing screen or redesigning a section, record an
   inventory of its live links, headings, form fields, and interactive handlers so nothing is
   silently dropped. Take the highest-ranked finding (Floor before Reflex), make the smallest
   change inside the repository's system (a token, a primitive variant, a layout decision, a
   rewritten string), render the affected cells again, and recheck against the
   [acceptance bar](references/catalog.md#acceptance-bar) and the preserved-wiring inventory.
   Keep the best render, not the latest: revert a fix that makes the render worse rather than
   patching on top. Repeat until the bar passes or the remaining findings need a decision from
   the owner. Never add a dependency, a second token set, or a new visual idea to fix a slop
   finding; the fix is subtraction or specificity. If a tell lives in a primitive, fix the
   primitive once. Edit mode does not authorize commits, pushes, or dependency installs.
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

- `scripts/ui-tells.sh PATH...` greps source trees (tsx, jsx, ts, js, vue, svelte, html, css, scss, mdx) for the
  class-name and markup tells and prints file:line hits grouped by tell. Exit 1 on a strong hit,
  0 when scanning succeeds without a strong hit, and 2 on invalid targets, missing dependencies,
  or scan failure. Each group displays at most 200 matches and reports when more were omitted.
  Strong tells prioritize inspection.
