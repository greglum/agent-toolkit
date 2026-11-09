---
name: bounded-generative-ui
description: Design, build, or review a UI that lets a model choose and arrange app-owned components from a catalog. Use for model-selected layouts, generative UI specs, and replayable layout demos. Compare with a fixed view and verify that required evidence survives every accepted layout.
---

# Bounded generative UI

Let a model choose how to present trusted results. Keep the app responsible for the results, the available components, and what every reader must see.

1. **Name the layout decision.** Pick one user task and identify two requests that benefit from different arrangements of the same data. Use a fixed view or a preset switch as the baseline. If the choice is fully determined by a small set of controls, use the baseline unless the task explicitly calls for a composition demo.
2. **Set the contract.** List the app-owned components, typed props, valid record IDs, and allowed layout decisions. Keep the source link, warnings, provenance, and required actions in the fixed UI when the model has no reason to move them. Resolve facts, URLs, and permissions in the app. Prefer a read-only first slice with a working fixed view.
3. **Check before rendering.** Accept only known component types, props, and data references. Bound size and depth and reject cycles, duplicate references, and missing required content. Permit expressions and action bindings only when the task needs them. Validate resolved values and authorize side effects at the handler. Keep the fixed view available if validation fails, the renderer fails, or the model returns a partial result. For JSON Render and Jev, read the [integration notes](references/json-render.md).
4. **Prove the decision.** Run one valid layout, a contrasting layout over the same data, and a malformed or incomplete output. In the browser, check the same facts and source links, visible and keyboard order, narrow layout, and fallback. Compare with the baseline. A fixture proves rendering, a scripted evaluator proves composition mechanics, and a captured model response proves one real decision. Label each accordingly.

Finish with the layout decision and why it earns the extra machinery, the accepted output contract, and which checks ran. A replay or static demo can finish without provider access.
