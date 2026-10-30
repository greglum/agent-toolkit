# Accepted exports and interpretation

The CLI reads explicit regular files, never directories, glob expressions, compressed files,
SQLite databases or remote URLs. Shell expansion happens before the CLI. Limits are 128
inputs, 64 MiB per file and 1 MiB per record. An oversized input is excluded in full.
Malformed JSON, duplicate object members, invalid UTF-8 and non-object records are counted; other readable records
may still contribute to a partial ledger. Errors identify input ordinals, not paths or content.

## Codex rollout JSONL

The first parsed record must be `session_meta` with `payload.id` and `payload.source`.
Supported source values are `cli`, `vscode` and `mcp`. Source is a metadata assertion, not
proof that a human supplied every message. Missing, custom or unknown provenance is excluded
with partial coverage. Known internal, exec, subagent, parent, fork and inherited-history
metadata exclude the entire session, including its first turn.

Only `event_msg` with `payload.type: user_message`, a string `payload.message` and a
nonempty stable `timestamp` contributes. Untimed user events make coverage partial.
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
