# Capture and export review helpers

Use the project's existing capture, comparison, and delivery tools first. When none exist,
these bundled Python 3 helpers inspect local media using installed `ffmpeg` or `ffprobe`.
They install nothing, make no network calls, and never overwrite existing outputs. Extraction
or metadata checks alone never establish visual quality, pacing, or playback acceptance.

## Extract review sheets

```sh
python3 <motion-film>/scripts/contact_sheet.py film.mp4 review/film-v2 --every 1
```

[`contact_sheet.py`](../scripts/contact_sheet.py) requires a new output directory, writes
4 by 4 pages of 360 px-wide samples (`sheet-NNNN.png`), and saves `ffmpeg.log` and
`manifest.json` mapping one-based row and column positions to decoded frame seconds from the
first video frame. Blank trailing cells are unused.

- Open every page (including the last) and use `manifest.json` to locate findings.
- Extract the final frame separately if needed; `--every` selects the next actual frame at
  least N seconds after the previous sample, not exact grid times or the end frame.
- `EXTRACTED` (exit 0) means sheets were written; exit 1 is failure, exit 2 is invalid input
  or unavailable FFmpeg. On failure, retry into a new directory.
- A sheet is an overview only; run consecutive-frame cut checks and playback review in
  `references/render-review.md`.

## Compare captured frames

```sh
python3 <motion-film>/scripts/compare_frames.py review/fresh.png review/backward-seek.png
```

[`compare_frames.py`](../scripts/compare_frames.py) reads local PNG, JPEG, BMP, PPM, or PAM
stills, decodes one frame as 8-bit RGBA without resizing, emits JSON, and writes no files.
Exit 0 passes, 1 fails, 2 means invalid input or unavailable FFmpeg.

- Different dimensions fail. Do not use it to certify HDR, wide-gamut, or high-bit-depth
  equivalence (8-bit RGBA conversion drops higher bit depths). Alpha and RGB behind
  transparency count as channels.
- Exact match is default. If the capture contract permits noise, declare both
  `--max-channel-delta` (0 to 255) and `--max-different-pixels` before running. Small pixel
  counts can still hide a changed number or label.
- Compare the same time after different seek histories, and compare two times with planned
  motion (identical captures across motion imply a broken time control). Keep visual review
  separate (`references/render-review.md`).

## Compare reference and draft frames

```sh
python3 <motion-film>/scripts/pair_event_frames.py reference.mp4 draft.mp4 pairs.json review/v2
```

[`pair_event_frames.py`](../scripts/pair_event_frames.py) compares known cleared local media at
1 to 64 named event time pairs (`[{"event": "...", "reference_seconds": 1.2, "draft_seconds": 1.8}]`)
into a new output directory. For trimmed edits, map output times back to source times first.

- Times are seconds from each input's first decoded video frame; the helper picks the first
  actual frame at or after each request.
- Each `pair-NNN.png` places reference left and draft right inside 360 px square cells without
  cropping (preserving display aspect with padding), alongside `manifest.json` (requested and
  decoded times, input SHA-256 digests, FFmpeg version, commands) and per-pair logs.
- Choose pairs from the scene contract before judging fidelity; extract native-size and
  consecutive frames for fine detail or timing. `EXTRACTED` does not prove conformance,
  playback, or audio.

## Inspect encoded metadata

```sh
python3 <motion-film>/scripts/probe_export.py film.mp4 \
  --width 1920 --height 1080 --fps 30 --duration 30 \
  --require-audio --video-codec h264 --pixel-format yuv420p
```

[`probe_export.py`](../scripts/probe_export.py) checks a local media file against the
declared delivery contract using installed `ffprobe`. Pass the contract values, never values
copied from the output being inspected. Exit 0 is `PASS`, 1 is `FAIL`, 2 is `UNAVAILABLE`.

- FPS accepts rationals such as `30000/1001` (0.001 rounding). Duration and start tolerance
  default to 0.1 s (`--tolerance`). Omit `--require-audio` when audio is optional, or
  codec/pixel constraints when unspecified.
- Requires one primary video stream (excluding attached cover art). Intentionally silent
  deliverables or multi-angle/delayed-audio tracks need the project's verifier.
- Uses `duration_ts * time_base` for stream lengths and never substitutes container length for
  missing stream duration (reporting `UNAVAILABLE` instead).
- Metadata agreement does not prove constant frame cadence, decoded picture quality, sync,
  loudness, captions, or target playback. Verify audio channel layout and actual preview
  playback in the target environment, since metadata alone cannot prove audible playback.
- Check installed FFmpeg CLI options after tool upgrades: FFmpeg 9 removed
  `-filter_complex_script` (use `-/filter_complex <file>`; observed October 23, 2026; recheck
  when upgrading FFmpeg or running custom filter-script pipelines).
