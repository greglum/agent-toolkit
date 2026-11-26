# Model routing

These role defaults were checked against one local T3 catalog on 2026-11-24. Resolve these display labels to exact IDs. Recheck the active runner before assignment and after quota, catalog, account or permission changes.

| Work | Preferred models when available |
| --- | --- |
| Parent integration and broad advice | Codex Sol 6.2 for implementation and checks. Astra 6.2 for a read-only cross-workstream advisor. |
| Deep architecture and correctness | Claude Opus 5.5, on the designated account. |
| Scoped implementation | Claude Sonnet 5.5, Gemini 4 Hydrogen or Codex Sol 6.2. |
| Independent review and evidence reconciliation | Gemini 4 Neon or Claude Sonnet 5.5, distinct from the implementation owner. |
| Adversarial verification and difficult tradeoffs | Gemini 4 Carbon. Give it the failure hypothesis and checkable acceptance conditions. |
| Small source inventories and bounded triage | Codex Luna if the requested version is callable. |

1. Resolve the exact model ID, provider account, allowed effort options, and permission mode. In T3 Code call orchestrator_capabilities before the first delegation in a thread, then pass the advertised selections to delegation. On 2026-11-24, requesting `runtimeMode: "full-access"` from an `auto` parent failed with `runtime_mode_escalation_denied`; omitting `runtimeMode` launched. Recheck when the runner's permission model changes. Other harnesses use their native selection mechanisms.
2. Record requested and executed models separately for every lane, the parent included, with isolation and permission mode. The 2026-11-24 catalog listed gpt-6-luna and did not expose Luna 6.2. A similar name is insufficient evidence for an exact version. Credits and authentication can differ across accounts offering the same model.
3. Propose routing corrections from fresh observations and edit this reference only when catalog maintenance is authorized. Record quota details, account identifiers and temporary receipts in the task’s local work record. A successful run confirms availability for that run. Compare matched work and checkable results before changing a default on performance grounds.
