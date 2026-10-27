# Seekable simulations

Read this when a film uses physics, particles, accumulated drawing or another effect whose
state depends on earlier updates. A seeded initial state alone does not make it seekable.
Reuse the project's simulation and renderer. Drive the effect from film time during export.

1. Record the initial state, seed, ordered inputs, engine version, step size and scene-time
   origin. Advance with fixed simulation steps independent of display refresh and render
   speed. Record how output times map to simulation steps, including any interpolation.
2. Prefer the existing time-evaluable implementation. Otherwise replay fixed steps from the
   initial state to the requested time. Reuse baked states or complete checkpoints when the
   measured replay cost warrants them; replay the same ordered steps after a checkpoint.
   A checkpoint must include solver, random-generator and effect history needed to resume;
   visible positions alone may be insufficient. Bind baked states and checkpoints to the
   [source and cache identity](production.md#preserve-reproducible-revisions).
3. Give render workers independent state. Repeated requests for one time must not advance it,
   and backward seeks must restore or reconstruct it. Keep collision callbacks from emitting
   duplicate external actions or audio during replay; record collision cues in simulation
   time and consume them through the film's existing cue timeline.
4. Compare a frame reached sequentially, directly from a fresh instance, after a later frame,
   and, for a multi-worker render, on another worker. Inspect a collision or trail boundary and the final state,
   not only an empty opening. Check the encoded section at the intended fps. Report the
   tested runtime and tolerance; engine determinism does not establish identical GPU pixels
   across machines.

Done when the same requested time produces the intended state under those seek histories.
When collision sound is in scope, verify it agrees with the encoded picture. If replay is too costly,
measure a representative section and use the project's bake or checkpoint path before
scaling the render. This procedure does not supply a physics engine or a baking adapter.
