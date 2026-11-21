# 0001: Use One Offline Verification Entrypoint and Isolate Git Hook Environment Variables

- Status: Accepted
- Date: 2026-11-20

## Context

Catalog checks run locally, in CI, and from the optional .githooks/pre-commit hook, and many unit tests create temporary Git repositories via subprocesses. Git injects local GIT_* environment variables (such as GIT_DIR and GIT_INDEX_FILE) into hook processes.

## Decision

Route local verification, CI, and the pre-commit hook through scripts/verify.sh with zero package installs or network calls, and unset all variables listed by `git rev-parse --local-env-vars` in a subshell before invoking verify.sh from .githooks/pre-commit.

## Consequences

Checks remain fast, reproducible, and offline across environments, and temporary Git repositories created by unit tests cannot accidentally read or corrupt the outer repository's Git state.

## Code References

- `.githooks/pre-commit:6`
- `scripts/verify.sh:2`
