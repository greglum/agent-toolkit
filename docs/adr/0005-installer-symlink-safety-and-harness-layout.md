# 0005: Preserve Installed Copies, Deduplicate Symlinked Harness Roots, and Support Direct Single-Harness Installs

- Status: Accepted
- Date: 2026-11-20

## Context

scripts/install.py links catalog skills into Codex, Claude Code, and Antigravity skill directories that may already contain user directories, directory-level symlinks across harnesses, stale links, or a missing/invalid packs.json.

## Decision

Roll back archived directories if symlink creation fails; deduplicate resolved harness roots in stale-link scans; flush stdout before writing unknown-skill errors to stderr so stale links appear first on merged pipes; fall back to empty packs for plain installs when packs.json is unreadable; and link single-harness Claude or Antigravity installs directly to the catalog without creating ~/.agents/skills.

## Consequences

Failed installs never leave a previously working skill missing, shared harness directories are counted once, piped diagnostics stay deterministically ordered, and single-harness users avoid unwanted cross-harness directories.

## Code References

- `scripts/install.py:112`
- `scripts/install.py:150`
- `scripts/install.py:174`
- `scripts/install.py:211`
- `scripts/install.py:247`
