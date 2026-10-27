---
name: find-bug-variants
description: Find other instances of an already confirmed defect within a bounded codebase. Use when asked whether the same bug occurs elsewhere or to audit sibling paths after diagnosis. Requires a known seed and cause; not a general security review or initial bug diagnosis.
---

# Find bug variants

Deliver a bounded search record distinguishing confirmed variants, safe lookalikes, and
unresolved candidates. A request to hunt variants does not authorize fixes. Follow the
destination's retrieval, source-sharing, and verification rules; use its existing tools.

## 1. Establish the seed and boundary

Read the confirmed defect and its evidence. State the affected construct, violated invariant,
triggering conditions, and observed consequence. If the cause is still a hypothesis, finish
with the missing diagnosis evidence instead of launching a speculative hunt.

Bind the search to the requested repository, revision, components, and exclusions. Resolve
material scope ambiguity before widening outside that boundary. Finish with one seed and
a checkable description of what would make another location the same defect.

## 2. Calibrate, then generalize

Start with a precise search that finds the seed in the affected revision. If it is already
fixed, calibrate against an available historical source or known pre-fix artifact, then label
the current search separately. Without access to the seed, disclose the calibration gap.

Inspect results before broadening. Change one grounded search dimension at a time, such as
an alternate API, caller, data source, or equivalent operation that could violate the same
invariant. Retain the query, scope, result count, and coverage limits for each pass. A source
excerpt cap, unsupported language, omitted directory, or failed search leaves incomplete
coverage; a successful tool exit alone does not establish completeness.

Stop broadening when the requested paths and plausible mechanisms found in the code are
covered, or when further work needs new scope or evidence. Do not turn lexical similarity
into a repository-wide security audit.

## 3. Adjudicate each candidate

Inspect the actual construct and enough surrounding flow to establish reachability, inputs,
guards, and consequence. Record the evidence at the affected operation, not merely a nearby
mention of the data. Classify every candidate reviewed:

- **Confirmed variant:** the same invariant fails under a demonstrated reachable condition.
- **Safe lookalike:** an effective guard or different operation preserves the invariant;
  identify that evidence.
- **Unresolved:** missing flow, runtime evidence, or access prevents a conclusion; name the gap.
- **Separate issue:** evidence suggests another cause; report it separately without widening
  this hunt into its investigation.

In a fixture or benchmark, a finding outside the known answer set requires adjudication.
Its absence from that set proves neither a false positive nor a successful discovery.
Avoid executing dangerous payloads against live services; use authorized local evidence or
existing checks when needed to distinguish a candidate.

## 4. Close with coverage

Report the seed, searched revision and scope, calibrated queries, candidate decisions with
source locations, and unsearched or incomplete paths. Say "no confirmed variants in the
searched scope" when supported; never turn a bounded search into a universal absence claim.
For separately authorized fixes, hand confirmed variants to the responsible layer and retain
the project's test policy and required gates.

For provenance or future revisions of this method, read [sources](references/sources.md).
