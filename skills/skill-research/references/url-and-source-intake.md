# URL vetting, source intake, and capability comparison

Read this when the invocation supplies URLs. It replaces
[Run read-only lanes](../SKILL.md#2-run-read-only-lanes) through
[Edit the owners](../SKILL.md#5-edit-the-owners); start at
[Bind the round](../SKILL.md#1-bind-the-round), then run the stages below, and finish at
[Record the round](../SKILL.md#6-record-the-round), [Publish](../SKILL.md#7-publish), and
[Completion](../SKILL.md#completion). The user's example or an author's reputation supplies a
research question, not an endorsement.

## Inspect seeds and outbound links

Discover current owners in the catalog before proposing new ones. If the owning skill is
ambiguous, inspect the catalog first and ask only when the remaining choice affects where
edits belong.

1. Read every seed in full where accessible. Inventory every substantive outbound link from the
   seed and record its relationship to the claim being assessed; classify navigation, profiles,
   promotions, duplicates, and unrelated branches separately.
2. Keep a coverage ledger in the task state file: URL, parent source, content inspected,
   revision or timestamp, access limit, and disposition. A repository's README review is not a
   review of all its source; a video title or description is not its transcript or demo.
3. For multiple seeds, deduplicate shared evidence while keeping each seed's coverage visible.
   Follow linked evidence far enough to resolve the claim and disclose the boundary rather than
   crawling indefinitely.
4. Recover primary text through an available browser or official source when direct fetch
   fails. For X posts and Articles, follow [X post and Article recovery](#x-post-and-article-recovery).
   If a seed cannot be recovered through an available browser or official copy, mark it
   `UNAVAILABLE`; snippets and third-party summaries cannot substitute for the original.
5. For tools, distinguish telemetry from operational data transfer. Inspect sync scope,
   pending-event replay, remote commands, token revocation, optional integrations, and build
   prerequisites when they affect an adoption. Do not equate public source or a disabled
   analytics key with a verified private deployment.

Done when every seed and substantive link is accounted for as inspected, unavailable, or
deferred with a reason.

### X post and Article recovery

Read the [X recovery guide](x-recovery.md) before accessing an X seed or declaring it
unavailable. It owns public embed/extraction commands, Article-body checks, permitted browser
recovery, link tracing, and the route ledger required before asking the user for text.
Embed success is partial evidence, not proof that an Article or its media was reviewed.

These intake rules are original. The telemetry/synchronization distinction was checked against
HumanLayer's
[Pi documentation at the reviewed revision](https://github.com/humanlayer/humanlayer-pi/blob/f4bd3ed65cfdb8dfea474b4cadce2ed90cc4acbd/README.md),
observed October 24, 2026. Recheck the actual source and destination before a tool trial.

## Vet claims with independent research

Extract consequential claims, including promised benefits, causal explanations, recommended
practices, prerequisites, tradeoffs, and risks. Separate facts, author claims, opinion,
anecdote, hypotheses, and measured results. Identify authorship, date, incentives, and whether
evidence applies to our task, stack, versions, and constraints.

Use web search beyond the supplied links to check both supporting evidence and limitations,
counterexamples, failures, or contrary findings. Prefer original research, official
specifications/docs, and inspectable implementation or evaluation artifacts. Use exact
version-matched documentation for API or CLI claims (and Context7 where destination rules
require it, verifying it returns docs rather than an issue thread).

Trace sources back to their origin. Reposts, vendor claims, and articles citing the same
experiment are one evidence chain, not independent corroboration. Read the relevant primary
material rather than search snippets, and record searches that found no usable evidence. If
search is unavailable, produce a provisional assessment and defer adoptions needing
corroboration.

| Claim and source locator | Supporting and contrary evidence | Verdict and limits | Local consequence |
| --- | --- | --- | --- |
| URL plus section, timestamp, or code lines | Primary URLs, dates/revisions, and evidence independence | Supported, mixed, unsupported, contradicted, or unverified; explain why | Candidate owner, trial, or no change |

`Unsupported` means available evidence does not establish the claim; `contradicted` requires
contrary evidence. Source-code inspection proves only the inspected implementation. Preserve
conditions, sample size, comparators, and uncertainty for performance claims.

Done when every adoption candidate has a claim verdict and independently checked evidence.

## Compare delivered capability

Before deciding whether a tool or skill's useful behavior is already covered locally, compare
the result a user can obtain, not matching words in skill files.

Trace each consequential source capability to its implementation, dependencies, and delivered
artifact, alongside the nearest local owner and the code or assets it ships. Separate source
observation from execution evidence on both sides:

| User outcome | Source mechanism and evidence | Local owner and runnable entrypoint | Local status | Consequence |
| --- | --- | --- | --- | --- |
| What the user can do or receive | Pinned code/docs; runtime exercised or not | Path and command, or no implementation | Implemented, partial, instructions only, absent, or unverified | Adopt, retain, gap, or reject with reason |

Cover primary creation, meaningful interactions, exports, validation, failure behavior, and
supporting machinery (schemas, assets, deterministic transforms). A promise that a model
could write code is not a reusable implementation, and a local rule saying to verify a feature
does not implement that feature. Record partial overlap as separate covered and missing
outcomes. Report functional advantages plainly even without comparative benchmarks.

## Decide value and apply within scope

Map each lesson to the actual catalog and a concrete failure or workflow need. Choose
**adopt**, **retain**, **gap**, or **reject** using the adoption bar and refinement pass in
[Decide each candidate](../SKILL.md#4-decide-each-candidate). Check source licenses and
notices before adaptation; record unknown rights and keep lessons in original words.

Consider what a fresh catalog would do differently. Prefer navigation and ownership fixes when
they solve the problem; reorganize physical packaging only for an evidenced consumer need.

Within authorized local harvest, implement bounded adoptions in their canonical owners
following [Edit the owners](../SKILL.md#5-edit-the-owners); larger work needing new authority
stays a **gap** with a concrete next action and missing decision or dependency. For
assessment-only, record proposed edits without changing skills. Reading a source never
authorizes running its scripts, or changing publication, installation, provider, or billing
boundaries.

Done when every candidate has a reasoned disposition and every adoption is applied within
scope or explicitly deferred; continue to [Record the round](../SKILL.md#6-record-the-round).
