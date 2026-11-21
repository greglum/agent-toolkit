# Signals, lenses and limits

## Reading the inventory

- `codex_chains`: one entry per directory that holds an instruction file. Codex reads one file per
  directory from the repository root down to the working directory: `AGENTS.override.md`, then
  `AGENTS.md`, then each configured fallback name, and skips empty files. `bytes` joins the files
  with blank lines, so it can differ from Codex by a few bytes per file; call it measured within
  that margin. The user's global `AGENTS.md` and its effect on the limit are not measured. `near`
  means at least 90 percent of the limit: the next useful line may be cut.
- `claude_chains`: `CLAUDE.md`, `.claude/CLAUDE.md` and `CLAUDE.local.md` from the root to that
  directory with `@imports` expanded, or the `AGENTS.md` files when the chain has no `CLAUDE.md`
  (Claude Code's default). `missing_imports` lists imports that resolve to nothing. A scoped package
  name written in prose, such as `@scope/pkg`, parses as an import; that is a real but harmless
  miss unless it sits in a code span. `on_demand_over_char_cut` marks a nested file past the
  per-file cut; `over_line_target` is advisory.
- `claude_rules`: rules without a `paths` field load at launch and add to every chain.
- `skills`: unique `SKILL.md` bodies by word count. `mirrors` are symlinks or byte-identical
  copies in a second skill root; count them once. Compare the spread with any repository budget
  and its exemption list. A budget that exempts many skills, or an exemption list that grows over
  the window, is a finding.
- `missing_paths`: `link` targets are high confidence. `code_span` targets are candidates: a skill
  that generates files names paths that do not exist yet, and `gitignored: true` marks build
  output or local files. Confirm each at the head before reporting it.
- `code_index`: whether an index folder exists in this checkout, the nearest ancestor index a
  tool would use when this checkout has none, other worktrees with one, and each owning
  checkout's distance from the analyzed ref. An index owned by a checkout many commits behind,
  or one that only an ancestor or another worktree has, answers from other source. Index
  freshness inside a checkout is not measured; say so.

## Lenses

Group evidence by the invariant it breaks:

- **Near a limit:** a chain at or over a hard limit, or one that grew across the window. One
  measurement at the head is enough for `confirmed`. Report its bytes and the next file that
  would be cut.
- **Silent wrong source:** a code index, generated projection or mirrored skill that answers from
  another checkout or an older copy.
- **Repeated drift:** two or more corrections in the window of the same doc area or the same claim
  class, such as stale commands, wrong config locations or moved paths, even when the files
  differ. Read the diffs, not only `--stat`, to name the class. Hand the next correction to
  docs-sync, and ask whether a check could catch the class.
- **Owned elsewhere:** instruction lines removed because a gate, type or manifest already enforced
  them. Each removal is evidence that more such lines remain; list the remaining candidates.
- **Unenforced rule:** a prose rule that commits keep breaking or reviews keep restating.
- **Budget erosion:** exemptions added to a size or context budget instead of trims.
- **Dead pointer:** a link, import or named path that no longer exists.

Discard preference edits and wording polish with no behavioral reason.

## Ledger additions

Context findings use the [ledger](ledger.md) schema plus a `measure` object when a size drives the
finding: `{"value": 0, "limit": 0, "unit": "bytes", "ref": "commit", "source": "measured"}`. A
later run compares the same chain or file against it. Store paths and counts, never file text.

## Harness limits

Observed 2026-11-18. Recheck when a harness changes its loading rules.

- [Codex, AGENTS.md guide](https://developers.openai.com/codex/guides/agents-md): concatenates
  root to working directory, one file per directory, and stops adding files once the combined
  size reaches `project_doc_max_bytes`, 32 KiB by default and configurable. The
  [advanced configuration page](https://developers.openai.com/codex/config-advanced) describes the
  same key as a per-file amount; the inventory uses the combined reading, so say so when a chain is
  near. That page also says a repository's `.codex/config.toml` applies only to a trusted project,
  so a limit read from it is unconfirmed until the user confirms trust.
- [Claude Code, memory](https://code.claude.com/docs/en/memory): launch files load whole up to
  4 MiB; imports expand at most four hops and skip code spans and fences; on-demand nested files
  and path-scoped rules are cut at 40,000 characters with a 200K context window and higher limits
  with 1M; under 200 lines per `CLAUDE.md` is a target, not a limit.

A repository may set a lower budget of its own to leave room for global files. Report both, and
say which one the finding breaks.
