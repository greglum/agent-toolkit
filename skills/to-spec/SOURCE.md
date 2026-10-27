# Research-to-design source

Observed October 24, 2026. The added research handoff guidance is original procedure informed
by HumanLayer's Apache-2.0 source at `2f66a45b186d88488fa356862be0117db1ccae9f`:

- [Workflow phases](https://github.com/humanlayer/humanlayer/blob/2f66a45b186d88488fa356862be0117db1ccae9f/apps/docs/explanation/workflow-phases.md): current-state research, desired-state design, and verifiable slices.
- [Technical design](https://github.com/humanlayer/humanlayer/blob/2f66a45b186d88488fa356862be0117db1ccae9f/apps/riptide-rpi-claude-plugin/skills/create-tdd/SKILL.md): system boundaries before code shape; keep resolved decisions coherent.
- [Structure outline](https://github.com/humanlayer/humanlayer/blob/2f66a45b186d88488fa356862be0117db1ccae9f/apps/riptide-rpi-claude-plugin/skills/create-structure-outline/SKILL.md): each phase produces a result that can be checked without waiting for the next phase.

No upstream text, template, code, or asset was copied. This catalog keeps `to-spec` as one
conversation-derived spec, with no required interview, Linear integration, named worker,
artifact service, extra document, or automatic commit. User and repository authority remain
above any generated artifact. Existing test policy governs new tests; rendered and human
judgment checks remain separate from automated checks.

Recheck source-sensitive facts before implementing a spec. Source review supports these
design choices; it does not establish a measured improvement in agent behavior.

## AI system contracts

Observed October 25, 2026. Original procedural synthesis; no upstream text or code copied.

- Om Bharatiya, MIT, [AI system design guide](https://github.com/ombharatiya/ai-system-design-guide/tree/ed955b27d94201b663a741284767a1136dc83e5e),
  durable-execution and loop-engineering chapters: recovery, stopping and budget decisions.
- Anthropic, [context engineering](https://www.anthropic.com/research/effective-context-engineering-for-ai-agents),
  September 29, 2025, context retrieval sections; [agent evals](https://www.anthropic.com/research/demystifying-evals-for-ai-agents),
  January 9, 2026, evaluation structure: context ownership and actual final state.
- Taylor Mullen and Christian Gunderman, Google, [behavioral evaluation](https://developers.googleblog.com/the-anatomy-of-harness-engineering-how-to-evaluate-iterate-and-guard-ai-coding-agents/),
  September 9, 2026, suite design: consequential behavior plus end-to-end outcomes.
- Anthropic, [infrastructure noise](https://www.anthropic.com/research/infrastructure-noise),
  February 5, 2026, recommendations: environment is an evaluation variable.
- Temporal, [SDK 1.34.0 sandbox semantics](https://github.com/temporalio/sdk-python/blob/1.34.0/temporalio/contrib/strands/README.md),
  checked through version-specific Context7; Nikolay Advolodkin, [idempotency tutorial](https://learn.temporal.io/tutorials/python/standalone-activities/),
  June 15, 2026, Module 2: at-least-once execution needs receiver-side deduplication.

Living-page reuse rights were not established. The guide's numerical loop defaults, blanket
provider failover, persistent memory and exactly-once wording are not adopted. This remains
a spec procedure, not a shipped agent runtime or a measured performance improvement. Recheck
when execution semantics or the target system's contracts change. Paired behavioral evaluation
is not yet run. The dated catalog report records the full assessment and source boundaries.
