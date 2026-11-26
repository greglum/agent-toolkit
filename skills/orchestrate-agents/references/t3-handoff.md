# T3 handoff and recovery

Follow the host's orchestration instructions and the live tool schema. If a required route is unavailable, report which lane is blocked. Use native same-provider subagents when the host directs. Use an app-owned child for a lane that needs a different provider or a T3-managed worktree.

## Give each child a self-contained brief

Include the outcome, exact base or artifact, owned paths, dependencies, permitted actions, and the checks the child must return. T3 app-owned children receive the brief without the parent conversation. Put necessary facts in the brief and verify that referenced files are readable on the child's environment. A managed worktree starts from the committed base. For a lane that depends on local edits, confirm its input can actually include them before launch.

Request the designated provider instance and live model options. Inherit the parent's permission ceiling. When read-only behavior is required, use a reader mode the provider actually supports or preserve the lane as unrun. A role label alone does not enforce file access.

## Collect the result

Keep the identifiers in the existing task record when work spans turns. Record lane, task ID, child link, input revision, requested and reported model, output revision or artifact, and required checks. Follow the runner's returned completion instruction. Keep a paused approval or blocked lane visible. Use a fresh reviewer for a changed candidate and provide the original brief, exact candidate, findings, and open objections.

The parent verifies the candidate and any required checks at the integrated revision. Use the repository's delivery gates and merge only the exact reviewed head. When that head changes, obtain fresh review and recheck whether the existing authorization covers the new changes. Identify absent or denied checks explicitly and reserve pushes, merges, deployment, or cleanup for covered authority.

## Reconcile on resume

Read the task record and reconcile completed, active, blocked, and cancelled lanes against the host before dispatching. Reuse accepted work if its required evidence still applies. Preserve unresolved outputs before cancelling or reassigning ownership. Treat a new head or changed input as a reason to recheck affected evidence. Keep a child worktree until its output is safely transferred and any cleanup is authorized.

See [T3 host orchestration instructions](https://github.com/pingdotgg/t3code/blob/main/packages/provider-core/src/server/orchestrationInstructions.ts) and [T3 context transfer](https://github.com/pingdotgg/t3code/blob/main/docs/orchestration-v2/thread-lineage-and-context-transfer.md).

The brief-only stop and resume checks draw on [Copybook’s MIT-licensed standalone coordinator](https://github.com/Heyvhuang/copybook-skills/tree/25e0f98415098366601cfd9e0b37d8e5ae387cb7/standalone/coordinator), reviewed November 25, 2026. This skill uses T3’s completion signals and the parent’s permission ceiling.
