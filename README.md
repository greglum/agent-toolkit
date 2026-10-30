# Agent toolkit

Skills, command-line tools, and workflow guides for Claude Code and Codex,
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
| Explain a system and explore its relationships | [diagram-design](skills/diagram-design/SKILL.md) | A diagram or standalone graph viewer |
| Check a rendered film | [motion-film](skills/motion-film/SKILL.md) | Source, playback and export checks using its production tools |
| Turn a conversation into buildable work | [to-spec](skills/to-spec/SKILL.md) | A spec with scope, decisions and acceptance conditions |

Browse the [full catalog](docs/catalog.md) or [workflow map](docs/workflows.md).
For a copyable first task, see [usage examples](docs/examples/getting-started.md).

## Install a few skills

Requires Python 3.10+ and macOS or Linux. Windows symlinks need Developer Mode
and have not been tested. Some bundled checks also require Node.js 18+.

```bash
git clone https://github.com/greglum/agent-toolkit.git
cd agent-toolkit
python3 scripts/check.py
python3 scripts/install.py --dry-run --only fit-surface,guided-review
python3 scripts/install.py --only fit-surface,guided-review
```

Read the selected skills before running the installer, then inspect the dry-run output
before installing. Add `--harness claude` or `--harness codex` to select one
harness; the default is both. Leave out `--only`
to install the whole catalog.

The installer creates links into your clone. Keep it in one place. It archives
an identical existing directory before linking, reports differing copies or
links to another clone as conflicts, and leaves those conflicts untouched.
It reports stale links; only `--prune-stale` removes those links.
It does not change providers, permissions, credentials, settings, or Git hooks.

After installation, check the skill list in your harness. Restart the session
if a newly installed skill is missing. A personal skill can shadow a project
skill with the same name; check names before installing globally.

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

A skill supplies a method. The agent runs it through your existing tools and
permissions. Your task and repository instructions govern the work. Installing
one does not authorize publishing, spending, deleting data, or sending source
to another service.

## What is checked

The catalog validator checks packaging, invocation controls, portable paths and
local links. Bundled tools have automated tests. Review a skill's output using
the destination project's own tests, browser checks and release gates.

From the clone's root, run `sh scripts/verify.sh` for the automated checks. See
[verification and limitations](docs/verification.md) for prerequisites and coverage.

For a longer explanation with a runnable example, see [how the toolkit works](docs/overview.md).

## Sources and credits

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

For linked X sources, the [recovery procedure](skills/skill-research/references/source-intake.md#x-post-and-article-recovery)
checks other permitted browsers and rendered text when a reader or browser backend fails.

For generated 3D props, the [film mesh checks](skills/motion-film/references/material-3d.md#qualify-an-imported-mesh)
cover coarse inputs, scene scale and exported geometry cost.

For recorded footage, the [speech-editing notes](skills/motion-film/references/sources-editing.md#october-27-video-editor-review)
explain verbatim transcript checks and matched-frame correction review.

Source notes stay beside the skill they inform. Adapted text and values retain
credit in [third-party notices](THIRD_PARTY_NOTICES.md).

Existing users can follow the [name migration guide](docs/migrations.md).
Report problems and requests through [issues](CONTRIBUTING.md).

## License

[MIT](LICENSE), with the third-party copyright and license notices listed in
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). Linked websites, model weights,
media and services have their own terms.
