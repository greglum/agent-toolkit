# Authoring skills

A skill supplies working knowledge a capable agent would otherwise lack. Start with the
[workflow map](workflows.md) and extend an existing owner when it already handles the job.
Use [curation](curation.md) to assess sources and [verification](verification.md) to run checks.
For a full audit and behavioral comparison, explicitly invoke `/harden-skill <path>` in
Claude Code or `$harden-skill <path>` in Codex.

## Choose the boundary

Keep one skill per coherent, independently requestable outcome. A neighboring pipeline stage
can deserve its own skill when its trigger, inputs, final artifact and proof differ, and it
can finish without loading the other stage. Shared subject matter alone does not settle ownership.
Use a conditional reference for a format, engine, stack or permission mode of the same job.
Do not split only because a file is long or because a workflow has several steps.

Before extracting, name the handoff and canonical owner. Move the procedure instead of copying
it, repair callers and discovery text, preserve invocation and action boundaries, and check
single-bundle installation. Added descriptions consume discovery context; a cleaner split
is not a measured speed, cost or selection improvement. Record the evidence and migration.

## Write the procedure

- Put the job and its distinct use cases in `description`. Selection guidance hidden in the
  body arrives too late. Keep descriptions within the catalog's 360-character automatic or
  600-character explicit-only budget; passing the budget does not prove native selection.
- Use ordered steps, concrete decisions and a checkable finish. Preserve a material finding
  as soon as it is known; a staged output format must not delay its disclosure.
- Keep the execution path in `SKILL.md`. Load long rubrics, variants and schemas from linked
  `references/` only when needed. Put repeatable operations in `scripts/`.
- Keep each rule in one owner. Move a skipped instruction to the step that needs it instead
  of duplicating it. Before adding a rule, confirm the skill loaded and the rule was reached.
- Use examples to explain the symptom and the evidence that exposes it. Keep incident history
  and project-specific commands with their project or research record.
- Write short sentences in plain English. Avoid em dashes and inflated claims. Cut text that
  would not change a decision, action or acceptance check.
- Preserve the user's task and repository rules. A skill does not authorize commits, pushes,
  merges, spending, provider calls, data deletion or test removal.

## Keep the bundle portable

Each `skills/<name>/` folder must work when installed alone. Keep linked resources inside that
folder. Load a reference at the step that uses it. State required tools and an honest fallback
for optional tools in `compatibility`, within its 500-character limit. Avoid hidden installs,
credential setup, hooks or permission grants.

Inherit the user's harness, model and effort settings. Global skills omit Claude Code's
`model` and `effort` overrides. Keep trigger text in `description`; Codex does not use Claude's
`when_to_use`. Describe required capabilities rather than named worker types or a second
provider. Report what remains unverified when a capability is unavailable.

Read the destination repository's instructions, versions, design system and required gates.
A portable method discovers local owners; it does not impose another project's stack, paths
or deployment process. Keep canonical project prompts and generated projections in their owner.
Validate an extracted project method on a different stack or fixture before enabling it broadly.

An explicit-only skill carries both:

- `disable-model-invocation: true` in `SKILL.md` for Claude Code.
- `policy.allow_implicit_invocation: false` in `agents/openai.yaml` for Codex.

The checker enforces that pair. Metadata controls selection, while task authority comes from
the user. Claude Code `allowed-tools` is a permission grant for the invocation turn, not an
exclusive allowlist or a read-only boundary. Omit tool grants when the skill does not need them.

Before adding a name, check project, installed, vendor and harness-bundled skills for collisions.
A personal skill may shadow a project skill. Use a distinct name or preserve the specialized
project owner. Treat renaming and removal as breaking changes; update callers, catalog entries
and [migration guidance](migrations.md) together. A consumer may require the old name before
inference begins. Explicit-only workflows must remain explicitly invoked.

This catalog targets Claude Code and Codex. Other upload formats may accept fewer frontmatter
fields and may not preserve invocation controls. Validate a separately packaged copy against
its destination before distributing it; do not silently weaken an explicit-only contract.

## Evaluating

Run `sh scripts/verify.sh`, then test the behavior the skill must preserve or prevent. Examples
include an audit that stays read-only, a review that follows the destination's rules, a
preserved modified file, or an export that matches its preview.

For a behavioral comparison, use fresh runs with and without the skill on the same input.
Keep the expected result and other runs' answers out of their prompts. A separate judge who
did not author the candidate grades end artifacts against stated assertions. If that judge
is unavailable, report the comparison as incomplete. Check the judge against known-good and
empty results. Rerun every comparison case after an edit, repeat uncertain cases and separate
skill defects from fixture defects. Include the intended smaller model when applicable and
authorized. A fixture that directly states the lesson cannot test whether the skill adds it.

Record the source revision, model, harness, input, assertions, results and unrun dimensions.
A static pass establishes structure. A supplied-skill run establishes behavior on that case.
Automatic selection needs an invocation trace from the target harness. A good answer alone
proves neither selection nor a general quality, speed or cost improvement. Preserve guards,
scope words and quantifiers during a condensing edit, then recheck affected behavior.

## Record sources

For adopted material, record the upstream URL, observation date, verified immutable revision,
license, adopted idea, local departure and recheck trigger. Preserve copyright and license
notices when adapting text or code. Public access alone does not permit redistribution.
Keep linked media, models and services under their own terms.

A skill installer's `skillFolderHash` is a folder's Git tree hash, not a commit. If exact
provenance matters, find the commit whose `git rev-parse <commit>:<folder>` matches it.
Use the explicitly invoked `skill-research` workflow for a source assessment; it creates or
updates dated reports and indices in the development catalog. Keep reusable source notes
inside the affected bundle so a public install does not depend on that research archive.

## Skills that coordinate workers

Keep one parent responsible for scope, integration and verification. Give each worker an
independent question, original evidence and explicit file ownership. Treat worker claims as
leads until checked against the source. Do not turn agreement into proof.

Keep resumable progress in the task's existing record. Track source identity, unresolved
findings, decisions left open by the brief and the next action. Protect shared writes with a
stable key and the revision read. On conflict, reread and retry once; stop on a second conflict.
A progress record or generated plan never expands action authority.
