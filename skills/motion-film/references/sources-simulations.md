# Simulation and synthesized-audio sources

[Seekable simulations](simulations.md) and the synthesized-audio export check in
[narration](narration.md) are original procedures informed by Liam Brummitt's Matter.js
[Runner](https://github.com/liabru/matter-js/blob/b8ee71cd7f9b49f53639ddaedd6254f1929bcbe5/src/core/Runner.js)
and [Engine](https://github.com/liabru/matter-js/blob/b8ee71cd7f9b49f53639ddaedd6254f1929bcbe5/src/core/Engine.js)
(MIT, September 30, 2026), and Yotam Mann's Tone.js
[offline renderer](https://github.com/Tonejs/Tone.js/blob/445b94d4c0ade2d5c2f60c60f3e48749eb5322d9/Tone/core/context/Offline.ts)
(MIT, October 25, 2026). License files checked at those commits; no upstream code or prose copied.
Independent corroboration: Remotion's [frame-order guidance](https://www.remotion.dev/docs/flickering),
Dimforge's [JavaScript determinism conditions](https://rapier.rs/docs/user_guides/javascript/determinism/),
and MDN contributors' [offline audio rendering](https://developer.mozilla.org/en-US/docs/Web/API/OfflineAudioContext/startRendering),
observed October 25, 2026. These are living pages; redistribution rights were not checked.
The replay/checkpoint and cue checks are local design conclusions, not a claim that Matter.js
supplies complete snapshots or that this skill bundles a simulation/audio renderer.
Recheck on engine, replay, frame sampling or audio export changes. Behavioral control runs
and media rendering were not performed.
