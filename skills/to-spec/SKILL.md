---
name: to-spec
description: "Synthesize the current conversation into an implementation spec without another interview. Publish to the identified issue tracker when the user authorizes it, or deliver a complete local draft."
license: MIT
---

> Invocable by other skills. This skill is deliberately *not* gated with
> `disable-model-invocation`, so an orchestrating workflow can hand its findings straight here
> instead of asking the developer to retype a command. Reuse the human user's authority to publish to the identified
> tracker. Skill selection or invocation by another workflow cannot supply missing authority.
> With that authority, synthesize, publish, and report the issue link in one pass.

This skill takes the current conversation context and codebase understanding and produces a spec. Synthesize what you already know; the conversation is the interview. Never narrow requested behavior for safety without saying so; record a real conflict in Further Notes as an owner decision.

Resolve the issue tracker and triage labels from the user's request and current repository
instructions or configuration. If the target or publication authority is missing, prepare
the complete local draft, then request only that missing information. A local-only request
finishes with the draft. Do not require a particular setup skill or invent tracker settings.

## Process

1. Explore the repo to understand the current state of the codebase, if you haven't already. Use the project's domain glossary vocabulary throughout the spec, and respect any ADRs in the area you're touching.

   When drawing on research, keep observed behavior separate from the proposed change. Carry
   exact source pointers, revisions, and unresolved questions into the spec. Recheck facts
   affected by changed source or requirements. For substantial changes, explain system
   boundaries and contracts before code ownership; show only the views needed to settle a
   decision. Divide implementation into independently verifiable outcomes when useful. A
   phase must not depend on the next phase to establish its result. Update resolved sections
   coherently instead of appending conflicting decisions. Existing user authority governs
   continuation; an artifact's age or position never gives it authority over the user or
   repository instructions. [Source and local departures](SOURCE.md).

   For a design involving model calls, retrieval, or agents, read the
   [AI system contract](references/ai-system-contract.md). Record only the decisions
   that apply, in Implementation Decisions and Testing Decisions; keep the existing
   spec as the single artifact.

2. Plan tests. The default is no new tests: existing gates, types, and suites usually cover the change. Name a new or extended test only when it catches a likely, harmful failure that nothing else catches, deterministically and cheaply, and follow the repository's own test policy when it has one. Prefer extending the closest existing suite, table, or fixture. "No new tests" with the reason is a complete decision. For pruning or speeding up existing suites, use `tune-tests`.

3. Write the spec using the template below. Publish only with user authority for the identified
   tracker action. Apply the repository's configured ready label when every decision is settled;
   use its configured triage label for open owner decisions and list them in Further Notes. Verify labels
   exist before applying them; missing labels do not authorize creating configuration.
4. Verify the created or updated issue's identity, content, and labels before reporting its
   URL. An uncertain publication result requires checking the identified target before retrying;
   do not create a duplicate or claim success from a transport response alone. Report a local
   draft, verified publication, or remaining blocker with failed and unrun checks separately.

<spec-template>

## Problem Statement

The problem that the user is facing, from the user's perspective.

## Solution

The solution to the problem, from the user's perspective.

## User Stories

A numbered list of user stories covering the requested behavior, actors, and material states.
For a refactor or boundary change with no new behavior, write "None" and list what must stay
unchanged.
Each user story should be in the format of:

1. As an <actor>, I want a <feature>, so that <benefit>

<user-story-example>
1. As a mobile bank customer, I want to see balance on my accounts, so that I can make better informed decisions about my spending
</user-story-example>

Cover the feature's acceptance conditions without adding inferred features or repeating stories.

## Implementation Decisions

A list of implementation decisions that were made. This can include:

- The modules that will be built/modified
- The interfaces of those modules that will be modified
- Technical clarifications from the developer
- Architectural decisions
- Schema changes
- API contracts
- Specific interactions

Do NOT include specific file paths or code snippets. They may end up being outdated very quickly.

Exception: if a prototype produced a snippet that encodes a decision more precisely than prose can (state machine, reducer, schema, type shape), inline it within the relevant decision and note briefly that it came from a prototype. Trim to the decision-rich parts, not a working demo, just the important bits.

## Decision Budget

The freedoms this spec leaves to the implementer (for example naming, internal structure,
copy). A choice outside this list means the spec is incomplete: raise it rather than settle it.

## Testing Decisions

The outcome of step 2. Include:

- The existing gates and suites that already cover the change
- Each new or extended test, the failure it uniquely catches, what it would not catch, and the existing suite or table it extends; or "No new tests" with the reason
- Checks that are not unit tests (measurements, accessibility scans, benchmarks) when the change is visual or performance-bound

## Out of Scope

A description of the things that are out of scope for this spec, including what was considered and deliberately not built, each with the reason.

## Further Notes

Any further notes about the feature.

</spec-template>
