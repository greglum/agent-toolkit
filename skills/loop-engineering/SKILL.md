---
name: loop-engineering
description: Design or run a bounded engineering feedback loop with a fixed objective, observable acceptance, independent checks, and stop conditions. Use for repeated improve-review-verify work; skill-specific evaluation belongs to harden-skill.
---

# Loop engineering

Make each iteration earn the next. Reuse the repository's task record, checks and review
workflow; an improvement loop does not need another scheduler or agent framework.

## Freeze the contract

Read the repository's instructions, current evidence and authorized action boundary.
Name the result, baseline revision and dirty diff, acceptance conditions, preservation
checks, iteration or time budget, and stop conditions before editing. Honor stronger
repository bounds. A single correction with a decisive check needs only one pass.

Separate deterministic checks from judgment. A rubric needs observable evidence for each
dimension and a fixed threshold. Unknown or unrun evidence stays unknown; an average or
a self-assigned score cannot substitute for a required dimension. Keep an independent
acceptance case when tuning against examples, and do not rewrite it to make a result pass.

**Ready:** another reader can decide pass, fail or unknown from the contract and artifacts.

## Run a whole iteration

1. Observe the current result and record one concrete failure or uncertainty.
2. Choose a change at its responsible owner. State the expected observable difference.
3. Apply the complete change within scope. Preserve a way to recover the prior state.
4. Run the focused check and required preservation gates. A failed prerequisite stops
   dependent work; independent diagnosis can continue.
5. Review the actual artifact against the frozen conditions. Use fresh reviewers when
   required or authorized and useful. Give them original evidence and the current change,
   without the implementer's preferred verdict. Label self-review when that is all available.
6. Record the diff identity, result, check exit statuses, reviewer findings and next decision
   in the existing task record. Feedback becomes evidence only after source or runtime
   verification. Store accepted corrections with their owner and recheck trigger; generated
   answers fed back into a graph remain attributed claims until independently verified.

**Ready:** the iteration has an inspectable result and evidence tied to its exact content.

## Stop or continue

Stop when acceptance and required checks pass. Continue only for a verified unmet condition
within the remaining bound. Rerun checks when changed content, dependencies or environment
invalidate them. Repeating an unchanged pass is not progress.

At the bound, on repeated failure without a new hypothesis, on a material authority change,
or when progress needs a user decision, stop dependent actions and return the exact blocker
and next step. Preserve stronger repository plateau rules. Never silently increase budgets,
loosen criteria, skip failing checks or promote a model's favorable review into a fact.

Deliver baseline versus final evidence, completed iterations, remaining failures/unknowns,
and action state. Claims about this skill's added value require a blind run and a no-skill control.
A successful project run proves only that run.

Source scope and intentional departures: [provenance](references/sources.md).
