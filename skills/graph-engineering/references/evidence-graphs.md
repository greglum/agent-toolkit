# Source-bound evidence graphs

Use this adapter to preserve a small reviewed dependency graph across edits and query its
consumers. Prefer existing extraction/index tools for discovery. This tool does not parse
source, resolve names, detect newly added files or establish that an authored edge is true.
It checks source bytes, source line existence, graph shape and the repository HEAD.

Author a JSON file with this shape:

```json
{
  "version": 1,
  "question": "Which consumers need checking when the guide registry changes?",
  "coverage": "Reviewed guide registry and hub only. Build and runtime consumers still need inspection.",
  "nodes": [
    {"id": "registry", "source": {"file": "src/guides.ts", "line": 1}},
    {"id": "hub", "source": {"file": "src/Hub.tsx", "line": 1}}
  ],
  "edges": [
    {"from": "hub", "to": "registry", "relation": "imports", "status": "observed",
     "source": {"file": "src/Hub.tsx", "line": 1}}
  ]
}
```

Every arrow points from consumer to dependency. `observed` means source-checked,
`inferred` is a tool or analyst lead, and `proposed` describes an intended relationship.
Retain conditions in the relation or an extra `condition` field; traversal does not evaluate
them. Multiple relations between a pair remain separate. Cycles terminate safely.
Node IDs must be unique; every edge and node needs a repository-relative source locator.
Do not include credentials or private source text. The tool rejects paths escaping the
supplied root, including symlinks. Use only a repository root you are authorized to read.

Commands use the installed skill's directory as `<skill>`:

```bash
node <skill>/scripts/evidence-graph.mjs seal authored.json . > snapshot.json
node <skill>/scripts/evidence-graph.mjs check snapshot.json .
node <skill>/scripts/evidence-graph.mjs impact snapshot.json . registry
```

Write a new snapshot file, preserving the original for comparison. `seal` reads only and
prints JSON; the shell redirection owns the output. Never redirect over the input. `check`
and `impact` fail with exit 1 on stale, missing, edited or malformed evidence. They hash
whole referenced files, so even a same-HEAD dirty edit invalidates the snapshot. Changes
outside those files, newly introduced consumers and semantic truth require independent
source review. Hashes detect accidental drift, not malicious forgery.

After changing an owner, inspect the affected source and update the model before sealing
again. A successful check proves that the recorded evidence is unchanged, not that the
implementation works or the index covers the workspace. Attach real gate and browser results
to the task record. Use diagram-design when the reader also needs a visual map.
