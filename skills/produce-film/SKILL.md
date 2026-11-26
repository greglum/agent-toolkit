---
name: produce-film
description: >-
  Coordinate end-to-end film production across optional 3D assets (blender-scene), hand-drawn
  SVG scenes (svg-illustration), timeline build and motion QA (motion-film), short-clip
  cutdowns (repurpose-long-video), and covers (thumbnail-production). Explicit only
  (/produce-film or $produce-film). Never auto-invokes distribution-draft; hands off social
  copy explicitly. Arguments: scope (full, assets-and-film, film-only, repurpose, plan-only)
  and max-workers=N. Not for a standalone film edit (motion-film) or standalone cover
  (thumbnail-production).
disable-model-invocation: true
compatibility: >-
  Requires motion-film; optional stages require blender-scene, svg-illustration,
  repurpose-long-video, or thumbnail-production when selected. Installing this bundle alone
  does not install companions. Missing companions mark only dependent stages unavailable or
  blocked without installing them. Never commits, publishes, or authorizes paid takes.
---

# Produce film

Explicit-only orchestrator (`/produce-film` in Claude Code, `$produce-film` in Codex) for
end-to-end film production. You are the director and integrator: you bind the brief, freeze the
shared clock (`timing.json` or cue sheet), dispatch isolated asset and film stages, keep the
blind reviewer separate from the builder, and deliver one reconciled package. This skill owns
no render or asset evidence itself; each child skill produces and verifies its own artifacts.

## Arguments and authority

- `scope`: `full` (default), `assets-and-film`, `film-only`, `repurpose`, or `plan-only`.
- `max-workers=N`: positive integer capping concurrent local build or render processes (default
  `2`). Never spawn unbounded parallel renders.

| Scope | Phases run | Skipped phases (recorded `skipped` or `not run`) |
| --- | --- | --- |
| `full` | 1, optional 2, 3, optional 4, optional 5, 6 | Any unrequested optional stage |
| `assets-and-film` | 1, 2, 3, 6 | Phases 4 and 5 |
| `film-only` | 1, 3, 6 | Phases 2, 4, and 5 |
| `repurpose` | 1 (bind existing approved master cut and rights), 4, optional 5, 6 | Phases 2 and 3 |
| `plan-only` | 1 (brief, clock plan, companion check), 6 | Phases 2 through 5 (`not run`) |

Stop with a clear error before starting if `scope` is unrecognized or `max-workers` is not a
positive integer. Preserve existing project work and action authority: this orchestrator leaves
changes uncommitted and never authorizes installs, paid voice/video generation, or publishing.

## Run state

Keep resumable state outside version control at `<git-dir>/produce-film/<run-id>/state.md`
(where `<git-dir>` comes from `git rev-parse --git-dir`, or a task-specific scratchpad without
Git). Use a unique run ID and never overwrite an existing run's state. Record the base
revision, brief path, frozen clock path, companion availability, asset ledger, stage statuses
(`pending`, `running`, `passed`, `failed`, `blocked`, `unavailable`, `not run`, `skipped`),
exact check receipts, and open user decisions.

## Before each stage

Check that the stage's child skill is installed before invoking it. If a required child is
missing:

1. Name the missing skill and the stage it blocks.
2. Tell the user to install it with `python3 scripts/install.py --only <name>` (or
   `--pack film-and-content`).
3. Mark that stage `unavailable`, mark dependent stages `blocked`, and continue any independent
   stage that can finish honestly.

Pass and check stage artifacts using [the handoff contract](references/handoff.md).

## Phases

1. **Bind the brief and master clock.**
   - Read repository instructions, existing film briefs, brand tokens, and cleared asset
     records. Record thesis, audience, delivery formats, fps, dimensions, duration budget,
     audio/caption scope, and numeric process cap (`max-workers`).
   - Write or freeze the shared cue sheet or `timing.json` (seconds and derived frame indices)
     before dispatching asset or scene stages so picture, 3D/SVG elements, and sound share one
     clock.
   - In `plan-only`, stop after recording the brief, clock plan, and companion inventory, and
     jump to Phase 6 (Report) with build and render stages marked `not run`.

2. **Prepare custom assets (optional; skipped for `film-only`, `repurpose`, `plan-only`).**
   - **3D props, costumes, or scenes:** when the brief needs custom Blender assets, invoke
     `blender-scene` (`#1-bind-target-units-and-safety-boundary` through `#6-export-and-hand-off`,
     including `#3-write-version-portable-bpy-scripts-and-lint-them` and
     `#4-import-ground-and-license-external-assets`) with units, pivot rules, clearance
     constraints, and target format.
   - **Hand-drawn or animated SVG scenes:** when the brief needs original vector art or living
     line-art components, invoke `svg-illustration` (`#1-pin-the-look-and-scope` through
     `#6-hand-off`, including `#3-enforce-the-svg-file-contract`,
     `#4-add-seekable-motion-animated-components-only`, and
     `#5-run-static-lint-and-zoomed-inspection`) with `viewBox`, palette, `id` prefix, and
     deterministic clock contract.
   - Run disjoint 3D and SVG asset tasks in parallel up to `max-workers`, each with its own
     distinct folder and brief. Record every asset path, license, attribution, and lint receipt
     in the state file before Phase 3.

3. **Build, verify motion, and blind-critique the film (skipped for `repurpose`, `plan-only`).**
   - Invoke `motion-film` (`#1-resolve-the-brief-and-owner` through
     `#6-finish-the-requested-delivery`, including `#2-ground-the-story`,
     `#3-write-the-scene-contract`, `#4-build-seekable-motion`, and
     `#5-review-the-rendered-film`) passing the brief, frozen clock, cleared assets, and
     Phase 2 outputs.
   - Enforce reviewer separation: the agent that built the scenes or renders never runs the
     blind critique. Pass only rendered contact sheets, consecutive cut strips, motion-check
     outputs (`check_motion.py`), and encoded probe receipts (`probe_export.py`) to a fresh
     reviewer with the brief and script withheld. If no separate worker is available, record
     the critique as `same-agent` / unverified independent review.
   - Fix confirmed defects at their earliest owning stage (asset, scene, or timing), recapture,
     and keep the best render.

4. **Cut short vertical clips (optional; skipped for `assets-and-film`, `film-only`, `plan-only`).**
   - When the brief requests Shorts, Reels, or highlight cutdowns from a finished long cut,
     invoke `repurpose-long-video` (`#1-bind-the-source-and-rights` through
     `#9-record-and-hand-off`, including `#5-select`, `#6-check-context-and-claims`,
     `#7-reframe-to-the-target-aspect`, and `#8-caption-and-export`) with the approved master
     cut, rights record, and target aspect. Verify exported clips through `motion-film` export
     and caption checks before accepting them.

5. **Produce thumbnail or social cover (optional; skipped for `assets-and-film`, `film-only`, `plan-only`).**
   - When the brief requests a thumbnail or cover image, invoke `thumbnail-production`
     (`#1-research-and-brief`, `#2-select-photos-and-face-references`, `#3-produce-and-inspect`)
     with the approved title/promise, finished cut or script path, opening payoff, cleared
     asset IDs, and target platform sizes. Do not run this before the film's title and opening
     payoff are settled.

6. **Report and explicit social handoff.**
   - Lead with items needing the user: missing companions, failed or unrun checks, asset or
     voice approvals, and any playback/listening checks only a person can confirm.
   - Report the stage table (using the Run state statuses), artifact paths (brief, clock,
     assets, master video, cutdowns, covers, captions), asset licenses, and exact validator
     receipts (`lint_bpy.py`, `lint_svg.py`, `check_motion.py`, `probe_export.py`) labeled
     `passed`, `failed`, `blocked`, `unavailable`, `not run`, or `skipped`.
   - When social post copy is requested, do not invoke `distribution-draft` automatically;
     supply the handoff packet from [the handoff contract](references/handoff.md) and tell the
     user to invoke `/distribution-draft` (Claude Code) or `$distribution-draft` (Codex).

Finish when all requested in-scope stages pass their checks or every remaining blocker and
missing dimension is reported explicitly without claiming completion.
