# Source and departures

Inspired by Lauren Tan (`poteto`), [pstack /correct](https://github.com/cursor/plugins/blob/e5136d82418d2db3165ea1050d17577cd618cc05/pstack/skills/correct/SKILL.md),
reviewed at `e5136d82418d2db3165ea1050d17577cd618cc05` on 2026-10-15 UTC.
The official source is `cursor/plugins/pstack`. Version 0.15.9 announced the workflow;
the reviewed plugin metadata says 0.15.25. Its [license](https://github.com/cursor/plugins/blob/e5136d82418d2db3165ea1050d17577cd618cc05/pstack/LICENSE)
is MIT, copyright 2026 Lauren Tan. This is original local prose, with no copied code or text.

The adaptation extends our existing `encode-correction` owner instead of adding an overlapping
`correct` skill. Adopt history-backed mistake classes, architecture before checks, diagnostics
that teach the supported path, and proof against past mistakes. The companion
[architect red flags](https://github.com/cursor/plugins/blob/e5136d82418d2db3165ea1050d17577cd618cc05/pstack/skills/architect/references/design-red-flags.md)
inform the single-owner and caller-migration review.

Keep our task authority, test-preservation policy, evidence limits, and repository gates.
Use existing rule owners instead of requiring a new table in every AGENTS.md. Inherit the
active harness and model; no Cursor plugin, model routing, telemetry, hook, or new runtime
dependency is installed. Preserve normal automatic discovery for the existing local skill.
Repeated runs may make no change when evidence does not support one.

Recheck upstream when its workflow changes or a real run exposes a prevention failure.
