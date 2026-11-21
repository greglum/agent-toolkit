# Choose a workflow

Start with the outcome below. The [alphabetical catalog](catalog.md) lists every
skill and its invocation mode. This map suggests a path; it does not invoke skills or grant
permission. Use the shortest path that resolves the task's uncertainty.

| Outcome | Start here | Continue when needed | Completion evidence |
| --- | --- | --- | --- |
| Turn a conversation into buildable work | [to-spec](../skills/to-spec/SKILL.md) | Repository-owned implementation and checks | A spec (local draft path or verified tracker URL) with scope, decisions, allowed choices, source pointers in Further Notes, and observable acceptance criteria |
| Prepare a repository for agent work | [agent-readiness](../skills/agent-readiness/SKILL.md) | Existing project owners and native gates | A plan backed by evidence, local changes made, existing work kept and an independent check |
| Assess codebase quality | [codebase-metrics](../skills/codebase-metrics/SKILL.md) | Implement the selected improvement in its owner | Scores against a fixed codebase or task/harness profile, with source evidence and comparable measurements |
| Understand and review a change | [guided-review](../skills/guided-review/SKILL.md) | [global-code-review](../skills/global-code-review/SKILL.md), or an explicit specialized review | A reading order tied to the exact revision, and findings checked independently |
| Model threats, review a model change, audit security or interpret existing SARIF | [security-audit](../skills/security-audit/SKILL.md) | Repository remediation workflow when requested | A reproduction or specific proof in the source, with open limits stated |
| Diagnose database behavior | [postgres-investigate](../skills/postgres-investigate/SKILL.md) | [reconcile-metric](../skills/reconcile-metric/SKILL.md) for disputed aggregates | Plans, locks, or source rows that explain the symptom |
| Find related confirmed bugs | [find-bug-variants](../skills/find-bug-variants/SKILL.md) | Fix each confirmed owner | A search with set limits, each candidate classified and existing behavior kept |
| Audit a whole repository for what can be removed | [delete-first](../skills/delete-first/SKILL.md) | The repository's own checks | Refuted candidates, verified cuts applied when requested, and owner decisions listed with evidence |
| Simplify code or comments, delete dead code, or prevent repeated mistakes | [delete-first](../skills/delete-first/SKILL.md), [audit-ai-code](../skills/audit-ai-code/SKILL.md), [simplify-code](../skills/simplify-code/SKILL.md), or [encode-correction](../skills/encode-correction/SKILL.md) | Existing behavior checks and blind refutation | Dead code removed safely, behavior unchanged, or a correction checked at its cause |
| Audit or update project docs | [docs-sync](../skills/docs-sync/SKILL.md) | Repository documentation gates | Claims checked against owning source, stale docs corrected |
| Review current source without edits | [review-source](../skills/review-source/SKILL.md) | Conditional stack-specific source contract references (`java.md`, `react.md`) | Evidenced findings for current source and open limits stated |
| Audit, speed up, or prune tests | [tune-tests](../skills/tune-tests/SKILL.md) | Target test suite and gates | Measured timings, coverage kept, and dead-code or approved prunes verified |
| Find an offline design starting point or check a color pair | [web-app-design](../skills/web-app-design/SKILL.md) and its [reference tool](../skills/web-app-design/references/design-reference-tool.md) | Existing product design owners and rendered verification | A draft you can trace to its sources or a plain no-match, contrast calculated for the declared color pairs and accepted rules kept |
| Build or improve a web surface | [web-app-design](../skills/web-app-design/SKILL.md) | [fit-surface](../skills/fit-surface/SKILL.md), [deslop-ui](../skills/deslop-ui/SKILL.md) | Layout, focus, accessibility and key user actions checked in the running app |
| Let a model arrange trusted results | [bounded-generative-ui](../skills/bounded-generative-ui/SKILL.md) | Existing UI components and a fixed view | A validated layout with source, keyboard, and fallback checks |
| Establish app verification | [app-verifier](../skills/app-verifier/SKILL.md) | The relevant design or behavior skill | Launch and feature checks rerun from the saved record |
| Choose and build interface motion | [find-animation-opportunities](../skills/find-animation-opportunities/SKILL.md), then [animate](../skills/animate/SKILL.md) | [review-animations](../skills/review-animations/SKILL.md) | Motion tested with real triggers, interruption and reduced motion, with its cost measured |
| Fix existing interface motion | [ui-motion](../skills/ui-motion/SKILL.md) | [review-animations](../skills/review-animations/SKILL.md) | States that stay continuous in the running app and end in the correct final state |
| Make film thumbnails or social covers | [thumbnail-production](../skills/thumbnail-production/SKILL.md) | Existing image-generation or composition tools; film production only when requested | Exports checked for each platform, an editable source and a private record of where each asset came from |
| Make a film | [motion-film](../skills/motion-film/SKILL.md) | Its production and export references | A full render, a listening pass, checked exports and an editable handoff when asked |
| Trace the impact of a repository change | [graph-engineering](../skills/graph-engineering/SKILL.md) | Existing index and source checks; [diagram-design](../skills/diagram-design/SKILL.md) for a visual | Dependency paths tied to the source, uncertainty stated, affected code checked and the graph reconciled with the source after edits |
| Get up to speed on new data in an unfamiliar domain | [onboard-data](../skills/onboard-data/SKILL.md), by name | [learn-domain](../skills/learn-domain/SKILL.md) and [map-data-source](../skills/map-data-source/SKILL.md) | A cited primer and glossary, a data dictionary with a meaning status per column, re-checkable claims and one ranked question list |
| Learn an unfamiliar domain or industry | [learn-domain](../skills/learn-domain/SKILL.md) | [extract-documents](../skills/extract-documents/SKILL.md) to prepare document corpora | Every primer and glossary claim cited with a status, and SME questions tied to the decision and evidence |
| Understand an unfamiliar dataset or database | [map-data-source](../skills/map-data-source/SKILL.md) | [telemetry-contract](../skills/telemetry-contract/SKILL.md) for sensor data with a known contract | Grain proven by exact counts, joins scored by containment and fan-out, and a dictionary with no guessed meanings |
| Check sensor or telemetry data before analysis | [telemetry-contract](../skills/telemetry-contract/SKILL.md) | [telemetry-anomalies](../skills/telemetry-anomalies/SKILL.md) once the data meets its contract | Each channel checked for units, rate, range, saturation and time, with counts kept distinct and no silent repair |
| Find faults in sensor telemetry | [telemetry-anomalies](../skills/telemetry-anomalies/SKILL.md) | [telemetry-contract](../skills/telemetry-contract/SKILL.md) first when the data is unchecked | Events within a stated false-alarm budget, scored at event level against a trivial baseline, never point-adjusted |
| Validate a model on time-ordered or grouped data | [temporal-validation](../skills/temporal-validation/SKILL.md) | [compare-experiments](../skills/compare-experiments/SKILL.md) to compare candidate runs | A written temporal contract, an audit with no leakage findings, and results beside a naive baseline on the same folds |
| Compare noisy experiment evidence | [compare-experiments](../skills/compare-experiments/SKILL.md) | Existing measurement collector; [loop-engineering](../skills/loop-engineering/SKILL.md) for implementation | Paired results with failures shown, the chosen option confirmed on fresh runs and limits stated (descriptive, not statistical significance) |
| Carry a verified lesson into future work | [learn-taste](../skills/learn-taste/SKILL.md) | The skill doing the work and the project’s guidance | A targeted update at the existing owner, with evidence and scope |
| Run a general retro on recent work | [retro](../skills/retro/SKILL.md) | The focused retro skills it selects | One report with triage scores, two full focuses and owned action items |
| Find what agents read and get wrong | [retro-agent-context](../skills/retro-agent-context/SKILL.md) | [docs-sync](../skills/docs-sync/SKILL.md) for drift, [agent-readiness](../skills/agent-readiness/SKILL.md) for a restructure | A report with measured instruction budgets, recurring drift and the owner for each fix |
| Find wasted agent turns and tokens | [retro-agent-friction](../skills/retro-agent-friction/SKILL.md) | Harness settings (`update-config` or `fewer-permission-prompts`), [encode-correction](../skills/encode-correction/SKILL.md) for code-level controls | A report with text-free friction counts, verified records and the owner for each fix |
| Find the checks that keep letting defects through | [retro-verification](../skills/retro-verification/SKILL.md) | Nearest suite owner or [encode-correction](../skills/encode-correction/SKILL.md) (behavior test level) for a missing test, [encode-correction](../skills/encode-correction/SKILL.md) for a gate | A report of traced escapes, the layer each passed and the fix per layer |
| Find which recent mistakes keep recurring, on request or on a schedule | [retro-guardrails](../skills/retro-guardrails/SKILL.md) | [encode-correction](../skills/encode-correction/SKILL.md) to implement a recommended control | A report with coverage, admitted findings with evidence, earlier controls checked, and the marker state |
| Find repeated feedback in agent sessions | [analyze-agent-history](../skills/analyze-agent-history/SKILL.md) | [encode-correction](../skills/encode-correction/SKILL.md) only after verifying incidents | Counts of possible corrections with no message text, excluded sources named and coverage stated honestly |
| Improve through repeated feedback | [loop-engineering](../skills/loop-engineering/SKILL.md) | Repository-owned checks and review; [codebase-metrics](../skills/codebase-metrics/SKILL.md) for scored assessment | Fixed acceptance criteria, check results tied to the exact content and a clear decision to stop |
| Audit an implicit state machine or a risky event ordering | [state-machine-audit](../skills/state-machine-audit/SKILL.md) | The closest existing test or model checker when the question requires it | Source-backed transitions, a scoped result, and a chart derived from the same evidence |
| Explain a system visually | [diagram-design](../skills/diagram-design/SKILL.md) for static diagrams or searchable graph maps; [system-anatomy](../skills/system-anatomy/SKILL.md) for spatial explainers | Source, interaction and rendered-output checks | Accurate relationships, working tracing and comparison, and checked exports |
| Explain a moving physical mechanism | [system-anatomy](../skills/system-anatomy/SKILL.md) and its [mechanism branch](../skills/system-anatomy/references/mechanisms.md) | Existing project renderer or the bundled offline slider-crank example; film delivery when requested | Declared inputs, units and assumptions, numerical checks, accessible controls and a checked artifact |
| Prepare source-backed writing | [extract-documents](../skills/extract-documents/SKILL.md), then [deslop](../skills/deslop/SKILL.md) when needed | Explicit distribution workflow for social drafts | Claims you can trace, source locations checked, and input/output accounting reconciled |
| Promote owned work and review traffic | [content-marketing](../skills/content-marketing/SKILL.md) | [thumbnail-production](../skills/thumbnail-production/SKILL.md), film production, or explicit distribution drafting when requested | Channel briefs backed by sources, checked links, decision rules set before results and results measured over comparable periods |
| Learn what works for peers and audiences | [social-research](../skills/social-research/SKILL.md) | [content-marketing](../skills/content-marketing/SKILL.md) to plan the next experiment | Each account's gain over its peers with raw numbers, audience claims quoted with where they appear, or a plain statement that evidence is too thin |
| Cut short clips from a long video | [repurpose-long-video](../skills/repurpose-long-video/SKILL.md) | [Local export](../skills/repurpose-long-video/references/clip-export.md), then [motion-film](../skills/motion-film/SKILL.md) caption and export checks; explicit distribution drafting for posts | Rights confirmed, clips checked in context, frames reviewed, outputs inspected and an edit list for each clip |
| Retrieve exact technical documentation | [find-docs](../skills/find-docs/SKILL.md) | Current repository implementation | Primary documentation for the exact version in use |
| Resume or reassess existing PR work | [continue-pr](../skills/continue-pr/SKILL.md) | Repository delivery plus optional [monitor-pr](../skills/monitor-pr/SKILL.md) for live PR watching | The original intent recovered, current architecture checked, contributors credited and the continuation checked |
| Plan dependencies across several PRs | [plan-pr-stack](../skills/plan-pr-stack/SKILL.md) | Repository delivery plus [monitor-pr](../skills/monitor-pr/SKILL.md) for each live PR | Proposed merge waves tied to one snapshot, open dependencies listed and overlap decisions recorded |
| Watch CI and review on a PR | [monitor-pr](../skills/monitor-pr/SKILL.md) | Authorized fixes and repository delivery gates | Events you can resume from, readiness checked independently and the watcher stopped at the end |
| Clean stale branches, PRs, and worktrees | [repository-cleanup](../skills/repository-cleanup/SKILL.md) | Delegated recovery, repository delivery and safe cleanup | Every branch, worktree and stash accounted for, useful work landed or kept, only the named targets removed and proof they can be recovered |
| Assess and refresh worktrees | [refresh-worktrees](../skills/refresh-worktrees/SKILL.md) | Repository setup and checks | Local work kept, and each worktree confirmed on the right base and revision |
| Write or revise Swift code | [write-swift](../skills/write-swift/SKILL.md) | Target build/tests and platform UI guidance when needed | Supported toolchain and isolation owners checked, cancellation/errors preserved and build evidence separated from device behavior |

Explicit workflows require a named invocation. Use `/name` in Claude Code or `$name` in
Codex; respect the catalog's harness restrictions.

| Explicit request | Skill |
| --- | --- |
| Vet linked sources and harvest lessons, or research the whole catalog | [skill-research](../skills/skill-research/SKILL.md), with URLs for a focused assessment |
| Audit and behavior-test an existing skill | [harden-skill](../skills/harden-skill/SKILL.md) |
| Review client/API integration | [review-integration](../skills/review-integration/SKILL.md) |
| Clean out code comments, extract ADRs, draft excuse issues, and install a comment-ban ratchet | [delete-comment](../skills/delete-comment/SKILL.md) |
| Run the full delegated animation loop | [polish-animations](../skills/polish-animations/SKILL.md) |
| Take branch work (or authorized in-scope dirty branch paths) to merged | [land-pr](../skills/land-pr/SKILL.md) |
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
