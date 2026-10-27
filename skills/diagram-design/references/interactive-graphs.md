# Interactive node maps

Use the bundled tools for architecture, workflow, data-flow and lifecycle **node/edge maps**.
They generate one offline HTML file with search, component details, source locators, directional
reach, a directed route, stable-identity comparison and PNG/SVG downloads. The implementation
is original and has no runtime packages, remote resources, telemetry or installer step.

Use the ordinary skill workflow to inspect source, choose meaning and verify the result.
This renderer consumes authored facts; it does not infer architecture or observe execution.
For sequence lifelines, ERDs, spatial anatomy, arbitrary drawing or video, use the appropriate
existing workflow. These are outside the graph renderer's current capabilities.

## Author and generate

Use [the example](../examples/diagram-pipeline.json) for the complete input shape, not facts
to copy. Paths in these commands are relative to the working directory; replace `<skill>`
with this installed skill's directory. Create the destination directory first.

```bash
node <skill>/scripts/draw-graph.mjs graph.json system-map.html
node <skill>/scripts/draw-graph.mjs after.json comparison.html --before before.json
```

Existing outputs are preserved unless `--force` is explicit. A forced replacement validates
and builds before replacing the previous artifact. Inputs cannot be output targets. The CLI
receipt reports generation and a SHA-256; it does not claim browser verification.

The top-level fields are `version: 1`, `type`, `title`, `summary`, `revision`, `nodes`, `edges`
and optional `mainPath` (node IDs with an authored directed connection at every step).
Use the exact source revision or a visible synthetic/proposed label. The validator rejects
unknown fields and invalid references instead of guessing.

| Object | Fields |
| --- | --- |
| Node | Unique `id`, `label`; optional `kind`, `detail`, `sources`, paired `x` and `y` |
| Edge | Unique `id`, `from`, `to`, `label`; optional `condition`, `sources`, `via` |

IDs start with a letter and contain letters, digits, underscores or hyphens. Node kinds are
`component`, `actor`, `external`, `database`, `gate`, `artifact`. `sources` is a list of inert
source-locator strings. Put long explanations in `detail`; keep a behavior-changing condition
in the edge's `condition`. Missing sources remain explicitly unverified in the ledger.

Default placement follows input order in three columns. For a coherent primary path, supply
coordinates: nodes are 220 × 104; x/y name the top-left corner, y starts at 160 below the
heading. Reserve at least 200 pixels of clear space for an edge label. `via` is a list of
`[x, y]` bends when a branch or return needs a separate corridor. Coordinates are finite and
between 0 and 10000. Keep titles/labels concise enough for the measured layout.

Generation rejects overlapping nodes, labels on nodes, overlapping edge labels and routes
through unrelated nodes. It does not prove crossing-free routing, text metrics, contrast or
perceptual quality. Inspect the render, measure actual text bounds and adjust the connected
neighborhood. There is no general graph-layout solver or source-backed trust-boundary grouping.
Label material boundaries explicitly or use a static diagram when grouping is essential.

## Explore and compare

Search matches labels, IDs, kinds, details and source locators. Select a component in the list
or diagram; both support the keyboard. Upstream/downstream traverses authored directed edges
and handles cycles. Route inspection picks one shortest directed route in edge order; it is
not all possible routes and does not evaluate conditions. An unreachable destination reports
no directed route. Reset clears search, selection and tracing. The URL fragment restores the
snapshot, search and selected path without a server.

With `--before`, both snapshots remain visible side by side on wide screens and stack on narrow
ones. Choose the active snapshot for controls and export. The change ledger distinguishes
added, removed, changed, moved, rewired and rerouted identities. Preserve IDs between versions;
a renamed ID is a removal plus an addition. This is a comparison of authored models, not proof
of runtime impact or migration safety.

## Export and prove

Download SVG or the exact 2400 × 1260 PNG from the viewer. Both capture the active snapshot
and current highlight, retain the complete graph with aspect-ratio containment, and include
the title, path scope and connection legend. They do not capture the HTML detail panel or
complete source ledger. Keep the HTML/JSON beside them; any essential tooltip-only meaning
must also appear on the graph before export. There is no video encoder in this bundle.

Open the HTML directly with network unavailable. Exercise search, selection, both directions,
a route, no-route feedback, reset, keyboard focus and comparison snapshot switching. Verify
the hash restores the same state. Test the no-script figure/ledger, narrow local scrolling,
text bounds, contrast and the available accessibility rig. Export, open the actual SVG/PNG,
and verify dimensions, styles, complete edges and the selected state. Report each unrun check.

The portable model, rendering and input-boundary regressions run with:

```bash
python3 -m unittest discover -s <skill>/scripts -p 'test_*.py'
```

Browser checks additionally use an installed Playwright package and Chrome:

```bash
node <skill>/scripts/check-browser.mjs <path-to-playwright-index.mjs> output-folder [path-to-axe.min.js]
```

No package is installed by that command. It generates fixtures in the named folder, checks
interactions and exports, measures text/overflow, and saves captures. Without axe-core it
reports that check as unavailable. These fixture checks do not establish quality of future
authored diagrams; verify each requested artifact.
