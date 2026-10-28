# Skill catalog

Choose a job in the [workflow map](workflows.md), or browse every skill below.
From the clone's root, preview an individual install with
`python3 scripts/install.py --dry-run --only name`. Remove `--dry-run` after reviewing it.

“Automatic” means the agent can select a skill from its description. “By name” requires
`/name` in Claude Code or `$name` in Codex. Five Git workflows are Codex-only; the installer skips their Claude Code links.
[harnesses.json](../harnesses.json) records those names. Each bundle includes the
references and tools it needs. Extra runtime tools are listed in its `compatibility` field.

| Skill | What it does | Runs |
| --- | --- | --- |
| [`acp`](../skills/acp/SKILL.md) | Review task-owned changes, commit them in cohesive groups, and push to the authorized destination. | By name, Codex only |
| [`agent-readiness`](../skills/agent-readiness/SKILL.md) | Assess a repository for agent work, then plan and implement supported improvements. | Automatic |
| [`animate`](../skills/animate/SKILL.md) | Build interface motion with purposeful timing, interruption, and reduced-motion behavior. | Automatic |
| [`app-verifier`](../skills/app-verifier/SKILL.md) | Record and prove how to launch an app, reach its features, and check their results. | Automatic |
| [`codebase-metrics`](../skills/codebase-metrics/SKILL.md) | Measure codebase quality against a fixed rubric with source evidence. | Automatic |
| [`content-marketing`](../skills/content-marketing/SKILL.md) | Plan source-backed website, YouTube and LinkedIn content, then compare matched measurement windows. | Automatic |
| [`continue-pr`](../skills/continue-pr/SKILL.md) | Recover inherited work or reassess an old PR before continuing it. | Automatic |
| [`create-pr`](../skills/create-pr/SKILL.md) | Create a PR after checking the repository, head, base, push destination, and existing PRs. | By name, Codex only |
| [`deslop`](../skills/deslop/SKILL.md) | Edit prose and interface copy for AI writing patterns while preserving meaning. | Automatic |
| [`deslop-ui`](../skills/deslop-ui/SKILL.md) | Review and improve repetitive layouts, generic copy, and other AI-looking UI patterns. | Automatic |
| [`diagram-design`](../skills/diagram-design/SKILL.md) | Create static diagrams or searchable graph maps with tracing, comparison, and export. | Automatic |
| [`distribution-draft`](../skills/distribution-draft/SKILL.md) | Prepare source-backed LinkedIn and X drafts for human review; never posts them. | By name |
| [`docs-sync`](../skills/docs-sync/SKILL.md) | Check or update project documentation against current source and commands. | By name |
| [`encode-correction`](../skills/encode-correction/SKILL.md) | Turn repeated mistakes into constraints at the source of the problem. | Automatic |
| [`extract-documents`](../skills/extract-documents/SKILL.md) | Extract document collections with source locators, provenance, and content-loss records. | Automatic |
| [`find-animation-opportunities`](../skills/find-animation-opportunities/SKILL.md) | Identify useful interface motion and explain where motion would not help. | Automatic |
| [`find-bug-variants`](../skills/find-bug-variants/SKILL.md) | Find and verify other instances of an already confirmed defect. | Automatic |
| [`find-docs`](../skills/find-docs/SKILL.md) | Resolve uncertain technical behavior against exact-version primary documentation. | Automatic |
| [`fit-surface`](../skills/fit-surface/SKILL.md) | Measure and fix a web surface across viewports, chrome, themes, and content states. | Automatic |
| [`global-code-review`](../skills/global-code-review/SKILL.md) | Review a diff against user-specified and repository coding standards. | Automatic |
| [`graph-engineering`](../skills/graph-engineering/SKILL.md) | Trace source-backed dependencies and change impact, then verify affected consumers. | Automatic |
| [`guided-review`](../skills/guided-review/SKILL.md) | Build a human reading guide for a PR or significant diff. | Automatic |
| [`harden-skill`](../skills/harden-skill/SKILL.md) | Audit, revise, and behavior-test an existing skill across supported agent clients. | By name |
| [`loop-engineering`](../skills/loop-engineering/SKILL.md) | Run bounded improve, review, and verify iterations against fixed acceptance conditions. | Automatic |
| [`monitor-pr`](../skills/monitor-pr/SKILL.md) | Watch PR events and independently assess CI, reviews, and readiness. | Automatic |
| [`motion-film`](../skills/motion-film/SKILL.md) | Create and check films, with rendered, audio, export, and editable-handoff proof. | Automatic |
| [`polish-animations`](../skills/polish-animations/SKILL.md) | Coordinate the full interface-motion assessment, build, review, and verification loop. | By name |
| [`postgres-investigate`](../skills/postgres-investigate/SKILL.md) | Investigate PostgreSQL query, lock, connection, and row-security behavior. | Automatic |
| [`reconcile-metric`](../skills/reconcile-metric/SKILL.md) | Trace a disputed aggregate to source records and recalculate it independently. | Automatic |
| [`refresh-worktrees`](../skills/refresh-worktrees/SKILL.md) | Assess and refresh Git worktrees while preserving local and uncertain work. | Automatic |
| [`repository-cleanup`](../skills/repository-cleanup/SKILL.md) | Recover useful unfinished work and clean verified completed branches and worktrees. | Automatic |
| [`repurpose-long-video`](../skills/repurpose-long-video/SKILL.md) | Select context-preserving short clips from cleared footage and produce an edit list. | Automatic |
| [`review-animations`](../skills/review-animations/SKILL.md) | Audit existing motion for purpose, timing, interruption, cost, and reduced motion. | Automatic |
| [`review-integration`](../skills/review-integration/SKILL.md) | Review client/API contracts, transformations, validation, and error handling. | By name |
| [`review-pending-changes`](../skills/review-pending-changes/SKILL.md) | Review staged, unstaged, untracked, renamed, and deleted work before committing. | By name, Codex only |
| [`review-pr`](../skills/review-pr/SKILL.md) | Review a committed PR diff for defects, unnecessary complexity, and guideline compliance. | By name, Codex only |
| [`review-recent-commits`](../skills/review-recent-commits/SKILL.md) | Review selected Git history against repository rules and the current state. | By name, Codex only |
| [`review-source`](../skills/review-source/SKILL.md) | Audit named current source, including unchanged files, with conditional runtime checks. | By name |
| [`security-audit`](../skills/security-audit/SKILL.md) | Verify repository security findings and remediate confirmed issues when requested. | Automatic |
| [`simplify-code`](../skills/simplify-code/SKILL.md) | Simplify code while preserving behavior; supports explicitly requested comment-only work. | Automatic |
| [`skill-research`](../skills/skill-research/SKILL.md) | Vet linked sources or research the catalog and apply supported improvements. | By name |
| [`social-research`](../skills/social-research/SKILL.md) | Research public posts and comments for outliers and source-backed audience questions. | Automatic |
| [`system-anatomy`](../skills/system-anatomy/SKILL.md) | Create an interactive anatomy, cutaway, or spatial explanation grounded in source. | Automatic |
| [`thumbnail-production`](../skills/thumbnail-production/SKILL.md) | Create YouTube thumbnails, LinkedIn video covers, and social images from cleared sources. | Automatic |
| [`to-spec`](../skills/to-spec/SKILL.md) | Turn the current conversation into a spec with scope, decisions, and acceptance conditions. | Automatic |
| [`tune-tests`](../skills/tune-tests/SKILL.md) | Audit, prune, or speed up tests while preserving failure detection and required gates. | By name |
| [`ui-motion`](../skills/ui-motion/SKILL.md) | Diagnose and fix loading continuity, transitions, overlays, and gestures in a running app. | Automatic |
| [`web-app-design`](../skills/web-app-design/SKILL.md) | Build or redesign a web app from researched references, or document its design language. | Automatic |

See [name migrations](migrations.md) before updating an older install.
