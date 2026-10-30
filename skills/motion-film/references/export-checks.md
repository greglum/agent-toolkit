# Encoded metadata helper

Use the project's delivery verifier first. When none exists, the bundled
[`probe_export.py`](../scripts/probe_export.py) checks a local file using installed `ffprobe`
and Python's standard library. It installs nothing and never rewrites the media.

Pass the actual delivery contract, not values copied from the output being checked:

```bash
python3 <skill>/scripts/probe_export.py film.mp4 \
  --width 1920 --height 1080 --fps 30 --duration 30 \
  --require-audio --video-codec h264 --pixel-format yuv420p
```

FPS accepts a rational such as `30000/1001`. Omit `--require-audio` when audio is optional;
present audio is still checked. A required absence of audio needs the project verifier.
Omit codec or pixel format constraints when the destination
does not specify them. The helper requires one primary video stream, excluding attached cover
art. A multi-angle or intentional delayed-audio deliverable needs its own project verifier.

The JSON result reports PASS, FAIL or UNAVAILABLE with each measurement. Exit codes are 0,
1 and 2 respectively. It compares dimensions, average fps, required audio, requested codec and
pixel format, container duration, and every video/audio stream's duration and start time.
Duration and start tolerance defaults to 0.1 seconds; use `--tolerance` for the documented
destination allowance, not to hide a defect. The fps comparison allows 0.001 fps rounding.

Some containers omit stream durations. The helper uses `duration_ts * time_base` when present,
otherwise marks that check UNAVAILABLE. It never substitutes the container length for a
missing video or audio duration. Use a suitable project verifier to establish the missing
evidence; an unavailable measurement cannot pass by assumption.

This proves metadata agreement only. Average fps does not establish constant frame cadence.
It does not decode frames, listen, validate color or alpha, measure loudness, compare captions,
or prove synchronization, complete tail speech, absence of black frames or target playback.
Continue through [capture and export review](render-review.md). A full decode with the
installed encoder can expose damaged packets; watching and listening still establish the
picture, pacing and sound. Keep the JSON beside the final file's other evidence.

Before sending a master, also check that its audio is stereo and not silent, then play it in
the preview where it will be reviewed. In one case a mono AAC master played silently in a chat preview.
Check that a tool's options still exist after an upgrade; ffmpeg 9 removed
`-filter_complex_script` (use `-/filter_complex <file>`).
