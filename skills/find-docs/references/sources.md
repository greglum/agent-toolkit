# Documentation tool and source reference

Load this reference when querying Context7 CLI or Google Developer Knowledge, or when
rechecking tool names, CLI subcommands, and observation dates.

## Context7 CLI and ID conventions

Observed November 20, 2026 (against `ctx7` CLI / Context7 MCP conventions). Recheck when
Context7 changes its CLI subcommands, library ID format, or MCP tool signatures.

If the Context7 MCP integration is unavailable and `ctx7` is already installed in the
environment, use:

```bash
# Step 1: Resolve library ID (use official name and narrowest relevant version)
ctx7 library <name> "<query>"

# Step 2: Query documentation (library IDs require a leading '/', such as /facebook/react)
ctx7 docs <libraryId> "<query>"
```

Do not install tooling or request escalation merely to perform documentation lookup.

## Google Developer Knowledge

Reviewed November 14, 2026. Draws on the Apache-2.0
[Developer Knowledge skill](https://github.com/google/skills/blob/e3c591afe426ea585e4c21799e5199d6d47cd1be/skills/developers/retrieving-developer-knowledge/SKILL.md)
and the [official tool guide](https://developers.google.com/knowledge/mcp#server-capabilities).
Local departures from `google/skills`: original prose throughout, subordinate to local repo
and Context7 sources, explicit fallthrough to official public web sources when unavailable or
stale, and living-page reuse rights marked unassessed.
Recheck when Google changes the tool names or source coverage.

When the Google Developer Knowledge MCP tools are already connected and authorized:

1. Search with `search_documents`.
2. Call `get_documents` when the search excerpt omits relevant conditions or limits.
3. Fall through to official public web sources if the result is empty, failed, or cannot
   establish the applicable version.
