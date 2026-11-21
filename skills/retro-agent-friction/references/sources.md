# Sources and departures

Observed 2026-11-18, Pacific time. All bundled code and prose are original. No upstream text,
prompts or code were copied.

| Source | Adopted idea | Rights |
| --- | --- | --- |
| This catalog's `retro-guardrails` skill | Tracked versus one-off runs, the state folder, ledger fields, dispositions and the report shape. `retro_state.py` and `references/ledger.md` are byte-identical copies | Same catalog |
| This catalog's `analyze-agent-history` skill | `session_records.py` and `antigravity_records.py`, the shared session readers, are byte-identical copies; their canonical copies and format notes live there | Same catalog |
| Native session records inspected locally on 2026-11-18 and 2026-11-21 (client versions checked 2026-11-20: Claude Code `2.1.325`, `codex-cli 0.165.0`) | Field names only: `toolDenialKind`, `hook_*` attachments, `compact_boundary`, `api_error`, `toolUseResult`, `dangerouslyDisableSandbox`, Codex `item_completed` `CommandExecution` and `ContextCompaction`, and Antigravity `step_index`, `type`, `status`, `created_at`, `output_tokens`, `tool_calls`, `content`, `error`, and `conversation_summaries.db` workspace/parent columns. Only key names and enum values were read; no session text is bundled | Fields observed, not a published schema |

Departures: this skill only reports. It reads sessions by the working directory each one
recorded, never by folder name, emits counts and hashes instead of text, uses a timestamp marker
instead of a commit, and leaves each fix to its named owner.

Recheck when a harness version renames these fields, when a real run shows a category that is
always empty or always wrong, or before adding another harness.
