# Speech editing and frame-feedback sources

The recorded-footage branch now settles the speech cut before intro effects, preserves
meaning when moving a line, and selects complete takes. The critique loop binds spatial
feedback to the reviewed render, output time and marked frame or region; moved targets
need relocation. These are original procedural refinements, with no editor or ASR bundled.

Sources: Peter Yang's interview with Jake Moran,
[video](https://www.youtube.com/watch?v=MC1g2fHYC88), October 25, automatic English captions
at 2:21-7:59, 23:39-26:39 and 36:18-38:27; and the linked
[editing guide](https://video-editing-101.vercel.app/), Main cut, Intro reel and Polish.
Independent checks: Adobe's
[transcript editing](https://helpx.adobe.com/premiere/desktop/edit-projects/edit-video-using-text-based-editing/detect-and-delete-pauses-in-transcripts.html),
January 7, 2026, and
[frame comments](https://helpx.adobe.com/premiere/desktop/collaborate-with-others/share-for-review-using-frame-io/add-comments-on-shared-projects.html),
November 19, 2025. The latter describes the Legacy panel, not a current V4 integration recipe.
All observed October 25, 2026; redistribution rights for these living pages and video are
unestablished. No text, prompts, code or media copied. Recheck when the timeline, render
identity or review surface changes. Paired behavioral evaluation and footage rendering
were not run. The catalog assessment records tooling gaps separately.

## October 27 video-editor review

Tobia Donadon's [Video Editor article](https://x.com/tobiadonadon_/status/2115190452202660333),
published October 27, 2026, and its linked public V1/V2 offers prompted two original
refinements: distinguish verbatim speech from cleaned transcripts, and compare corrections
at matching source frames. The packages and their licenses were not inspected; their
advertised editing, masking and preference-learning machinery is not bundled here.

Independent evidence: Wagner, Thallinger and Zusag's
[CrisperWhisper paper](https://www.isca-archive.org/interspeech_2024/zusag24_interspeech.pdf),
Interspeech 2024, introduction and section 4.3.2, documents omitted disfluencies and the
separate task of locating them. Adobe's
[frame comparison guide](https://helpx.adobe.com/uk/premiere/desktop/edit-projects/compare-edits-to-source-clips/compare-edits-to-clips-in-the-program-monitor.html),
updated January 21, 2026, distinguishes same-frame effects review from shot matching. Its
[color matching guide](https://helpx.adobe.com/premiere/desktop/correct-color/add-color-effects/match-color-between-shots.html),
updated August 18, 2026, calls for representative frames when brightness changes over time.
Observed October 27, 2026; living-page and paper redistribution rights were not established.
No text, code, prompts or media copied. Recheck on ASR mode, source, edit mapping, color
pipeline or comparison-tool changes. Paired behavioral evaluation and footage review were
not run; structural checks do not prove editing quality.

## November 6 video-editing toolkit review

The recorded-footage procedure checks detector-proposed removals on the selected source
track, including the audio just before and after each interval. The editable handoff
procedure binds required approval to the actual proposal and its saved base revision.

[FFmpeg Skill's pause detector](https://github.com/kajisho5/ffmpeg-skill/blob/9bdb444fdd569bcf50276337b36164fadf54b363/scripts/silence.py)
(MIT, November 6, 2026) derives candidates from levels and supports margins and time maps.
[Herk Edit Kit's cut script](https://github.com/nateherkai/herk-edit-kit/blob/10511e5af86fc47756ea89803b397422e2d89284/.agents/skills/cut-silences/scripts/cut-silences.mjs)
(MIT, October 14, 2026) starts from gaps between timed words. The
[FFmpeg filter reference](https://ffmpeg.org/ffmpeg-filters.html#silencedetect) defines the
level and duration test. [OpenChatCut's external edit sessions](https://github.com/0xsline/OpenChatCut/blob/9242a95aea248ff3a8dab495514384e858320d47/README.md#L314-L319)
(AGPL-3.0, November 6, 2026) separate tool permissions from manual proposal approval and
document how auto mode applies a draft. Observed November 6, 2026. These are original
procedures. Recheck if the detector, selected track, editor mode or save contract changes.
