# Updating an existing install

New users can choose current names from the [catalog](catalog.md).
These legacy names have current replacements:

| Previous name | Current name | Preserved scope |
| --- | --- | --- |
| `review-java` | `review-source` | Explicit current-source audit with the Java reference |
| `review-react` | `review-source` | Explicit current-source audit with the React reference |
| `prune-comments` | `simplify-code` | Explicitly requested comment-only audit or cleanup |

Update any project instructions that require an old name before installing its
replacement. An unclear comment request stays read-only. Ordinary simplification
does not automatically start comment cleanup.

```bash
python3 scripts/install.py --only review-source,simplify-code --dry-run
python3 scripts/install.py --only review-source,simplify-code
```

The installer reports stale links into this clone. Inspect them before using
`--prune-stale`. Links to another clone are conflicts, so a new clone
will not silently replace an installation from another location. Record the old link
targets, remove only the specific links you intend to replace, then rerun the
dry run against the new clone. Keep modified real directories and the original clone
until their work and installed links have been reconciled.

Keep each clone at a stable path. Changing the public repository's display name
or Git remote does not require changing individual skill names or folder layout.
