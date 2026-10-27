---
name: review-pending-changes
description: Assess all requested uncommitted changes, including staged, unstaged, untracked, deleted, and renamed paths, for defects and over-engineering before committing. Read-only assessment with APPROVE/REVISE/REJECT verdict.
disable-model-invocation: true
argument-hint: "[files or all pending changes]"
compatibility: Requires read-only Git and file access. Does not execute target code unless separately authorized, or change the index or working tree.
---

# Pending changes assessment

Review the requested local changes without editing files, staging, checking out revisions, or
committing. Run no target-controlled code unless the user separately authorizes it. Run an
authorized test command only after reading the changes, and report it as gate status; a pass is
not evidence when the pending set changes tests or the command. Use `review-recent-commits` for
committed work. Read repository instructions and required gates before judging a change.

## Procedure

Order governs presentation, never disclosure. Report a security, data-loss, or credential
finding as soon as it is found, even though later steps are unfinished. A credential-shaped
literal counts even when it looks fake; in a single final reply, lead with it.

1. **Bind the scope.** Record HEAD and Git status, including staged, unstaged, untracked,
   deleted, renamed, type-changed, executable-mode, and conflicted paths. Default to all
   pending changes; honor an explicit path limit. If there are none, report that and finish.
   Track complete requested coverage in bounded batches. A large diff does not shrink scope.
2. **Read all three states.** Inspect index versus HEAD, working tree versus index, and the
   resulting file or absence. Read untracked files directly. For deletions and renames, read
   original committed/index blobs and surviving callers. Use Git object reads, not checkout.
   Prefer reads that never write the index: `git --no-optional-locks status`, `git diff --cached`,
   `git diff-files -p`, and `git diff-index -p HEAD`. Plain `git status` and `git diff` can refresh
   its stat cache.
   Inspect executable and type changes. For lockfiles, generated files, and binaries, record
   the appropriate consistency or artifact check and its result or limitation; do not silently
   exclude them. Conflicts block approval until resolved and reviewed.
3. **Trace the intent.** For each logical group, identify the original problem, the behavior
   changed, and the current owning layer. Trace affected callers, serialization, routes,
   consumers, and resource lifecycles where relevant. Inspect what removed validation,
   authorization, transactions, cleanup, or redaction protected. Use targeted history when
   needed. An authenticated caller can still violate role, tenant, or object boundaries.
4. **Try to disprove each finding.** Verify a reachable failure against the actual framework,
   serializer, consumer, and surrounding safeguards. Separate introduced defects from
   pre-existing behavior, design tradeoffs, and style nits. Preserve uncertainty when a
   needed fact is missing; do not invent a mitigation. Unknown external use is not proof of
   dead code. A proposed simplification must still solve the original problem and preserve
   safety, compatibility, accessibility, and required tests. Where the user supplied a spec or
   issue, report requirements missing, partial, wrong, or unrequested, or say "no spec
   available". Check docs that describe the changed behavior and report only drift this change
   introduced.
5. **Conclude within the evidence.** Report actionable findings, covered paths, unresolved
   coverage, and required gates that remain unrun. A read-only review cannot establish a
   runtime check it did not perform. Confirm staged entries (`git ls-files -s`) and
   working-tree content were not changed by the review; a refreshed index stat cache is not
   a change. If concurrent work moved them, disclose the changed snapshot.

## Output and completion

Give the inspected HEAD/scope, a short explanation of each logical change, and findings with
file:line, severity (`bug`, `design`, or `nit`; a security, credential, or data-loss finding is
a `bug`), reachable impact, evidence, attribution, and smallest fitting correction. List
excluded, inaccessible, or partially inspected paths and unrun checks separately. Finish with
one verdict and its reason:

- **APPROVE:** no blocker in the completely inspected requested scope. Nits alone do not block.
  This is a review result, not commit authority or proof that unrun gates passed.
- **REVISE:** useful work has a confirmed bug, an unresolved security or credential finding,
  or a material design problem, or unresolved
  coverage/checks prevent unconditional approval. Name the fix or missing evidence.
- **REJECT:** a confirmed regression, security problem, or failure to meet the requested
  outcome leaves the change unsuitable even after the named fixes. State the concrete reason.

Done when the verdict, coverage, and evidence are delivered. Do not apply its fixes unless
the user separately authorizes implementation.
