# Narration and sound

Read this when the brief requests narration or other audio. Reuse the recorded voice/provider
decision within its scope. A new person's recording or synthetic likeness needs the relevant
rights and consent; another application's voice decision does not supply them. Keep secrets
and private provider identifiers out of the brief and tracked artifacts.

## Write the script

Write and check the script before any take is generated. It covers spoken lines and the
on-screen text that goes with them. Claims in a named person's voice, including their habits
and their account of their own work, need that person's approval of the exact words.

For a new or rewritten script, draft two or three scripts independently from one fact sheet;
no drafter sees another's draft. An editor who wrote none of them merges the strongest lines
into one script. Lock it only after every claim passes the claim check in
`references/production.md`; a line changed after the lock goes back through that check.
Apply these checks to the merged script:

1. **One thing to remember.** Write it as one sentence a viewer could repeat to someone else.
   Keep a line only when it serves that sentence.
2. **Open on the claim or a concrete case.** The first line says what is at stake, or shows
   the case where it matters. A warm-up about the author's habits, a "here is" run-up, or a
   restated title delays the film.
3. **Plain words for the actual audience.** Use the words that audience already uses. A
   technical term earns its place when the picture shows what it names at that moment.
   Tool, service, and version names go in the credits unless the film is about them.
4. **One qualifier where the evidence needs it.** Scope a claim once, precisely ("one reason",
   "looks like"), and keep the rest of the scoping in the brief. Avoid chains of repeated
   hedges ("usually" line after line) or defensive filler ("real", "honestly").
5. **Say what is shown; show what is said.** Make a said/shown table: each line, and what is
   on screen while it plays. Move or cut a line with nothing to show, and show each result
   while its line plays (especially the closing claim). On-screen text anchors the line; it
   does not repeat it word for word.
6. **Budget the pace.** Measure the voice's actual rate (synthetic voices often run near
   2.2 words/s, ~19 words per 9 s). Keep spoken sentences under ~14 words and vary length.
   When lines overrun, cut words instead of speeding up the voice or stretching motion.
7. **Reveal on the spoken word.** Each part appears when the narration names it, spread across
   the scene (`references/timing.md` holds reading windows and eases).
8. **Read it aloud** at normal speed with a timer. Fix every stumble and second-breath line.
   Keep display spelling separate from phonetic respellings needed for pronunciation.
9. **Check the prose.** Run the catalog's `deslop` skill, then review against `humanizer`
   ([blader/humanizer](https://github.com/blader/humanizer), if installed separately) because
   short spoken lines can pass scanners and still sound generated. If either skill is
   unavailable, report that check as unrun.

Done when the one-sentence takeaway is recorded, every said/shown row is matched or
deliberately cut, the read-aloud time fits the budget, prose checks are resolved, and the
script is locked after the claim check.

## Produce and time the audio

1. **Caption rules and grouping.**
   - Keep captions faithful to speech; include meaningful non-speech sound and identify
     speakers when unclear from picture, omitting incidental noise.
   - Group words 3 to 5 at a time for conversational narration, breaking at a sentence end or
     ~150 ms pause; hold each group at least 0.7 s at <= 17 characters/s, avoiding 1 to 3
     frame gaps and trailing-silence words.
   - With multiple synthetic voices, confirm every line carries one valid speaker before
     generating takes.

2. **Regeneration, timing, and word alignment.**
   - Read the manifest's generation unit (scene clip or continuous track). Regenerate that
     whole unit when text changes, updating audio, word timings, captions, scene offsets,
     cues, and fallback durations together.
   - Check predicted or chunk-relative synthesizer word timings against the final-mix
     transcript (listening step below) before captions rely on them.
   - Compare forced alignment against full spoken text; review interpolated intervals for
     numbers, currency, or special tokens against audio, keeping written caption text even if
     alignment used spoken form. Fall back to checked phrase-level cues (with word highlights
     disabled) when word timing cannot resolve.
   - Land each on-screen beat by looking up the exact spoken word rather than spacing beats
     evenly, so re-voicing fails loudly instead of drifting from speech.
   - Keep paid takes outside the worktree, listen to every re-voiced line, preserve the
     source manifest identity, and verify track-to-scene time conversion. Missing or
     mismatched required narration blocks narrated acceptance.
   - Apply trim and speed once on the shared timing parent, keeping captions relative to
     source media.

3. **Loudness, mix, sound effects, and music.**
   - Follow the owner's loudness, mastering, and disclosure rules (or record the destination's
     target; web/streaming commonly normalize near -14 to -16 LUFS integrated, <= -1 dBTP).
   - Measure the final mix (such as two-pass EBU R128), then re-measure the encoded
     deliverable because lossy encoders (AAC) can raise true peak by several dB; leave
     headroom or re-limit and re-measure.
   - Installations, hosted/paid fallbacks, and provider spend require authority for that
     target and scope.
   - Duck music ~9 to 12 dB under speech and confirm in the final-mix transcript. Give every
     SFX a visible cause from the same cue, peaking at or 1 frame after contact (~3 to 6 dB
     above bed), rotating takes on repeated sounds.
   - For music-led edits, derive the beat/phrase grid from the actual track or score in one
     shared cue timeline, keeping readable holds and deliberate silence without forcing
     narration onto beats.
   - For browser-synthesized audio, render an offline buffer or stem with explicit duration,
     sample rate, and cue origin, await readiness, include it in the encode, and check start
     and end cues for drift. Live transport playback alone does not prove audio in captures.

4. **Listen and transcribe the final mix.**
   - Listen to regenerated takes and the changed film sequence for pronunciation, level,
     sentence pace, pauses/noise floor, cut-off endings, sync, and caption agreement.
   - Where speech-to-text is available, transcribe the final mix (not the clean take) and
     compare against captions, names, and numbers first.
   - Trim dense or repeated copy before altering voice speed; any audio retiming also
     changes word timings. Distinguish generated, reused, transcribed, and listened-to takes
     in the report.

A placeholder or silent fallback can support local picture work, not complete a narrated
film or establish listening quality. Keep the source and successful captures, and name
missing audio work when provider access or an approved voice is unavailable.

## Alignment evidence

The timing-coverage refinement is original synthesis, observed October 27, 2026. WhisperX
[alignment.py](https://github.com/m-bain/whisperX/blob/5d3678b8535698a2826a5db9eb3e4105aef85dd9/whisperx/alignment.py)
(BSD-2-Clause) can return a segment with no timed words and interpolate missing word times;
its README documents dictionary and language limits. PyTorch's independent
[CTC alignment tutorial](https://docs.pytorch.org/audio/stable/tutorials/ctc_forced_alignment_api_tutorial.html)
shows that vocabulary and transcript coverage affect alignment. This is mechanism evidence,
not a measured caption accuracy guarantee. Recheck on aligner, language, or take changes.
