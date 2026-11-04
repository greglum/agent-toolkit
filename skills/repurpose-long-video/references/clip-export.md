# Export supplied local clips

Use the project's existing cutter first. Otherwise `scripts/export_clips.py` completes a
bounded local path from the selector's output, supplied timed transcript and manual crop
plan to MP4 clips, SRT sidecars and a source-bound edit list. It uses Python 3.10+ and existing
FFmpeg/ffprobe with the libx264 and AAC encoders. It downloads nothing and selects no service.

This path supports a fixed crop per clip. A moving subject, shot change or layout that needs
a changing crop uses the project's reviewed crop path instead. Do not substitute one static
crop when it cuts off the subject or necessary on-screen text.

## Prepare the inputs

Complete the rights, context and transcript checks in the skill before export. Record the
actual source SHA-256 in the transcript's `source.sha256` before selection; the selector
copies that source identity into its output. The export requires both files and the crop
plan to name the same actual source digest. A matching hash binds files, not their accuracy.

The transcript uses the existing `segments` contract: `start`, `end` and `text`, in seconds
from the source's first decoded video frame. Decimal numbers or rational strings such as
`"1001/30000"` work for export. Preserve the existing selector's numeric timing contract
when using the same file for selection. Keep word or phrase timings as supplied; no
transcription or forced alignment runs here.

Write a crop plan with exactly one row per selected id:

```json
{
  "source_sha256": "<recorded source SHA-256>",
  "output_size": [180, 320],
  "clips": [
    {"id": "w1-01", "crop": [114, 10, 90, 160], "context_verdict": "pass"}
  ]
}
```

The example crop fits a 320 by 180 source and has the same display aspect as its output.
Choose actual coordinates from the reviewed source. `crop` is `[x, y, width, height]` in
encoded source pixels; all four must be even integers and the box must fit the source.
Its display aspect, including the source's sample aspect, must match `output_size` so the
helper cannot stretch people. Output dimensions must be positive even integers at most
8192. Declared display matrices and rotation metadata are refused before any output is
created. Normalize a reviewed copy first, then bind the transcript, selection and crop plan
to that copy and check its encoded-pixel coordinates. A supplied context verdict is `pass` or `extended`; the helper does not adjudicate it.

## Run the complete path

```sh
python3 -I <skill>/scripts/export_clips.py source.mp4 selection-01.json crops.json clips-01 \
  --transcript candidates.json
```

`clips-01` must not exist, and its parent must already exist. Existing outputs are never
overwritten. Inputs must be local files, with the video in MP4, MOV, MKV, WebM, AVI or M4V;
playlists and network sources are refused. The helper probes decoded presentation timestamps
and can scan the full source, so allow time for long recordings. A positive decoded
last-frame duration is required; the helper refuses an unknown tail rather than extrapolating
a variable-rate endpoint. It supports 1 to 64 clips.

For each requested half-open interval `[start, end)`, export begins at the first decoded
video frame at or after `start` and excludes the frame at or after `end`. The receipt keeps
both requested bounds and effective source-frame bounds. Source timestamps and encoder time
base preserve fractional rates and variable-rate timing; no assumed 30 fps or keyframe copy.
Audio is trimmed against the effective video origin, preserving any delayed onset with
leading silence and padding its tail to the video interval. It is encoded when the source
has audio. The output probe checks encoded audio start and duration and records actual audio
metadata, dimensions, frame count, rate and duration.

Each clip has an MP4 and an SRT sidecar. Caption intervals are clipped and rebased to the
effective video start; text stays plain and is escaped for SRT viewers. Sidecars are not
burned into the picture. Check the destination's caption-upload or burn-in requirements
with the existing film workflow. The encode removes inherited file metadata.

## Read the result and finish acceptance

Exit 0 and `EXPORTED` mean frame count/timestamps, video duration, dimensions, audio presence and timing,
and unchanged input digests passed. `edit-list.json` records input/output/caption digests,
requested/effective cuts, crop, supplied context verdict and all unverified review dimensions.
Output filenames use ordinal clip numbers rather than untrusted candidate ids.

The helper cannot certify rights, transcript accuracy, meaning, crop safety, caption
readability, loudness, listening, playback or account-specific limits. Review every output
through motion-film's existing checks before calling the delivered clips accepted. A parsed
context verdict is not independent review. Do not clear the receipt's unverified list merely
because encoding succeeded; retain actual review evidence beside it.

An input/usage/tool failure exits 2. A failure after the new output directory was created
leaves its partial files and `failure.json` for diagnosis, without a success edit list.
Interruptions can leave partial files without that failure record. Preserve the directory
and rerun only into a new path. Recheck the original source identity before resuming.

## Provenance

Original implementation, November 4, 2026. The current source comparison with MIT
[Clipify](https://github.com/hadimousavi79/clipify-skill/tree/621855bdc0ea67c40d872ffb8f216f5f10c7bc73)
identified a useful crop/caption capability; no upstream code, prompts or media copied.
The local tool uses supplied fixed crops and actual decoded timestamps, rather than its
speaker heuristic or 30 fps assumption. Checked installed FFmpeg option help for encoder
time base and frame synchronization. Recheck decoding, timestamp mapping and the chosen
destination after tool/input changes. Synthetic CLI proof does not establish broader skill
selection, semantic quality or a no-skill benefit.
