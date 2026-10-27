# Imported animation players and timelines

Read this when a film embeds an animation asset or timeline, such as Lottie or GSAP.
Keep live application motion with the application's owner. A browser animation playing
correctly does not establish that it can render arbitrary film frames.

1. Reuse the renderer's maintained integration for the installed versions before writing an
   adapter. Keep the film renderer in charge of time; pause an independently running player
   and disable autoplay. A wrapper that already maps time must not receive a second mapping.
2. Record the mapping from film time to the imported animation's local time: scene start,
   trim, rate, direction, selected segment and loop or end hold. Distinguish seconds,
   milliseconds and asset frames. Do not assume the asset fps equals the composition fps,
   or that a wrapper preserves the asset's original playback speed. Check the installed
   integration's semantics. Set the subframe policy deliberately where the player supports it.
3. Inspect the actual seek path's callback policy. Some seeks suppress callbacks; others
   replay them when jumping. A callback that once revealed a label or changed a scene must
   not be the only source of that visual state. Derive it from the requested time instead.
   Keep external effects, notifications and sound playback out of repeated capture seeks;
   placed audio belongs to the film's audio path.
4. Bind readiness to the imported data and its required fonts and images. A parsed animation
   or an event saying image loads finished can still contain a failed asset. Surface required
   asset failures and preserve the prior export. Dispose the player and its listeners when
   their owner leaves; use the renderer's existing readiness and cleanup mechanism.
5. Inspect a fresh seek into the middle before ordinary playback, then repeat that time after
   forward and backward seeks. Include a callback boundary, selected segment boundary, loop
   wrap or final hold when used. For differing frame rates, check a cue near the start and
   another near the end for speed drift. Verify the same content in the encoded result using
   [capture and export review](render-review.md).

Done when requested times produce the intended state independently of seek history, required
assets are present, and the requested export passes its checks. This is integration guidance,
not a bundled player, adapter, asset library or renderer.

## Sources and limits

Original guidance, observed October 26, 2026. Checked against Airbnb's
[AnimationItem](https://github.com/airbnb/lottie-web/blob/bede03d25d232826e0c9dca1733d542d8a7754fb/player/js/animation/AnimationItem.js)
and [README](https://github.com/airbnb/lottie-web/blob/bede03d25d232826e0c9dca1733d542d8a7754fb/README.md)
(MIT, lottie-web 5.13.0), HeyGen's
[GSAP frame adapter](https://github.com/heygen-com/hyperframes/blob/165744edc07447aea6f6f93aaeb48abc965e5212/packages/core/src/adapters/gsap.ts)
(Apache-2.0), and Remotion's
[Lottie integration](https://github.com/remotion-dev/remotion/blob/1c5244bde079a3e399e287f369e6fb807dbae598/packages/lottie/src/Lottie.tsx)
(Remotion License, not MIT). Independent
[GSAP seek documentation](https://gsap.com/docs/v3/GSAP/Timeline/seek%28%29/)
explains suppressed callbacks; Remotion's
[frame-order guidance](https://www.remotion.dev/docs/flickering) establishes the capture constraint.
Living docs have no verified redistribution grant here. No source text, code or assets copied.
Recheck on integration, player, timing, segment or asset changes. No runtime or paired
behavioral trial was run for this guidance.
