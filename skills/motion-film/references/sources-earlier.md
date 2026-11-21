# Earlier reviews and speech-editing sources

Original guidance; no upstream prose, renderer code, or media is bundled. Read when reviewing
earlier provenance or adapting an upstream change.

## September 29 to October 7, 2026 reviews

Reviewed September 29, 2026, with Remotion/alpha refresh October 5, application-film refresh
October 6, and explainer refresh October 7:

- Original application-film rules (Oct 6, 2026): scene claims, explicit readiness, seek
  checks, narration identity, frozen reads, unsaved previews, muted comprehension, manifest-owned
  regeneration.
- [Remotion markup](https://github.com/remotion-dev/skills/blob/473352613039e718e48c4aa/skills/remotion-markup/SKILL.md),
  [connected compositions](https://github.com/remotion-dev/skills/blob/473352613039e718e48c4aa/skills/remotion-markup/connected-compositions.md),
  and [official skills docs](https://www.remotion.dev/docs/ai/skills) (no license file found):
  frame-driven animation, composition fps, independently previewable scenes.
- [iart lower-thirds](https://github.com/iart-ai/lower-thirds-skills/blob/aa8ef7ed9fa59d0a79fc57701e493cfd8197b5d8/skills/lower-thirds/SKILL.md),
  [renderer](https://github.com/iart-ai/lower-thirds-skills/blob/aa8ef7ed9fa59d0a79fc57701e493cfd8197b5d8/skills/lower-thirds/scripts/render.mjs),
  and [delivery reference](https://github.com/iart-ai/lower-thirds-skills/blob/aa8ef7ed9fa59d0a79fc57701e493cfd8197b5d8/skills/lower-thirds/references/delivery.md)
  (MIT): decoded-alpha checks, composited review, target playback evidence.
- [HyperFrames determinism](https://github.com/heygen-com/hyperframes/blob/ae914334f279ee53b3aebd0437ef7a9c4d20f8b0/skills/hyperframes-core/references/determinism-rules.md)
  and [seam craft](https://github.com/heygen-com/hyperframes/blob/ae914334f279ee53b3aebd0437ef7a9c4d20f8b0/.agents/skills/seam-craft/SKILL.md)
  (Apache-2.0): explicit timeline readiness, measured bounds, overlap checks.
- [Charlie Hills motion brief writer](https://github.com/charlie947/motion-graphics-skills/blob/092a38dc8f3b84dc4887048a0f62bdb2e4abde25/skills/motion-brief-writer/SKILL.md)
  and [reel export](https://github.com/charlie947/motion-graphics-skills/blob/092a38dc8f3b84dc4887048a0f62bdb2e4abde25/skills/reel-export/SKILL.md)
  (MIT): brand ownership, claim status, encoded inspection.
- [Hanif claude-animation](https://github.com/buildwithhanif/claude-animation-skill/blob/4ddb8c80fdec96dc9f55d4b9bdee60bde6f0134b/plugins/claude-animation/skills/claude-animation/SKILL.md)
  and [film harness](https://github.com/buildwithhanif/claude-animation-skill/blob/4ddb8c80fdec96dc9f55d4b9bdee60bde6f0134b/plugins/claude-animation/skills/claude-animation/lib/film.mjs)
  (MIT): stable seeds, out-of-order pixel comparison, consecutive-frame strips, staged replacement.
- [Movez motion-studio article](https://x.com/0xMovez/article/2104216919033192746) (Sept 29, 2026;
  no reuse license): explicit states, reference analysis, captured-frame critique.
- [HyperFrames faceless-explainer](https://github.com/heygen-com/hyperframes/blob/891a18af76bc24f8b8b5895a43b51df58dde8713/skills/faceless-explainer/references/story-design.md)
  and [motion language](https://github.com/heygen-com/hyperframes/blob/891a18af76bc24f8b8b5895a43b51df58dde8713/skills/faceless-explainer/references/motion-language.md)
  (Apache-2.0), [anything2explainer](https://github.com/Vincentwei1021/anything2explainer/tree/735c79c8724e897e8971cd59dde7e5aa11e4d6ce)
  (PolyForm Noncommercial 1.0.0, concept only), `@0xCarnagee` explainer note (Oct 7, 2026),
  and Meaghan Choi talks ([Dive Club](https://dive-club.beehiiv.com/p/new-post-8b4a),
  [Behind the Craft](https://creatoreconomy.so/p/full-tutorial-from-design-to-code-with-claude-code-meaghan-choi),
  [Product School](https://productschool.com/resources/product-podcast/meaghan-choi-anthropic-claude-code-fastest-growing-dev-tool)).
- Access and learning standards: Mayer multimedia principles ([summary](https://ugc.futurelearn.com/uploads/files/7d/d6/7dd6188d-c343-4311-b064-ac98d2c95abc/Multimedia_Principles._R._E._Mayer__2020.pdf)),
  Grant Sanderson ([talk notes](https://math.mit.edu/amc/2020ay/sanderson.pdf)), WCAG 2.3.1, EBU R128.
- October 8 sweep (MIT, ideas only): [demo-video-creator](https://github.com/chacha95/demo-video-creator) `7947a8b`,
  [showreel](https://github.com/revfactory/showreel) `bf62d0b`, [kit-video-ia](https://github.com/paulocastellano/kit-video-ia) `dfe1650`.
- October 26 interchange refinement: ASWF OpenTimelineIO
  [timeline structure](https://github.com/AcademySoftwareFoundation/OpenTimelineIO/blob/94e1ad6c9b3c550b7ef06d999166c99b4be3025a/docs/tutorials/otio-timeline-structure.md)
  (Apache-2.0; source ranges and handles vs available media). Pixel comparison provenance lives in
  `references/sources-craft.md`.

Recheck when renderer/version, delivery contract, interchange format, or capture defects change.

## Speech editing and frame-feedback sources (October 25 to November 6, 2026)

Original procedural refinements in `references/genres.md` and `references/production.md`, with
no editor or ASR bundled:

- **October 25, 2026:** Peter Yang interview with Jake Moran ([video](https://www.youtube.com/watch?v=MC1g2fHYC88),
  [editing guide](https://video-editing-101.vercel.app/)), Adobe
  [transcript editing](https://helpx.adobe.com/premiere/desktop/edit-projects/edit-video-using-text-based-editing/detect-and-delete-pauses-in-transcripts.html)
  (Jan 7, 2026), and [frame comments](https://helpx.adobe.com/premiere/desktop/collaborate-with-others/share-for-review-using-frame-io/add-comments-on-shared-projects.html)
  (Nov 19, 2025): settle main speech cut before intro polish, bind feedback to render and region.

### October 27 video-editor review

- Tobia Donadon's [Video Editor article](https://x.com/tobiadonadon_/status/2115190452202660333),
  [CrisperWhisper paper](https://www.isca-archive.org/interspeech_2024/zusag24_interspeech.pdf) (Interspeech 2024),
  Adobe [frame comparison](https://helpx.adobe.com/uk/premiere/desktop/edit-projects/compare-edits-to-source-clips/compare-edits-to-clips-in-the-program-monitor.html)
  (Jan 21, 2026), and [color matching](https://helpx.adobe.com/premiere/desktop/correct-color/add-color-effects/match-color-between-shots.html)
  (Aug 18, 2026): verbatim vs cleaned speech transcripts, matching source-frame comparisons.

### November 6 video-editing toolkit review

- [FFmpeg Skill silence.py](https://github.com/kajisho5/ffmpeg-skill/blob/9bdb444fdd569bcf50276337b36164fadf54b363/scripts/silence.py) (MIT),
  [Herk Edit Kit cut-silences.mjs](https://github.com/nateherkai/herk-edit-kit/blob/10511e5af86fc47756ea89803b397422e2d89284/.agents/skills/cut-silences/scripts/cut-silences.mjs) (MIT, Oct 14, 2026),
  [FFmpeg silencedetect](https://ffmpeg.org/ffmpeg-filters.html#silencedetect), and
  [OpenChatCut](https://github.com/0xsline/OpenChatCut/blob/9242a95aea248ff3a8dab495514384e858320d47/README.md#L314-L319) (AGPL-3.0):
  check silence removals against surrounding audio, bind draft approvals to saved base revision.

Recheck when ASR mode, detector, editor save contract, or timeline changes.
