---
name: state-machine-audit
description: Find implicit state machines in existing code, map source-backed transitions, and check a risky invariant or event ordering. Use for lifecycle, retry, cancellation, stale callbacks, concurrent state, or user-flow statecharts. Report counterexamples and what the evidence covers.
---

# State machine audit

## Find the state owners

1. Pin the source revision and name the user outcome or protocol boundary. For a broad
   audit, inventory subsystems first. Start with the state that controls a decision and
   trace its readers, writers and entry points.
2. Search beyond reducers and enums. Check native dialogs, media events, timers, navigation,
   storage, requests, queues and durable writes where relevant. Follow their callbacks,
   cleanup and completion guards. Separate independent state dimensions, such as a selected
   item and a pending request. Show how they interact before combining them into phases.
3. Pick one risky slice per subsystem you model. Write its expected invariant and the harm
   if it breaks. Cite the contract or label the invariant as proposed.

**Ready:** each scoped state owner has a source location, and the chosen check has a reason.

## Trace and check

1. List the initial conditions and transitions with **from, event, guard, effects, to, source**.
   Follow each asynchronous event from the point that starts it to the state it can update.
   Check who still owns the result after close and reopen, replacement, or teardown. If the
   UI can return to the same visible state, track the attempt or session separately. A step
   is atomic only where the source or platform provides that guarantee.
2. Use the lightest check that answers the question. Trace a deterministic case against source,
   run the real code with controlled events, or use the project's checker for orderings that
   need enumeration. Record the checked property, tool or method, bounds, assumptions,
   explored outcomes and omissions. A source walk stays source evidence. A model result covers
   its stated abstraction. For a race, control the order at the real entry point and record
   which platform behaviors are stubbed. For example, a synchronous dialog mock cannot test
   a deferred native close event. When feasible, break the specific guard in scratch space,
   confirm the expected assertion fails, then rerun on the restored source.
3. Give the shortest demonstrated failing sequence in the code's terms. For a model
   counterexample, replay each step through the real entry point before calling it a
   reproduced product bug. Keep contradictions, infeasible steps and unavailable checks visible.

**Ready:** a reviewer can reproduce the check or see exactly what prevented it.

## Show the flow and hand off

Draw a small Mermaid `stateDiagram-v2` from the transition ledger. Use recognizable state
labels and event labels with guards where they change the outcome. Keep relevant failure,
recovery and stale-event paths visible. For independent state dimensions, use separate views
unless one view needs to explain their interaction. State which transitions were left out.

Return the revision, source ledger, chart, invariant, evidence, and the recheck trigger.
Keep models, scripts and app edits in scratch space unless the task authorizes retaining them.
If the project already owns a model, check the code it covers since its last verified revision
before trusting a passing run.

## Sources

Original procedure. Lauren Tan's Pstack
[verification workflow](https://github.com/cursor/plugins/blob/6b0300214a09fd6029cfb7077043125758cd1fd2/pstack/skills/create-formal-verification-skill/SKILL.md)
and [statechart tool](https://github.com/cursor/plugins/blob/6b0300214a09fd6029cfb7077043125758cd1fd2/pstack/skills/statechart/SKILL.md)
informed source mapping and counterexample replay. Inspected November 8, 2026 under the
[pinned MIT license](https://github.com/cursor/plugins/blob/6b0300214a09fd6029cfb7077043125758cd1fd2/pstack/LICENSE).
[W3C SCXML](https://www.w3.org/TR/scxml/) describes transition selection and parallel states.
[Newcombe et al.](https://lamport.azurewebsites.net/tla/formal-methods-amazon.pdf) separate
checking designs from testing production code. Recheck these boundaries when a tool changes.
