# Recurring repository audit

## Set up the profile

1. Find the repository's quality profile and local checks in its agent instructions or
   contributor guide. Use those entry points for both ad hoc and scheduled runs. If the
   repository has no profile, start with a bounded ad hoc audit and report findings. For
   requested scores or recurring runs, define the profile before assigning ratings.
   Reuse existing checks and score contracts.
2. Freeze the profile and evidence scope before the baseline. Give each measure an ID,
   scale and scoring anchors, sample or denominator, evidence source, and recheck trigger.
   Record the source revision and whether the audit includes working-tree changes. Keep
   required checks and release gates separate from the audit.
3. Run a baseline. When authorized, have reviewers independently score one shared sample
   on the same revision to calibrate the rubric. They can divide the rest of the work.
   Resolve disagreements by clarifying the anchor, sample, or evidence rule. Recompute the
   baseline when the profile changes and identify the new version in later reports.

## Select evidence

Use the repository's profile when it exists. When defining one, sample normal entry points
and recent changes. Separate facts from judgment.

| Area | Evidence to sample |
| --- | --- |
| Simplicity and abstraction | Trace callers through a real change. Identify the rule or independent implementations each abstraction owns. Preserve boundaries that enforce an invariant or support an exercised replacement. Flag pass-through layers and shared code whose callers change for different reasons. Use file size, dependency depth, and complexity as review leads. |
| Test economy | Map a sample of tests to the failure each catches. Check for a distinct, consequential regression that other tests or gates miss. A case count alone gives no evidence of maintenance value. Preserve required gates and follow local approval rules for removing tests. |
| Documentation and context | Follow the instructions for a representative task. Check whether links resolve, commands match current entry points, and one document owns each rule. Measure always-loaded instruction bytes and relevant tool output separately. For measured token use, use comparable completed tasks and record model, input, cache, output, and correctness. |
| Modularity and local checks | Find the contract and normal check for each sampled component. Verify that independently edited stages can run at the documented boundary and that outputs needed downstream remain reproducible. |

## Run and report

1. Run the profile's documented checks at the declared scope. Bound output and retain the
   evidence needed to verify each rating. Use the profile's unavailable and unrun states
   when evidence is missing. Compare with the prior run only where scope and measurement
   match. Reuse earlier evidence only if the profile allows it and its inputs still match.
2. Record the revision, profile version, applicable scores, prior values and changes,
   evidence links, and open findings. Separate changes to the rubric or environment from
   changes in the code. Report a short summary for recurring runs and retain the complete
   record at the repository's designated path.
3. Create a recurring task only when requested and after a manual trial. Pin the target
   checkout or ref policy, exact profile entry point, report destination, cadence, and
   authorized actions in the task prompt. Keep routine audits read-only apart from the
   report. If a scheduled run cannot locate its target or pinned profile, record the blocker
   and stop. If a check fails or is unavailable, stop its dependent work, finish independent
   checks, and record the missing evidence. Apply fixes in a separate authorized run.
