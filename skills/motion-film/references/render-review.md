# Capture and export review

Use the project's existing capture and renderer interfaces. Record the source revision,
browser/renderer, dimensions, fonts, palette, motion mode, fixed data, assets, scene, and time.
Bundled CLI helper commands (`contact_sheet.py`, `compare_frames.py`, `pair_event_frames.py`,
`probe_export.py`) live in `references/review-helpers.md`.

## Frames and handoffs

1. Wait for explicit readiness: required assets decoded, fonts loaded, timeline built, and the
   requested frame applied. A fixed delay alone does not establish readiness. Stop dependent
   capture on an asset error or timeout.
2. Capture the opening, meaningful action, and payoff of each changed scene (using the
   project's sheet tool or `contact_sheet.py` as an overview). Also inspect consecutive frames
   across each cut and changed handoff (last frame before to first frame after, including
   overlap). For loops, check consecutive frames across the end/start seam for position,
   velocity, visibility, and audio, plus any reset or empty interval and settled frame
   separately against the approved still. Keep fixed backgrounds unchanged through the reset.
3. Confirm seeking changes the picture: identical frames at different planned-motion times
   mean capture ignores time and invalidate frame evidence. Compare a chosen time (plus a
   transition time and endpoint) after forward, backward, and unrelated seeks under identical
   conditions (with the project comparator or `compare_frames.py`). Encoded file hashes are
   not frame evidence.
4. Inspect images at delivery size:
   - Unless the owner sets other sizes, keep body text >= ~2.6% of the short side (28 px at
     1080), titles 4 to 9% of frame height, and hero text >= 1.8x the next text size, all
     inside safe margins. Shorten headlines that wrap past two lines rather than shrinking.
   - Review a 360 px-wide sheet for phone destinations; text unreadable there fails.
   - Place captions as an overlay in the lower title-safe area; re-split overflowing caption
     groups rather than shrinking below minimum readable size or clipping. Keep only small
     critical labels out of the caption span and leave room for platform controls.
   - Check peak motion extent, blank frames, stranded layers, competing focal points, and
     >= 4.5:1 contrast behind text/marks (never relying on color alone). Check each aspect
     variant at its own size (`references/direction.md`, Choreograph the handoff).
   - For demonstrated clicks, inspect target visibility through approach, press, and result;
     for typing, inspect focus, character progression, blur, and populated field.
5. Watch normal playback end to end for a new film (or the changed sequence and neighbors for
   an update). Check holds, pacing, transitions, and player controls; verify changed flashes
   against the flash rule in `SKILL.md`. Flag stretches with no new element against the
   stillness limit in `references/timing.md`, weighing stillness leads against intended reading
   holds before adding motion. Check muted playback and, for narrated films, audio-only comprehension. Profile costly filters/3D layers under playback conditions,
   and run real-time checks (`references/live-browser.md`) for live browser films.

## Compare an adopted reference

For a requested reference match, compare the draft against adopted relationships in its
reference spec (`references/direction.md`, Study a reference), matching key events across
explicit time pairs (via the project tool or `pair_event_frames.py`). Inspect consecutive
frames for motion and listen for sound cues. Keep this conformance pass separate from the
blind critique (`references/production.md`, Run the critique loop). Tie findings to the
reviewed render, fix the owning cue/scene input, and recapture affected events and neighbors.
Missing reference media leaves the requested match unverified; continue independent checks.

## Check execution and coverage

Read each audit section's execution status and sampled times, not just its finding count.
Zero findings with zero samples, an unstarted browser, or an earlier lint failure is unrun.
Record omitted samples and inspect omitted changed handoffs before claiming coverage. Capture
or decode success never marks visual review, watching, or listening complete.

This evidence check is informed by the HyperFrames
[check command](https://github.com/heygen-com/hyperframes/blob/8bca7c4417b59b47fca851183a8d47a4565bad0c/packages/cli/src/commands/check.ts)
(Apache-2.0, observed October 10, 2026; recheck when audit output or renderer changes).

## Encoded output

When a media file is requested, use the installed renderer and encoder matching the target
container. Inspect metadata with the project verifier or `probe_export.py` (container, codecs,
dimensions, duration, fps, pixel format, audio streams, color metadata, AI-disclosure/provenance
metadata, and subtitle/chapter sidecars). Check video, audio, and container durations and start
offsets separately. Compare decoded audio with picture on the encoded presentation timeline,
and decode/play representative frames and loop boundaries.

Inspect each thumbnail or poster as its own settled scene frame (never a transition, end card
only, or placeholder subtitle). For requested transparency, decode alpha-aware frames,
inspect alpha and transition edges composited over light and dark footage, and verify target
browser/editor playback (reporting unavailable target playback as unverified).

Report only files actually produced; separate passed, failed, unavailable, and unrun checks.
Subjective scores and fixed review-round counts are not acceptance evidence. Restore inspection
aids before export, and never hide a defect by fading or shrinking it.
