# Compare reference and draft frames

Use this for a reference match or a before/after correction check with known local media
and explicit time pairs. For a trimmed edit, map each output time to its source time first;
the extractor does not infer that mapping. Reuse the project's comparison tool first.
Otherwise the bundled
[extractor](../scripts/pair_event_frames.py) needs Python 3 and installed FFmpeg:

```sh
python3 <motion-film>/scripts/pair_event_frames.py reference.mp4 draft.mp4 pairs.json review/v2
```

The output directory must be new. Write `pairs.json` as a list of 1 to 64 named events:

```json
[
  {"event": "title landing", "reference_seconds": 1.2, "draft_seconds": 1.8},
  {"event": "payoff", "reference_seconds": 4.0, "draft_seconds": 5.4}
]
```

Times are seconds from each input's first decoded video frame. The tool selects the first
actual frame at or after each request. Different frame rates can yield different sampled
times. `manifest.json` records both requested and decoded times, source SHA-256 digests,
event names, FFmpeg version and commands. It compares input digests before and after
extraction. Each `pair-NNN.png` places reference left and draft right in 360 px square cells,
fitting their display aspect ratios without cropping. Black padding is added where needed.
The separate images and decoder logs remain beside each pair.

Inspect every pair and record findings against its event and input identity. These are
overview images; extract native-size and consecutive frames for fine detail or timing.
Choose pairs from the scene contract before judging fidelity. Moving the draft's timestamp
until the pictures look alike can hide the timing error being checked.

`EXTRACTED` means images were produced. Visual conformance, playback, pacing and listening
remain unverified. A missing frame, decode failure or input change fails without a success
manifest; retain its diagnostic directory and retry into a new one. Existing output is never
overwritten. The helper reads local inputs only and does not fetch references or render source
code. Use cleared media; an author's code license does not license its reference clip.
