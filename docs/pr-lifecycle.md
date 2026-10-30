# Carry a PR through its requested finish

Choose the user's finish first. Local completion, PR creation, readiness, merge and deployed
behavior are different outcomes. Skills provide procedures; authority comes from the task.

| Stage | Owner | What carries forward | Finish evidence |
| --- | --- | --- | --- |
| Recover inherited or old work | [continue-pr](../skills/continue-pr/SKILL.md) | Original goal, corrections, source and current endpoints, unresolved findings, human credit | Continue/rework/superseded disposition supported by current architecture |
| Implement and prove | Repository implementation and verification workflow | Scope, task-owned files, required gates, observed behavior | Checks on the final implementation, with limits stated |
| Review | Repository review or a requested catalog reviewer | Immutable comparison, governing instructions, path coverage, finding IDs | Revision-bound verdict; material findings fixed or explained |
| Publish | Repository publication workflow; [create-pr](../skills/create-pr/SKILL.md) when explicitly invoked in Codex | Exact repository/head/base, complete change scope and proof | Verified created or existing PR; no implied readiness |
| Reconcile CI/review | [monitor-pr](../skills/monitor-pr/SKILL.md) | Live endpoints, current gates, unresolved findings and watcher ownership | Ready, waiting or blocked, independently assessed from event notifications |
| Merge or hand off | Repository delivery workflow | Verified gates, action authority and final head | Open and unmerged, or verified merge commit, according to the request |

For several dependent PRs, [plan-pr-stack](../skills/plan-pr-stack/SKILL.md) can build candidate
waves from a supplied snapshot. Unknown file coverage, outside dependencies and ambiguous
overlap remain explicit. This ordering artifact does not establish readiness; each landing
still requires fresh repository gates and action authority.

For a requested fix-and-review loop, set a bounded round/time budget in the task record.
Use the existing harness/model unless the user chose another. Give a reviewer the original
intent, fixed comparison and checks. Independently verify its findings. Track stable IDs;
a later pass checks changed code, open findings and invalidated context. A score, reviewer
agreement or a round limit does not establish that repository gates passed. A missing reply
leaves review incomplete. A disputed material concern remains visible at the budget boundary. Review does not expand the task.

`review-pr` owns one read-only verdict and its repeated-review evidence rules, not an author
loop. Multi-provider execution needs the user's provider and data scope. This guide does not
install a review service, launch other models, or create recurring monitoring.

For a leave-unmerged finish, account for pre-existing auto-merge and merge queue entries before
pushing. Do not silently disable another actor's configuration. A missing decision can block
that write while local preparation and read-only checks continue. For an authorized merge,
recheck the live head/base, review and check requirements and repository merge method. Honor
branch protection and queue policy. Never bypass them. Then verify the recorded merge; a merge
does not prove deployment or live behavior unless the requested workflow checks those too.

The continuation and monitoring bundles include their own source notes. Install only the
owners the task needs; these stages do not require a shared orchestration service.
