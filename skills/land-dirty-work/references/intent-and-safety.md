# Evidence, splitting, and live-checkout safety

Use this reference when classifying mixed, old, or sensitive dirty worktrees.

## Evidence hierarchy for proving intent

Never invent a narrative from filenames alone. Cite concrete lines from at least one primary artifact:

1. **Executable proof:** modified or new tests, assertions, schemas, migrations, or gate scripts.
2. **Code and diff intent:** staged vs unstaged changes, removed workarounds, new public callers, and commit deltas already on the dirty branch ahead of `<default>`.
3. **Repository records:** local task ledgers, `PLAN.md`, `ROADMAP.md`, audit notes, or updated docs matching the touched symbols.
4. **Remote context:** open PRs on the same branch or recent commits touching the exact same module.

Mark a cluster `NEEDS_INPUT` whenever:
- two competing approaches exist in the same dirty tree (for example, old code left half-replaced alongside new code);
- tests are absent or failing and the intended behavior cannot be established from repository contracts;
- the diff touches database migrations, auth/RBAC, credentials, billing, CI workflows, release-note/doc-sync gates, or `AGENTS.md`/`CLAUDE.md` without matching prior task authority.

## Splitting mixed dirty work cleanly

When one checkout holds multiple unrelated changes:

1. Generate a full patch per tracked file or hunk (`git diff HEAD -- <path>`) and inspect untracked files directly. When `--max-paths` caps scanner arrays, inspect exact git counts directly with `git status --porcelain=v1` inside the targeted checkout (read-only).
2. Group changes that share a single feature, bugfix, or gate owner into one cluster; keep orthogonal fixes in separate clusters.
3. In meta-repos (for example control-plane workspaces that ignore nested sub-repositories in `.gitignore`), verify each imported path belongs exclusively to the meta-repo tree and never mixes commits across nested `.bare`/worktree boundaries.
4. When one file holds two unrelated edits, apply selective hunks in the isolated branch and verify both clusters compile and pass tests independently. Record which paths and hunks stayed out of each PR so nothing is lost.

## Secret, symlink, and sensitive-file triage

Halt staging, committing, or pushing any cluster containing `credential_or_env_candidates` (`.env*` excluding templates, private keys, certificates, auth configs, `secrets/` or `credentials/` subpaths, or secret/credential data files), `symlink_candidates`, or literal tokens/emails/host paths in diffs. Alert the user with the exact file path and line range without echoing secret values. Never follow symlinks when inspecting or copying untracked files.

## Multi-repo sweep ordering, 3-phase airlock, and idempotency

For unattended scheduled runs across `--repos-root`, enforce a 3-phase airlock so no single context holds live filesystem access, untrusted diffs, and GitHub push credentials together:

1. **Deterministic Phase 1 gate (`0` tokens):** Run `scan_dirty.py` and OS/session liveness checks (`lsof` + active agent transcripts), check open PRs for matching `<!-- dirty-fingerprint: <fp> -->` markers, write `ledger.jsonl`/`latest.md`, and prepare sanitized `WORK/<cluster>/` clones via `--reference-if-able <live> --dissociate <origin_url>`. Exit at `0` tokens if no actionable clusters remain or load exceeds budget.
2. **Isolated Phase 2 author + blind reviewer:** Run one fresh worker per cluster inside `WORK/<cluster>/` with only its own directory writable and only its repository's toolchain granted; verify in a separate read-only review turn without author rationales.
3. **Deterministic Phase 3 publisher (`0` tokens):** Never run `git` inside agent-writable `WORK/` directories. Fetch branches into a trusted bare clone, enforce protected-path blocklists (`AGENTS.md`, `CLAUDE.md`, `lefthook.yml`, `.lefthook.yml`, `.github/`, `.gitattributes`, `.gitmodules`, `.env*`, `Makefile`, `.husky/`, `.githooks/`, `.mcp.json`), private-path/`Co-Authored-By`/`gitleaks` scans, exact-SHA `APPROVE` verdict check, and `<!-- dirty-fingerprint: <fp> -->` embedding before pushing draft PRs.

Across every sweep:
1. Always stop first on `SECRET_OR_UNSAFE`, `symlink_candidates`, `merge_conflicts`, `active_git_op`, or scanner exit `2` gaps; disclose them before proposing edits.
2. Skip worktrees with `recently_modified: true` (`ACTIVE_SESSION_SKIP`, using `.git/index` mtime when dirty paths are missing or deleted) and worktrees with active editors/builds/sessions (`pgrep`/`lsof`/session transcripts).
3. Check each dirty worktree's `dirty_fingerprint` against `ledger.jsonl` and open PR markers (`<!-- dirty-fingerprint: <fp> -->`) before opening a PR (`ALREADY_OPEN_PR`), and process only the named/default primary copy when `duplicate_of_worktree` is set.
4. For `heavily_behind: true` feature worktrees (`>= 50` commits behind `<default>`), inspect `git log` / remote PR history before reviving or rebasing.
5. Verify `likely_scratch_only: true` worktrees (untracked `.log`, `.tmp`, `.orig`, `.rej`, IDE workspace noise) as `SCRATCH_OR_DISPOSABLE` rather than shipping log dumps as code PRs.
6. Process dirty default branches (`on_default_branch: true`) before feature branches.

## Concurrency locks and atomic lease hygiene

Prefer OS-level `flock` serialization for scheduled machine runners, paired with an atomic file lease (`os.O_CREAT | os.O_EXCL`) only when coordinating across unlinked harnesses (`run_id` UUID/hex, UTC `started_at`, `ttl_minutes`, replaced atomically with `os.replace` only on expiry, removed only when `run_id` matches).

## Protecting and backing up live checkouts

Under audit-only, scheduled, or PR-only authority, never write inside a live dirty checkout. Reconcile live checkouts only through an explicit manual run after verifying 100% of intended hunks landed on `<remote>/<default>`:

1. Verify zero active processes (`lsof` / `pgrep`), active sessions, `.git/index.lock`, or active rebase/merge.
2. Archive every dirty tracked diff, staged index, and untracked file into an external `0700` directory with `0600` archive permissions (`~/.local/state/dirty-work-backups/<repo>-<timestamp>/`) and verify unpack/byte counts.
3. Compare live dirty files against the landed commit; refuse destructive cleanup automatically whenever `REVISE_AND_LAND` or `SPLIT_INTO_PRS` hunks diverge from what merged, and never run `git clean -x` so gitignored `.env*` files remain intact.
