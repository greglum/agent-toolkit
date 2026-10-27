# Improving a portfolio with skills and small swarms

Use this example to assess an existing portfolio, make bounded changes, and check the
result in another round. These prompts work with Claude Code or Codex. Each run discovers
the target repository's current rules, owners, and checks.

## Choose skills from the task

Start with the [workflow map](../workflows.md). Read the selected skill before using it.

| Task | Choose when needed |
| --- | --- |
| Improve a visitor's discovery journey or redesign a surface | [web-app-design](../../skills/web-app-design/SKILL.md) |
| Measure width, height, sticky chrome, or dense content | [fit-surface](../../skills/fit-surface/SKILL.md) |
| Diagnose generic layout or repeated product copy | [deslop-ui](../../skills/deslop-ui/SKILL.md) |
| Diagnose existing loading or transition behavior | [ui-motion](../../skills/ui-motion/SKILL.md) |
| Review a diff against the project's coding rules | [global-code-review](../../skills/global-code-review/SKILL.md) |
| Update affected documentation and check prose | [docs-sync](../../skills/docs-sync/SKILL.md), [deslop](../../skills/deslop/SKILL.md) |

Load the skills that match the actual work. A discovery audit need not become a redesign,
and a source finding does not establish a rendered failure. The repository's design system,
primitives, accessibility rules, and required gates govern the work.

## Round 1: assess the current journey

Replace bracketed values before copying. This prompt authorizes the named swarm to inspect
local source and the local app. Remove browser work when that access is outside the task.

```text
Assess [routes and visitor task] at [repository and revision]. Begin at AGENTS.md,
then read the design owner, relevant tokens, state owners, and required checks.
Use web-app-design; use fit-surface when geometry or viewport coverage matters.
Consider what a fresh design would do differently before proposing edits.

Use a small swarm: one worker traces the journey and URL/state contracts; another
checks layout, accessibility, and the relevant rendered states. Give each worker
its own question and original source. Keep one parent responsible for integration.
Do not share proposed findings between workers before their reports are complete.

Change no source. Preserve ongoing builds and unrelated work. Use local fixtures;
do not call paid models, production APIs, or submit forms that write real data.
Report up to four useful improvements with the input that exposes each problem,
source ownership, evidence, confidence, and the next check. Distinguish observed
failures, source defects, and hypotheses. Record every uninspected matrix cell.
The parent must check claims against source, API contracts, and rendered evidence
before selecting a bounded implementation. A supported no-change result is valid.
```

Keep a short record with the source revision, route/state, finding, owner, disposition,
and evidence location. Separate worker reports help preserve disagreements. For a skill
comparison, add a fresh no-skill control on the same input and revision. Keep expected
findings out of both prompts. Use an author-independent judge, as described in
[authoring](../authoring.md#evaluating). One pair cannot establish general superiority.

## Round 2: make the accepted changes

Choose findings only after checking their evidence. This prompt authorizes local edits
and local verification in the named scope. Publication and deployment need separate authority.

```text
Implement [accepted findings and acceptance conditions] in [target repository].
Read AGENTS.md and the current owners first. Preserve unrelated dirty files and
use a task-owned worktree where the repository requires isolation.

Use the relevant skills selected in the assessment. Keep one integration owner.
Delegate only independent changes with explicit file ownership; keep a shared
hook or state contract with one worker. Preserve existing tokens, primitives,
URLs, keyboard behavior, full initial content, and accessibility contracts.
Choose the smallest change that satisfies the visitor task.

Record decisions where the brief leaves a choice. Add tests only under the
project's test policy; retain existing tests and required gates. Run the closest
meaningful checks and inspect affected callers. Measure the changed journey in
the local app across its supported widths, themes, motion settings, and states.

Stop dependent work on failure and diagnose safely. Report PASS, FAIL,
UNAVAILABLE, and NOT RUN separately. Do not commit, push, merge, publish, deploy,
spend money, or write production data without authority for that action and target.
```

## Round 3: review the final change independently

```text
Review [base revision] through [final revision or task-owned diff]. Use fresh
reviewers who did not implement the change. Give them the original task, acceptance
conditions, source, and repository rules before giving them implementation claims.
Use the relevant review skill after checking its actual scope.

Split review questions: one reviewer checks behavior, URL/state preservation,
and regressions; another checks rendered layout, keyboard/focus, and accessibility.
Include dedicated security coverage when the repository or change requires it.
Recheck every claimed fix against original evidence. Challenge rejected hypotheses
as well as accepted findings. The parent resolves conflicting reports with evidence.

Do not edit source during review. Report actionable findings with locations and
reproduction inputs. Say which checks ran and which remain unverified. If a fix
changes the reviewed source, check the affected conditions again at the new revision.
Finish when acceptance and required gates pass, or report the remaining blocker.
```

Use another bounded round when a real failure remains. Keep the finding ledger and stop
condition. Completing a round alone does not justify adding work or rerunning passed checks.
