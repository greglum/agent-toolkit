---
name: simplify-code
description: Simplify code in named files or directories, including unchanged code, while preserving behavior and project conventions. Use for recursive, filtered, shallow, or dry-run simplification. For an explicit comment-only request, audit or clean comments without changing code behavior. For prose use deslop.
---

# Simplify code

Cover the requested scope completely. A clean file can finish with no changes. For a directory,
track each file as changed, already clear, excluded, or blocked, in bounded batches, so a large
scope does not silently turn into a sample.

For an explicit request to review or clean only comments, follow
[comment review and cleanup](references/comments.md) and finish with its report. An unclear
comment request is an audit. Automatic selection for ordinary code simplification does not
start a comment audit or pruning pass. Keep comment changes needed by an authorized code
edit with that edit; otherwise preserve them.

1. **Bind the scope.** Resolve tagged, relative, or absolute paths. Read applicable repository
   instructions and record existing changes. A directory recurses by default; honor `--only`,
   `--exclude`, `--shallow`, and `--dry-run`, and respect ignored files and dependency or build
   folders. Exclude generated files. Include tests only when the user does, preserve their
   behavior, and preserve all required checks. For an audit or dry run, report proposals without editing.
2. **Trace behavior.** Read each included file in full and follow its exports, callers, and the
   nearest useful tests. Identify inputs, outputs, errors, side effects, and ordering or
   concurrency guarantees before choosing a simplification. Process shared types and helpers
   before consumers. Distinguish intended duplication from two copies of the same responsibility.
3. **Simplify at the owner.** Reuse an existing helper or standard API where it fits. Prefer clear
   control flow, useful names, and one owner for an invariant. A cross-file change within the
   scope is appropriate when it fixes ownership. Keep abstractions that protect a real boundary,
   and do not extract one just to shorten files. Judge complexity by what a maintainer must
   understand, not line count or a global style preference.
4. **Prove preservation.** A check that selected zero tests, was skipped or cached, or masked
   its exit code did not run; a forced failure counts only after confirming the forcing edit
   applied. Inspect the complete diff, account for affected callers, and run the closest
   meaningful existing checks plus repository gates. When no existing check exercises the
   changed behavior, a type check or lint pass does not prove preservation: compare old and new
   outputs with a throwaway script outside the repository, or report preservation unverified.
   Add tests only under the repository's test-value policy. Keep adjacent changes to what the
   requested simplification needs; surface a material public-contract, risk, or scope decision
   before changing it.

Report what changed and why, which files needed no changes (coverage totals for a directory),
and the passed, failed, and unrun checks. Finish when every included file is accounted for and
the required checks pass, or name the specific evidence or decision still needed.
