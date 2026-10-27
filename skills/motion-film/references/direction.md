# Direction and choreography

Read this for a new creative film, reference-led treatment, or changed scene choreography.
For render-only work, keep the existing direction. Put decisions in the current storyboard
or manifest rather than creating a second brief or motion system.

## Make the idea visible

State the one thing viewers should understand. Choose a visual action that demonstrates it:
a receipt separating by who ordered each item tells more than four cards beside a feature
name. For an explainer, show the mechanism or causal relationship. A metaphor can carry the
story when viewers still recognize the subject and outcome. Preserve truthful values, units,
relationships, and labels during intermediate frames as well as at the payoff. For a text
reveal of a fixed source amount, keep its currency and complete number together: typing
`USD 2,400` must not briefly present `USD 2` as the amount. Progressive prose and numeric
interpolation remain valid when their intermediate states truthfully convey the intended meaning.

For an open creative brief, compare a few materially different concepts before coding. A
narrow update can use its established concept. Choose by product specificity and comprehension,
not by the number of effects. Carry a subject, shape, direction, or meaningful color across
shots when it helps orientation; give a cut a reason when continuity would obscure the story.

Done when the chosen concept can be stated plainly and each scene visibly advances it.

## Study a reference

Give each reference one job: a card entrance, a transition, a cursor action, a title reveal.
A reference asked to supply a whole film yields a mood and no usable timing.

1. Sample the clip at 2 frames a second for an overview sheet. Then extract every frame
   around the key event, from a few frames before it starts until it settles. The overview
   finds the event; the consecutive frames show how it moves.
2. Write a reference spec beside the storyboard. For the key event, record timestamps and
   frame numbers, subject bounds, direction of travel, duration, scale and opacity change,
   any overshoot, entry order of the parts, readable hold, the handoff, and any sound cue.
   Measure small motion as a number: track the subject's edges in every frame at the source
   frame rate, and record amplitude as a percent of its size plus the period. Sample colors
   from pixels.
3. Label every value **measured** (read from frames), **estimated** (inferred, such as a
   curve), or **proposed** (our choice for this film). A proposed value never passes as
   measured. Where the spec has no measured value, use [timing defaults](timing.md) and say so.
4. Take the grammar, never the subjects or copy. The film keeps its own story, brand, assets,
   and words; the reference lends composition, rhythm, and motion relationships. See
   [references as visual grammar](genres.md#use-references-as-a-visual-grammar).

Read the creator's prompt and actual source when available; missing assets, context, and
iteration history make a gallery prompt an incomplete reproduction recipe.

Name which relationships the film will retain and how they fit its own brand and content.
Use [Prompt Motion](https://prompt-motion.com/) or [Oneshotted](https://oneshotted.io/) for
prompt/result discovery, [Cinetic](https://github.com/Leonxlnx/cinetic) for concept and cue
organization, and [product-film](https://github.com/Rieranthony/product-film-skill) for
product-led discovery. Their default engines, taste bans, timing grids, interview gates, and
render presets are optional source choices. Inspect licenses before reusing code or media.

Done when each reference has one named job and a spec with labeled values, and the film's
own scene contract says which of those values it adopts.

## Choreograph the handoff

Use the existing scene contract to name the subject, camera, text, and outgoing layer at each
handoff. Set eases, exits, stagger, and moving cuts from [timing defaults](timing.md) unless
the owner's motion tokens or a measured reference set them. A shared object needs identity,
mapped bounds, transform origin, and compatible silhouette.
Match the camera's coordinate space and motion direction on both sides. Where
shapes cannot morph legibly, use a deliberate cut, mask, or occlusion instead of forcing
unrelated path points to interpolate.

Overlap entry and exit when it preserves continuity, while keeping one readable focal point.
Lay out progressive text in its final slots so already visible words do not recenter. Preserve
glyph shaping, reading order, and counters for the actual language; inspect intermediate
reveals that could clip glyphs or briefly imply another word. Check the largest motion extent
for collisions and the camera endpoint for clipping. Compare a representative style frame and
short moving draft before spending on full-resolution or subframe rendering.

For multiple aspect ratios, recompose subject, text, and safe areas from the same content and
timeline. A crop is acceptable only when the actual variant remains complete and readable.
For a loop, design the return path as part of the action. Match position, direction, speed,
layer visibility, and applicable audio across the seam; endpoint similarity alone can hide
a pause or reversal. Sample the cycle without duplicating its endpoint frame as an extra hold.

Done when the handoffs, readable intervals, and requested variants work in moving review.
Use [capture and export review](render-review.md) for evidence and encoded-output checks.
