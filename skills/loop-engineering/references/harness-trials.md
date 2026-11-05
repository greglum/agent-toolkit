# Contrastive harness trials

Use when changing the prompts, skills, tools or coordination around an agent. Reuse the
project's task and evidence records. A decisive mechanical fix still needs only its focused
check; competing hypotheses or subjective results justify candidate trials.

## Execution mode

Use the executor and permissions selected for the task. Record its version, effective
settings, access boundary and execution mode with the result. A changed execution boundary
is a distinct experiment. Do not infer permission changes from a benchmark or a trial plan.
An unavailable executor leaves that trial unrun; continue independently permitted work.

## Trial

1. **Bind the experiment.** Record the frozen task/rubric and input hashes, repository and
   harness revisions or dirty fingerprints, model/settings, tool versions, execution profile,
   access boundary and sampling plan. A changed input starts a distinct experiment. Keep
   evaluator answers outside candidate access; report any leakage or unavailable isolation.
2. **Propose and probe.** Name the observed failure and expected difference for each candidate.
   When causes differ, separate procedure/tool changes from task-domain knowledge changes.
   Execute against the same baseline and matched tasks. Keep each attempt's artifact, trace,
   status and cost/time when available, including failures and retries. A skill that never
   loaded or a rule never reached supplies no evidence for that change's effect.
3. **Compose and confirm.** Review actual artifacts and their behavioral contrasts. Combine
   only supported changes and resolve overlapping instructions at their owner. Test the
   composed result afresh; separate candidate passes do not prove their combination. Keep
   unchanged baseline eligible, and revert a regressing candidate. An anonymized comparison
   can reduce author or candidate-label bias when judgment matters.
4. **Retain at the proven scope.** A successful task-local edit proves that trial. Durable
   promotion needs a transferable cue, checked evidence, affected owner and a recheck trigger.
   Use fresh tasks outside the tuning examples for transfer claims. When claiming efficiency
   or harness benefit, compare against a baseline with matched inference resources, and inspect
   for shortcuts tied to evaluator artifacts. Record extra compute separately from design gain.

Budget the full experiment before starting: baseline runs, candidate runs, composition,
confirmation, review, retries and reflection all consume work. At the bound, keep supported
results and expose remaining uncertainty. This reference grants no new provider, permission,
installation, publication or task authority. Preserve required repository gates and the
explicit invocation requirement of any skill-specific evaluation workflow.

Source identity and intentional departures: [provenance](sources.md#recursive-harness-trials).
