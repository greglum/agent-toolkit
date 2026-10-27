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

## Sources and contributions

For generated 3D props, the [film mesh checks](skills/motion-film/references/material-3d.md#qualify-an-imported-mesh)
cover coarse inputs, scene scale and exported geometry cost.

Source notes stay beside the skill they inform. Adapted text and values retain
credit in [third-party notices](THIRD_PARTY_NOTICES.md).

See [curation](docs/curation.md) for adoption and retirement decisions,
[authoring](docs/authoring.md) before changing a skill, and
[contribution guidance](CONTRIBUTING.md) for the checks to run.
Existing users can follow the [name migration guide](docs/migrations.md).

## License

[MIT](LICENSE), with the third-party copyright and license notices listed in
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). Linked websites, model weights,
media and services have their own terms.
