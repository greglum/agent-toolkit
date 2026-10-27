# Try one bounded task

Choose a task you can inspect yourself. Read its skill, install only that bundle,
and run it in a repository you can safely examine. Supply the branch, route,
file or local fixture the task needs. Begin at that project's `AGENTS.md`.

From this clone's root, preview the two examples below with:

```bash
python3 scripts/install.py --dry-run --only guided-review,fit-surface
```

Read the two skills and the dry-run output, then repeat without `--dry-run` to
install them. Start a new harness session if they do not appear in its skill list.

## Understand a change

In your project repository, ask Codex:

```text
$guided-review Read AGENTS.md and explain this branch against main.
Describe the behavior change, give me a sensible reading order, and point out
what still needs checking. Do not edit source or publish anything.
```

In Claude Code, replace `$guided-review` with `/guided-review`.
Check the guide against the actual diff. A reading guide is not a defect verdict.

## Check a web page

Start the app using its own documented setup and replace “settings page” below
with the route you want to check. In Claude Code:

```text
/fit-surface Read AGENTS.md and audit the local settings page at narrow and wide
widths with its longest available fixture content. Inspect overflow, keyboard
focus and accessibility. Report source findings and rendered evidence separately.
Do not change source in this pass.
```

In Codex, replace `/fit-surface` with `$fit-surface`. If the app or browser tools
are unavailable, keep the result as a source assessment and list the missing proof.
Use local fixtures or approved test identities.

## Produce a standalone diagram

Install `diagram-design`. In either harness, ask it to use that skill to explain
one named subsystem from current source. Request a small diagram first; ask for
the bundled interactive graph viewer when search or upstream/downstream tracing
would help. Check labels and relationships against source before sharing it.
The skill includes its own renderer, example input and verification instructions.

For a larger sequence with separate assessment, implementation and review, see
[the portfolio workflow](portfolio-improvement.md). Delegation is optional and
requires a harness with worker support and task authority for that work.
For Greg's projects and longer explanations, visit [GregLum.com](https://greglum.com/).
