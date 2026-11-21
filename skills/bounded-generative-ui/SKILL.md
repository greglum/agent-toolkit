---
name: bounded-generative-ui
description: Design, build, or review UI where a model selects and arranges app-owned catalog components (dynamic or adaptive layouts, generative UI specs, JSON Render, replay demos). Audits edit nothing. Not for general/fixed web design (web-app-design), AI-slop audits (deslop-ui), or viewport width fit (fit-surface).
compatibility: Requires source access and browser tooling for rendered checks; without a browser, static contract checks proceed and rendered checks are reported unavailable. Optional React/JSON Render and model provider tooling require user authority; offline scripted or replay demos need no provider access.
---

# Bounded generative UI

Let a model choose how to present trusted results. Keep the app responsible for the results, the available components, and what every reader must see.

Choose the mode before touching code:
- **Review mode** is read-only: write no application or spec files. Inspect the component catalog, validator bounds, fixed baseline, fallback path, and rendered or static evidence, then report findings (`file:line`, gap, proposed fix) and limits.
- **Build mode** designs or implements the bounded catalog, validator, fixed baseline, and fallback within the requested files.

Package installs, paid or hosted model provider calls, network egress of app data, and edits outside the requested scope require explicit user authority. Use a scripted evaluator or replayable capture when provider access or data scope is unavailable.

1. **Name the layout decision.** Pick one user task and identify two requests that benefit from different arrangements of the same data. Use a fixed view or a preset switch as the baseline. If the choice is fully determined by a small set of controls, use the baseline unless the task explicitly calls for a composition demo.
2. **Set the contract.** List the app-owned components, typed props, valid record IDs, and allowed layout decisions. If required app components, data contracts, or trusted data sources are missing or malformed, stop and report the missing contract before building or accepting a layout. Keep the source link, warnings, provenance, and required actions in the fixed UI when the model has no reason to move them. Resolve facts, URLs, and permissions in the app. Prefer a read-only first slice with a working fixed view.
3. **Check before rendering.** Accept only known component types, props, and data references. Bound size and depth and reject cycles, duplicate references, and missing required content. Permit expressions and action bindings only when the task needs them. Validate resolved values and authorize side effects at the handler. Keep the fixed view available if validation fails, the renderer fails, or the model returns a partial result. Read the [JSON Render and Jev notes](references/json-render.md) only when the destination uses JSON Render or Jev.
4. **Prove the decision.** Run one valid layout, a contrasting layout over the same data, and a malformed or incomplete output. In the browser, check the same facts and source links, visible and keyboard order, narrow layout, and fallback. Compare with the baseline. If browser tooling is unavailable, complete static contract, schema, and scripted evaluator checks, and report rendered DOM, keyboard, contrast, and narrow-layout checks as unavailable. A fixture proves rendering, a scripted evaluator proves composition mechanics, and a captured model response proves one real decision. Label each accordingly.

## Completion

Finish with the layout decision and why it earns the extra machinery, the accepted output contract, and check receipts separating passed, failed, unavailable, and unrun checks (including browser or provider limits). A replay or static demo can finish without provider access when those limits are named.
