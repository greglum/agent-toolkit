# Skill catalog

Choose a job in the [workflow map](workflows.md), or browse every skill below.
From the clone's root, preview an individual install with
`python3 scripts/install.py --dry-run --only name`. Remove `--dry-run` after reviewing it.

“Automatic” means the agent can select a skill from its description. “By name” requires
`/name` in Claude Code or `$name` in Codex. Codex-only skills have names that could shadow a project's own skills; the installer skips their Claude Code and Antigravity links.
[harnesses.json](../harnesses.json) records those names. Each bundle includes the
references and tools it needs. Extra runtime tools are listed in its `compatibility` field.

| Skill | What it does | Runs |
| --- | --- | --- |
| [`acp`](../skills/acp/SKILL.md) | Review task-owned changes, commit them in cohesive groups, and push to the authorized destination. | By name, Codex only |
| [`agent-readiness`](../skills/agent-readiness/SKILL.md) | Assess a repository for agent work, then plan and implement requested improvements (defaults to assessment-only when edit mode is unclear). | Automatic |
| [`analyze-agent-history`](../skills/analyze-agent-history/SKILL.md) | Analyze this repository's agent sessions, or supplied exports, into text-free correction candidates and coverage counts. | Automatic |
| [`animate`](../skills/animate/SKILL.md) | Build interface motion with purposeful timing, interruption, and reduced-motion behavior. | Automatic |
| [`app-verifier`](../skills/app-verifier/SKILL.md) | Record and prove how to launch an app, reach its features, and check their results. | Automatic |
| [`audit-ai-code`](../skills/audit-ai-code/SKILL.md) | Audit changed code after AI work for AI-authoring defects and apply minimal --fix edits when requested. | Automatic |
| [`bounded-generative-ui`](../skills/bounded-generative-ui/SKILL.md) | Design, build, or review model-selected component layouts that preserve app-owned facts and evidence. | Automatic |
| [`cloud-ops-audit`](../skills/cloud-ops-audit/SKILL.md) | Audit recurring cloud alerts, reconcile live spend and free-tier cliffs against IaC and docs, and check cross-cloud cost-bound parity. | Automatic |
| [`codebase-metrics`](../skills/codebase-metrics/SKILL.md) | Score codebase or task/harness quality against a frozen eight-dimension profile and run recurring repository audits. | Automatic |
| [`compare-experiments`](../skills/compare-experiments/SKILL.md) | Compare paired observations with visible missing/failure evidence and selected-candidate confirmation. | Automatic |
| [`content-marketing`](../skills/content-marketing/SKILL.md) | Plan and review source-backed campaigns (briefs, UTM links, matched-window reviews) for owned web, YouTube, and LinkedIn. | Automatic |
| [`continue-pr`](../skills/continue-pr/SKILL.md) | Recover inherited work or reassess an old PR before continuing it. | Automatic |
| [`create-pr`](../skills/create-pr/SKILL.md) | Create a PR after checking the repository, head, base, push destination, and existing PRs. | By name, Codex only |
| [`delete-comment`](../skills/delete-comment/SKILL.md) | Audit and delete non-directive code comments, move decisions into ADRs, draft excuse issues, and set up a comment-ban ratchet. | By name |
| [`delete-first`](../skills/delete-first/SKILL.md) | Remove dead code and overbuilt layers in the requested scope using blind refutation. | Automatic |
| [`deslop`](../skills/deslop/SKILL.md) | Edit prose and interface copy for AI writing patterns while preserving meaning. | Automatic |
| [`deslop-ui`](../skills/deslop-ui/SKILL.md) | Review and improve repetitive layouts, generic copy, and other AI-looking UI patterns. | Automatic |
| [`diagram-design`](../skills/diagram-design/SKILL.md) | Create or redraw static diagrams or searchable graph maps with tracing, comparison, and export. | Automatic |
| [`distribution-draft`](../skills/distribution-draft/SKILL.md) | Prepare source-backed LinkedIn and X drafts for human review; never posts them. | By name |
| [`docs-sync`](../skills/docs-sync/SKILL.md) | Audit or update project documentation against current source, commands, plans, and ownership. | Automatic |
| [`encode-correction`](../skills/encode-correction/SKILL.md) | Turn repeated mistakes into constraints at the source of the problem. | Automatic |
| [`extract-documents`](../skills/extract-documents/SKILL.md) | Extract document collections and reconcile input coverage, provenance and content-loss records. | Automatic |
| [`find-animation-opportunities`](../skills/find-animation-opportunities/SKILL.md) | Identify useful interface motion and explain where motion would not help. | Automatic |
| [`find-bug-variants`](../skills/find-bug-variants/SKILL.md) | Find and verify other instances of an already confirmed defect. | Automatic |
| [`find-docs`](../skills/find-docs/SKILL.md) | Resolve uncertain technical behavior against exact-version primary documentation. | Automatic |
| [`fit-surface`](../skills/fit-surface/SKILL.md) | Measure and fix a web surface across viewports, chrome, themes, and content states. | Automatic |
| [`global-code-review`](../skills/global-code-review/SKILL.md) | Review a diff against user-specified and repository coding standards. | Automatic |
| [`graph-engineering`](../skills/graph-engineering/SKILL.md) | Trace source-backed dependencies and blast radius for read-only impact questions or verified edits. | Automatic |
| [`guided-review`](../skills/guided-review/SKILL.md) | Build a human reading guide for a PR or significant diff. | Automatic |
| [`harden-skill`](../skills/harden-skill/SKILL.md) | Audit, revise, and behavior-test an existing skill or declared portfolio across supported agent clients. | By name |
| [`iac-teardown`](../skills/iac-teardown/SKILL.md) | Preflight traps and execute safe Terraform or OpenTofu stack decommissioning and cross-stack state migrations. | By name |
| [`land-pr`](../skills/land-pr/SKILL.md) | Take branch work (or authorized in-scope dirty branch paths) from ready to merged through review, fixes, gates, and repo-allowed merge. | By name |
| [`learn-domain`](../skills/learn-domain/SKILL.md) | Build a cited domain primer, glossary, source map and ranked SME questions for an unfamiliar field. | Automatic |
| [`learn-taste`](../skills/learn-taste/SKILL.md) | Carry verified lessons into project standards or skill guidance. | Automatic |
| [`loop-engineering`](../skills/loop-engineering/SKILL.md) | Run bounded improve, review, and verify iterations against fixed acceptance conditions. | Automatic |
| [`map-data-source`](../skills/map-data-source/SKILL.md) | Survey unfamiliar files or a SQLite database, prove grain and keys, score joins, and write an evidence-backed data dictionary. | Automatic |
| [`monitor-pr`](../skills/monitor-pr/SKILL.md) | Watch PR events and independently assess CI, reviews, and readiness. | Automatic |
| [`motion-film`](../skills/motion-film/SKILL.md) | Create and check films, with rendered, audio, export, and editable-handoff proof. | Automatic |
| [`onboard-data`](../skills/onboard-data/SKILL.md) | Sequence domain learning and data mapping for a new project, then merge their open questions. | By name |
| [`plan-pr-stack`](../skills/plan-pr-stack/SKILL.md) | Plan candidate dependency waves from a supplied PR snapshot, without claiming merge readiness. | Automatic |
| [`polish-animations`](../skills/polish-animations/SKILL.md) | Coordinate the full interface-motion assessment, build, review, and verification loop. | By name |
| [`postgres-investigate`](../skills/postgres-investigate/SKILL.md) | Investigate PostgreSQL query, lock, connection, and row-security behavior. | Automatic |
| [`reconcile-metric`](../skills/reconcile-metric/SKILL.md) | Trace a disputed aggregate to source records and recalculate it independently. | Automatic |
| [`refresh-worktrees`](../skills/refresh-worktrees/SKILL.md) | Assess and refresh Git worktrees while preserving local and uncertain work. | Automatic |
| [`repository-cleanup`](../skills/repository-cleanup/SKILL.md) | Recover useful unfinished work and clean verified completed local or remote branches, PRs, and worktrees. | Automatic |
| [`repurpose-long-video`](../skills/repurpose-long-video/SKILL.md) | Select and export short clips from cleared local footage, supplied timings and fixed crops. | Automatic |
| [`retro`](../skills/retro/SKILL.md) | Triage recent work across the retro focuses and run the two most useful. | Automatic |
| [`retro-agent-context`](../skills/retro-agent-context/SKILL.md) | Find instructions, docs and indexes that mislead agents or near an instruction/context budget limit, and report the fix for each. | Automatic |
| [`retro-agent-friction`](../skills/retro-agent-friction/SKILL.md) | Count recurring agent friction in this repository's sessions and report the durable fix for each. | Automatic |
| [`retro-guardrails`](../skills/retro-guardrails/SKILL.md) | Find mistakes that recur in recent commits and reviews, check earlier controls, and report which lessons deserve a control. | Automatic |
| [`retro-verification`](../skills/retro-verification/SKILL.md) | Trace defects that got past tests, gates, self-scores or review, and route the missing layer to the nearest suite owner or encode-correction. | Automatic |
| [`review-animations`](../skills/review-animations/SKILL.md) | Audit existing motion for purpose, timing, interruption, cost, and reduced motion. | Automatic |
| [`review-integration`](../skills/review-integration/SKILL.md) | Review client/API contracts, transformations, validation, and error handling. | By name |
| [`review-pending-changes`](../skills/review-pending-changes/SKILL.md) | Review staged, unstaged, untracked, renamed, and deleted work before committing. | By name, Codex only |
| [`review-pr`](../skills/review-pr/SKILL.md) | Review an open PR or local branch diff (and repeat reviews) for defects, spec fit, and standards; read-only unless PR comment is authorized. | By name, Codex only |
| [`review-recent-commits`](../skills/review-recent-commits/SKILL.md) | Review selected Git history against repository rules and the current state. | By name, Codex only |
| [`review-source`](../skills/review-source/SKILL.md) | Audit named current source, including unchanged files, with stack-specific source contract references. | Automatic |
| [`security-audit`](../skills/security-audit/SKILL.md) | Model threats, triage SARIF scanner reports, verify security boundaries, and remediate confirmed findings when requested. | Automatic |
| [`simplify-code`](../skills/simplify-code/SKILL.md) | Simplify code while preserving behavior; supports comment-only audit or cleanup scopes. | Automatic |
| [`skill-research`](../skills/skill-research/SKILL.md) | Vet linked sources or research the catalog and apply supported improvements. | By name |
| [`social-research`](../skills/social-research/SKILL.md) | Research public posts and comments for outliers and source-backed audience questions. | Automatic |
| [`state-machine-audit`](../skills/state-machine-audit/SKILL.md) | Trace implicit state, check risky transitions, and draw a source-backed statechart. | Automatic |
| [`system-anatomy`](../skills/system-anatomy/SKILL.md) | Create or audit an interactive anatomy, cutaway, or spatial explanation grounded in source. | Automatic |
| [`telemetry-anomalies`](../skills/telemetry-anomalies/SKILL.md) | Detect, calibrate and score anomalies in multichannel sensor telemetry at event level against a false-alarm budget. | Automatic |
| [`telemetry-contract`](../skills/telemetry-contract/SKILL.md) | Check sensor data against a declared contract for units, rates, ranges, saturation, timestamps and ingest lag. | Automatic |
| [`temporal-validation`](../skills/temporal-validation/SKILL.md) | Plan and audit leakage-safe validation for time-ordered or grouped data, with baselines on the same folds. | Automatic |
| [`thumbnail-production`](../skills/thumbnail-production/SKILL.md) | Create, revise, or review post-release tests for YouTube thumbnails, LinkedIn video covers, and social images from cleared sources. | Automatic |
| [`to-spec`](../skills/to-spec/SKILL.md) | Turn the current conversation into a spec with scope, decisions, and acceptance conditions. | Automatic |
| [`tune-tests`](../skills/tune-tests/SKILL.md) | Audit, speed up, or prune tests while preserving live failure detection and required gates. | Automatic |
| [`ui-motion`](../skills/ui-motion/SKILL.md) | Diagnose and fix existing loading continuity, transitions, overlays, gestures, and stutter in a running app. | Automatic |
| [`web-app-design`](../skills/web-app-design/SKILL.md) | Design, build, redesign, or audit a web app from references, or derive/apply DESIGN.md. | Automatic |
| [`write-swift`](../skills/write-swift/SKILL.md) | Implement Swift changes with explicit toolchain, isolation, cancellation and error contracts. | Automatic |

See [name migrations](migrations.md) before updating an older install.
