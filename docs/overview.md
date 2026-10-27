# Example: an explorable diagram

This walkthrough uses the bundled diagram renderer without starting an agent session.
It turns an authored graph into an offline HTML viewer with search, component details,
directional tracing and SVG/PNG export.

## Generate the example

Requires Node.js 18+. From the clone's root:

```bash
node skills/diagram-design/scripts/draw-graph.mjs skills/diagram-design/examples/diagram-pipeline.json diagram-demo.html
```

Open `diagram-demo.html` in a browser. The input is a synthetic workflow that shows the
diagram pipeline itself. The command preserves an existing output rather than overwriting it.

Try searching for a component, selecting it with the keyboard, tracing upstream or downstream,
and finding a route to another component. Export the selected view and inspect the actual
SVG or PNG. The [graph guide](../skills/diagram-design/references/interactive-graphs.md)
covers comparison, input requirements and verification.

## Use it for a real system

Invoke `diagram-design` in Claude Code or Codex and identify the subsystem and source revision.
The skill asks the agent to inspect source, record the supported relationships and author a
graph with stable identities. The renderer validates that model; it does not discover the
architecture or establish runtime behavior. Check the relationships against source and the
layout in the browser before sharing it.

This distinction applies across the toolkit. Some bundles include executable tools;
others provide a method. Use [verification](verification.md) to distinguish structural checks,
tool tests, supplied-skill trials and real app or media checks.

For a first agent task, see [getting-started examples](examples/getting-started.md).
Browse other jobs in the [workflow map](workflows.md) or [full catalog](catalog.md).
Source notes remain with the bundles; [third-party notices](../THIRD_PARTY_NOTICES.md)
preserve credit for adapted material.
