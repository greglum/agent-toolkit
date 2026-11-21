# Production and handoff

Read this for a new film, a commissioned film, a recurring series, multiple delivery variants,
an enterprise handoff, the critique loop, or multi-film release coordination. Extend the
project's brief and manifest rather than keeping parallel records.

## Establish the production contract

Write a brief before any picture work in the project's existing record, or using the schema in
`references/production-record.md` when none exists (covering the one-sentence thesis,
audience and decision, cleared assets, visual keep/avoid rules, hard lines, and
deliverables).

Record each material claim's source and who owns unresolved decisions. Specify destinations,
aspect ratios, languages, audio, captions, and editable-source expectations. Clear rights
for music, footage, fonts, logos, voices, and likenesses: a repository's code license does
not clear demo assets, and a generator's code license does not clear weight variants (read
exact weight licenses and disclosure duties).

Assign visual roles (evidence, mechanism, analogy, decoration, orientation); keep confidential
data in permitted tools, and label synthetic substitutes so they never pose as evidence.
Choose each shot's method (truthful UI capture, coded graphics, character performance,
supplied footage, or authorized generated plate), recording why hybrid shots need generation
and which parts stay editable. Resolve blocking content or rights gaps before dependent
generation or delivery while continuing independent picture work.

## Check claims against the record

For a film about real work (shipped changes, incidents, reviews), verify every claim against
primary records (session logs, commits, CI logs, review threads) rather than summaries or PR
recaps. Record each fact's status (`confirmed`, `contradicted`, or `not found`) with its
settling locator in the production record. Fix or cut contradicted lines, cut or plainly
hedge not-found ones, and confirm each capture matches the words spoken over it.

Done when every spoken and on-screen claim has a status and a primary-record source.

## Pass the production gates

Pass gates in order for a new film (rerun touched gates for scoped updates). Fix defects at
the earliest owning gate rather than patching downstream. Stop for direction approval after
Gate 2 when requested; otherwise record and continue.

1. **References and assets:** each reference has one job and spec (`references/direction.md`),
   and required assets carry cleared rights.
2. **Style guide and shot list:** palette, type, camera, and shot list as events (entry state,
   action, exit state, reason), with move start, duration, destination, and landing stored in
   seconds first and frames derived from fps.
3. **Stills per shot:** one still per shot at delivery size (opening, product result, close),
   reviewed with `#run-the-critique-loop`.
4. **Animatic with placeholder audio:** low resolution at final fps and timing to prove
   sequence, holds, and pace before expensive renders or paid voice.
5. **Full pass:** final resolution and audio checked via `references/render-review.md` and
   the critique loop.
6. **Formats:** variants recomposed from the same timeline, plus poster, captions, transcript,
   and delivery package (after primary-cut approval if required).

For reusable campaigns, validate variant combinations, fonts, overflow, label collisions, and
resolved inputs in the render manifest before batch rendering. Raise owner-wait questions
immediately when ready, run source gates (lint, types) before expensive renders, and stop
only processes this run started by PID.

## Prove the difficult shot first

Build a style frame and short moving section (2 to 4 s, or enough to expose the risk) for the
hardest mechanism at delivery size and fps. Inspect picture and sound before scaling across
the film. Keep lower-res drafts at final timing and fps; when changing fps, preserve intended
seconds, recalculate frame indices, and recheck durations. Estimate final time/disk use from
a representative section, naming hardware, settings, and uncertainty.

Done when the difficult mechanism works in motion within delivery constraints.

## Run the critique loop

Use at Gates 3, 4, and 5, and on any new film or rebuild:

1. Give an independent reviewer (fresh session/subagent with no build context) only rendered
   frames: review sheets, consecutive-frame cut strips, and the phone-width sheet with
   captions. Withhold the brief, script, and storyboard.
2. The reviewer states the film's one-sentence point and describes key frames cold. Any
   mismatch with the brief's **Film** line or unidentifiable object becomes correction #1.
3. Return at most five corrections ordered by missing info/unreadable text, then timing, then
   detail, each with four fields: **location** (render ID, scene, time/frame), **problem**,
   **change**, and **what stays fixed** (attach marked spatial regions where needed; relocate
   notes if later edits shift targets).
4. Apply each correction as one named change keeping fixed parts, recapture under identical
   conditions, and keep the better render.
5. Repeat with a fresh reviewer until the point lands and no missing-info or readability
   corrections remain (or the round budget ends).

Subjective scores never pass a gate. If no independent reviewer can run, report critique as
unrun; builder self-review is not a substitute.

## Score against a frozen rubric

Use only when the owner sets a numeric quality target or scored rounds (never replaces the
critique loop or gates):

1. Freeze and date the rubric first: viewer, viewing condition, professional comparison class,
   5 to 10 render-observable dimensions with >= 4 anchored word levels, and separate pass/fail
   gates. A changed rubric starts a new baseline.
2. Use at least two fresh independent scorers per round with render evidence only (withhold
   builder notes and earlier scores).
3. Cite exact times and on-screen evidence per score; mark unobservable dimensions
   `UNAVAILABLE` (blocks target).
4. Record render ID, per-scorer scores, and spread; resolve spreads > 1 point in evidence,
   not by averaging.
5. Fix the lowest dimension first via located corrections.
6. Show side-by-side pairs in both orders. Re-score an unchanged render periodically to measure
   scorer noise; treat gains smaller than that noise as unestablished.
7. Stop when all dimensions meet target, two consecutive rounds gain less than the owner's
   step, or a cap requires an owner decision (report plateau with measured noise).

## Preserve reproducible revisions

Record source revision, local edits, input/asset digests, seed, generator revision/weight
variant, fonts, render settings, renderer/browser/encoder versions, and lockfile identity.
Do not downgrade missing required fonts, images, or media to warnings; when a generator has
no seed or determinism, treat the output file as source of truth.

For series/episodes, keep shared design/rigs/sound separate from episode story/claims/takes,
never mutate prior released episodes, and preview scenes standalone to catch hidden parent
dependencies. For resumable renders, bind cached frames to source/asset/seed/dimensions/fps/
settings, verify cache manifests rather than filenames alone, write atomically into task-owned
paths, bound worker/memory/disk usage, verify contiguous frame coverage, and check all worker
and encoder exit codes. State whether reproducibility was checked for narrative/layout, pixels,
or encoded bytes.

## Verify an editable studio handoff

Identify the actual edit target (source code, props, project file, or session draft) and
preserve user edits before applying external changes (one writer per scene). When approval
is required, show the draft against the saved revision it changes and re-approve if either
changes. Preserve or migrate saved selector/clip bindings during scene rewrites so overrides
still reach their targets.

Test one representative copy/style edit and one timing edit through the promised editor,
save, inspect the diff, reopen in a fresh session without pending drafts, and verify the
changed scene, neighbors, and export (using task-owned copies or restoring approved values).
For timeline interchange files, verify referenced media ranges and handles exist and confirm
the receiving renderer supports promised transitions/effects instead of silently dropping
them. Keep development-only tuning controls bound to canonical scene inputs.

## Delegate independent scene work

Keep story direction, shared design, narration, and global timing with one integrator. Freeze
shared coordinates, typography, safe areas, asset IDs, cue sheet, and source revision before
dispatching scene workers with owned files, explicit intervals, entry/exit states, and
required captures. Route shared-input changes back through the integrator and invalidate
affected captures. Integrate and inspect one adjacent scene boundary before scaling out, then
review the joined film against the common brief. Without workers, apply the same contracts
sequentially. Compare agent workflows on complete delivered films with identical usage basis,
not isolated scores or generation times.

## Coordinate several films toward one release

Keep one private release ledger, one coordinator, one owner per film, and one integrator for
shared renderer/caption/narration tooling. Record branch/revision, approved words, take ID,
asset status, rendered outputs, blockers, and release slot per film. Authority stays in the
session where the user gave it; relayed quotes do not authorize merges, paid takes, or commits.

When changing shared tooling, pin each shipped film's take settings and thumbnail time in its
manifest (or re-render and recheck) and recompute take cache keys to reuse paid takes. For
serialized repository gates, inspect the queue before promising times, bundle related changes
before queuing, and freeze the head once queued.

## Deliver a usable package

Use `references/production-record.md` when no project record exists. Include editable source,
run instructions, input/asset identities and rights, master and variants, promised audio
stems, captions, transcript, poster, and per-file checks, naming blockers and owners. Keep
prior successful renders until staged replacements pass. For locales, keep semantic scene
IDs, translate script/text, regenerate audio/timings (`references/narration.md`), reflow for
target fonts/shaping/reading order, and keep a review record per locale.
