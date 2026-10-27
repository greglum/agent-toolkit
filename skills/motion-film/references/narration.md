# Narration and sound

Read this when the brief requests narration or other audio. Reuse the recorded voice/provider
decision within its scope. A new person's recording or synthetic likeness needs the relevant
rights and consent; another application's voice decision does not supply them. Keep secrets
and private provider identifiers out of the brief and tracked artifacts.

## Write the script

Write and check the script before any take is generated. It covers spoken lines and the
on-screen text that goes with them. Claims in a named person's voice, including their habits
and their account of their own work, need that person's approval of the exact words.

For a new or rewritten script, draft two or three scripts independently from one fact sheet; no drafter
sees another's draft. An editor who wrote none of them merges the strongest lines into one
script. Lock it only after every claim passes the
[claim check](production.md#check-claims-against-the-record); a line changed after the
lock goes back through that check. The steps below apply to the merged script.

1. **One thing to remember.** Write it as one sentence a viewer could repeat to someone else.
   Keep a line only when it serves that sentence.
2. **Open on the claim or a concrete case.** The first line says what is at stake, or shows
   the case where it matters. A warm-up about the author's habits, a "here is" run-up, or a
   restated title delays the film. The first few seconds alone should tell a viewer what the
   film is about.
3. **Plain words for the actual audience.** Use the words that audience already uses. A
   technical term earns its place when the picture shows what it names at that moment.
   Tool, service, and version names go in the credits unless the film is about them.
4. **One qualifier where the evidence needs it.** Scope a claim once, precisely ("one reason",
   "looks like"), and keep the rest of the scoping in the brief. A run of hedges such as
   "usually" line after line makes the narrator sound unsure and adds no accuracy. Words that
   answer an objection nobody raised, such as "real" or "honestly", read as defensive.
5. **Say what is shown; show what is said.** Make a said/shown table: each line, and what is on
   screen while it plays. Move or cut a line that has nothing to show, and name anything shown
   that matters. Show a result while its line plays, so the picture proves it.
   The closing claim needs its evidence on screen when it is spoken. On-screen text anchors
   the line; it does not repeat it word for word.
6. **Budget the pace.** Measure the voice's actual rate. Synthetic voices often run about 2.2
   words a second, so a 9 s scene holds about 19 words. Keep spoken sentences under about 14
   words, and vary their length: a run of same-length short lines sounds like a recited list.
   When lines overrun, cut words; keep the voice speed and the motion timing.
7. **Reveal on the spoken word.** Each part appears when the narration names it, spread across
   the scene. A scene whose content is all on screen in its first quarter reads as a slide.
   [Timing defaults](timing.md) hold the reading windows and eases.
8. **Read it aloud** at normal speed, start to finish, with a timer. Fix every stumble and
   every line that needs a second breath. Keep display text and spoken text as two layers when
   a word needs a respelling to be pronounced; captions and the screen keep the real spelling.
9. **Check the prose.** Run the catalog's `deslop` skill, then read the script against the
   `humanizer` skill's patterns ([blader/humanizer](https://github.com/blader/humanizer), installed separately).
   Short spoken lines can pass the scanners and still sound generated, so the judgment pass
   is required. If either skill is unavailable, report that check as unrun.

Done when the one-sentence takeaway is recorded, every said/shown row is matched or
deliberately cut, the read-aloud time fits the budget, the prose checks are resolved, and
the script is locked after the claim check.

## Produce and time the audio

1. Keep captions faithful to what is said. Include meaningful non-speech sound and identify
   speakers when the picture does not make them clear. Omit incidental sound that adds no
   meaning. Fix pronunciation through the existing generation workflow. Group caption words
   3 to 5 at a time for conversational narration, break at a sentence end or a pause of about
   150 ms, show one group at a time for at least 0.7 s, and keep reading speed at or under
   about 17 characters a second. Avoid gaps of one to three frames between groups. Drop
   transcriber words that fall in trailing silence. With two or more synthetic voices, check
   that every line carries exactly one valid speaker before any take is generated.
2. Read the manifest's generation unit: a scene clip or a continuous film track. Regenerate
   that whole unit when its text changes, then update its audio, word timings, captions,
   scene offsets, cues, and fallback durations together. Use actual duration and word timings
   to align scene action and captions. Word timings a synthesizer predicts can be estimates,
   relative to a chunk, or missing for some languages: rebase them onto the track and check
   them against the final-mix transcript (step 4) before captions rely on them. For forced
   alignment, compare the full spoken transcript with the timed tokens. Numbers, currency,
   unsupported characters or a failed segment can leave words untimed; some tools interpolate
   them from neighbors. Review those intervals against the recording, preserving the written
   caption text even if alignment needs a spoken-form transcript. Use a checked phrase-level
   cue when word timing cannot be resolved; keep word highlights disabled for that interval.
   Check cue occurrence, lead-in, complete sentence ending,
   and tail hold against the scene duration.
   Preserve the source manifest and its text/audio identity. A new picture, line, or take must
   not leave stale timing or speech behind. For a shared track, verify scene intervals and
   conversion between track time and scene time. Missing or mismatched required narration
   blocks narrated acceptance, even when the player can fall back to silence.
   Captions share one timing parent with their media: apply trim and speed once on that parent,
   and keep caption timestamps relative to the source media.
3. Use the owner's existing loudness, mastering, disclosure, and playback contracts. An embedded
   player follows its explicit audio-start policy. With no owner target, record the
   destination's: web and streaming commonly normalize near -14 to -16 LUFS integrated with
   true peak at or below -1 dBTP. Measure the final mix (for example, two-pass EBU R128
   analysis) rather than trusting the generator's level, then measure the encoded deliverable
   again: lossy encoders such as AAC can raise true peak by several dB. Leave headroom, or
   re-limit and re-measure. Installations, external generation (including a local tool's hosted or paid
   fallback), and provider spending need the authority for that target and scope.
   Narration sits on top: duck music about 9 to 12 dB under speech, then confirm with the
   final-mix transcript in step 4. Give every sound effect a visible cause on screen. Place
   it from the same named cue as the picture, with its measured peak at the contact frame or
   one frame after; a long whoosh starts earlier so its peak lands there. Keep hits about 3
   to 6 dB over the bed, and rotate two or three takes of a repeated sound.
   For music-led choreography, derive the beat and phrase grid from the actual track or the
   authored score. Store named visual and audio cues in the same timeline with explicit units
   and offsets. Preserve readable holds and deliberate silence. A musical grid does not
   require an effect on every beat, nor should narration be forced into that grid.
   For browser-synthesized sound, prepare an offline audio buffer or stem through the
   project's existing audio path, with explicit duration, sample rate and cue origin. Await
   required samples and rendering, then include that result in the encode. Live sound from
   a browser transport does not establish that frame captures contain audio. Compare a
   known cue near the start and end of the encoded section for missing sound or drift;
   preserve effect tails within the agreed duration.
4. Listen to regenerated takes and the changed film sequence. Check pronunciation, level,
   sentence-to-sentence pace, pauses and their noise floor, cut-off endings, audio/action
   synchronization, and caption agreement. Where speech-to-text is available, transcribe the
   final mix, not the clean take, and compare it with the captions, names and numbers first.
   Trim dense or repeated copy before changing voice
   speed; any audio retiming also changes its word timings. Distinguish generated, reused,
   transcribed, and listened-to takes in the report.

A placeholder or silent fallback can support local picture work. It cannot complete a
requested narrated film or establish listening quality. Keep the source and successful
captures, and identify the missing audio work when provider access or an approved voice is
unavailable.

## Alignment evidence

The timing-coverage refinement is original synthesis, observed October 27, 2026. WhisperX
[alignment.py](https://github.com/m-bain/whisperX/blob/5d3678b8535698a2826a5db9eb3e4105aef85dd9/whisperx/alignment.py)
(BSD-2-Clause) can return a segment with no timed words and interpolate missing word times;
its README documents dictionary and language limits. PyTorch's independent
[CTC alignment tutorial](https://docs.pytorch.org/audio/stable/tutorials/ctc_forced_alignment_api_tutorial.html),
Tokenize the transcript and Advanced handling of partial transcripts, shows that vocabulary
and transcript coverage affect alignment. This is mechanism evidence, not a measured caption
accuracy guarantee. Tutorial prose rights not assessed; no source text or code copied.
Recheck on aligner, language or take changes. Inference, listening and paired skill/control
evaluation were not run for this refinement.
