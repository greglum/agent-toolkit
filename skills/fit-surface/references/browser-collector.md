# Collect rendered geometry

Use the bundled `scripts/collect-surface.mjs` when the current browser rig can evaluate
JavaScript on the already-open surface. It returns structured measurements without
navigating, resizing, scrolling, hiding overlays, changing theme, submitting forms or editing
the DOM. Existing launch and fixture owners still choose the page and state.

## Existing Playwright page

Import `collectSurface` from this skill's `scripts/collect-surface.mjs`, then:

```javascript
const report = await page.evaluate(collectSurface, {
  root: '#workbench',
  state: 'narrow / dark / loading / details open',
  maxElements: 5000
});
```

Other browser rigs can evaluate the self-contained function's source. Preserve the supplied
function and pass options as data through the browser API. The root must match exactly one
element. A missing or ambiguous root, invalid selector or invalid options throws; record a
failed probe, never substitute an empty report. Omit `root` to inspect the body.

Call after the scenario's observable readiness assertion. It captures the current scroll
state, so record/reset scroll as the measurement method requires before calling it. Collect
before and after with the same root, state, viewport and scroll positions. Saving the returned
JSON is a caller operation; use an explicit evidence path and preserve existing artifacts.

## Read the result

- `environment` records layout/client size, visual viewport, scroll, scale, device pixel
  ratio and system color/motion preferences. The color preference does not identify an
  app's selected theme; put that in `state`.
- `document` records page dimensions and horizontal overflow even when root scope is narrow.
- `scroll-container` observations distinguish horizontal/vertical scroll extents from
  `clipped-content` observations. Nested text wrappers are included. Clipping can be
  intentional decoration or approved truncation; the collector does not infer lost meaning.
- `viewport-edge` records bounds outside the horizontal layout viewport with the nearest
  clipping or scrolling ancestor, so a deliberately wide grid is not mistaken for an
  uncontained page leak. Bounds use CSS pixels relative to the layout viewport.
- `small-target` reports enabled semantic control dimensions under 24 CSS pixels. It does
  not check WCAG's spacing, inline, equivalent, user-agent or essential exceptions and is
  never a conformance verdict. Custom clickable elements without semantics need manual review.
- Every observation is `needs-review`. Selectors locate current DOM nodes; they are not
  source-file mappings or stable component identities across arbitrary app updates.

`coverage.status` is `partial` when an inspected frame, open shadow root or element cap leaves
content uninspected. The collector does not enter frames or shadow trees. Closed shadow
roots cannot be detected. A cap stops traversal without counting remaining descendants;
it bounds visited nodes, not serialized bytes or selector length.
`complete-light-dom` means only that this light-DOM traversal finished, never that the page
passes. Occlusion, clip-paths, masks, pseudo-elements, accessibility, contrast, semantic reachability, focus,
touch and physical-keyboard behavior remain separate checks. No text, input values, page URL
or screenshot is collected; selectors and the caller's state label can still be sensitive.
Use the existing axe-core rig for accessibility and preserve its incomplete results.

## Exercise the bundled browser fixture

With an existing Node.js, Playwright and local Chrome installation:

```bash
node scripts/check-browser.mjs /path/to/playwright/index.mjs /path/to/evidence
```

Resolve paths from this skill's directory. The check uses an isolated offline browser
context and synthetic content. It tests desktop/narrow geometry, nested clipping versus
intentional scrolling, RTL, hidden/disabled controls, unchanged page/focus/scroll state,
bounded coverage, malformed inputs and ordinary content. No dependency is downloaded.
It proves the collector on that fixture, not the destination product's fit or accessibility.

## Sources

Original implementation after inspecting Impeccable's
[detector interface](https://github.com/pbakaus/impeccable/blob/ade37830fee364c1457f9ada479470296f80dbbb/crates/detect/src/cli.rs)
and [measurement gates](https://github.com/pbakaus/impeccable/blob/ade37830fee364c1457f9ada479470296f80dbbb/crates/core/src/checks/measures.rs),
Apache-2.0, observed October 26, 2026. No upstream code or rule catalog copied.
Independent contracts: [MDN scrollWidth](https://developer.mozilla.org/en-US/docs/Web/API/Element/scrollWidth)
and [WAI target-size exceptions](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum),
observed October 26. Recheck on a browser geometry change or a reproduced missed condition.
