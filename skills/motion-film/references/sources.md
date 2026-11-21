# Sources and adaptation

## November 11 live browser films and scored rounds

`references/live-browser.md` records its own sources and limits in place.
`references/sources-craft.md` covers the frozen rubric and craft sweeps.

## November 7 reference format adaptation

The story structure mapping in `references/direction.md` is original guidance informed by
Scenario Inc.'s [Content Engine](https://www.scenario.com/explorations/content-engine/),
observed November 7, 2026, and its downloadable scenario-remake ZIP, SHA-256
`1bd3eb59a361e67edde6be79b72d97ca196b27443e3df6d1c26bbde0e366d9f`.
The ZIP separates the function of a beat from the example's subject. Higgsfield's
[Content Factory guide](https://higgsfield.ai/blog/higgsfield-introduces-content-factory)
uses references for pacing and format.
[TransNet V2, §1](https://arxiv.org/html/2008.04838#S1) documents missed cuts and false
positives; a detected cut differs from a story beat. The ZIP has no license notice; living-page
reuse rights were not established. No upstream text, code, or media was copied. Recheck when
the input scope, bundle, or rights change.

## November 4 reference reconstruction

The reconstruction checks in `references/direction.md` are original guidance informed by HeyGen
contributors' Apache-2.0
[reverse skill](https://github.com/heygen-com/hyperframes/blob/73e65e2c7826ba1e33382f1f09d66f4e115e3aaa/skills/reverse-any-video/SKILL.md)
and [matching notes](https://github.com/heygen-com/hyperframes/blob/73e65e2c7826ba1e33382f1f09d66f4e115e3aaa/skills/reverse-any-video/references/match.md),
observed November 4, 2026; source commit dated the same day. Independent FFmpeg
[stream/frame inspection](https://ffmpeg.org/ffprobe.html) and
[scene scoring implementation](https://github.com/FFmpeg/FFmpeg/blob/eeca9d9280a92ef1536c154346c126cfb9d0ed6a/libavfilter/vf_scdet.c)
support timing inspection and distinguishing a score from a verified cut. No upstream text,
code, or media copied. Recheck when source timing, caption origin, renderer mapping, or
reconstruction scope changes.

## October 29 OpenFilm review

The saved-edit binding check in `references/production.md` is original guidance informed by
OpenFilm contributors' MIT-licensed
[override application](https://github.com/openfilm/openfilm/blob/de5a98bd46e2edfe8a98a6ca5343f925f71d53ff/packages/openfilm/src/overrides.mjs)
and [missing-target warning](https://github.com/openfilm/openfilm/blob/de5a98bd46e2edfe8a98a6ca5343f925f71d53ff/packages/openfilm/src/look.mjs#L56-L64),
observed October 29, 2026. Independent [Upwelling research](https://www.inkandswitch.com/upwelling/),
Ink & Switch, March 2023, section Automatic merging is necessary but not sufficient, supports
reviewing preserved intent after merges. No source text, code, or media copied. Recheck when
editor bindings, scene identity, or save behavior changes.

## October 26 design showcase review

Elaya's [design-to-motion](https://github.com/elayadesign/ai-design-skills/blob/a2735a3eaf092eaaffb6dc17df25de33ef3bd048/skills/design-to-motion/SKILL.md)
(MIT) B9 distinguishes the seam, empty interval, and final resting frame. The reset-interval
check in `references/render-review.md` is original guidance based on that distinction.
Observed October 26, 2026; recheck when the capture contract changes.

## October 25 eight-repository refresh

The reusable-style and actor-seed refinements in `references/genres.md` are original wording
informed by LemoLab's
[MY-STYLES.md](https://github.com/lemomo-ai/lemo-opuscar/blob/413a6bd6d78ebd3bdd5abaec9538a26867f890df/MY-STYLES.md)
(MIT code/docs) and John Heibel's
[clawd.js](https://github.com/JohnHeibel/ClaudeAnimationBase/blob/0ac8bf2b31942376cb6b8c4074715595d512acd2/src/clawd.js)
(MIT), corroborated by [Remotion flickering guidance](https://www.remotion.dev/docs/flickering)
(observed October 25, 2026). No upstream code, prompts, characters, or media copied. Recheck
when the base style, actor identity scheme, render sampling, or handoff contract changes.

## October 25 data-to-film review

The data check in `SKILL.md` (`## 2. Ground the story`) is original guidance informed by
Francesco's [production-studio article](https://x.com/francescoinweb3/status/2108882188624121896)
(Oct 10, 2026), Anthropic's
[Dashboards and Motion](https://claude.com/resources/articles/dashboards-and-motion) (Oct 8)
and [Motion export guide](https://support.claude.com/en/articles/17454997-get-started-with-claude-motion),
observed October 25, 2026, and [Spider 2.0](https://proceedings.iclr.cc/paper_files/paper/2025/hash/46c10f6c8ea5aa6f267bcdabcb123f97-Abstract-Conference.html)
(ICLR 2025). No prose, code, or prompts copied. Recheck when data lineage or metric contract changes.

## October 23 studio workflow review

Verification and delegation refinements in `references/production.md` draw on Motion's
[Studio editing](https://motion.dev/docs/studio-editing) and Remotion's
[interactivity guide](https://www.remotion.dev/docs/studio/interactivity-best-practices)
(observed Oct 23, 2026), Apache-2.0
[HyperFrames workflow](https://github.com/heygen-com/hyperframes/blob/aa4b53533414e5669caf6a9910c499143bbe0465/skills/hyperframes/SKILL.md)
(Oct 22, 2026), and Anthropic's
[agent architecture article](https://claude.com/resources/articles/building-agents-when-to-fold-subagents-into-your-main-agent-loop)
(Oct 22, 2026). No source text or code copied. Recheck when editor persistence, harness
capabilities, or the installed renderer change.

## October 6-7 direction and October 21 production review

`references/direction.md` is informed by [Prompt Motion's continuous-object example](https://prompt-motion.com/twoclipping-5cba86),
[phrase-led typography](https://prompt-motion.com/gdgtify-287ddf), MIT
[Cinetic](https://github.com/Leonxlnx/cinetic/blob/bee5d7807205d5543472c38312507f9bf366cbbf/skills/cinetic/SKILL.md),
and MIT [product-film](https://github.com/Rieranthony/product-film-skill/blob/fe11efc429d5903e37274d0b294e1b95745b2881/plugins/product-film/skills/product-film/SKILL.md).
`references/production.md` and `references/genres.md` (Oct 21, 2026) generalize ideas from:
[yihui-dev collection](https://github.com/yihui-dev/awesome-opus5-5-videos/tree/92aee2f586ac0715cb3cbcb6384834f98a33383d) (MIT),
[Lemo](https://github.com/lemomo-ai/lemo-opuscar/tree/b5e8ef93930b6d828f352055a689320f138237b1) (MIT code),
[Mexicat MV](https://github.com/mexicat/pdoom-video/tree/fa164b74fd0b26a99375715b619c55b4a0fb3d05) (MIT),
[JohnHeibel MV](https://github.com/JohnHeibel/PDoomVideo/tree/fa546a38092e75f2b079e6a86d6abc54dd525d17),
[MG styles](https://github.com/Vincentwei1021/mg-styles-15/tree/49052d80bfaf9fa8412cc9710530e5e95a3b8d8c) (MIT),
[AnimationBase](https://github.com/JohnHeibel/ClaudeAnimationBase/tree/0ac8bf2b31942376cb6b8c4074715595d512acd2) (MIT),
[Athemeroy brief/effect-fit](https://github.com/athemeroy/awesome-claude-5-5-videos/blob/87e5cbfaa4bf1f6516a6c69be58c42a9b85a1041/docs/production-brief.md) (CC BY 4.0), and
[Chinese prompt collection](https://github.com/joeseesun/opus-video-prompts/tree/7977c807781d4ba7c235247b8899a72575a30d00).
Recheck selected files and asset rights before reuse.

## October 24 recorded-footage and beat-grid reviews

Recorded-footage edits in `references/genres.md` draw on Browser Use's
[video-use](https://github.com/browser-use/video-use/tree/43cfc566833548093455c9d4a46bd69913b7e552) (MIT, Oct 24, 2026),
[OpenTimelineIO time ranges](https://github.com/AcademySoftwareFoundation/OpenTimelineIO/blob/main/docs/tutorials/time-ranges.md),
[FFmpeg 8.0 trim/atrim](https://raw.githubusercontent.com/FFmpeg/FFmpeg/n8.0/doc/filters.texi), and
[W3C WAI captions](https://www.w3.org/WAI/media/av/captions/) (Sept 17, 2024). Music-led downbeat
checks draw on [librosa 0.11.0 beat_track](https://librosa.org/doc/0.11.0/generated/librosa.beat.beat_track.html)
and [MIREX Audio Downbeat Estimation](https://music-ir.org/mirex/wiki/2026:Audio_Downbeat_Estimation) (Oct 24, 2026).

## Reusable campaigns (November 14, 2026)

eigen's [roundup](https://x.com/e1genqq/status/2121340063254556890) and linked
[campaign article](https://x.com/i/article/2109996653650354178) (Oct 13, 2026) plus Remotion v4.0.540
[Passing props](https://github.com/remotion-dev/remotion/blob/596c2ed0cd3b274065bc1ef76eb82241bd6dbf19/packages/docs/docs/passing-props.mdx)
motivated approved variant inputs, transition copy checks, and per-format layouts in
`references/production.md`. Recheck when campaign inputs, layout, fonts, or renderer change.
