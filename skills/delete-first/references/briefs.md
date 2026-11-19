# Briefs and records

Read this before spawning finders or refuters.

## Shared finder brief

Every finder gets this text plus its partition:

- **Target:** the frozen SHA and the excluded paths.
- **Partition:** the exact paths it owns. It may read outside them to trace callers, but it
  reports only candidates inside them.
- **Contracts:** the instruction files and product docs that define required behavior, by path.
- **Hidden consumers:** reference paths plain search misses in this stack, such as names built
  from strings or called from another language, and script, hook and check registries.
- **Shared surfaces:** paths copied by other repositories or templates, published components and
  generated files. A candidate that touches one says so in `risk`.
- **Questions:** the two questions from step 3 and the delete-first ladder.
- **Prior ledgers:** Never treat a prior audit ledger as current; check `git log` after the
  ledger's date before relying on earlier findings, exclusions, or dispositions.
- **Workspace paths:** When worker sandboxes isolate coordinator scratch directories across
  harnesses (such as Antigravity), place read-only clones and shared brief artifacts in a
  shared shell-readable temp path, and keep finder records off public swarm boards.
- **Boundaries:** read and search only. No edits, no commits, no checks that write files, no
  network calls. Report an unreadable area as blocked, never as clean.
- **Return:** only candidate records, at most the 12 strongest, strongest first, then one coverage
  line. No narrative.

```text
coverage: <read fully> | skimmed: <sampled> | blocked: <unreadable> | withheld: <candidates not returned>
```

## Candidate record

```text
id: <partition>-<n>
rung: delete | simplify | simplify-original | idea
paths: <file:line, ...>
claim: <one sentence: what to remove or change>
evidence: <what was searched and what was found or not found>
assumption: <the belief that kept it, and why current evidence does not support it>
risk: <who or what could break>
proof: <the search and the check that would catch this cut being wrong>
confidence: <0-100>
```

`idea` marks optimization or automation. It is reported and never applied.

## Refuter brief

Give `id`, `rung`, `paths`, `claim` and `proof`. Withhold `evidence`, `assumption`, `risk` and
`confidence`. Where workers share a visible board or channel (such as a swarm board), keep finder records
off the public board in separate files (using a shared shell-readable temp path when worker
sandboxes isolate coordinator scratch directories) or run refuters outside it, so refuters
stay independent.

Include step 4's proof rule and its always-Decide list. Ask each refuter to find the strongest
reason the change is unsafe, using the hidden-consumer and shared-surface lists and the closest
tests, failure paths and state transitions. It stays read-only and marks anything it could not
verify. It returns, for each candidate:

```text
id: <id>
verdict: cut | decide | drop
reason: <one or two sentences>
evidence: <exact searches or file:line relied on>
required_edits: <everything the change must also touch, or none>
search_control: <a known use of the same kind that the reference search found>
check: <the narrowest check that should fail if the cut were wrong>
unverified: <what could not be confirmed for this candidate, or none>
```
