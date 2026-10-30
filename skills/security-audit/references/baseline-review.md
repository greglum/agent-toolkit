# Review changes against a prior threat model

Use this procedure when the request supplies an existing model and asks how a change affects
it. It extends the audit's evidence ledger; it does not require a particular JSON format.

1. Bind the caller's baseline model, its source revision and scope, and the exact proposed
   change endpoints. Record whether the comparison uses endpoint commits or a merge base.
   Keep current working-tree observations separate from other revisions. If the baseline
   is missing or incompatible, record the blocked comparison and continue any independent
   analysis as a new model. Ask for the missing baseline when comparison is required.
2. Read the baseline and bounded change with surrounding owners. Trace affected actors,
   assets, flows, trust boundaries, permissions and lifecycle states into existing threats
   and controls. Include affected unchanged dependencies. An unchanged file is not evidence
   that its assumptions or protections still hold.
3. Preserve IDs for the same scenario. Add an ID for a distinct scenario and record changed
   premises or confidence under the existing ID. An omitted record needs investigation;
   absence from a newer document does not resolve or retire it. Retain counterevidence and
   identify inherited analysis separately from newly checked observations.
4. Record each material threat as unchanged, modified, new, reopened, resolved or retired,
   with evidence and a reason. Resolution requires evidence that the relevant protection
   works at the claimed scope. Retirement means the scenario no longer applies and needs
   evidence of that change. A proposed mitigation resolves neither. Reopen the same ID if
   later evidence restores its prerequisites.
5. Deliver the baseline identity, change scope, affected threat/control records, assumptions,
   residual risks and verification results or plans. List inaccessible evidence and unreviewed
   paths. Preserve the original model and follow the audit's report-location boundary.

Done when every examined baseline scenario affected by the change has a disposition and
new scenarios have source evidence or explicit design premises. A design-level threat is
a hypothesis until its prerequisites and reachable impact are verified; keep it separate
from confirmed vulnerabilities. This procedure does not reconcile arbitrary model schemas,
validate graph semantics, or establish exhaustive coverage.

Sources and reuse limits are recorded in [method sources](sources.md).
