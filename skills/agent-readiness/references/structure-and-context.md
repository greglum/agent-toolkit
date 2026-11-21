# Structure and context cost

Read this when work touches agent instructions, module boundaries, folder structure, file size,
or a decided architecture rule. Everything here is judgment unless a check in the repository
enforces it. In the step 2 discovery lane, survey the requested surface and return candidates
without editing.

## Hold the scope

Apply the named-file edit rule in [SKILL.md](../SKILL.md) (narrow path step 2): delete or inline
only code the task already changes, with a check covering its behavior. Except for step 4 of
"Measure before adding instructions", list other candidates in the report with path and reason,
and leave them unchanged.

Whole-repository cuts, folder moves, and unneeded file splits need a request for that scope. A
general request to optimize for agents does not supply it.

## Measure before adding instructions

1. Find what each harness in use loads at startup and on demand: root and nested instruction
   files, imports, rules, and memory.
2. Check each harness's current documented limit and what happens past it. Measure in the limit's
   own unit, after imports expand. Content may be cut off, skipped, or replaced by a pointer. A
   correct rule past the limit is a rule the agent never saw.
3. Classify the failure: rule missing, rule contradicted by a stale one, or rule not loaded. Fix a
   contradiction or a loading problem at its source. Adding a warning beside a stale rule leaves
   the conflict in place.
4. If a hard limit is cutting off an instruction file the task edits, or the edit adds to that
   overflow, make room in that file in the same change. This is required scope, even when the
   request names one rule. It is not a whole-repository cut. Advisory targets do not trigger this
   step. Remove only text you confirmed the code or manifests state, condense repetition without
   losing its facts, and move area-specific rules to a file the harness loads there. Stop once the
   file fits and the new rule loads. Keep every other rule. If the file is generated, edit its
   source. If it still does not fit, or another file causes the overflow, report that instead of
   cutting more.
5. Add only what the agent cannot infer: non-standard commands, constraints, and dangerous
   operations. Prefer wording that covers every case, such as "Add X to every function you
   change". Keep a condition when the rule applies only in that case.
6. Report the size before and after, each limit checked, and each limit you could not confirm.

## Keep always-loaded context small

- Remove overviews, listings, and other text only where the code or manifests state the same facts.
- Put a rule for one area in that area's nested instruction file or path-scoped rule. Confirm the
  harness loads it when an agent works there.
- Use a pointer for detail that is safe to miss until needed. Keep must-follow rules direct or
  enforce them with a check. An import that inlines a file saves no context.
- Keep one owner per rule. Point to it from elsewhere.

## Weigh abstraction against locality

- Keep code that changes together close together. Use `git log` on the files to see what does.
- Add an abstraction only when two real callers need it today, unless it owns a real boundary or
  invariant.
- Deleting code and inlining a one-caller wrapper are valid results. First search for consumers a
  name search misses: names built from strings, registries, config, reflection, generated code,
  validators, and other repositories. Keep a wrapper that owns a real boundary or invariant.
- Vertical slices and deep modules are design options. No controlled benchmark was found for their
  effect on agents, so choose from this repository's change history and claim no measured gain.

## Treat an oversized file as a seam decision

A line count is a prompt to look, not a goal. Ask which parts change independently and have
separate callers. Name a new file for the behavior it owns, never `utils`, `helpers`, or `part2`.
Leave a large file alone when nothing needs it split.

When a size gate blocks a correct change, keep the gate. Do not bypass it, and do not shrink the
file by removing comments or reformatting. If the file has a clear seam and the task allows the
wider diff, make a move-only split with checks passing and keep it separate from the change. Commit
only if the task authorizes commits. Otherwise keep the patch and report the seam you would use.

## Enforce a decided architecture rule

Use this only when the invariant is already decided and prose alone carries it (for unclear
recurring mistakes, follow the `encode-correction` handoff in
[step 3](../SKILL.md#3-plan-around-existing-owners)).

1. If a type or module boundary can make the violation impossible, do that instead.
2. Otherwise extend the repository's existing checker or an installed tool. Add no second framework.
3. Make the failure repairable: file and line, the rule, and what to do instead.

   ```text
   app/services/receipts.py:1: services must not import app.handlers.
   Move shared code to app/services/ or pass the value in from the handler.
   ```

4. Prove bad and valid forms per [step 5](../SKILL.md#5-verify-and-review-the-resulting-tree). Fix
   existing violations at their owner, or record a named baseline. Add no blanket exemption.
5. Reduce the prose copies to one short statement that names the check.
6. Prefer a repository check, which every harness and CI can run. A harness hook covers one
   harness; confirm which of its events and exit codes actually block.
7. Report a check that cannot run as unavailable. Do not remove it to get a passing result.

Structural checks do not replace behavior tests.

## Source note

Observed November 18, 2026. No source text is bundled. Recheck when a harness changes its loading
rules or a cited paper is revised.

- Hard limits: [Codex](https://developers.openai.com/codex/guides/agents-md) stops adding project
  instructions at a combined 32 KiB by default, and the limit is configurable.
  [Antigravity](https://antigravity.google/docs/rules-workflows) truncates a rule file past 24,000
  bytes after includes expand and demotes the largest rules to pointers past 20,000 tokens in total.
  [Claude Code](https://code.claude.com/docs/en/memory) skips a file over 4 MiB and cuts on-demand
  instruction files at a per-file character limit that depends on the context window.
- Advisory target: the same Claude Code page suggests under 200 lines per `CLAUDE.md` and states
  that imports do not reduce context. Its [hook reference](https://code.claude.com/docs/en/hooks)
  lists which events can block.
- Instruction files: [Gloaguen et al., v3](https://arxiv.org/abs/2602.11988v3) found no general gain
  in task success and over 20% more inference cost, with overviews unhelpful.
  [Lulla et al., v2](https://arxiv.org/abs/2601.20404v2) found lower median runtime and output tokens
  with `AGENTS.md` across 10 repositories. These preprints measure different things and do not
  settle the question, so measure locally.
- Wording: [Tsuchida et al., v1](https://arxiv.org/abs/2611.04367v1) found conditional policies
  followed less often than direct ones. It tested one policy with one text per style and did not
  test pointers.
- Maps and repair messages: [OpenAI](https://openai.com/index/harness-engineering/) reports a short
  `AGENTS.md` used as a map and lint messages that carry repair steps; this is one team's account
  with no control. [Anthropic](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
  describes loading context just in time through lightweight references.
