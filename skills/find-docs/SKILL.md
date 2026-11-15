---
name: find-docs
description: Retrieve current authoritative documentation when an answer depends on uncertain, version-specific, or exact API, configuration, migration, CLI, or library behavior. Do not use for general concepts or facts already established by the current repository and task.
compatibility: Uses available local versioned sources, Context7 through MCP or an installed ctx7 CLI, and web access. Without a docs integration, read official versioned documentation, release notes, or source through an available web capability; with none, report the gap. Nothing is installed.
---

# Documentation Lookup

Retrieve current documentation and code examples when exact external behavior is material to the answer or implementation.

## Workflow

1. State the precise fact or API behavior that is uncertain and identify the relevant library and version when known.
2. Read matching local documentation or dependency source when it establishes the exact installed version's behavior. Discover available documentation tools instead of assuming a particular local service exists.
3. If local evidence is absent or insufficient and the uncertainty remains material, resolve the exact library and version in Context7, then query that ID through its MCP integration or an installed CLI.
4. If Context7 is unavailable or insufficient and the question is about a Google product,
   use Google Developer Knowledge when its tools are already connected and authorized.
   Search with `search_documents` and use `get_documents` when the excerpt leaves out
   relevant conditions. Continue to the official web sources below if the result is empty,
   failed, or cannot establish the applicable version.
5. Use available web/search tools to read official versioned documentation, release notes,
   or source if the integrations above leave the question open.
   Search snippets are leads; read the cited page before relying on them. When the answer
   is in a dependency's source, read it at the version the lockfile pins, for example a
   shallow clone of that tag outside the repository, not the default branch.
6. Stop when the precise uncertainty is resolved. Report the source link or local
   reference, applicable version, and any mismatch or inference. Current documentation
   does not prove compatibility with an older installed version. The absence of an exact
   local source does not require another lookup when the available evidence resolves the question.

Keep queries specific and omit credentials, personal data, proprietary code, and other sensitive content.

## Conditional CLI reference

If the MCP integration is unavailable and `ctx7` is already installed in the environment, it may be used. Do not install tooling or request escalation merely to perform documentation lookup.

Typical CLI flow:

```bash
# Step 1: Resolve library ID
ctx7 library <name> "<query>"

# Step 2: Query documentation
ctx7 docs <libraryId> "<query>"
```

Resolve a library ID when one is not already known, then query that ID. Stop after a proportionate number of focused attempts and explain any unresolved gap.

## Selecting and querying a source

Use the official library name and the narrowest relevant version. When alternatives exist, prefer the exact name, version, primary-source provenance, and coverage relevant to the uncertainty. Keep each query to one topic unless the interaction between topics is the question. Describe the API behavior to look up rather than pasting task context or source code. Library IDs need a leading `/`, such as `/facebook/react`; write descriptive queries ("React useEffect cleanup function", not "hooks").

## Error Handling

If no available source resolves the uncertainty, explain the gap and any qualified inference. Do not expose or solicit credentials to work around a documentation lookup limitation.

## Sources

Reviewed November 14, 2026. The optional Google fallback draws on the Apache-2.0
[Developer Knowledge skill](https://github.com/google/skills/blob/e3c591afe426ea585e4c21799e5199d6d47cd1be/skills/developers/retrieving-developer-knowledge/SKILL.md)
and the [official tool guide](https://developers.google.com/knowledge/mcp#server-capabilities).
This bundle uses an existing connection when available and falls through to public sources.
Recheck when Google changes the tool names or source coverage.
