---
name: orchestrate-agents
description: Coordinate parallel implementation and independent review across agent models and providers. Use for a requested swarm, cross-provider delegation, or advisor-led work with distinct owners. Use loop-engineering for the improvement loop and codebase-metrics for scoring.
compatibility: Requires native delegation or a supported cross-provider task runner. Report when a selected model cannot run and continue independent authorized work.
---

# Orchestrate agents

For evaluation or brief-only planning, use read-only discovery, show the proposed lanes, and stop before dispatch. Run workers only when the user's task authorizes delegation.

1. Record the objective, base revision, allowed actions, required checks and stop conditions. Separate implementation, independent review, adversarial verification and the advisor's decisions. The parent owns integration.
2. Split independent work by ownership. Give each writer exclusive paths or a managed checkout based on the correct revision. A managed checkout built from a commit omits uncommitted local work; when writers must build on it, share the workspace and give each writer strictly disjoint paths. Give reviewers an exact source and read-only scope. Keep independent verdicts separate until each reviewer reports.
3. Discover callable provider, account, model and effort combinations. Honor the requested model for its role. A listed model can still fail at launch. Read [model routing](references/model-routing.md) for dated role defaults and a recheck procedure.
4. Use native delegation for compatible same-provider work and the harness's supported runner for cross-provider work, explicit settings or managed isolation. Request no higher permission mode than the parent holds; a runner can refuse the escalation at launch, so omit the mode or match the parent's. Fill available slots with useful independent work. Order dependent work and share no mutable runtime without deliberate sequencing. A worker needs authority for the exact external target.

## Brief and collect

Give each worker the source, owned paths, deliverable, dependencies, acceptance checks, file-size or hook limits (edited tests included) and authority boundary. State which sibling work to preserve. When a sandboxed worker cannot write a tool's home cache, point that cache at a writable temporary directory (for example `UV_CACHE_DIR="$TMPDIR/uv-cache"` for uv) before asking for wider permissions. Keep credentials and unnecessary private data out of briefs. Ask for source references, test receipts, and the actual executed model when the runner exposes it.

For T3 child tasks, use the [T3 handoff and recovery reference](references/t3-handoff.md) for brief transfer, completion, and resuming interrupted work.

Give the advisor a read-only view of the assignment graph, evidence and open decisions. The advisor proposes priorities and thresholds. The parent acts within the user's authority and integrates accepted work. If the advisor cannot run, continue work whose scope and acceptance are already settled.

- Follow the runner's completion mechanism. Distinguish a queued launch, completed work, missing access and quota failure. Report an unavailable named provider or model and keep independent active lanes running. For a role default, choose another authorized model if it meets the same brief. Retry a quota failure only when availability changes. Cancel a replaced worker before reassigning its paths.
- Check worker patches against their stated base, owned paths and size limits: an already-oversized file must shrink or split. Verify a patch without receipts in isolation when its effects are uncertain. Integrate an independent slice if it meets its own gates, then rerun checks at shared boundaries. Separate source checks, fixture behavior, and live acceptance.
- Keep one receipt per lane, including the parent. Record the owner, requested provider and model, executed provider and model, effort, isolation, permission mode, revision, outcome and open gates. If the runner confirms only the selection, record the executed model as unverified.
- Report what changed, what was verified and what remains open. Leave required slices, reviews and checks open until proven. A launch or a worker's self-score earns no acceptance credit.
