# Compact production record

Use this as a starting shape when the project has no brief, storyboard or delivery record.
Keep its existing format when one exists. Replace example values with actual decisions; omit
inapplicable sections. Store it with the film's source, never with credentials or private keys.

```yaml
film: example-mechanism
revision: source revision plus identity of local edits
audience_and_decision: who watches and what they should understand or decide
thesis: one source-backed promise
visual:
  keep: relationships taken from each reference
  avoid: looks to avoid, named concretely
hard_lines: what the film never does, such as inventing a screen or metric
deliver: storyboard, review sheets, master and variants, poster, captions, transcript, source
scope: new film, update, audit, or render only
destinations:
  - id: web-en
    dimensions: [1920, 1080]
    fps: 30
    language: en
    duration_seconds: 30
    audio: narration and music
    output: film-web-en.mp4
    captions: film-web-en.vtt
    transcript: transcript-en.txt
    mastering: destination requirement or owner decision
claims:
  - id: c1
    statement: illustrative claim to replace before production
    source: exact source revision and locator
    status: confirmed, contradicted, not found, or illustrative
assets:
  - id: a1
    role: evidence, mechanism, analogy, decoration, or orientation
    origin: owner and exact source
    rights: permission, license, required credit and limitations
    identity: digest or pinned version
    generator: for generated assets, revision, weight variant, seed, or none
    required: true
scenes:
  - id: s1
    purpose: what changes in the viewer's understanding
    interval_seconds: [0, 5]
    method: capture, coded graphics, character, footage, or generated plate
    claims: [c1]
    assets: [a1]
    entry_state: what is on screen as the shot begins
    action_and_payoff: visible mechanism and its result
    exit_state: what is on screen as the shot hands off
    cue: named cue from the audio or timeline owner
    readable_hold: measured interval with final text present
    handoff: identity and space of the carried subject, or a deliberate cut
    inspection_times: opening, action, payoff and consecutive boundary frames
    failure_signal: what a reviewer would see or hear if this is wrong
render:
  owner: existing renderer and entry command
  versions: renderer, browser, encoder and lockfile identity
  inputs: data, fonts, media, seeds and digests
  draft: lower resolution or quality, same timing and fps
  final: required settings and destination profile
  cache_identity: source, assets, settings and runtime identity
checks:
  - output: film-web-en.mp4
    source_revision: exact source and input identity for this output
    source: NOT RUN
    captures_and_seeks: NOT RUN
    reference_conformance: NOT RUN
    playback: NOT RUN
    listening: NOT RUN
    encoded_metadata: NOT RUN
    decoded_output: NOT RUN
    captions_and_locale: NOT RUN
    evidence: paths, sampled intervals, actual commands and results
blockers: missing input, affected deliverable, owner and next action
```

Use PASS, FAIL, UNAVAILABLE, NOT RUN or N/A per check with its scope and evidence. A successful
encode does not fill the playback or listening fields. A hash identifies a file; it does not
prove that the story, rights, timing or picture is correct.
