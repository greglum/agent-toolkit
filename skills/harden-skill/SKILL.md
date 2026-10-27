---
name: harden-skill
description: >-
  Audit, revise, and evidence-test one existing Agent Skill or the declared portfolio
  across Codex, Claude Code, GitHub Copilot, and compatible clients. Invoke explicitly
  with $harden-skill PATH, /harden-skill PATH, or /harden-skill portfolio. Do not use to
  create a new skill from scratch, or to research outside sources for the catalog (use
  skill-research).
disable-model-invocation: true
---

# /harden-skill

Invocation guard: Run this workflow only when the user explicitly names `$harden-skill` or
`/harden-skill`. If selected implicitly, stop without taking action and tell the user to invoke it
by name.

Improve existing skills in place only after staged candidates beat or match their current
versions. Treat repository rules and local canonical/wrapper conventions as authoritative.

## Input and modes

Accept one skill directory or `SKILL.md` path, resolving relative paths from the current
working directory. The literal `portfolio` selects the declared portfolio; in that mode,
read [`references/portfolio.md`](references/portfolio.md) in full and follow its scope,
isolation, integration, and disposition protocol instead of the single-target workflow below.

Default to **apply and verify**. Honor these modifiers wherever they appear:

- `audit only`: inspect and report; do not edit the target, wrappers, or repository docs.
- `focus on triggering`: prioritize discovery, description boundaries, conflicts, and
  observable trigger tests while still running structural checks.
- `full benchmark`: use the repeated train/validation protocol in
  [`references/evaluation.md`](references/evaluation.md), not the adaptive default.
- `keep eval artifacts`: persist the evaluation workspace at a user-visible path;
  otherwise use the operating system's temporary directory and leave no repo artifacts.

## Workflow

1. **Resolve the target.** Find the canonical skill, referral wrappers, repository rules,
   nearby skill catalogs, harness metadata, validators, and git status. Run
   `scripts/inspect_skill.py <skill-directory> --profile auto`. If the input is a wrapper,
   follow its referral and operate on the canonical body. Record pre-existing changes and
   never overwrite unrelated work. Before running target-supplied validators, scripts,
   hooks, or setup, inventory the whole bundle and trace its execution and data effects
   using the [trust intake](references/rubric.md#whole-bundle-trust-intake). The known local
   inspector is a structural check; a target's executable validator is a separate trust decision.

2. **Snapshot before reasoning about edits.** Following
   [`references/apply.md`](references/apply.md#snapshot) for workspace placement, the path
   set, and the snapshot command, build an external workspace whose repo-shaped `baseline/`
   is then copied entire to `candidate/`. Record target paths, profile, and validators, then
   snapshot the selected live paths. Never place a patch, draft, or transient workspace in
   the current repository. If no external temp root is writable, request access or report
   the blocker before editing.

3. **Audit with evidence.** Read [`references/rubric.md`](references/rubric.md) in full.
   Score every dimension against cited files, lines, validator output, or observed runs.
   Check adjacent skill descriptions for trigger conflicts. Separate structural errors,
   behavioral gaps, and optional improvements; a numeric score never cancels a blocker.
   In `audit only` mode, report here and verify the target hash and git diff are unchanged.

4. **Build one coherent candidate.** Edit only the external candidate bundle. Preserve valuable
   local extensions and reduce duplication before adding instructions. Keep `SKILL.md`
   operational; move detail into directly linked references. Update scripts and linked
   resources together. Stage required wrapper, catalog, routing, test, and documentation changes
   in the same bundle rather than deferring them until after the skill is live. Run the static
   checker and every discovered target validator on the staged candidate where possible.

5. **Compare behavior in isolation.** Read
   [`references/evaluation.md`](references/evaluation.md) in full and run its
   baseline-versus-candidate cases. Grade checkable assertions with concrete evidence,
   then review qualities that need human judgment.

6. **Test triggering when relevant.** If the description changed or the reported problem
   is triggering, run five realistic positive and five near-miss negative queries once.
   Rerun only failures twice, using invocation logs or an equivalent trace that proves the
   target `SKILL.md` was loaded. For an explicit-only target, verify suppression metadata
   and one explicit invocation instead. Never report trigger accuracy from inferred
   behavior or final-answer quality.

7. **Apply only a passing candidate.** Require structural checks to pass and behavioral
   results to show no material regression. Snapshot `candidate/`, preview the bundle apply,
   and review the exact writes, baseline-owned deletions, and preserved post-snapshot files;
   [`references/apply.md`](references/apply.md#apply) has the commands and the helper's
   guarantees. Rerun with `--apply` only while both manifests still match. Do not install or
   apply a failing or drifted candidate.

8. **Verify the live result.** Re-run the static checker, repository validators, link
   checks, tests for bundled code, and `git diff --check` where applicable. Compare the
   live target to the candidate and inspect the final diff for unrelated changes. Remove
   temporary artifacts unless persistence was requested.

## Completion contract

An `audit only` run finishes after the evidence audit when it reports the canonical target,
wrappers, profiles, rules, dirty state, validator output, rubric scores, findings, trigger
evidence or observability limit, and unchanged before/after hashes. It does not require a
candidate, comparison run, or applied files.

An apply run finishes only when the report states:

- canonical target, wrappers, harness profiles, repo rules, dirty state, and snapshot path;
- before/after rubric evidence and every material change;
- baseline-versus-candidate cases, assertions, results, and any human-review need;
- trigger evidence, or an explicit `not applicable` / `not observable` limitation;
- live validators and tests with commands and exit results;
- applied files, or proof that `audit only` made no edits;
- residual risks and the retained-artifact path, if any.

If isolation, invocation observability, permissions, or a required validator is unavailable,
report that boundary plainly and do not substitute an accuracy or completion claim.
