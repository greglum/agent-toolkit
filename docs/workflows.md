# Choose a workflow

Start with the outcome below. The [alphabetical catalog](catalog.md) lists every
skill and its invocation mode. This map suggests a path; it does not invoke skills or grant
permission. Use the shortest path that resolves the task's uncertainty.

| Outcome | Start here | Continue when needed | Completion evidence |
| --- | --- | --- | --- |
| Turn a conversation into buildable work | [to-spec](../skills/to-spec/SKILL.md) | Repository-owned implementation and checks | Scope, decisions, allowed choices, and observable acceptance |
| Prepare a repository for agent work | [agent-readiness](../skills/agent-readiness/SKILL.md) | Existing project owners and native gates | Evidence-backed plan, implemented local changes, preserved work and independent verification |
| Assess codebase quality | [codebase-metrics](../skills/codebase-metrics/SKILL.md) | Implement the selected improvement in its owner | Fixed rubric, source evidence, comparable measurements |
| Understand and review a change | [guided-review](../skills/guided-review/SKILL.md) | [global-code-review](../skills/global-code-review/SKILL.md), or an explicit specialized review | Revision-bound reading path and independently checked findings |
| Model threats, review a model change, audit security or interpret existing SARIF | [security-audit](../skills/security-audit/SKILL.md) | Repository remediation workflow when requested | Reproduction or concrete source proof, with unresolved limits |
| Diagnose database behavior | [postgres-investigate](../skills/postgres-investigate/SKILL.md) | [reconcile-metric](../skills/reconcile-metric/SKILL.md) for disputed aggregates | Plans, locks, or source rows that explain the symptom |
| Find related confirmed bugs | [find-bug-variants](../skills/find-bug-variants/SKILL.md) | Fix each confirmed owner | Bounded search, distinct defects, preserved contracts |
| Simplify or prevent repeated mistakes | [simplify-code](../skills/simplify-code/SKILL.md) or [encode-correction](../skills/encode-correction/SKILL.md) | Existing behavior checks | Preserved behavior or a verified correction at its cause |
| Find an offline design starting point or check a color pair | [web-app-design](../skills/web-app-design/SKILL.md) and its [reference tool](../skills/web-app-design/references/design-reference-tool.md) | Existing product design owners and rendered verification | Traceable draft, explicit no-match, measured declared pairs and preserved accepted rules |
| Build or improve a web surface | [web-app-design](../skills/web-app-design/SKILL.md) | [fit-surface](../skills/fit-surface/SKILL.md), [deslop-ui](../skills/deslop-ui/SKILL.md) | Running-app layout, focus, accessibility, and meaningful user actions |
| Establish app verification | [app-verifier](../skills/app-verifier/SKILL.md) | The relevant design or behavior skill | Repeated launch and feature checks from the saved record |
| Choose and build interface motion | [find-animation-opportunities](../skills/find-animation-opportunities/SKILL.md), then [animate](../skills/animate/SKILL.md) | [review-animations](../skills/review-animations/SKILL.md) | Real triggers, interruption, reduced motion, and measured cost |
| Fix existing interface motion | [ui-motion](../skills/ui-motion/SKILL.md) | [review-animations](../skills/review-animations/SKILL.md) | State continuity in the running application |
| Make film thumbnails or social covers | [thumbnail-production](../skills/thumbnail-production/SKILL.md) | Existing image-generation or composition tools; film production only when requested | Checked platform exports, editable source and private asset provenance |
| Make a film | [motion-film](../skills/motion-film/SKILL.md) | Its production and export references | Joined render, listening, export, and requested editable handoff |
| Trace the impact of a repository change | [graph-engineering](../skills/graph-engineering/SKILL.md) | Existing index and source checks; [diagram-design](../skills/diagram-design/SKILL.md) for a visual | Source-bound paths, uncertainty, consumer checks and reconciled final evidence |
| Compare noisy experiment evidence | [compare-experiments](../skills/compare-experiments/SKILL.md) | Existing measurement collector; [loop-engineering](../skills/loop-engineering/SKILL.md) for implementation | Matched observations, failures and content-bound confirmation, with descriptive limits |
| Find repeated feedback in selected exports | [analyze-agent-history](../skills/analyze-agent-history/SKILL.md) | [encode-correction](../skills/encode-correction/SKILL.md) only after verifying incidents | Text-free candidate counts, provenance exclusions and honest coverage |
| Improve through repeated feedback | [loop-engineering](../skills/loop-engineering/SKILL.md) | Repository-owned checks and review; [codebase-metrics](../skills/codebase-metrics/SKILL.md) for scored assessment | Fixed acceptance, content-bound check results and an explicit stop decision |
| Explain a system visually | [diagram-design](../skills/diagram-design/SKILL.md) for static diagrams or searchable graph maps; [system-anatomy](../skills/system-anatomy/SKILL.md) for spatial explainers | Source, interaction and rendered-output checks | Accurate relationships, working tracing/comparison and checked exports |
| Prepare source-backed writing | [extract-documents](../skills/extract-documents/SKILL.md), then [deslop](../skills/deslop/SKILL.md) when needed | Explicit distribution workflow for social drafts | Traceable claims and verified source locators |
| Promote owned work and review traffic | [content-marketing](../skills/content-marketing/SKILL.md) | Film production or explicit distribution drafting when requested | Source-backed channel briefs, verified routes, declared decisions and comparable measured windows |
| Learn what works for peers and audiences | [social-research](../skills/social-research/SKILL.md) | [content-marketing](../skills/content-marketing/SKILL.md) to plan the next experiment | Per-account lift with raw values, quoted and located audience claims, or insufficient evidence |
| Cut short clips from a long video | [repurpose-long-video](../skills/repurpose-long-video/SKILL.md) | [motion-film](../skills/motion-film/SKILL.md) caption and export checks; explicit distribution drafting for posts | Rights confirmed, context-checked clips, frame review, probed outputs and a per-clip edit list |
| Retrieve exact technical documentation | [find-docs](../skills/find-docs/SKILL.md) | Current repository implementation | Version-matched primary references |
| Resume or reassess existing PR work | [continue-pr](../skills/continue-pr/SKILL.md) | Repository implementation and publication workflow | Recovered intent, current architecture, preserved contributors and checked continuation |
| Plan dependencies across several PRs | [plan-pr-stack](../skills/plan-pr-stack/SKILL.md) | Repository delivery plus [monitor-pr](../skills/monitor-pr/SKILL.md) for each live PR | Snapshot-bound candidate waves, unresolved dependencies and overlap decisions |
| Watch CI and review on a PR | [monitor-pr](../skills/monitor-pr/SKILL.md) | Authorized fixes and repository delivery gates | Resumable events, independently verified readiness and a stopped watcher |
| Clean stale branches and worktrees | [repository-cleanup](../skills/repository-cleanup/SKILL.md) | Delegated recovery, repository delivery and safe cleanup | Every resource accounted for, useful work landed or preserved, exact-target removal and recovery proof |
| Assess and refresh worktrees | [refresh-worktrees](../skills/refresh-worktrees/SKILL.md) | Repository setup and checks | Preserved local work and verified base/revision identity |

Explicit workflows require a named invocation. Use `/name` in Claude Code or `$name` in
Codex; respect the catalog's harness restrictions.

| Explicit request | Skill |
| --- | --- |
| Vet linked sources and harvest lessons, or research the whole catalog | [skill-research](../skills/skill-research/SKILL.md), with URLs for a focused assessment |
| Audit and behavior-test an existing skill | [harden-skill](../skills/harden-skill/SKILL.md) |
| Audit or update project docs | [docs-sync](../skills/docs-sync/SKILL.md) |
| Review current source, including Java or React | [review-source](../skills/review-source/SKILL.md); read-only, including unchanged code |
| Review client/API integration | [review-integration](../skills/review-integration/SKILL.md) |
| Audit tests | [tune-tests](../skills/tune-tests/SKILL.md) |
| Audit or clean only comments | Request that scope explicitly with [simplify-code](../skills/simplify-code/SKILL.md); an unclear comment request is an audit |
| Run the full delegated animation loop | [polish-animations](../skills/polish-animations/SKILL.md) |
| Prepare social drafts | [distribution-draft](../skills/distribution-draft/SKILL.md) |
| Review pending changes, commits, or a PR in Codex | [review-pending-changes](../skills/review-pending-changes/SKILL.md), [review-recent-commits](../skills/review-recent-commits/SKILL.md), [review-pr](../skills/review-pr/SKILL.md) |
| Commit/push or create a PR in Codex | [acp](../skills/acp/SKILL.md), [create-pr](../skills/create-pr/SKILL.md), with authority for the identified destination |

## Combine only the steps the task needs

For a web page, use `web-app-design` to establish the direction, `fit-surface` to measure
layout and focus, and `review-animations` when motion needs a separate review. A layout audit
can finish without a redesign. Use [the portfolio example](examples/portfolio-improvement.md)
for a bounded assessment, implementation and review sequence.

For a film and its cover, `motion-film` owns the film and `thumbnail-production` owns the
thumbnail or social-cover artifact. Share the approved brief and assets, then check each
export separately. Creating one does not authorize producing or publishing the other.

Carry the task, source revision, artifact paths, decisions and unresolved findings between
stages. Follow the destination project's checks. A source assessment, rendered result and
deployment check supply different evidence; report any missing dimension. Worker support
and permission to delegate depend on the harness and task.

See [verification](verification.md)
for the catalog's automated checks.

## PR lifecycle

Use [the PR lifecycle guide](pr-lifecycle.md) for continuation, publication, monitoring and
merge handoffs. It connects existing owners and explains their distinct finish lines.
It grants no action authority and does not invoke explicit-only workflows.
