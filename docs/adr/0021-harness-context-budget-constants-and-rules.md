# 0021: Document External Agent Harness Context Limits, Precedence Rules, and Mirror/Ancestor Index Semantics

- Status: Accepted
- Date: 2026-11-20

## Context

retro-agent-context/scripts/context_inventory.py models Codex and Claude Code instruction loading, skill mirrors, and code-index lookup rules based on vendor documentation observed on 2026-11-18.

## Decision

Encode the documented limits and rules: CODEX_DEFAULT_BYTES = 32 KiB (developers.openai.com/codex/guides/agents-md, observed 2026-11-18), CLAUDE_IMPORT_HOPS = 4, CLAUDE_ON_DEMAND_CHARS = 40,000 (200K context cut), and CLAUDE_LINE_TARGET = 200 advisory (code.claude.com/docs/en/memory); take the first non-empty candidate per directory for Codex; fall back to AGENTS.md in Claude chains only when no CLAUDE.md is present; detect cross-root skill mirrors by stripped body text (allowing differing frontmatter); and report ancestor code indexes only when the current checkout lacks its own.

## Consequences

Context audits match real harness behavior and preserve vendor-doc provenance and observation dates so future maintainers know when to re-verify limits.

## Code References

- `skills/retro-agent-context/scripts/context_inventory.py:24`
- `skills/retro-agent-context/scripts/context_inventory.py:25`
- `skills/retro-agent-context/scripts/context_inventory.py:26`
- `skills/retro-agent-context/scripts/context_inventory.py:27`
- `skills/retro-agent-context/scripts/context_inventory.py:141`
- `skills/retro-agent-context/scripts/context_inventory.py:186`
- `skills/retro-agent-context/scripts/context_inventory.py:244`
- `skills/retro-agent-context/scripts/context_inventory.py:312`
