# Specify the system around the model

Use for model calls, retrieval, or agent actions. Extend the existing spec, not a second
checklist. Resolve applicable rows from source and the conversation; mark unknown values
as open decisions rather than inventing targets or granting new authority.

| Contract | Decision to make explicit |
| --- | --- |
| Outcome | Observable user result and error tolerance; compare deterministic code, retrieval plus one call, a fixed workflow, and an agent only as far as the need requires |
| Context | Authoritative data, retrieval permission checks, freshness and provenance; where working state ends and persistent memory starts, including scope, correction and deletion when memory is needed |
| Actions | Tool arguments and target validation; who authorizes each side effect and where code enforces that decision outside model-controlled text |
| Termination | Success predicate, failure and cancellation states, progress detection, and limits on calls, time and spend; name the enforcing owner and include retries and fan-out |
| Recovery | What survives interruption, how completed work is recognized, and what happens when an external action may have committed but its result was not recorded |
| Evidence | Task-specific baseline and acceptance cases; separate final-state correctness, consequential action behavior, model quality, latency and cost |

A model saying it is done is not a success predicate. A completed tool response can still
leave the requested outcome unmet. Keep authority, budgets and stopping decisions enforceable
by the host even when retrieved text or model output asks to bypass them.

For external writes, distinguish replay of recorded results from re-execution of an action.
Name the receiving system's idempotency or transaction boundary and a stable logical operation
identity across retries. Durable execution alone does not guarantee exactly-once effects in
another system. If safe deduplication is unavailable and the result is uncertain, specify
reconciliation before another write. Add a workflow engine only when the required recovery,
waiting or coordination cannot be met by the existing owner.

When assessing a proposed optimization, hold the task set and relevant model, prompt, tool,
retrieval and environment versions fixed, or report the changed variables. Define acceptance
before tuning. Use deterministic checks for enforceable contracts, task outcomes for usefulness,
and calibrated human or model judgment where needed. Do not force one tool sequence when
several safe paths satisfy the contract. Report denominators, repeated-trial limits and unrun
checks; a canned replay proves control flow, not fresh model quality or live performance.

**Ready:** each applicable contract has an owner, an observable acceptance condition and a
failure response, or an explicitly unresolved decision. Small read-only tasks need no durable
runtime, persistent memory, multi-agent plan or new evaluation service merely to fill this table.
