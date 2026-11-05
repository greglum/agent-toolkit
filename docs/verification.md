# Verification and limitations

## Run the checks

From the clone's root:

```bash
sh scripts/verify.sh
```

This runs the catalog validator, installer and validator tests, and every bundled
Python and JavaScript test suite. Python 3.10+ and Node.js 18+ must be on PATH.
The diagram generator uses Node; media helpers use FFmpeg/ffprobe when exercised
against real media. Optional browser, graphics, document and provider tools are
listed in the selected skill. No provider call or dependency install is part of
this command. Tests use local fixtures and mocked boundaries where appropriate.
The development checkout also runs its maintainer tests, including public snapshot
preservation checks. Public archives omit that private directory and run the same
entrypoint with the portable suites.

The optional repository pre-commit hook adds a staged secret scan and requires
Gitleaks. Keep any existing global hook policy; run these checks
manually or integrate them through the hook owner instead of replacing it blindly.

For a local snapshot secret scan with an installed Gitleaks:

```bash
gitleaks dir . --redact --no-banner
```

For existing Git history, use `gitleaks git . --redact --no-banner`.
A clean scan does not establish the absence of private names or all sensitive data.
The validator also reads a local private-name list when configured, and reports
when that check is skipped. Keep that list outside the clone.

## What the checks establish

| Evidence | Supports | Does not establish |
| --- | --- | --- |
| Catalog validator | Bundle structure, invocation metadata, portability rules, relative links, the catalog's skill table agreeing with skill folders | Native automatic skill selection or successful execution |
| Installer tests | Link, archive and conflict behavior on temporary directories | Every operating system or an existing user's installation |
| Bundled tool tests | The cases asserted by each suite | Every input, optional integration or real-media result |
| Supplied-skill trial | Behavior on its recorded task, model and environment | General superiority over a no-skill control |
| Source or license note | The recorded source and its stated reuse boundary | Current service terms or a license for linked assets |

Use the destination project's source, runtime and human checks for the result you intend
to deliver. These catalog checks do not measure general productivity, model quality or
production readiness.

## Tested in real harnesses

Run on November 4, 2026, on macOS, against the skills as they stood just before the release this
table ships in (52 skills). Of the four skills below, only `fit-surface` changed after the runs, by
the sandbox note its table row describes. Later edits to a skill are not covered until it is rerun.
Claude Code 2.1.312 ran with `--model sonnet` (`claude-sonnet-5-5`), `acceptEdits` and a 22-entry tool
allowlist that included `python3` and `node`. Codex 0.165.0 ran `codex exec --sandbox workspace-write`; its session logs name `gpt-6.1-sol`.
Each run's request named one installed skill (`/name` or `$name`) on a small synthetic sample
project, and a separate script then compared the result with answers kept out of that project.
The `fit-surface` sample came with `puppeteer-core` and `CHROME_PATH` already set up; the skill does
not provide them.

| Skill and task | Claude Code | Codex |
| --- | --- | --- |
| `guided-review`: explain a sample branch, covering every changed path | Passed | Passed |
| `reconcile-metric`: find why a dashboard total disagrees with a closed figure | Passed | Passed |
| `compare-experiments`: pick from noisy runs without counting failed ones | Passed | Passed |
| `fit-surface`: fix overflow on a sample page and measure it | Passed, measured in a browser | Page fix passed; rendered fit unverified because the browser did not start |

These are the limits of that record:

- Under Codex's `workspace-write` sandbox on macOS, headless Chromium stopped before loading a
  page. The Codex run said so and reported rendered fit as unverified; the separate script measured
  that run's page afterward. Treat rendered measurement in that sandbox as unproven. Other Codex
  sandbox settings and Linux were not tried.
- `/name` and `$name` both ran the installed skill. In one trial each, both harnesses chose
  `guided-review` from its description alone and did not use the by-name `docs-sync` when it was
  not named. One trial does not establish how reliably an agent selects a skill.
- Codex read skills from an isolated `~/.agents/skills`. Claude Code could not log in under a
  temporary home on macOS, so its runs loaded the installed links through the sample project's
  `.claude/skills`, with user settings excluded. A separate session in a real home, whose links
  point at another checkout at an unpinned revision, listed skills linked the way the installer
  links them and did not list a Codex-only skill.
- With an allowlist of `Bash(cat:*)`, Claude Code ran `cat` on a project file and through a link
  that stays in the project, and blocked it through a link that resolves outside the project. Its
  message names the session's allowed working directories. Its file-read tool read that path in
  the task runs.
- The other 48 skills were not run this way. There was no no-skill control, so this does not show
  that a skill improves on an agent working without one.

`sh scripts/verify.sh` passed on those same skills with Python 3.10.22 and Node.js 18.20.8, the
stated minimums.

## New local evidence tools

The clip exporter has synthetic NTSC and variable-frame-rate media checks. Encoding and
timestamp proof remain separate from context, crop safety, listening and normal playback.
The extraction checker reconciles declared inputs/outputs and hashes; it does not certify
content fidelity or locator accuracy. The Codex receipt importer preserves reported runtime
state and usage; it does not run a model or produce grading, control or invocation evidence.
See each bundle's guide for its actual input contract and unverified dimensions.
