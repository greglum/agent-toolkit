# Accepted exports and interpretation

In explicit mode the CLI reads regular files, never directories, glob expressions, compressed
files, SQLite databases or remote URLs. Shell expansion happens before the CLI. Limits are 128
inputs, 64 MiB per file and 1 MiB per record. An oversized input is excluded in full.
Malformed JSON, duplicate object members, invalid UTF-8 and non-object records are counted; other readable records
may still contribute to a partial ledger. Errors identify input ordinals, not paths or content.

## Repository discovery

`--repo <path> --days <n>` lists `~/.claude/projects/*/*.jsonl`,
`~/.codex/sessions/YYYY/MM/DD/*.jsonl`, and
`~/.gemini/antigravity/brain/*/.system_generated/logs/transcript.jsonl`, skips files not
modified in the window, and reads the first recorded `cwd` (Claude records, Codex
`session_meta.payload.cwd`) or, for Antigravity, decodes `workspace_uris` from read-only
`~/.gemini/antigravity/conversation_summaries.db`. That directory is
resolved with `git rev-parse --git-common-dir` and must equal the repository's common dir or
belong to another clone with the same normalized origin URL (`matched_other_clone`), so linked
worktrees and clones of one remote match and a lookalike folder slug does not. A folder the run
cannot read is `unreadable_cwd`, and an unreadable store is listed under `blocked`. A deleted
worktree resolves through its nearest existing parent and is counted separately. A cwd that
resolves nowhere is `unresolved_cwd`. Folder names are never matched.

When more than 2000 sessions match, the newest 2000 are kept and read newest first; the excess
count is reported in `discovery.sessions_capped`. In this mode a
record over 1 MiB is skipped and counted instead of excluding the file. Claude subagent
transcripts and Antigravity child sessions (`parent_conversation_id` set or `nesting_depth > 0`)
are skipped as delegated when `include_subagents=False`. Legacy Antigravity
`conversations/*.db` files lacking a brain transcript are counted under
`uncovered_stores.antigravity_sqlite_not_parsed` and never opened. Copilot stores are not discovered.

The readers, `scripts/session_records.py` and `scripts/antigravity_records.py`, are shared:
`retro-agent-friction` carries byte-identical copies. Change them here, then copy them there.

## Codex rollout JSONL

The first parsed record must be `session_meta` with `payload.id` and `payload.source`.
Supported source values are `cli`, `vscode` and `mcp`. Source is a metadata assertion, not
proof that a human supplied every message. Missing, custom or unknown provenance is excluded
with partial coverage. Known internal, exec, subagent, parent, fork and inherited-history
metadata exclude the entire session, including its first turn.

Only `event_msg` with `payload.type: user_message`, a string `payload.message` and a
nonempty stable `timestamp` contributes. Untimed user events make coverage partial. Newer
rollouts carry user turns only as `event_msg` `item_completed` items of type `UserMessage`,
keyed by item `id`; their text blocks contribute. The two shapes were not seen in one file.
`token_usage_record`, `world_state` and `inter_agent_communication_metadata` count as
non-message records.
`response_item` messages are deliberately never a fallback: they can duplicate user events
or contain developer instructions and inherited context. Older exports without user events
may therefore produce no eligible messages; this is not proof of no corrections. Assistant,
tool and other event records do not contribute. Unknown top-level record types make coverage
partial. Session IDs stay internal and group exported copies of the same session.

## Copilot session events JSONL

The first parsed record must be `session.start` with string `data.sessionId` and integer
`data.version`. Version is shape metadata, not certification that every version is supported.
A detached parent or root `agentId` excludes the entire session. Only `user.message` records
with string `data.content` and stable `data.messageId` or event `id` contribute. The tool uses
displayed content, never `transformedContent` or attachments.

Messages with an `agentId`, `parentAgentTaskId`, `isAutopilotContinuation`, or `data.source`
other than absent/`user` are excluded. The SDK permits omitted source by default, including
for callers that automate input; this tool cannot prove human authorship from absence.
Assistant/tool/session/subagent event families are counted as non-message records. Other
top-level types make coverage partial. The parser does not resolve `parentId` references.

## Claude Code transcript JSONL

A file is Claude Code when an early `user` or `assistant` record carries string `sessionId`
and `uuid`. A first such record with `isSidechain` or `agentId` excludes the session as
delegated. Only `user` records contribute, and only typed prompts: records with `isMeta`,
`isCompactSummary`, `isSidechain`, `toolUseResult` or a `tool_result` block, a `userType` other
than `external`, `promptSource: system`, a `turnOrigin` other than `human`, or an `origin` whose
`kind` is not `human` are excluded. These cover injected context, compaction summaries, tool
output, peer and handback messages, task notifications and scheduled turns. Absent fields, as
in older CLI transcripts, cannot prove human authorship. Text blocks are joined; slash-command
and local-command wrappers are excluded as envelopes. Message identity is the global `uuid`,
so a forked or resumed copy counts once. All other record types are non-message records.

## Antigravity transcript JSONL

A file is Antigravity when its first record carries integer `step_index`, string `created_at`,
and a `type` in `USER_INPUT`, `PLANNER_RESPONSE`, `GENERIC`, `SYSTEM_MESSAGE`, or
`CHECKPOINT`. Transcripts that begin with `SYSTEM_MESSAGE` swarm/subagent prompts or contain no
`USER_EXPLICIT` `USER_INPUT` are excluded as delegated. Only `USER_INPUT` records with
`source: USER_EXPLICIT`, string `content`, integer `step_index`, and non-empty `created_at`
contribute; `<USER_REQUEST>...</USER_REQUEST>` wrappers are unwrapped so `<ADDITIONAL_METADATA>`
and `<USER_SETTINGS_CHANGE>` tags cannot generate false cue matches. Other step types count as
non-message records. Message identity pairs a deterministic session seed with `step_index` and
`created_at`.

## Text-free candidates

Four fixed English lexical categories flag repeated requests, scope corrections, verification
requests and preservation requests. Fenced code and Markdown blockquote lines are ignored.
Recognized leading instruction/context envelopes are excluded. These filters are intentionally
conservative, incomplete heuristics. Natural-language quotes, pasted source, unusual wrappers,
negation and genuine new requirements can still produce false positives. Non-English or
indirect corrections can be missed. No sentiment or performance score is calculated.

The output never includes message text, paths, IDs or hashes. Raw input still exists in process
memory while parsing, and filesystem permissions remain those of the caller. Text-free output
reduces disclosure; it does not establish anonymity or permission to share the ledger.

A duplicate byte-identical export is counted once. Within each harness/session, stable
Copilot message IDs or Codex timestamps suppress replayed messages. Ordinal positions are
not message identities; untimed events are excluded rather than counted again. Conflicting text for the same native message identity keeps the first observation
and marks later input partial; resolve conflicting originals before using candidate counts.
Forked Codex sessions are excluded rather than guessed into distinct incidents. Distinct-session counts use harness-qualified native identity;
multiple sessions can still describe the same incident.

`complete_for_supported_messages` means this bounded parser accounted for the supplied
recognized shapes. It does not establish full transcript completeness, native-schema validity,
human authorship, correct semantic classification or review of actual behavior.
Claude Code fields and newer Codex `UserMessage` shapes reflect local exports inspected on 2026-11-18 (harness versions unrecorded); see [sources and departures](sources.md) for recheck triggers.
