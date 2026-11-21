# Craft, simulation, and review-tool sources

Original synthesis and local helpers. Pinned sources below establish upstream ideas, licenses,
and recheck triggers; they do not establish local render quality or behavioral skill lift.

## November 11, 2026 rubric review

The frozen-rubric section in `references/production.md` is original guidance from scored
production rounds. Two sources informed order and noise checks: Wei Lin,
["Reels-RSI"](https://arxiv.org/abs/2610.14495v1), arXiv 2610.14495v1, submitted October 10,
2026 (CC BY 4.0; judges picked the second-shown reel 62 to 81 percent of the time), and
Abhay Zala and others, HeyGen Research,
["Benchmarking Code-to-Video"](https://www.heygen.com/research/introducing-code2video-benchmark),
September 18, 2026 (no reuse license established; ~75 percent human-VLM agreement with
position and own-family bias). Observed November 11, 2026, rechecked November 12. No text,
code, or data copied. Recheck when scored rounds show disagreement above recorded noise.

## October 23, 2026 craft sweep

Defaults in `references/timing.md`, script checks in `references/narration.md`, reference desk
in `references/direction.md`, gates/critique in `references/production.md`, and motion notes in
`references/genres.md` and `references/remotion.md` are original guidance (source numbers are
paraphrased defaults, not locally measured). No upstream prose, code, presets, or media copied.

- [LottieFiles motion-design-skill](https://github.com/LottieFiles/motion-design-skill/tree/f9a8a041b85185ee4881b3471d3415e939aac772/skills/motion-design) (MIT): eases by direction, shorter exits, stagger budgets, one-third moving rule.
- [Barty-Bart motion-graphics](https://github.com/Barty-Bart/motion-graphics/tree/3d83d987d658601d8a1269eb691622bdcd427335/skills) (README MIT, API NOASSERTION): mix priority, duck depth, encoded loudness, sound placement by cue.
- [howseen-ai claude-motion-design](https://github.com/howseen-ai/claude-motion-design/blob/3d90d349ef3fdde9b7e89de4df4a2159c9e8697f/skill/motion-design/SKILL.md) (MIT): perceptual zoom, caption reading speed, blind frame restatement.
- [Remotion skills](https://github.com/remotion-dev/skills/tree/6c67adcd9cdbe6eb84d76342da89b225f9161cb2/skills/remotion-best-practices) (no license file): type floor, safe area scaled to width, narration-sized scenes.
- [HyperFrames public skill](https://github.com/heygen-com/hyperframes/tree/29643c7c8a3a4085f08f895d56c4b7cc072f2d69/skills/hyperframes) (Apache-2.0): eases by role, reading holds, still beat, narration pace, reveal on spoken word, caption grouping, sound cause, 360 px sheet, moving-cut vector rule, slow-fast-slow nudge, overlay captions.
- [Mort1d motion-graphics-skills](https://github.com/Mort1d/motion-graphics-skills/tree/7f0c3714dc81bea52644a5287c6350345009e579/skills/motion-graphics) (README MIT): one read at a time, hold floors, hierarchy ratio, encoded peak checks.
- [charlie947 motion-graphics-skills](https://github.com/charlie947/motion-graphics-skills/tree/229022ebca6972e119e36ada23a1648d51665ab) (MIT): hedged claim wording, fixing one named target at a time.
- [Liamrjohnston remotion-motion-graphics-skill](https://github.com/Liamrjohnston/remotion-motion-graphics-skill/tree/b860c7921f2220b9e2a84e815ba0ae7b10858f08/skills) (MIT) and [flyl1u fly-remotion](https://github.com/flyl1u/fly-remotion/blob/c5308fb028d78b7bf3b126d192c6153f66fceb91/skills/f-remotion/references/motion-library.md) (MIT): separate critic, one relationship per chart, density limits.
- X articles (no reuse license established): Francesco ([Oct 10, 2026](https://x.com/francescoinweb3/status/2108882188624121896)), seeco ([Oct 2, 2026](https://x.com/seeconvm/status/2106096193235259564)), beamnxw ([Oct 9, 2026](https://x.com/beamnxw/status/2108616740846420354)), rari ([Oct 1 and 27, 2026](https://x.com/0xwhrrari/status/2105643919119696297)), observed Oct 23-27, 2026: reference desk, six gates, shots as events, 2 fps + consecutive-frame strips, 4-field corrections.
- MIT motion packs checked Oct 23, 2026 (ideas only): [rossark-motion-skill](https://github.com/rossark0/rossark-motion-skill/tree/9b20964e32f07f8ac7e2948cd175746fa4a7712f), [saas-product-demo-video](https://github.com/noamdorr/saas-product-demo-video/tree/566294746adfdf5f2d8e86869f8c123c1648693e), [claude-remotion-skill](https://github.com/haidrrrry/claude-remotion-skill/tree/1dcbe5e3fc6cf970bd10d3cc05f0a8a5d19d0383), iart.ai ([kinetic-typography](https://github.com/iart-ai/kinetic-typography-skills/tree/fccc94bd325d824235ee9e815e65abde57b6513a), [data-animation](https://github.com/iart-ai/data-animation-skills/tree/8ce2709c3992490251e8a991535b1945f01c6865), [motion-design](https://github.com/iart-ai/motion-design-skills/tree/3c129f769d90a1328c209c386492333c9ac62312)), [remotion-marketing-video-skill](https://github.com/xsourabhsharma/remotion-marketing-video-skill/tree/a7f01a8ffdab4c02f54a8a1649f1f40d32efd529).
- Remotion 4.0.535 (observed Oct 23, 2026): closed-form `spring()` behavior and per-segment `interpolate` easing.
- Content-tool notes (Oct 23, 2026, ideas only): [FLUX.2 @ 50fe516](https://github.com/black-forest-labs/flux2/tree/50fe5162777813d869182b139e83b10743caef15) (Apache-2.0 code), [Kokoro @ dfb907a](https://github.com/hexgrad/kokoro/tree/dfb907a02bba8152ca444717ca5d78747ccb4bec) (Apache-2.0), [ACE-Step 1.5 @ ca1e85f](https://github.com/ace-step/ACE-Step-1.5/tree/ca1e85fe9430179831e6bc6be790c332190a3866) (MIT), [Podcastfy @ 053b54a](https://github.com/souzatharsis/podcastfy/tree/053b54a0917e35edb2808049499292361ccaae7b) (Apache-2.0), [short-video-factory @ 5ade9ec](https://github.com/YILS-LIN/short-video-factory/tree/5ade9ecfe0feab4c022710140efb3703004691f4) (AGPL-3.0).
- Recheck when pinned sources change timing, caption, or audio defaults, or owner tokens disagree.

## Painted-material sources (October 25, 2026)

Original texture-space and exposure-cadence guidance in `references/genres.md` prompted by
Tobia Donadon's [Shorts Animator post](https://x.com/tobiadonadon_/status/2114445880522604545)
and [product page](https://www.tobiadonadon.com/projects/construct/material/skills/shorts-animator)
(license unavailable). Corroborated by Toon Boom
[Harmony 25 Pencil Line Texture](https://docs.toonboom.com/help/harmony-25/premium/reference/node/filter/animate-pencil-line-texture-node.html)
(updated March 26, 2026), Disney Animation's
[Texture Mapping for Cel Animation](https://media.disneyanimation.com/uploads/production/publication_asset/45/asset/2DTextureMapping_1998.pdf),
and Remotion's [Flickering](https://www.remotion.dev/docs/flickering) (observed Oct 25, 2026;
redistribution rights not established). Recheck when style, sampling, or output profile changes.

## Simulation and synthesized-audio sources (October 25, 2026)

Guidance in `references/simulations.md` and `references/narration.md` informed by Matter.js
[Runner](https://github.com/liabru/matter-js/blob/b8ee71cd7f9b49f53639ddaedd6254f1929bcbe5/src/core/Runner.js)
and [Engine](https://github.com/liabru/matter-js/blob/b8ee71cd7f9b49f53639ddaedd6254f1929bcbe5/src/core/Engine.js)
(MIT, Sept 30, 2026), Tone.js
[offline renderer](https://github.com/Tonejs/Tone.js/blob/445b94d4c0ade2d5c2f60c60f3e48749eb3322d9/Tone/core/context/Offline.ts)
(MIT, Oct 25, 2026), Remotion [frame-order guidance](https://www.remotion.dev/docs/flickering),
Dimforge [JavaScript determinism](https://rapier.rs/docs/user_guides/javascript/determinism/),
and MDN [OfflineAudioContext.startRendering](https://developer.mozilla.org/en-US/docs/Web/API/OfflineAudioContext/startRendering)
(living pages observed Oct 25, 2026). Recheck on engine, replay, or audio-export changes.

## Review sheets, paired frames, and frame comparison (October 26, 2026)

All three comparison helpers in `references/review-helpers.md` are original Python/FFmpeg code
with no upstream prose or code copied:

- **Contact sheet (`contact_sheet.py`):** motivated by [echris6/motion-video-kit](https://github.com/echris6/motion-video-kit/tree/e4b1c0004080fe6a0deb883631bad5eba1e5f339) (MIT, Oct 14, 2026), Akshat Darshi's [Sept 30 account](https://milliondreams.vercel.app/blog/launch-film-in-code), and FFmpeg 8.1.1 [select/tile docs](https://ffmpeg.org/ffmpeg-all.html#select_002c-aselect).
- **Pixel comparator (`compare_frames.py`):** observed Oct 26, 2026; motivated by Mapbox [pixelmatch](https://github.com/mapbox/pixelmatch/tree/ab76f526ef951c0ec6284e314a700e161b1800e6) (ISC) channel-delta vs pixel-budget split, plus FFmpeg [image formats](https://ffmpeg.org/general.html#Image-Formats) and [image2pipe](https://ffmpeg.org/ffmpeg-formats.html#image2_002c-image2pipe).
- **Paired event frames (`pair_event_frames.py`):** prompted by Francesco's [review-loop post](https://x.com/francescoinweb3/status/2114600805579763971), Raphaël Aubry's MIT [comparison renderer](https://github.com/howseen-ai/claude-motion-design/blob/3d90d349ef3fdde9b7e89de4df4a2159c9e8697f/skill/motion-design/scripts/remake/remake_render.py) and [QA sheets](https://github.com/howseen-ai/claude-motion-design/blob/3d90d349ef3fdde9b7e89de4df4a2159c9e8697f/skill/motion-design/scripts/remake/remake_qa.py), Mort1d's MIT [reference analyzer](https://github.com/Mort1d/motion-graphics-skills/blob/7f0c3714dc81bea52644a5287c6350345009e579/skills/motion-graphics/scripts/ref-sheet.mjs), and FFmpeg 8.1.1 [filter manual](https://ffmpeg.org/ffmpeg-filters.html).
- Recheck when FFmpeg filters, pixel formats, comparison semantics, or review contracts change.
