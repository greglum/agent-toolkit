# Agent toolkit

Skills, command-line tools, and workflow guides for Claude Code, Codex, and Antigravity,
maintained by Greg Lum. They cover code review, debugging, web design, diagrams,
films, and source-backed writing.

Each skill combines instructions with the references or scripts needed for one job.
Install the parts you need and use them through your existing agent and tools.
Each skill lists its extra prerequisites.

Visit [GregLum.com](https://greglum.com/) for Greg's projects and longer explanations
of his work. This repository holds the installable bundles and usage documentation.

## Start with a task

| If you want to | Start with | What you get |
| --- | --- | --- |
| Compare noisy measurements | [compare-experiments](skills/compare-experiments/SKILL.md) | Paired effects, failed/missing observations and confirmation evidence |
| Order a set of pull requests | [plan-pr-stack](skills/plan-pr-stack/SKILL.md) | Candidate dependency waves and unresolved ordering decisions |
| Review selected agent-history exports | [analyze-agent-history](skills/analyze-agent-history/SKILL.md) | Text-free correction candidates and coverage limits |
| Check a web page across widths and states | [fit-surface](skills/fit-surface/SKILL.md) | A measured layout and accessibility check |
| Understand a large change before reviewing it | [guided-review](skills/guided-review/SKILL.md) | A reading guide tied to the actual diff |
| Investigate a disputed dashboard number | [reconcile-metric](skills/reconcile-metric/SKILL.md) | An independent calculation with the difference explained |
| Find and check an implicit state machine | [state-machine-audit](skills/state-machine-audit/SKILL.md) | Source-backed transitions, a bounded check, and a statechart |
| Explain a system and explore its relationships | [diagram-design](skills/diagram-design/SKILL.md) | A diagram or standalone graph viewer |
| Explore a system's parts and behavior | [system-anatomy](skills/system-anatomy/SKILL.md) | A source-grounded interactive anatomy or cutaway |
| Check a rendered film | [motion-film](skills/motion-film/SKILL.md) | Source, playback and export checks using its production tools |
| Export selected short clips | [repurpose-long-video](skills/repurpose-long-video/SKILL.md) | Local MP4s, caption sidecars and an edit list from supplied timings and crops |
| Reconcile an extracted corpus | [extract-documents](skills/extract-documents/SKILL.md) | Requested-input coverage, file identities and explicit conversion failures |
| Get up to speed on unfamiliar data and a new domain | [onboard-data](skills/onboard-data/SKILL.md) (by name), [learn-domain](skills/learn-domain/SKILL.md), [map-data-source](skills/map-data-source/SKILL.md) | A cited primer and glossary, an evidence-backed data dictionary and one ranked question list |
| Check sensor data, find faults or validate time-ordered models | [telemetry-contract](skills/telemetry-contract/SKILL.md), [telemetry-anomalies](skills/telemetry-anomalies/SKILL.md), [temporal-validation](skills/temporal-validation/SKILL.md) | Contract findings, budgeted event-level faults and leakage audits |
| Turn a conversation into buildable work | [to-spec](skills/to-spec/SKILL.md) | A spec with scope, decisions and acceptance conditions |

Browse the [full catalog](docs/catalog.md) or [workflow map](docs/workflows.md).
For a copyable first task, see [usage examples](docs/examples/getting-started.md).

## Install a few skills

Requires Python 3.10+ and macOS or Linux. If your `python3` is older, see
[troubleshooting](#troubleshooting). Windows symlinks need Developer Mode and have not
been tested. Some bundled checks also require Node.js 18+.

```bash
git clone https://github.com/greglum/agent-toolkit.git
cd agent-toolkit
python3 scripts/check.py
python3 scripts/install.py --dry-run --only fit-surface,guided-review
python3 scripts/install.py --only fit-surface,guided-review
```

Read the selected skills before running the installer, then inspect the dry-run output
before installing. Add `--harness claude`, `--harness codex`, `--harness antigravity`,
or `--harness all` to select harnesses; the default is `both` (Codex and Claude Code).
Leave out `--only` and `--pack` to install the whole catalog. Use `--only` with Antigravity to keep its
list curated; Codex-only skills get no Claude Code or Antigravity link.

To install a group, use a pack from `packs.json`. `--list-packs` prints each pack and its
skills. `--pack` takes comma-separated pack names and combines with `--only`:

```bash
python3 scripts/install.py --list-packs
python3 scripts/install.py --dry-run --pack engineering,data
python3 scripts/install.py --pack engineering,data --only fit-surface
```

An unknown pack name stops the run, changes nothing, and lists the valid packs. Some skills
need companions: for example, `polish-animations` needs `find-animation-opportunities`,
`animate` and `review-animations`. When a selected skill's companions are neither selected
nor installed, the run warns, names them, and prints the `--only` line that adds them. It
never installs a companion on its own.

The installer creates links into your clone. Keep it in one place. In `~/.agents/skills`
it archives an identical existing directory before linking. A differing copy there, any
real file or directory in `~/.claude/skills` or `~/.gemini/config/skills`, and a link to
another clone are reported as conflicts and left untouched.
It reports stale links; only `--prune-stale` or `--prune-only` removes those links.
It does not change providers, permissions, credentials, settings, or Git hooks.

After installation, check the skill list in your harness. Restart the session
if a newly installed skill is missing. A personal skill can shadow a project
skill with the same name; check names before installing globally.

## Update

```bash
git pull
python3 scripts/install.py --dry-run --only fit-surface,guided-review
```

Installed skills are links, so a pull updates their text. Preview using the names you
installed. To add skills, rerun the installer with those names after reviewing its dry run;
leaving out `--only` selects the whole catalog.

Stale links are reported and kept. If a name you installed has left the catalog, the run stops
with `unknown skills`, changes nothing, and still reports its stale links. Drop that name; leaving
out `--only` altogether would select the whole catalog. After reading the report, this removes
the stale links and installs nothing. Add `--dry-run` first to preview it:

```bash
python3 scripts/install.py --prune-only
```

## Troubleshooting

| What you see | What to do |
| --- | --- |
| `Python 3.10 or later is required` | Use a newer installed Python, for example `python3.12 scripts/check.py`. `sh scripts/verify.sh` always runs `python3`, so put the newer one first on your `PATH` for it. |
| `Node.js 18+ is required` | The full test run and some bundled tools need Node. Use a supported version, or choose skills that do not require it. |
| `unknown packs: ...` | Nothing was installed. Run `python3 scripts/install.py --list-packs` for the valid names. |
| `unknown skills: ...` | Nothing was installed. Check the spelling against the [catalog](docs/catalog.md). If a stale link has the same name, that skill has left the catalog; see [update](#update). |
| `conflict: ... differs from the catalog` | A real file or directory in `~/.agents/skills` differs from this clone's copy. It was left alone; other names in the same run were still installed. It stays a conflict until it matches or moves. To use the catalog version, copy out anything you want and move it elsewhere, then rerun. To keep yours, leave that name out of `--only`. |
| `conflict: ... is a real file or directory` | Something other than a link occupies that `~/.claude/skills` or `~/.gemini/config/skills` path. It is left alone even when its files match the catalog; only `~/.agents/skills` copies are archived. Handle it the same way. |
| `Stopped: ...` | The installer could not use a path, such as a file where a skills folder belongs. Fix that path and rerun. |
| `conflict: ... links to ...` | The skill is linked from another clone. See the [migration guide](docs/migrations.md). |
| A skill is missing from the agent's list | Start a new session. Codex-only skills have no Claude Code or Antigravity link; see the [catalog](docs/catalog.md). |
| A browser cannot start | Record its error and report rendered checks as unverified. See [what was tested](docs/verification.md#tested-in-real-harnesses). |

## Use a skill

In Claude Code:

```text
/fit-surface Audit the existing settings page at narrow and wide widths.
Report findings before changing source. Follow this project's AGENTS.md.
```

In Codex:

```text
$guided-review Explain the changes on this branch against main.
Give me a reading order and describe the important behavior changes.
```

In Antigravity, name the skill in your prompt or rely on automatic selection from its
`description` (it uses no `/` or `$` prefix).

[What was tested in each harness](docs/verification.md#tested-in-real-harnesses) records the
revision, versions and limits, including a browser that would not start under Codex's
`workspace-write` sandbox on macOS.

A skill supplies a method. The agent runs it through your existing tools and
permissions. Your task and repository instructions govern the work. Installing
one does not authorize publishing, spending, deleting data, or sending source
to another service.

## What is checked

The catalog validator checks packaging, invocation controls, portable paths, local
links, that the catalog table and workflow map agree with the skills folder, and that
`packs.json` names real skills and places every skill in a pack. Bundled tools have automated tests. Review a skill's output using
the destination project's own tests, browser checks and release gates.

From the clone's root, run `sh scripts/verify.sh` for the automated checks. See
[verification and limitations](docs/verification.md) for prerequisites and coverage.

For a longer explanation with a runnable example, see [how the toolkit works](docs/overview.md).

## Sources and credits

[Documentation lookup](skills/find-docs/references/sources.md#google-developer-knowledge) can use an existing Google
Developer Knowledge connection. The [security audit coverage guide](skills/security-audit/references/coverage.md)
records what a policy simulator evaluated and which cases need further checks.

The [editing notes](skills/motion-film/references/sources-earlier.md#speech-editing-and-frame-feedback-sources-october-25-to-november-6-2026) credit the research on
proposed speech cuts and saved revisions. The [21st.dev reference](skills/web-app-design/references/resource-index.md#21stdev-magic-proxy-and-request-boundary)
records the legacy Magic proxy and hosted request boundary.

The [campaign source notes](skills/motion-film/references/sources.md#reusable-campaigns-november-14-2026)
credit the review of reusable motion campaigns and parameterized rendering.

[Learn Taste](skills/learn-taste/SOURCE.md) credits the correction-to-guidance workflow and
explains the scope of the adaptation.

The [browser support check](skills/web-app-design/references/design-synthesis.md#browser-support-check)
credits the Modern Web Guidance research on browser targets and fallback behavior.

The [opening questions source note](skills/content-marketing/references/sources.md#opening-questions-november-8-2026)
credits a reader check for question-led openings and records the limits of the studies.

The [spec handoff source note](skills/to-spec/SOURCE.md#spec-handoff-review) credits the
independent comprehension check and describes its evidence limits.

The [drag recipe](skills/animate/references/recipes.md#drag-release) credits the AI for UI
gesture reviews and covers linked effects, release ownership and reversal.
The [Swift skill](skills/write-swift/SKILL.md#sources) explains how struct copies can
share mutable backing.

The [state machine audit source notes](skills/state-machine-audit/SKILL.md#sources) credit
the verification workflow and distinguish a model check from an implementation test.

The [cleanup inventory](skills/repository-cleanup/SKILL.md#1-establish-scope-and-a-complete-inventory)
keeps worktree status unavailable when inspection would need a configured Git filter.
The [extraction checker](skills/extract-documents/references/manifest-check.md) accounts for
unsupported inputs and refuses ambiguous manifest keys.

The [simplify-code source note](skills/simplify-code/SKILL.md#source-note) credits the
research behind using Git history to clarify ownership during a refactor.

For physical mechanisms, the [modeling guide and offline example](skills/system-anatomy/references/mechanisms.md)
cover parameter provenance, model limits, numerical checks and synchronized controls/readouts.

For GLB props, the [offline inventory and mesh checks](skills/motion-film/references/material-3d.md#qualify-an-imported-mesh)
list declared loader dependencies and animation data before scene review. The
[draft-finalization checks](skills/motion-film/references/generated-plates.md#preserve-requested-and-effective-inputs)
keep selected take identity and full-route pricing together.

For noisy improvement work, the [measurement procedure](skills/loop-engineering/SKILL.md#freeze-the-contract)
records unchanged-run variation and confirms selected or combined changes.
Its [source notes](skills/loop-engineering/references/sources.md#noisy-measurements-and-confirmation)
record the Lever revision and intentional departures.

For generated video edits, the [source and mask checks](skills/motion-film/references/generated-plates.md)
cover prepared input alignment and unintended changes outside the edit.

For editable films, the [saved-source handoff checks](skills/motion-film/references/production.md#verify-an-editable-studio-handoff)
cover saved edit targets as well as reopening and export.

For threat-model updates, the [baseline-review procedure](skills/security-audit/references/baseline-review.md)
preserves scenario IDs and separates resolved threats from retired ones. The
[failure-state checks](skills/security-audit/references/coverage.md#response-contracts-under-failure)
cover response guarantees and preserved failure detection.

For skill evaluations, the [case and grading protocol](skills/harden-skill/references/evaluation.md)
separates regression protection from capability probes and checks required behavior while
allowing valid alternative methods.

For linked X sources, the [recovery procedure](skills/skill-research/references/url-and-source-intake.md#x-post-and-article-recovery)
checks other permitted browsers and rendered text when a reader or browser backend fails.

For generated 3D props, the [film mesh checks](skills/motion-film/references/material-3d.md#qualify-an-imported-mesh)
cover coarse inputs, scene scale and exported geometry cost.

For recorded footage, the [speech-editing notes](skills/motion-film/references/sources-earlier.md#october-27-video-editor-review)
explain verbatim transcript checks and matched-frame correction review.

For a film based on an existing format, [map the reference's story beats to the new subject](skills/motion-film/references/direction.md#adapt-a-references-story-structure)
before making assets. The [source notes](skills/motion-film/references/sources.md#november-7-reference-format-adaptation)
explain the scope of the Scenario comparison.

For reference reconstruction, the [source notes](skills/motion-film/references/sources.md#november-4-reference-reconstruction)
record caption/text matching, timing checks and remaining tooling gaps.

The [local clip-export guide](skills/repurpose-long-video/references/clip-export.md) covers
supplied transcripts, fixed crops and encoded timestamp checks. The
[extraction manifest checker](skills/extract-documents/references/manifest-check.md) checks
file accounting while leaving content fidelity to source review. For skill comparisons,
the [runtime receipt importer](skills/harden-skill/references/native-receipts.md) preserves
reported Codex usage and incomplete runs without inventing grades or acceptance.

Source notes stay beside the skill they inform. Adapted text and values retain
credit in [third-party notices](THIRD_PARTY_NOTICES.md).

Existing users can follow the [name migration guide](docs/migrations.md).
Report problems and requests through [issues](CONTRIBUTING.md).

## License

[MIT](LICENSE), with the third-party copyright and license notices listed in
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). Linked websites, model weights,
media and services have their own terms.

The reusable [trial procedure](skills/loop-engineering/references/harness-trials.md)
compares candidates and their composition inside the task's selected execution boundary.
