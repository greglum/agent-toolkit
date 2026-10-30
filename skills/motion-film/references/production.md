# Production and handoff

Read this for a new film, a commissioned film, a recurring series, multiple delivery variants,
an enterprise handoff, or the critique loop. Extend the project's brief and manifest instead of keeping parallel records.
For a small change, update only the affected decisions and dependencies.

## Establish the production contract

Write a production brief in the project's existing brief, or in the
[production record](production-record.md) when none exists. Fill these fields before any
picture work:

- **Film:** the one sentence the viewer keeps (the record's `thesis`), plus duration and
  formats.
- **Audience:** who watches, where, with or without sound, and what they should understand
  or decide afterwards.
- **Assets:** the real UI, captures, data, brand, voice and music the film may use, each with
  its source and rights.
- **Visual:** what to keep from each reference, and the looks to avoid, named concretely
  enough that a reviewer can spot them in a frame.
- **Hard lines:** what the film never does, such as inventing a product screen, metric,
  quote or customer.
- **Deliver:** the storyboard, review sheets, master and variants, poster, captions,
  transcript and editable source the work must produce.

Record the source of each material claim and who owns unresolved content decisions. A longer
brief helps only when its added lines are decisions; restated taste adds nothing.
Define destinations, aspect ratios, languages,
duration, motion treatment, audio, captions, and editable-source expectations. Identify the
required rights for music, footage, fonts, logos, voices and likenesses, including commercial
use and attribution. A repository's code license does not clear the assets shown in its demo. A generator's code
license does not clear its weights or outputs: read the license of the exact weight variant,
since one model family can mix permissive and non-commercial weights, and record its output
terms and disclosure duties.

Make a short treatment with distinct visual roles: evidence, mechanism, analogy, decoration,
and orientation. A generated illustration can explain an analogy; it cannot establish that a
product screen, customer, factory, or measured result exists. Keep confidential references and
customer data within their permitted tools and storage. Use synthetic or cleared substitutes
where required, labeled so they cannot become evidence by accident.

For each shot, choose the method that fits its job: a truthful UI capture, deterministic
graphics, a character performance, supplied footage, or an authorized generated plate. Record
why a hybrid shot needs generation and which parts remain editable. A model name in a gallery
is not a requirement, a capability guarantee, or authority to use another provider.

Finish this phase with the required deliverables, content gaps, source/asset ledger, chosen
approach, and render budget recorded. Resolve blocking content or rights gaps before their
dependent generation or delivery, while continuing independent picture work.

## Check claims against the record

For a film about real work, such as a shipped change, an incident or a review, check every
claim against the primary record: session logs, commits, CI logs, and the review threads
themselves. A pull request body, brief or recap is a summary and can be wrong on counts, who
found what, who approved what, and the order of events. Give each fact a status in the
[production record](production-record.md) claims list with the locator that settles it:
confirmed, contradicted, or not found. Correct or cut a contradicted line, and cut or
plainly hedge a not-found one. Then check each capture against the words spoken over it: a
frame that shows something the line denies is a contradicted claim.

Done when every spoken and on-screen claim has a status and a primary-record source.

## Pass the production gates

Each gate ends on an artifact that can be inspected. Pass them in order for a new film. A
scoped update reruns only the gates its change touches. When a gate finds a defect, fix it
at the earliest gate that owns it: a timing problem found in the full pass goes back to the
animatic or the shot list, not into a render patch. When the user asked to approve the
direction, stop for that approval after gate 2; otherwise record each result and continue.

1. **References and assets.** Each reference has one job and a spec
   ([study a reference](direction.md#study-a-reference)). Required assets are collected with
   their rights.
2. **Style guide and shot list.** The style guide records palette, type, shot lengths,
   transitions and camera. The shot list writes each shot as an event: its entry state, the
   action (for a demo: the cursor reaches the target, presses, and the result appears), its
   exit state, and the reason the shot exists. Cut a shot whose reason cannot be stated.
   Store each move's start, duration, destination and landing together, in seconds first,
   with frames derived from the composition's fps.
3. **Stills per shot.** One still per shot at delivery size, at least for the opening, the
   product result and the close. Run the [critique loop](#run-the-critique-loop) on them.
4. **Animatic with placeholder audio.** Low resolution, the final fps and timing, and a
   placeholder or draft voice. It proves sequence, readable holds and pace before any
   expensive render or paid voice.
5. **Full pass.** Final resolution and audio, reviewed with
   [capture and export review](render-review.md) and the critique loop.
6. **Formats.** Each variant recomposed from the same timeline, plus poster, captions,
   transcript and the delivery package below. When the brief asks for approval of the primary
   cut, start them only after it; variants of a rejected cut are wasted renders.

When a brief makes a gate wait for the user, ask its exact question with the frames the moment
they are ready. A wait no one raised holds the work as surely as a failure. Run the source gates
(lint, types) before an expensive render, and stop only the processes your own run started, by
PID, never by a pattern another session's renders also match.

## Prove the difficult shot first

Build a style frame and a short moving section that exercises the most uncertain mechanism:
dense type, character contact, a heavy effect, a mixed-media transition, or synchronized lyrics.
Test it at the intended delivery size and frame rate. A two to four second section is often
enough; choose the duration needed to expose the risk. Inspect the actual visual and sound
result before multiplying the technique across the film.

Use a storyboard or animatic to establish sequence and readable holds before polishing every
shot. Render drafts at lower resolution or quality while preserving timing and frame rate.
Changing fps is a separate timeline change: preserve intended seconds, recalculate frame
indices, and verify video, audio and container durations before accepting it. Estimate final
time and disk use from a representative section, naming the hardware, settings and uncertainty.

Done when the difficult mechanism works in motion, the sequence teaches the intended idea,
and the final profile fits the agreed constraints. A still or an enthusiastic critic score
cannot replace that proof.

## Run the critique loop

Use it at the stills, animatic and full-pass gates, and on any new film or rebuild.
The [frame-feedback sources](sources-editing.md) record the render/region refinement.

1. Give an independent reviewer, a fresh session or subagent with no build context, only the
   rendered frames as a viewer would see them: review sheets, consecutive-frame strips around
   cuts, and the phone-width sheet, with captions as delivered. Withhold the brief, script and
   storyboard.
2. The reviewer first states the film's point in one sentence from the frames alone, and
   describes each key frame as a stranger would. Compare that sentence with the brief's
   **Film** line. A mismatch, or a frame object the reviewer cannot identify, becomes the
   first correction.
3. The reviewer returns at most five corrections, each with four fields: **location** (render
   identity, scene and output time or frame), **problem** as observed, **change** to make, and **what stays fixed**.
   For a spatial correction, attach the reviewed frame with the target marked, or identify
   its region unambiguously. Collect notes against that render before editing. If a later
   edit moves the target, relocate the note against the new render before applying it.
   Order them: missing information and unreadable text first, then timing, then detail.
4. Apply each correction as one named change that keeps its fixed parts. Recapture under the
   same conditions and keep the better render.
5. Repeat with a fresh reviewer until the point is restated correctly and no correction
   concerns missing information or unreadable text, or until the user's round budget ends.

The reviewer gives no score, and no score passes a gate: subjective ratings are not
evidence. Corrections are findings; acceptance still comes from the render review checks.
When no independent reviewer can run, report the critique as unrun. Builder self-review does
not stand in for it.

## Preserve reproducible revisions

Record source revision, local edits, input and asset digests, seed, the generator revision
and weight variant of generated assets, fonts, render settings,
renderer/browser/encoder versions, and dependency lockfile identity. Required assets must load
successfully; separate optional decoration from required story, font, data and audio inputs.
Package local licensed assets where practical so a network change cannot silently replace them.
When a generator exposes no seed or is not deterministic, the generated file is the source of
truth.
Do not downgrade required font, image or media failures to warnings.

Reuse the project's episode structure. Separate shared design, rigs, renderer and sound from
episode-specific story, claims, data, takes and cues. A new episode must not overwrite a prior
deliverable or mutate its source of truth. Snapshot the approved shared inputs for released
episodes. Preview one scene independently to expose initialization inherited only from its parent.

When chapter work is delegated, follow [scene delegation](#delegate-independent-scene-work).

For resumable renders, bind cached frames to source and asset identity, seed, dimensions,
fps, frame range and relevant runtime settings. An existing filename or nonempty JPEG proves
neither freshness nor completion. Verify the cache manifest before reuse; write completed
frames and exports atomically into task-owned locations. Bound worker count, queued frames,
memory and disk use. Verify contiguous frame coverage for the requested interval before
assembly. Keep encoding in frame order and check every worker and encoder result. Required
scene errors or diagnostic fallback frames block delivery even if encoding succeeds.
Do not adopt a third-party renderer's browser-sandbox flags or installation commands blindly.

Distinguish repeatable narrative/layout from identical pixels and identical encoded bytes.
Platform fonts, graphics drivers and synthesis dependencies can affect the latter. State which
property was actually checked rather than claiming universal reproducibility.

## Verify an editable studio handoff

When a visual editor or editable handoff is requested, identify its actual edit target:
source code, composition props, a project file, or only a session draft. Preserve the current
source and user edits before applying another editor or agent's changes. Reconcile a stale
preview against current source; keep one writer for the same scene at a time.

Exercise a representative copy or style edit and a timing edit through the promised editor.
Save through its supported path, inspect the source or project diff, then reopen in a fresh
session without pending drafts. Verify the changed scene, its neighbors and the requested
export from those saved inputs. Keep sample edits in a task-owned copy, or restore the
approved values before rendering the deliverable. An editable preview that loses changes on
reload does not satisfy an editable handoff; a successful export does not prove editability.

For a timeline interchange file, resolve required media and verify the selected source ranges
and transition handles against the actual files. A valid timeline can reference unavailable
frames. Check that the receiving renderer supports the promised transitions and effects;
successful parsing alone does not prove they survive the handoff. Report unsupported parts
instead of silently dropping them.

Use an existing tuning surface for repeated timing or easing adjustments when available.
Build a small development-only control only when repeated iteration warrants it. Keep its
values tied to the canonical scene inputs, so export cannot diverge from preview. Do not
introduce a general studio framework for one shot.

Done when the promised edits persist after reopening and the requested output reflects the
saved source. Report unavailable editor or export access separately from source review.

## Delegate independent scene work

Use authorized workers where a task has independent references, assets, bounded scenes or
rendered review. Keep story direction, shared design, narration and global timing with one
integrator. Serial stages that continually need each other's context stay together.

Before dispatch, freeze the shared coordinates, typography, safe areas, asset identities,
cue sheet and source revision. Give each scene worker its original brief, owned files,
explicit interval, entry and outgoing states, read-only shared inputs, and required captures.
Workers return changed paths, actual evidence and unresolved assumptions. A shared-input
change returns to the integrator; invalidate dependent captures instead of silently retiming
another scene. Research workers return primary-source locators; the critic receives rendered
evidence through the existing [critique loop](#run-the-critique-loop).

Integrate one adjacent scene pair and inspect its moving boundary before scaling out. After
integration, review the joined film against the common brief. Good isolated scenes do not
establish continuity, a consistent visual language or synchronized sound. Finish when every
scene belongs to the same revision and the joined-film checks pass. Without workers, use the
same contracts sequentially; independent critique remains unrun unless it actually happens.

When comparing agent workflows, retain the actual harness/model, source and input identities,
task, outputs, failures, repair effort and usage basis. Compare the complete delivered film;
a model label, isolated scene score or shorter generation time does not establish improvement.

## Coordinate several films toward one release

Keep one private release ledger, one coordinator, one owner per film, and one integrator for the
shared renderer, captions, closing card and narration tooling. Record each film's branch and
revision, approved words, take identity, asset status, rendered outputs, blockers and release slot.
Make each decision once per owner; a reversal costs that writer's work and blurs who may write where.

Authority stays in the session where the user gave it. A quote relayed by another session does not
authorize a merge, a paid take or an asset commit in a session whose rules require the user's own
word there. Either the session that holds the authority does the step, or the user answers in the
acting session. Ask once, early, with the exact action and cap.

A shared-engine change can alter already delivered films on their next render: caption breaks, the
default thumbnail frame, or the default narration model. In the same change, pin each shipped
film's take model and settings and its thumbnail time in its own manifest, or re-render and recheck
it. Recompute the take cache key to confirm a pinned re-cut reuses the paid take.

When a repository gate is serialized across sessions, read the queue before promising a time: who
holds the lock, who waits, and whether their revisions carry the current gate scripts. Fold related
film changes into one gated change before its run starts. Once the run is queued, freeze that head
and put later corrections in a follow-up, since each new head voids the queued run.

## Deliver a usable package

Use the compact [production record](production-record.md) when no project record exists.
Include the editable source and run instructions, source/input identities, cleared assets and
credits, requested master and variants, audio stems when promised, captions and transcript,
poster when needed, and checks tied to each final file. Name remaining blockers and their owner.
Keep the prior successful render until its staged replacement passes the required checks.

For localized versions, keep semantic scene IDs and translate the actual script and text.
Regenerate changed speech and timing as described in [narration](narration.md). Reflow using
the final language's font, shaping and reading order; inspect long labels, subtitle density,
names, numbers and the actual aspect ratio. Give each delivered locale its own review record.

The package is complete when another permitted operator can identify the inputs and reproduce
the workflow, and every promised output has its own evidence or explicit unresolved status.
Publication and customer delivery use the authority for that named target.
