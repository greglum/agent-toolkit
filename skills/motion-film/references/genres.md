# Genre-specific film direction

Read the relevant section when the brief calls for motion graphics, music-led typography,
character animation, recorded footage, or mixed media. These are branches of the same
production workflow, not universal style rules or new renderers.

## Use references as a visual grammar

Choose by communication task and brand fit. Describe composition, type hierarchy, material,
color roles, camera behavior, object continuity, texture and sound. Separate the style grammar
from the film's actual story, data and assets. Compare a few contrasting treatments for an open
brief; keep the existing treatment for a scoped update.

For a reusable style handoff, keep its visual rules separate from the example film's story,
shots and cue times. Record the base revision and intentional changes with a rendered example
and rebuildable source. Keep user variants outside an upstream library's update path; review
base changes before incorporating them. Prove reuse with different content through a short
moving section that exercises the style's defining treatment.

For a gallery case, inspect the original creator's sequence and available source alongside the
prompt. Record whether it is an original, remake, partial prompt, sampled stills or full moving
clip, and whether it mixes code with generated footage or audio. Nine sampled frames cannot
establish a continuous transition, accurate synchronization or a complete generation recipe.
Use the source's exact status instead of turning a curator's reconstruction into creator intent.

Test the chosen relationships with our own content, including its hardest text and handoff.
An asset must have a job in a shot, not merely appear in a mood board. Forced camera moves,
no-text rules, perpetual motion, exaggerated textures and a sound on every beat are genre
choices. Use them only when they make this film clearer.

For a painted or hand-drawn treatment, record which coordinate space owns each texture:
background paper, a moving subject's paint, or a screen overlay. Preserve that attachment
through subject and camera motion unless slipping texture is an intentional effect. Set a
texture-redraw cadence separately from the output fps. When the look uses held drawings,
derive each redraw from an explicit timeline exposure index and keep its variation fixed
through that exposure; keep the film and audio at the agreed delivery rate. Inspect a held
pose, a slow pan and an occlusion in encoded motion for unwanted texture swimming, flicker,
or lost silhouette. Keep captions and factual labels legible through the treatment.

## Music and kinetic typography

Treat lyrics, transcription, alignment and musical structure as different inputs. Preserve
the intended lyric text; an automatic transcript can confuse a sung word or invent speech in
an instrumental passage. Review uncertain alignment against the actual recording, including
repeated phrases, pickups, rests and phrase endings. Use the shared cue timeline in
[narration and sound](narration.md) for word highlights, beat accents, camera changes and
caption derivation. That workflow also owns mastering and listening.

For music-led cuts, distinguish detected beats from bar starts. Confirm the meter and first
downbeat against the recording before deriving bar accents. Taking every fourth detected
beat as a bar start assumes 4/4 meter and a grid beginning on a downbeat. Check pickups and
tempo or meter changes before reusing that grid across the track.

Use word or syllable timing only where it serves comprehension. Confirm the final glyph is
fully visible long enough to read before clearing a line. Reserve the entire shaped line's
space while revealing it; inspect the revealed glyphs, not just reported string bounds.
Keep typography variation subordinate to meaning. Do not stretch word timing to make a
fast-cut preset work. Captions or the transcript preserve the full accessible text even when
the picture deliberately abbreviates it.

Review sharp text and line art at final size, in motion and after encoding. Heavy texture,
grain, subframe blur and upscaling can harm type and inflate render cost. Keep detail such as
lyrics legible when motion-blurring the background. Measure any supersampling or parallel
rendering benefit on a representative shot rather than importing another machine's estimate.

Finish when the actual mix, cue sequence, word reveal and readable holds agree through the
encoded output.

## Character performance

Define a small model sheet: silhouette, proportions, face anchors, pose range, expression
meaning, contact points and relevant props. Reuse an existing rig before adding another.
Separate actor-local pose and expression from stage position and camera transforms so an
actor can be re-staged without deforming its face or losing a prop.

Write acting beats around intent, anticipation, action and response. A list of expressions
does not establish acting, anatomy, lip synchronization or continuity. Fix the random seed
and noise behavior for hand-drawn motion; deliberate line variation should not make eyes,
limbs or held objects detach. Key each actor's procedural variation by stable actor and part
identity, rather than draw order. Check that a second actor entering or leaving does not
change a held character's texture or expression unintentionally. Review blinks, gaze, silhouette,
occlusion and expression transitions between poses, not just the pose sheet.

Flow a pose through its keys on a monotone curve that never overshoots a key; easing in and
out of every key stops the character at each one. While a character is on screen, give it a
moving hold such as slow breathing. Make follow-through a delay: a child part reads its
parent 60 to 150 ms earlier at 0.3 to 0.6 of its strength. Keep volume when squashing, scale
a contact shadow with height, bring props in already moving, and give a blink enough frames
to read (about 110 ms to close and 190 ms to open). These numbers are defaults from a public
skill, not measurements made here.

For dialogue, check phoneme or mouth cues against the actual authorized take. Generic mouth
cycling is a stylized choice, not accurate lip sync. For contact, inspect planted feet,
hand/prop attachment and object identity before, during and after the action. Preserve these
constraints when the camera or parent scale changes. Use a simple cut or an occlusion where
a pose interpolation cannot preserve the silhouette.

Done when the character's intent reads in motion, identity stays stable, and the shot's
contacts and speech have been checked. Keep unverified lip sync or anatomy explicit.

## Recorded-footage edits

Keep originals intact. Record cut decisions in the existing timeline or edit list: source
identity, selected audio track, source in/out, output placement, and any speed change.
For speech-led edits, use a compact time-labelled transcript to compare takes, retaining raw
word timings, speakers and meaningful sound events for cut decisions. See the
[speech-editing sources](sources-editing.md) for this refinement. A phrase summary loses
interior word boundaries. First assemble the main speech cut, selecting the better complete
take and removing only repetitions, fillers and pauses that add no meaning. Check the retained
sentences in context before building an intro from them; moving a line must preserve its
meaning. Add B-roll, reframing and other polish after those cut decisions settle. Check
uncertain edges against the recording and waveform; preserve
breaths, reactions and complete words rather than trusting a fixed padding value.

Keep source time and output time distinct. For a unit-speed cut, a retained source cue lands
at `output_start + cue_source_time - source_in`; speed changes and overlaps need the timeline's
actual mapping. Derive captions and overlay cues from that mapping once, then check the
encoded joins against the intended placement. Reuse [narration checks](narration.md#produce-and-time-the-audio)
for caption accuracy and listening. Finish when every retained range resolves to its source
and track, and each changed join and its cues agrees with the encoded output.

## Mixed footage and generated plates

Use a shot list with subject continuity, direction of travel, camera, light, framing and
incoming/outgoing poses. Check source resolution, actual duration, frame rate, color and
available handles before editorial assembly. Record the selected take and its origin.
Reconcile aspect ratio and motion across adjacent shots; a successful isolated generation
does not prove the cut works.

Keep product evidence and factual labels in a layer that remains source-grounded and editable.
Compare representative adjacent moving shots before generating the remaining sequence.
Complete only the generation authorized for the selected provider, media and spending scope.
Do not ship an uncleared reference clip as final media.
