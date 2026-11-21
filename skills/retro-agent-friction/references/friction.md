# Friction categories

`friction_counts.py` emits one row per category with `events`, distinct `sessions`,
`est_result_tokens` (failed output length / 4, an estimate), `programs` (an allowlisted program
name, else `other`) and `top_hashes`. A hash is the first 10 hex digits of SHA-256 over the tool
name and its normalized command or input, so the same call in two sessions shares a hash.
Categories overlap: one blocked call can count as `classifier_no_verdict`, `rewrite_then_failed`
and `repeated_failing_call`.

`structural` rows come from native fields. `heuristic` rows match English error text, first rule
wins, and are leads until one record is verified.

| Category | Basis | Meaning | Likely durable fix and owner |
| --- | --- | --- | --- |
| `classifier_no_verdict` | structural | Claude auto mode gave no verdict (`toolDenialKind`), often after a hook rewrote the input | Stop the rewrite for that command, or allow it: `update-config` or harness settings |
| `classifier_blocked` | structural | Auto mode refused the call | Usually correct; a recurring false block needs a permission rule: `update-config` or harness settings |
| `permission_rule_denied`, `permission_denied_other` | structural | A permission rule or the user denied the call | Read-only calls: `fewer-permission-prompts` or harness permission rules; others: `update-config` or harness settings |
| `rewrite_then_failed` | structural | A PreToolUse hook rewrote the input and the call then failed | Fix or narrow the hook: `update-config` or harness hook config |
| `hook_blocking_error`, `hook_non_blocking_error`, `hook_cancelled`, `slow_hook` | structural | A hook blocked, failed, was cancelled or took 10 s or more | Repair or scope the hook: `update-config` or harness hook config |
| `rerun_without_sandbox` | structural | A call failed, then ran again with the sandbox disabled | A sandbox allowance (host, path) via `update-config` or harness settings, or a wrapper |
| `repeated_failing_call` | structural | The same call failed again in one session | Depends on the cause; read the paired category |
| `slow_call` | structural | A tool call took 120 s or more; `slow_calls_by_family` splits gate, build, install, git, gh, other | A faster or scoped gate, or a wrapper: `encode-correction` |
| `output_too_large` | structural | Output was persisted or refused as too large | A bounded command or wrapper, or one instruction line |
| `compaction`, `api_error`, `interrupted` | structural | Context compacted, the API failed, or a turn was aborted | Compactions: smaller outputs and reads; others are usually environment noise |
| `command_failed`, `tool_failed` | structural | A failed call that matched no text rule | Inspect the hash before acting |
| `hook_blocked` | heuristic | Error text reports a hook error or block (for example `PreToolUse:` or `PostToolUse:`) | Inspect the hash; repair or scope the hook via `update-config` or harness hook config |
| `sandbox_denied` | heuristic | Operation not permitted, read-only file system, sandbox text | Sandbox write path or host rule: `update-config` or harness settings (`~/.codex/config.toml`) |
| `tls_failure` | heuristic | Certificate, x509 or TLS errors, for example `gh` under the sandbox | Sandbox network or keychain allowance: `update-config` or harness settings |
| `network_failure` | heuristic | Name resolution or refused connections | Allowlist the host or accept as environment |
| `shell_alias_or_syntax` | heuristic | Command not found, alias or shell function breakage, zsh parse errors | Shell alias change or a wrapper script |
| `timeout` | heuristic | Timed-out commands | A bounded or backgrounded command; a gate fix |
| `tool_input_error` | heuristic | Tool contract errors such as an edit before a read | One instruction line or a skill fix |
| `gate_bypass_flag` | heuristic | A command carried `--no-verify`, `SKIP=` or a skip flag | Find why the gate was skipped; `encode-correction` |

## Verifying one record

`--locate <hash>` with the same window prints, for up to `--limit` in-window events (default 3),
`session <ordinal> record <line>`, the category, the record's native labels (record type, hook
event and name, denial kind, tool name, or Codex item status and exit code) and the first 200
characters of its error text. Absolute and `~` paths become `<path>`; keyword secrets and long
token-like strings become `<redacted>`. Redaction is a pattern, not a guarantee. Use the view to
confirm one mechanism and keep it out of the report. Call-side events, such as
`rerun_without_sandbox`, show the tool name but no command.

## Coverage notes

- Claude Code sessions are `~/.claude/projects/*/*.jsonl` and subagent transcripts
  `*/<session>/subagents/*.jsonl`; Codex rollouts are `~/.codex/sessions/YYYY/MM/DD/*.jsonl`.
- A session matches when its first recorded `cwd` resolves to the repository's git common dir, or
  to another clone with the same normalized origin URL (`matched_other_clone`). A
  deleted worktree resolves through its nearest existing parent and is counted as
  `matched_via_deleted_worktree`. A cwd that resolves nowhere is `unresolved_cwd`.
- Files older than the window are skipped by modification time; events are then windowed by
  record timestamp. Records over 1 MiB are skipped and counted under `limits`.
- Records are deduplicated by native ID across files, so forks and resumes count once.
- Antigravity conversations are SQLite; the script counts recent files in `uncovered_stores` and
  parses none. Copilot sessions are not discovered.
