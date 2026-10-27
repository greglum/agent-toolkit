# Review-sheet sources

Reviewed [echris6/motion-video-kit](https://github.com/echris6/motion-video-kit/tree/e4b1c0004080fe6a0deb883631bad5eba1e5f339),
MIT, commit dated October 14. The contact-sheet script motivated our own
[paginated extractor](contact-sheets.md); no upstream code, prompts or assets were copied.
Our tool retains actual sampled times and all pages, refuses an existing output directory,
and reports extraction separately from review. FFmpeg's installed 8.1.1 filter help and
[official filter documentation](https://ffmpeg.org/ffmpeg-all.html#select_002c-aselect)
support the select/showinfo/tile implementation.

The stillness-metric caveat in [render review](render-review.md) also draws on Akshat Darshi's
[September 30 production account](https://milliondreams.vercel.app/blog/launch-film-in-code),
Measuring motion: grain hid stillness, and lowering the stillness score could worsen the film.
That is a separate user's account using the same kit, not an independent controlled benchmark.
Living-page reuse rights were not established; wording here is original.

Recheck when FFmpeg filters or the review timeline change. Synthetic extraction was exercised;
blind skill/control evaluation, upstream runtime, film playback and listening were not run.
Audio solving, back-timing and 3D overlays remain tooling gaps rather than claimed parity.

## Paired reference review, October 26, 2026

Francesco's [review-loop post](https://x.com/francescoinweb3/status/2114600805579763971)
and linked [article](https://x.com/francescoinweb3/status/2108882188624121896) prompted a
refresh of all eleven linked repositories. Article/post reuse rights are unknown.
Raphaël Aubry's MIT [comparison renderer](https://github.com/howseen-ai/claude-motion-design/blob/3d90d349ef3fdde9b7e89de4df4a2159c9e8697f/skill/motion-design/scripts/remake/remake_render.py)
and [QA sheets](https://github.com/howseen-ai/claude-motion-design/blob/3d90d349ef3fdde9b7e89de4df4a2159c9e8697f/skill/motion-design/scripts/remake/remake_qa.py)
provide paired reference/draft images. Mort1d's MIT
[reference analyzer](https://github.com/Mort1d/motion-graphics-skills/blob/7f0c3714dc81bea52644a5287c6350345009e579/skills/motion-graphics/scripts/ref-sheet.mjs)
also supplies timing leads, not proof of perceived rhythm or quality.

Our [paired-frame helper](pair-event-frames.md) is an original implementation using Python's
standard library and installed FFmpeg. No upstream code, prompts, fonts, audio or media are
copied. It takes explicit event time pairs instead of assuming one source frame rate and
reports actual decoded times, input digests and extraction status. Installed FFmpeg 8.1.1
filter help and its [official filter manual](https://ffmpeg.org/ffmpeg-filters.html)
support selection, timestamp logging, aspect fitting and horizontal stacking.
The conformance procedure compares adopted relationships separately from blind comprehension.
Synthetic decoder checks establish extraction behavior, not an agent's review quality.
Recheck when comparison semantics, source timing, FFmpeg or the review contract changes.
