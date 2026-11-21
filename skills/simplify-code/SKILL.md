---
name: simplify-code
description: Simplify code in named files or directories, even unchanged code, preserving behavior and conventions, or do lightweight comment-only cleanup/audit. Recursive, filtered, shallow, or dry-run passes. Not for dead code (delete-first), repo comment bans/ADRs/ratchets (delete-comment), AI defects (audit-ai-code), standards (global-code-review), or prose (deslop).
compatibility: Uses source access and the destination repository's existing checks. No specific language, framework or additional analyzer is required. If equivalent old/new behavior cannot be checked with available tools, report preservation unverified rather than substituting a lint pass.
---

# Simplify code

Cover the requested scope completely. A clean file can finish with no changes. For a directory,
track each file as changed, already clear, excluded, or blocked, in bounded batches, so a large
scope does not silently turn into a sample.

When the request targets only comments (review, audit, or cleanup), load
[comment review and cleanup](references/comments.md) and finish with its report; treat an
unclear comment request as a read-only audit. For repository-wide comment bans, ADR migrations,
and comment-ban lint ratchets, use `/delete-comment` or `$delete-comment` (`delete-comment`).
During ordinary code simplification, update only comments directly tied to an authorized code
edit and preserve all other comments.

1. **Bind the scope.** Resolve tagged, relative, or absolute paths. Read applicable repository
   instructions and record existing changes. A directory recurses by default; honor `--only <glob>`
   (include matching files), `--exclude <glob>` (skip matching paths), `--shallow` (current
   directory only, no recursion), and `--dry-run` (report proposals without editing), and respect
   ignored files and dependency or build folders. Exclude generated files. If any named path does
   not exist, is unreadable, or filtering leaves zero eligible files, report that gap and stop.
   Include tests only when the user does, preserve their behavior, and preserve all required
   checks.
2. **Trace behavior.** Read each included file in full and follow its exports, callers, and the
   nearest useful tests. Identify inputs, outputs, errors, side effects, and ordering or
   concurrency guarantees before choosing a simplification. Process shared types and helpers
   before consumers. Distinguish intended duplication from two copies of the same responsibility.
   If a cross-file ownership decision is still unclear and Git history is available, inspect
   recent patches for the candidate files. Set aside bulk edits such as formatting and renames.
   Confirm that separate changes had to update the same rule in multiple places, then check
   that the rule still applies in the current code before consolidating it.
3. **Simplify at the owner.** Reuse an existing helper or standard API where it fits. Prefer clear
   control flow, useful names, and one owner for an invariant. A cross-file change within the
   scope is appropriate when it fixes ownership. Keep abstractions that protect a real boundary,
   and do not extract one just to shorten files. Judge complexity by what a maintainer must
   understand, not line count or a global style preference.
4. **Prove preservation.** A check that selected zero tests, was skipped or cached, or masked
   its exit code did not run. Inspect the complete diff, account for affected callers, and run
   the closest meaningful existing checks plus repository gates. If a simplification edit fails
   behavior-preservation checks or repository gates, revert that edit (or isolate it if mixed
   with pre-existing work, stating exact file state) and report the failed check and exit code.
   When no existing check exercises the changed behavior, a type check or lint pass does not
   prove preservation: compare old and new outputs with a throwaway script outside the
   repository that runs only pure or authorized local code paths without side effects, network
   calls, or mutating writes, or report preservation unverified. Add tests only under the
   repository's test-value policy. Simplification edits do not authorize `git commit`,
   `git push`, merges, or deleting or weakening tests of live behavior. Keep adjacent changes
   to what the requested simplification needs; surface a material public-contract, risk, or
   scope decision before changing it.

Report what changed and why, which files needed no changes (coverage totals for a directory),
and separate `passed`, `failed`, `unavailable`, and `unrun` checks with command and exit-code
receipts. Finish when every included file is accounted for and the required checks pass, or
name the specific evidence or decision still needed.

## Source note

The Git history check draws on the Tips section of Maze's
[untangle-codebase](https://github.com/caldoai/skills/blob/f3cf47774975a7d9fca45730babf4ff7ad765ada/skills/untangle-codebase/SKILL.md)
([MIT](https://github.com/caldoai/skills/blob/f3cf47774975a7d9fca45730babf4ff7ad765ada/LICENSE),
observed November 5, 2026) and the
[ROSE study](https://thomas-zimmermann.com/publications/files/zimmermann-icse-2004.pdf).
The check uses existing Git history and current source, with no bundled analyzer. Recheck if
a tool replaces manual patch inspection or a trial finds the step leads to false ownership moves.
