# JSON Render and Jev

Use this when the destination chooses JSON Render. Check the installed release and keep `@json-render/core` and the renderer on matching versions. Use the upstream package skills for package-specific setup. [Upstream skills](https://json-render.dev/docs/skills) · [Reviewed release](https://github.com/vercel-labs/json-render/releases/tag/v0.22.0)

## Render a small spec

A catalog describes the supported vocabulary. A registry maps it to real application components. A flat React spec has a root ID and an element map. Start with checked-in specs and a lazy entry point if the feature is optional. React-compatible runtimes need a build and a browser check in the destination app. [Specs](https://json-render.dev/docs/specs) · [React API](https://json-render.dev/docs/api/react)

For example, a support brief could allow a root with exactly one `Decision`, `Evidence`, and `PolicyNote` child, in any order. Resolve their content from the same trusted case. Put case identity and source attribution in the fixed shell. Reject an omitted child, a repeated child, an unknown ID, and any action or writable expression in this read-only example. Prefer a check for this small contract over a general-purpose validator. Catalog parsing and structural validation cover different checks, and the React runtime includes built-in state actions. [Core schema](https://github.com/vercel-labs/json-render/blob/18194121c8f087afacd9a8ef65fbda18374ee039/packages/core/src/schema.ts) · [React schema](https://github.com/vercel-labs/json-render/blob/18194121c8f087afacd9a8ef65fbda18374ee039/packages/react/src/schema.ts)

## Compose or replay

`experimental_composeSpec` takes concrete app-owned candidates and an evaluator. Try a scripted evaluator first. The supplied Gateway adapter is a separate server-side integration. Inspect the exact candidate descriptions, prompt, context, and topology that would leave the app. Send only data authorized for that provider. Use the scripted evaluator when access or data scope is unavailable. Keep credentials server-side and use a deadline and a bounded call count. Require a finished result that passes the app contract before replacing the fixed view. For a public teaching demo, replay a validated capture and label its source. [Jev integration](https://json-render.dev/docs/jev)

Reviewed November 6, 2026, against Apache-2.0 release `v0.22.0` at `18194121c8f087afacd9a8ef65fbda18374ee039`. This procedure adopts the catalog, registry, and candidate pattern in original prose and adds a fixed-view comparison and evidence checks. Recheck manifests, validation behavior, and the experimental API before upgrading. [License](https://github.com/vercel-labs/json-render/blob/18194121c8f087afacd9a8ef65fbda18374ee039/LICENSE)
