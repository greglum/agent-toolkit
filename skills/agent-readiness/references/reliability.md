# Reliability decisions

Read this for the ownership-and-invariants lane. Find a consequential gap before choosing
a technique. Existing guardrails may already be the right implementation.

## Trace the promise

For each important flow, identify its input boundary, accepted states, transformations,
side effects, error and cancellation behavior, and observable result. Locate the callers
and the check that currently protects the promise. A boolean or optional field is a lead,
not proof of an invalid-state bug. Show the harmful combination and a reachable transition.

Prefer constraints that reject the mistake at its owner over instructions that ask every
future editor to remember it. Static types describe validated internal values; untrusted
JSON, files, model output, and external API responses still need runtime validation.

## Choose the feedback

| Gap in the current system | Candidate | Required evidence |
| --- | --- | --- |
| Callers can construct a harmful combination of states | Existing union, enum, constructor, schema, or native constraint | Old combination is rejected; all current callers migrate; valid behavior remains |
| An input boundary admits malformed or ambiguous values | Existing parser or boundary validator | Real bad input is rejected at the boundary without damaging valid input or leaking secrets |
| A broad input space has a clear independent invariant | Property-based or bounded generated checks | Property follows the contract, generator reaches meaningful cases, seed/counterexample can replay, runtime is bounded |
| Correctness depends on retries, timing, ordering, or cancellation | Existing deterministic scheduler, fake clock, or scripted fault simulation | Relevant interleavings fail under a planted defect and replay without sleeps or live services |
| A complex deterministic transformation is hard to inspect | Existing fixture or golden-output convention | Output is small, stable, reviewable, and meaningful; updates require checking the semantic change |
| A critical protocol has subtle state transitions and credible failure impact | Bounded model or formal-method proposal | Explicit model, assumptions, failure property, counterexample or proof limits, and a justified cost |
| A failure escapes because tools check different file sets or revisions | Existing gate, generator, or source-bound evidence | Affected files are included and stale evidence cannot become a pass |

These are choices, not a checklist of technologies to install. Use ordinary table cases or
exhaustive small domains when they cover the invariant more clearly than a new property-testing
dependency. A generated test whose oracle repeats the implementation has little value. Seeded
sampling is reproducible sampling, not exhaustive proof. A model proves only its stated
assumptions and abstraction, not the deployed system.

Respect the destination repository's test policy. If it prohibits snapshots, preserve that
rule and use its accepted assertions or fixtures. If a new test does not uniquely catch a
credible harmful failure beyond types and existing gates, improve the existing owner instead.

## Make feedback usable by an agent

Run the focused check an editor can use during the change, then retain the full required gate
for integration. Errors should locate the violation and state the supported correction. A
fast feedback command must not imply that omitted security, browser, migration, or release
checks passed. Avoid a new fast tier when existing commands already cover the need.

Inspect stale recipes as executable guidance: outdated setup, lockfile repair, merge advice,
feature lists, and check commands can undo stronger current policy. Fix their current owner
and its route from the entry instructions. Keep generated copies generated.

Measure only what the task needs: a reproduced failure, acceptance of valid inputs, rejected
invalid states, an actual focused-check duration, or a cold setup result. Preserve the tested
revision and recheck trigger. Do not translate these into invented agent-readiness scores.

## Source

This procedure restates ideas from Ron Minsky's
[Bug Bash talk](https://www.youtube.com/watch?v=rUYP4C29yCw), linked by
[Lauren Tan](https://x.com/poteto/status/2114626630429913383), observed October 26, 2026.
The full English auto-generated transcript, including Q&A, was reviewed; complete
audiovisual playback was not. Key sections: types 7:06, state models 12:29,
readable examples 18:38, deterministic seams 23:52, review 33:44 and formal methods
45:32. The talk treats formal verification as an uncertain investment. The bounded
swarm procedure is a local design choice. No source text, code or media is bundled;
public access alone establishes no redistribution license. Recheck when the source
or the destination repository's contracts change.
