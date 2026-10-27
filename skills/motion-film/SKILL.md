---
name: motion-film
description: "Create, edit, audit, or render films: product demos, explainers, data graphics, motion graphics, music-led typography, and character animation. Reuse the project's renderer and verify the requested output. For application interaction motion, use ui-motion instead."
compatibility: Needs the project's existing renderer and capture surface, plus a way to inspect encoded output, such as ffprobe. Without them, do a source-only review and report rendered, encoded, and playback acceptance as unverified.
---

# Motion film

Deliver the film requested in the project's own visual language. An audit ends with evidence
and proposed fixes; a build or scoped update continues through its required checks. Rendering
and publication are different actions. Reuse the requested output contract and existing
authority; a source preview does not satisfy an explicit request for a video file.
In audit mode, inspect the scene and build steps below and propose changes; change no film
source, assets, narration, or deliverables. Use task-owned review captures where needed and
leave existing exports intact.
For a render-only request, use the procedure as checks and export the existing film without
rewriting its story, scenes, or audio. Report a source defect before making a repair outside
that scope.

For thumbnails or social covers, use `thumbnail-production`. When a film also needs
packaging, pass its approved title, script or cut, opening payoff, cleared assets and output
formats to that skill. Thumbnail production owns the images; this skill owns the video.

## Procedure

1. **Resolve the brief and owner.** Read applicable instructions, design/tokens, existing film
   sources, assets, renderer, and capture/export commands. Record audience, intended outcome,
   embedded or standalone delivery, format, dimensions, fps, duration budget, and audio scope.
   Reuse known decisions and prior approved briefs. For an existing film, preserve its player,
   opening/replay policy, content revision, and engine seams. Choose the existing renderer
   before introducing one. For generated video, including a replacement take, read
   [generated plates](references/generated-plates.md). For application films, read [application film setup](references/app-films.md)
   for a new film, a source refresh, or scenes using environment data. For a film that teaches
   a concept or mechanism, read [explainer films](references/explainers.md). Finish with the
   deliverable and its validation path identified. For a new or commissioned film, recurring
   series, multiple locales/formats, or editable handoff, read [production](references/production.md)
   for the brief and gates. When several films share one release, shared tooling or a serialized
   repository gate, also read [coordinating several films](references/production.md#coordinate-several-films-toward-one-release).
   For a visual-editor workflow or editable handoff, also verify the
   [saved-source round trip](references/production.md#verify-an-editable-studio-handoff).
2. **Ground the story.** For a product film, trace each shown journey to current routes,
   labels, behavior, and source revision. For a data graphic, retain supplied values, units,
   dates, and the distinction between results, targets, and examples. For queried data, record
   the metric definition, filters, time window, query or source locator, and extraction time;
   a visible query alone does not verify the value. For a disputed value, use `reconcile-metric`
   to calculate independently before treating it as fact. Render charts and labels from one
   checked data snapshot. A data correction requires a new checked export; an MP4 does not
   refresh with its dashboard. When animating data, held
   frames show sourced values, easing never overshoots a real value, and interpolation implies
   no rank change the data lacks. Label fictional examples on screen. Use permitted assets and
   record their origin. Cut unsupported claims or surface the material uncertainty. State
   only what the source states: a time saving is not a speed multiplier, similarity is "looks
   like", and one shown cause is "one reason". Do not perform a real application mutation to
   make a painted demonstration convincing. For a film about real work, check claims against
   the primary record, not a summary ([claims against the record](references/production.md#check-claims-against-the-record)).
   Completion means every scene claim and asset has a source, and each claim about real work
   has a recorded status.
3. **Write the scene contract.** Record each scene's purpose, visible action, payoff, text or
   spoken cue, readable hold, and handoff. For a new creative film, a supplied reference, or a
   choreography change, read [direction and choreography](references/direction.md).
   For style references, music-led typography, character performance, or footage editing,
   read the relevant branch of [genre direction](references/genres.md).
   Keep exact speech in captions and the transcript; use complementary takeaways when the
   design calls for them. Use the owner's terminology and brand, with one name per thing. Keep
   one focal point at a time; keep persistent objects across scenes rather than replacing them.
   Derive pace from what the audience must read and understand rather than a fixed scene count
   or fast-cut recipe; set holds, eases, and stagger from [timing defaults](references/timing.md).
   Use the shared storyboard or manifest already present. A changed narrated line requires
   coordinated audio, cues, captions, and timing; read [narration](references/narration.md)
   when audio is in scope, and pass its [script checks](references/narration.md#write-the-script)
   before generating a take. For each changed scene, record the expected behavior, its visible
   failure signal, and the times to inspect.
4. **Build seekable motion.** For tactile materials, deforming objects, cutaways, or 3D
   close-ups, read [material and mechanism shots](references/material-3d.md) before building
   the shot. Use the renderer's explicit frame or timeline time, with known
   units, fps, scene offsets, and interval boundaries. Declare each cut once and derive every
   visibility window from it. The same source, inputs, and requested time must produce the same
   visible state regardless of previous seeks. Derive visual state from time; seed
   random-looking choices and fix input data. For physics, particles, accumulated trails or
   other stateful effects, read [seekable simulations](references/simulations.md).
   For an embedded animation player or external timeline, read
   [imported animations](references/imported-animations.md) for time mapping and seek callbacks.
   Keep wall clocks, event history, and incomplete
   asset loads out of frame state. Await fonts, media, and timeline readiness before measuring
   or capturing. Measure geometry before transforms distort it. For an existing Remotion
   project, read [Remotion guidance](references/remotion.md). For cached frames or a resumed
   render, read [revision and cache checks](references/production.md#preserve-reproducible-revisions).
5. **Review the rendered film.** Follow
   [capture and export review](references/render-review.md). Inspect every changed scene's opening, action, payoff,
   and both sides of its handoffs. Compare out-of-order seeks under the same conditions and
   watch ordinary playback. Preserve readable captions, unclipped subjects, and a deliberate
   background during overlap. For a new film or rebuild, also run the independent
   [critique loop](references/production.md#run-the-critique-loop) on the rendered frames.
   In build/update mode, fix observed defects, then recapture the affected times and
   conditions. Keep the best render, not the latest: revert a fix that makes the render worse
   rather than patching on top. In audit mode, report their locations, evidence, and proposed
   fixes.
6. **Finish the requested delivery.** Run the required source and renderer checks. If an
   export was requested, produce it and inspect the encoded result. Stage replacement renders
   so a failed encode cannot overwrite a known good artifact. Preserve editable source
   when a dependency or access blocker prevents export; do not relabel another format as the
   requested one. Report source/preview, rendered captures, playback, listening, and encoded
   output separately. List actual artifact paths, format, dimensions, duration, fps, and
   remaining limitations. Include material choices and confidence, least confident first.
   An audit finishes with findings, inspected scene/time scope, and unverified conditions;
   existing defects can remain as findings. Report source-only review as rendered acceptance
   unverified. A build/update finishes when the requested deliverable and required checks pass,
   or its remaining blocker and missing evidence are explicit without a success claim.

## Playback and export are different contracts

- Embedded players follow the application's focus, keyboard, dismissal, reduced-motion,
  transcript/caption, audio-start, and hidden-tab policies. Preserve semantic meaning when
  reduced motion cuts to a settled state. Verify the actual player with DOM measurements,
  focus/contrast review, and the repository's UI test setup (axe-core).
- Exported videos have no runtime media preference. Render the agreed motion treatment;
  provide a reduced-motion version when requested or required by the delivery contract.
  It keeps the same sequence of ideas. A browser preference must not silently change the
  intended export.
- In either delivery mode, nothing flashes more than three times in any one second unless
  it stays below the WCAG general and red flash thresholds.
- Use the existing development capture surface. A new review-only seek API belongs in the
  development renderer or harness, not in the public production application.
- A still establishes appearance at one time. It does not prove scene continuity, readable
  pacing, audible quality, live data behavior, deployment, or a completed media export.

## Provenance

Sources and adaptation notes: [sources](references/sources.md).
