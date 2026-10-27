# PR lifecycle source context

Observed October 25, 2026 (Pacific/Honolulu):
[t3dotgg/tstack](https://github.com/t3dotgg/tstack/tree/7de017b3fc9d50c03cf3ecb98fb71e0ca65a78bd),
Theo Browne, MIT. Read all nine skills, their metadata and `babysit-pr/scripts/pr-wait`.
Ideas restated in original prose; no upstream text or code copied.

`babysit-pr`, `full-stop` and `leaving-pr-comments` informed single-owner monitoring,
explicit handoff, independent readiness checks and response-before-resolution ordering.
The bundled watcher is original code. It does not adapt upstream's hardcoded review-bot gate,
100-thread ceiling, or readiness verdict. No provider, attribution banner or mutation grant.

[GitHub CLI checks](https://cli.github.com/manual/gh_pr_checks) and
[API pagination](https://cli.github.com/manual/gh_api), GitHub CLI project, living manuals,
were read alongside local `gh 2.96.0` help. Context7 resolved `/cli/cli`, but could not serve
`/cli/cli/v2.96.0`; its current-source answer is not version-matched proof. Checked
[2.96.0 checks implementation](https://github.com/cli/cli/blob/v2.96.0/pkg/cmd/pr/checks/checks.go)
and [query builder](https://github.com/cli/cli/blob/v2.96.0/api/query_builder.go) for the adopted
JSON, pagination and missing-check behavior. These are API clients, not protection-rule audits.

[GitHub branch protection](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)
and [required-check troubleshooting](https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/troubleshooting-required-status-checks)
explain stale approvals, expected checks and accepted neutral/skipped states. GitHub, living
pages observed the same day; prose rights not assessed, no copying. Recheck when CLI output,
API schema, authentication, review requirements or queue behavior changes. Live authenticated
API collection was unavailable at intake. An October 26 read-only run against catalog PR 24
later passed with network permission. That single run does not prove multi-page live coverage;
offline CLI fixtures remain separate proof.
