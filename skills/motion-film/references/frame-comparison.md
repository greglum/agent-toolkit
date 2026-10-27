# Compare captured frames

Use the project's comparator first. Otherwise, compare two saved still captures with
Python 3 and the installed FFmpeg:

```sh
python3 <motion-film>/scripts/compare_frames.py review/fresh.png review/backward-seek.png
```

Exit 0 means the decoded pixel contract passes, 1 means it fails, and 2 means invalid input
or unavailable evidence. The tool reads local PNG, JPEG, BMP, PPM or PAM files, emits JSON,
and writes no files. It decodes one frame as 8-bit RGBA without resizing. Different dimensions
fail. Do not use it to certify HDR, wide-gamut or high-bit-depth equivalence: conversion to
8-bit RGBA loses information. Alpha and even RGB hidden by transparency count as channels.

Exact comparison is the default. If the owner's capture contract allows noise, declare both
`--max-channel-delta` (0 to 255) and `--max-different-pixels` (a pixel count) before inspecting
the result. One limits color change at a pixel; the other limits how many pixels may exceed
it. These are raw channel limits, not a perceptual similarity score. No anti-aliasing or
region is silently excluded. A small changed count can still hide a wrong number or label.

Use identical capture settings and record the source, assets, renderer/version, dimensions
and requested time beside each pair. Compare the same time after different seek histories.
Also compare two times with planned motion and require a difference; two identical captures
can mean a broken time control. This tool does not drive the renderer, attest capture
identity or judge whether a difference was intended. Inspect actual frames and keep
[render review](render-review.md) and playback checks separate.

## Sources

Original implementation and procedure, observed October 26, 2026. Mapbox's
[pixelmatch](https://github.com/mapbox/pixelmatch/tree/ab76f526ef951c0ec6284e314a700e161b1800e6),
ISC, README API and index.js comparison loop, distinguishes color sensitivity from differing
pixel count and exposes anti-alias exclusions. We use neither its algorithm nor defaults.
The existing FFmpeg prerequisite supplies decoding; no Node package or Python imaging
dependency was added. [FFmpeg image formats](https://ffmpeg.org/general.html#Image-Formats)
and [image2pipe](https://ffmpeg.org/ffmpeg-formats.html#image2_002c-image2pipe) document the
PAM/pipe path. Living documentation has no redistribution grant verified here; no source
code or prose copied. Recheck after decoder, pixel format or tolerance changes.
