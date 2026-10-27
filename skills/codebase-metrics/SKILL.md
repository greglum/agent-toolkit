---
name: codebase-metrics
description: Assess codebase quality with source-grounded measures and a frozen local rubric. Use for a quality baseline, scored improvement workshop, or checking a requested quality target across eight dimensions.
compatibility: Works with Codex and Claude Code. The optional scorer requires Python 3.10+ and only the standard library. Use existing project tools; unavailable analyzers remain unknown.
---

# Codebase metrics

Produce a reproducible eight-dimension baseline and, when requested, improve the same
scope against the same criteria. A local 0-10 rubric is an acceptance aid, never an
industry certification or a promise that a timebox can deliver 9.5.

## Discover and freeze

1. Read the target's `AGENTS.md`, requirements, current checks, analyzer configuration,
   design system, and existing quality records. Find the owner of each measurement;
   extend its evidence rather than create a second measurement framework. Record the
   revision and dirty diff, tools/versions, available runtime, and permitted actions.
   Finish with a scope inventory of files, features, journeys, trust boundaries,
   environments, and known exclusions, with reasons. Preserve unrelated work.
2. Read [measurement selection](references/measurements.md). Keep all eight dimensions
   visible: functional correctness; reliability and recovery; security and data handling;
   maintainability; test effectiveness; accessibility and interaction; performance and
   efficiency; build and evidence reproducibility. Choose risk-based obligations from
   the inventory and current project requirements. Freeze each obligation's ID, weight,
   critical flag, objective pass condition, required evidence level, raw measure and
   denominator, exclusions, and execution profile before improvements. Record justified
   inapplicability explicitly. Required project gates remain mandatory outside scoring.
3. Save the plan and its hash in the assessment record before edits. For calculated
   scores, read [the score contract](references/scoring.md) and run the optional scorer's
   `freeze` command. Retain the original plan and hash independently of later outputs.
   A changed scope, criterion, weight, exclusion, profile, or threshold creates a revised
   assessment: disclose the change and recompute both baseline and final. Never loosen
   these to obtain a desired rating. An uncovered defect adds an obligation openly;
   keep the original baseline and show the revised comparison.

## Measure and improve

4. Run the existing gates and representative running journeys. Preserve raw counts,
   denominators, individual performance runs, unknowns, command/exit status, tool version,
   source/diff identity, observation time, and artifact paths. Classify each obligation
   PASS, FAIL, UNAVAILABLE, or NOT RUN. Source inspection cannot replace declared runtime,
   browser, provider, field, or production evidence. Finish the baseline before fixes.
5. If improvement is authorized, use its time budget and rank reachable failures by user
   harm and expected evidence gain. State briefly what a fresh design would change;
   use the simplest responsible owner. Reuse project gates and tools. Add tests only
   when they meet the target's test policy. Do not install analyzers, add dependencies,
   change providers, publish, or make production writes merely to fill score cells.
   After each complete fix, capture focused regression evidence and update the work
   ledger. Stop starting fixes early enough to run required final checks.
6. Reassess the frozen obligations against final source and run required final gates.
   Reuse earlier evidence only when its source, dependencies, configuration, and runtime
   inputs are unchanged; record that provenance. A failed dependent gate halts dependent
   work. Continue safe diagnosis and independent checks. Preserve unknown weight and
   critical blockers. A two-hour workshop ends at its deadline with measured progress
   and remaining failures/unknowns, even when the target is unmet.

## Deliver

Publish one eight-row baseline/final ledger with raw measures and denominators, scope,
local score and possible interval or justified N/A, critical blockers, evidence links,
and source/diff identity. List required gate results separately. State whether **every
applicable dimension** meets the requested target; an average cannot establish this.
Keep failed, unavailable, and unrun checks distinct. Report material risks and the next
bounded action. The scorer checks arithmetic, IDs, hashes, and file presence; the agent
must still review whether evidence supports each claim. Finish when this record and
the requested authorized work are complete.
