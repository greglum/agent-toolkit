# Sources and departures

Observed October 29, 2026, Pacific/Honolulu. All bundled code, tests and prose are original.
No upstream prompts, implementation or transcript data copied. Fixtures are synthetic.

| Primary source and immutable revision | Read and consequence | Rights |
| --- | --- | --- |
| [GitHub Lever](https://github.com/github/lever/tree/f859d0aa2be96981157ee0480655c84877e3cd98) | prompt-mirror procedure and miner: extraction and model analysis are different privacy boundaries; counts are not verified mistakes | MIT, GitHub Inc. |
| [OpenAI Codex](https://github.com/openai/codex/blob/c9750d7f50052b29f53def02b5cf2160ae49a3d9/codex-rs/protocol/src/protocol.rs) | `UserMessageEvent`, `SessionSource`, `ThreadSource`, `SessionMeta`: source/subagent/internal distinctions, parent/fork/history fields; native user event text | Apache-2.0; LICENSE inspected |
| [Copilot SDK](https://github.com/github/copilot-sdk/blob/e22b95e6ead5e1de7e9a68d3087b8d28dc5f364a/nodejs/src/generated/session-events.ts) | `StartData`, `UserMessageData`, event agent IDs; source, autopilot, displayed versus transformed content. SDK README send options confirm omitted source and user/system/agent provenance | MIT, GitHub Inc.; LICENSE inspected |
| [Backpass](https://github.com/kunchenguid/backpass/tree/0c864ce29e355590a4ccea6eea79e5c3147b302b) | README, Codex/Claude discovery adapters and interaction classifier: separate interactive evidence, typed-role versus harness context, and distinct-session corroboration. Broader proposal/model pipeline not reviewed or reused | MIT, Kun Chen; LICENSE inspected |
| [claude-code-transcripts](https://github.com/simonw/claude-code-transcripts/tree/316fd093aca3c9c0ad8aa70092711aee3adacc6e) | README and summary/tool-result extraction sections: transcript publishing is a separate outcome; meta and tool-result records can share apparent user roles. A Claude adapter was added on 2026-11-18 from locally inspected fields, below | Apache-2.0; LICENSE inspected |
| [ccusage](https://github.com/ccusage/ccusage/tree/757b457f91028948f2cef22deeecf70f38fddfd8) | README supported-source table and resolved apps/ccusage license: usage/cost aggregation already has dedicated tooling. No token/cost parser or claimed equivalence adopted | MIT, ryoppippi; LICENSE inspected |

Public web searches independently discovered transcript, usage and correction-mining tools.
Search snippets were leads only. Public Git reads recovered pinned sources after web-reader
cache misses and sandbox DNS failures. No upstream program or private session store ran.
Code existence establishes format handling and available machinery, not efficacy or privacy.

A fresh owned slice is a bounded offline parser with fixed aggregate categories. It omits
SSH, SQLite, schema conversion, raw-text export, model scoring, prompt rewriting and instruction
application. These are separate capabilities with different input, provider or mutation
boundaries. Normalized interchange and compressed exports remain unsupported until a concrete
need justifies tested adapters.

## Repository discovery decision, 2026-11-18

The owner approved automatic discovery of the current repository's sessions on 2026-11-18,
reversing the earlier explicit-files-only decision. `--repo` reads only Claude Code and Codex
sessions whose recorded working directory resolves to the repository's git common dir, or to
another clone with the same origin URL (added after an Antigravity test found clones matched
nothing, 2026-11-19); it never
matches by folder-name slug. Antigravity's SQLite store is reported as uncovered, not parsed.
Explicit-file mode is unchanged. The Claude Code adapter and the newer Codex `UserMessage` item
shape come from schema field names and enum values inspected locally in `~/.claude/projects`
(`type`, `sessionId`, `uuid`, `cwd`, `isSidechain`, `agentId`, `isMeta`, `isCompactSummary`,
`toolUseResult`, `userType`, `promptSource`, `turnOrigin`, `origin`, and `message.content`
text/`tool_result` blocks) and `~/.codex/sessions` (`session_meta.payload.cwd`, `event_msg`
`item_completed` `UserMessage` item `id` and `content` text blocks) on 2026-11-18. Tool
version numbers were not recorded during that inspection; no session text was bundled and
fixtures stay synthetic. The reader moved to `session_records.py` and is shared byte-for-byte
with `retro-agent-friction`.

Recheck native fields, provenance enums, and session store layouts against current local
exports or upstream protocol definitions whenever the installed Claude Code or Codex release
changes, when new fields appear in `unsupported_records` or `excluded_messages`, when a
fixture reproduces misattribution, or before adding another format. Treat new metadata as
unknown until inspected; do not silently count delegated context as a new human incident.

Round 2 independently inspected [RFC 8259 section 4](https://www.rfc-editor.org/rfc/rfc8259.html#section-4),
IETF, December 2017, duplicate-member interoperability limits. Rights follow IETF Trust/BCP 78;
no text or code copied. Duplicate object members now count as malformed instead of silently
changing provenance. Untimed Codex messages remain partial coverage because ordinal fallback
cannot suppress shifted/repeated export views reliably.
