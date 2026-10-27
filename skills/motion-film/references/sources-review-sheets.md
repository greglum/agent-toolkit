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
