# Output template

Return findings first:

~~~text
## Findings
### [P1] Short title, path:line
Commit: <full SHA>
Evidence: <parent-versus-commit and current-state evidence>
Impact: <concrete failure>
Recommendation: <smallest safe correction>
~~~

Always include:

1. **Commits reviewed**: SHA, subject, author/date, inferred intent, and locally
   observed upstream containment.
2. **Scope and evidence**: initial/final HEAD, branch/upstream, dirty overlap,
   instruction files read, path coverage, generated/binary handling, and whether
   validation commands were authorized or run.
3. **Resolved or out-of-scope observations**: only when relevant.
4. **Verdict: APPROVE | REVISE | REVERT**: concise rationale tied to findings and
   coverage.

Cite line numbers from the inspected revision, for example
<short-sha>:src/file.ts:42; do not cite a later worktree line as proof of an older
commit.
