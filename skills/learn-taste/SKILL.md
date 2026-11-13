---
name: learn-taste
description: Turn repeated corrections, accepted tradeoffs, or verified gaps into durable project standards or better skill guidance. Use when work reveals a lesson that should carry into future sessions, or when asked to learn from project history. Pairs with the skill doing the work.
---

# Learn Taste

Carry a lesson into the next task by updating the guidance that task will use. At a
checkpoint or wrap-up, run this alongside the primary workflow when the work reveals a
reusable lesson. Start from work already in scope. A routine task with no such evidence
needs no documentation pass.

## Find the lesson

Start with the current task, its accepted decisions, relevant diffs and review outcomes.
For a requested sweep, bound the history by surface and revision range. Read supplied
history within its authorized scope. Preserve privacy when recording provenance.

Distinguish three signals:

- A user stated a preference or policy. Preserve its strength, scope and known exceptions.
- A checked implementation or review exposes a gap in existing guidance. Trace the current
  behavior and the supported intent. An accepted regression check or published gate can
  establish a project contract. A merged implementation alone shows what landed.
- A diff, revert, worker suggestion or repeated edit raises a question. Establish who made
  the decision and what it meant before treating it as a preference. Leave uncertain
  rationale or scope open when it changes the rule.

Write down the smallest class of future tasks where the lesson matters. Test it against the
original case, a different case in the same class, and a nearby case where the rule should
stop. Keep one-off choices local and leave inferred preferences open.

## Update the owner

Find the source a future agent or maintainer would reach. Read the nearby examples and
checks. If the rule exists, find whether the problem was discovery, wording, a misleading
example or an unenforced invariant. If existing guidance is partly right, replace the stale
or ambiguous wording in place. Keep judgment in the relevant design,
writing, engineering or skill guide. If a mechanical invariant fits a check, use the
project's existing enforcement workflow when in scope. Keep a short pointer where readers
start only if they would otherwise miss the owner.

State the expected behavior, when it applies, and the verified reason when that reason
changes future decisions. Link stable evidence when useful. Keep raw transcripts, private
details and unverified motivations out of shared guidance. Preserve intentional exceptions.
A project decision belongs in the project. Change a reusable skill only when the lesson
also applies outside that project or corrects the skill's general procedure.

Apply supported edits when documentation or skill maintenance is within the request. During
other work, surface the candidate if it falls outside the authorized edit. Read-only work
stays read-only. Implicit selection adds no action authority. Ask only when a material
preference, conflict or scope decision remains unresolved.

## Check the result

Follow the normal entry point as a fresh reader. Verify that it leads to the owner, the
guidance agrees with the current source and gates, and the wording handles the example and
its exception. When a trial exposes a skill defect, revise the relevant step and rerun the
affected case. Report the evidence, the changed owner, and any unresolved decision. A
supplied-skill trial and automatic selection in a fresh harness require separate evidence.

[Source and adaptation](SOURCE.md)
