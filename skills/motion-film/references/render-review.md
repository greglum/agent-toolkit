# Capture and export review

Use the project's existing capture and renderer interfaces. Record the source revision,
browser/renderer, dimensions, fonts, palette, motion mode, fixed data, assets, scene and time.

## Frames and handoffs

1. Wait for explicit readiness: required assets decoded, fonts loaded, timeline built, and the
   requested frame applied. A fixed delay alone does not establish readiness. Confirm required
   assets loaded successfully and stop dependent capture on an error or timeout.
2. Capture the opening, meaningful action, and payoff of each changed scene. A contact sheet is
   an efficient first pass but hides broken motion. Without a project tool, use the bundled
   [sheet extractor](contact-sheets.md). Also inspect the early frames and a run
   of consecutive frames across each cut and changed handoff, from the last frame before to
   the first frame after, including any overlap. For loops, inspect consecutive frames across
   the end/start boundary for position, velocity, visibility, and any audible seam; identical
   endpoint stills alone do not prove a continuous cycle. If a loop includes a reset or empty
   interval, inspect that interval separately against the intended empty state, plus the
   settled frame against the approved still. Matching seam endpoints can conceal a layer,
   mask, counter, or helper that resets late between them. Compare at the same capture scale
   and keep any background the brief holds fixed unchanged through the reset.
3. First confirm that seeking changes the picture: identical frames at different times where
   motion is planned mean the capture ignores time, and none of its frame evidence counts. Then
   seek to a chosen time after forward, backward, and unrelated seeks. Compare frame pixels or
   the relevant geometry, opacity, and layer visibility under identical conditions. Include a
   transition time as well as an endpoint. Encoded file hashes are not frame evidence.
   Without a project comparator, use the optional [pixel comparator](frame-comparison.md)
   on saved stills. Its numeric pass does not establish capture identity or visual quality.
4. Inspect the images. Measure text and subject bounds at the delivery size: captions, titles,
   controls, units, and camera targets must remain readable and unclipped. Unless the owner
   sets other sizes, body text is at least about 2.6% of the frame's short side (28 px at
   1080), titles 4 to 9% of frame height, and hero text at least 1.8 times the next text
   size. Keep key text inside the destination's safe margins. Check the longest copy in each
   format: shorten a headline that wraps to a third line and keep its size. For any
   destination watched on phones, review a contact sheet scaled to 360 px wide; text that
   cannot be read there fails. Captions sit as an overlay in the lower title-safe area.
   A caption group that still overflows its line cap at the minimum readable size fails:
   re-split it rather than shrink it further or let the renderer clip it.
   Keep the composition centered on the full frame, and keep only small critical text (a
   URL, a legal line, a lower-third label) out of the caption line's span. Leave room for any
   actual destination overlay, such as platform controls. Inspect peak motion extent as well as the
   resting layout. Check blank frames, stranded layers, unwanted backgrounds, competing focal
   points, and cursor/target alignment. Text, captions, and meaningful marks keep at least
   4.5:1 contrast against what is actually behind them; color is never the only signal.
   For several aspect ratios, check each variant against the
   [composition contract](direction.md#choreograph-the-handoff) and review each delivered
   format at its own size.
   For a demonstrated click, keep its target visible through approach and press, then inspect
   the stated result. For typing, inspect focus, character progression, blur, and the populated
   field. An end-state frame cannot establish those actions.
5. Watch normal playback end to end for a new film, or the changed sequence and its neighbors
   for an update. Check readable holds, pacing, transitions, and the player's controls where
   present. For changed flashes or strobing, check the affected interval against the shared
   flash rule in the skill entrypoint. If compliance cannot be established, remove the effect
   or leave acceptance unverified. Frozen frames and seek comparisons cannot prove playback
   behavior. Flag dead air with the stillness rule in [timing defaults](timing.md#holds-and-reading-windows).
   A stillness metric is a lead: changing grain or a background can hide a stationary subject,
   and adding motion to lower a score can make the film harder to follow. Inspect the flagged
   content against its intended reading hold before changing it.
   Check muted playback with the normal text settings: the workflow and payoff should remain clear. For
   narrated films, also listen without picture: the spoken line should carry the argument
   without depending on unnamed visuals. Keep the complete explanation available through
   captions or an accessible transcript. When changed effects cause stutter or introduce costly
   filters or 3D layers, profile the affected scene under the same conditions. Offline render
   speed does not prove a smooth player.

## Compare an adopted reference

For a requested reference match, compare the draft with the relationships adopted in its
[reference spec](direction.md#study-a-reference). Match events such as first motion, title
landing, payoff and cut boundaries; different lengths or frame rates need explicit time
pairs. Record the expected relationship, allowed difference, observed result and evidence.
Use the project's comparison tool, or the bundled [paired-frame extractor](pair-event-frames.md).
Inspect consecutive frames for motion and listen for sound cues; paired stills alone cannot
settle whether an entrance is a beat late. A changed brand or layout need not match pixels.

Keep this conformance pass separate from the [blind critique](production.md#run-the-critique-loop),
whose reviewer first sees the film without its brief. Tie findings to the reviewed render.
Fix the owning cue or scene input, then recapture its affected events and neighboring handoffs.
A shared timing change can invalidate later scenes even when its source diff is one line.
Missing reference media leaves the requested match unverified; obtain an accessible reference
before claiming fidelity. Continue independent checks under the existing brief.

## Check execution and coverage

Read each audit section's execution status and sampled times, not just its finding count.
Zero findings with zero samples, an unstarted browser, or an earlier lint failure is unrun,
not a clean render. Record omitted samples and inspect omitted changed handoffs before
claiming their coverage. Use the existing renderer's boundary samples where available;
midpoint captures do not replace the consecutive-frame handoff check above.
Capture, extraction, decode, or transport success cannot mark visual review, watching, or
listening complete. Record the actual inspection and its scope separately; otherwise leave
that review unverified.

This evidence check is informed by the HyperFrames
[check command](https://github.com/heygen-com/hyperframes/blob/8bca7c4417b59b47fca851183a8d47a4565bad0c/packages/cli/src/commands/check.ts),
Apache-2.0, observed October 10, 2026. No renderer code or command contract is copied.
Recheck when the project changes its audit output or renderer.

## Encoded output

When a media file is requested, use the installed renderer and encoder that fit the requested
container and destination. Inspect its metadata with the project's tools or an available media
probe: container, codecs, dimensions, duration, fps, pixel format, audio streams, and color
metadata when material to the destination. When the brief requires AI-disclosure or
provenance metadata, confirm the encoded file still carries it; re-encoding can strip it.
Check subtitles and chapter sidecars if promised.
Check video, audio and container durations separately, including start offsets. A full-length
container can conceal a shortened stream. If no project verifier exists, use the optional
[metadata helper](export-checks.md); its pass covers only its named measurements.
Compare decoded sound with picture on the encoded presentation timeline, accounting for
timestamps, offsets, and discontinuities. Concatenated PCM sample positions alone do not
establish cue timing when they omit presentation silence.
Decode representative output frames and play the output to catch encoding, color, timing,
missing audio, or clipping defects. Inspect a loop's encoded boundary.

Inspect each delivered thumbnail or poster as its own file. It must be a settled frame of the
intended scene, never a transition, and should state the film's subject rather than only its end
card. A default chosen relative to the last spoken word can land inside the closing dissolve and
double-expose two scenes. Placeholders must never reach a delivered export: a production note
rendered as a subtitle ("captures pending") reads to a viewer as unfinished work.

When transparency is requested, decode representative output frames with a supported
alpha-aware decoder and inspect the actual alpha, including transition edges. Composite
them over relevant light and dark footage to check legibility and unwanted fringes or
backgrounds. Exercise playback in the target browser or editor when available; a file
extension, alpha metadata, or one successful decoder does not prove that target works.
Report unavailable target playback as unverified.

Report only files actually produced. A render command that exits successfully, an HTML preview,
or a renamed extension does not establish that the promised output is correct. Separate failed,
unavailable, and unrun checks. Report each scene check as pass, fail, unverified, or not
applicable, naming its evidence. Recheck confirmed fixes under the same capture conditions;
subjective scores and a fixed number of review rounds are not acceptance evidence.
For an independent pass over the rendered frames, run the
[critique loop](production.md#run-the-critique-loop). Restore
every inspection aid (debug outlines, hidden layers, contrast backgrounds) before export. Never
hide a defect by fading or shrinking it.
