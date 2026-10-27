# Material and mechanism shots

Read when a film calls for tactile materials, procedural shaders, deforming geometry,
cutaways, or a 3D product close-up. Keep the existing renderer, scene contract, and export
pipeline. This reference guides shot construction; it supplies no renderer, physics engine,
material library, or proven quality level.

## Choose the shot's job

Write what the viewer should understand before choosing an effect. A material close-up can
establish the identity of a physical product. A cutaway can explain a mechanism. A staged
separation can illustrate a handoff. A decorative finish cannot establish product behavior,
security, speed, or a measured outcome. Keep real UI and data as sourced evidence; label
physical metaphors as illustrative where confusion is likely.

Use a shared visual grammar across a series: scale, lighting direction, camera perspective,
material roles, type, and sound. Vary the meaningful action by film. Metallic foil suits some
subjects; matte paper, glass, or simple diagram geometry may explain others better. Keep
one focal action legible at the intended viewing size. Captions and important UI text should
remain crisp and readable outside highly reflective, moving surfaces.

**Ready:** each proposed 3D shot has a communication purpose and a source or declared metaphor.

## Qualify an imported mesh

For an image-generated or downloaded prop, distinguish geometry, textures, rig and animation.
A successful mesh export establishes only the stages that ran. Save the selected asset and
its generator/weight revision and input identity in the existing asset ledger. Apply the
[production rights checks](production.md#establish-the-production-contract) before use.

Import it into the target scene and check scale, orientation, origin, silhouette, normals,
material and texture bindings, and geometry cost under the shot's actual camera and light.
For a deforming subject, test the required rig and pose range; a rigid prop needs no rig.
Render the shortest motion that exposes the needed rotation, contact or deformation before
reusing the asset across a series. Keep any repair and the accepted asset with the scene.

**Ready:** the imported asset supports its assigned shot, including required motion and the
existing measured render budget. Geometry generation alone does not establish that result.

## Convert interaction into authored time

Replace live pointer input with a recorded or authored path in scene time. Name contact,
load, release, recoil, and settle cues and derive camera, geometry, masks, and sound from
those cues. Trigger a simulated release at an explicit timeline event. Never let a browser
wall clock or the order of render-worker visits decide when the object breaks.

Prefer an analytic deformation or keyed pose when it provides the requested visible behavior.
For history-dependent motion, follow [seekable simulations](simulations.md). A deforming mesh's
checkpoint must also preserve its topology, active constraints and break events; positions
alone cannot reconstruct a tear. A texture-only wipe cannot stand in for physical separation.
Keep shadow deformation and cutouts consistent with the beauty pass, and match color management
across composited layers.

For procedural sound, follow [narration and sound](narration.md#produce-and-time-the-audio).
Keep contact, release and settle cues on the same timeline as the encoded audio.

**Ready:** repeated and out-of-order requests produce the same intended shot state and cues;
the encoded audio path is explicit.

## Prove a representative moving shot

Apply the existing production brief and difficult-shot gate. Make a style frame, then render
a short action at the final aspect ratio, fps, and a representative delivery resolution.
Inspect contact, maximum deformation, separation, payoff, and the transition into the next
scene. Check silhouette, occlusion, stable shadows, material response, readable holds, and
whether sound reinforces the picture without masking speech.

Fine glitter, guilloche, dot grids, and thin fibers can shimmer, alias, or disappear after
encoding and platform downscaling. Inspect consecutive frames and the encoded clip at actual
viewing size. Reduce spatial frequency or specular contrast before adding more samples.
Test motion blur and temporal samples with seekable state; they evaluate intermediate times.
Do not make the production export depend on live diagnostic overlays.

Measure final-profile render cost on this shot before committing the series to the effect.
Keep the successful clip as a visual reference with its source and settings. If the effect
misses the deadline or readability budget, use a simpler authored version with the same
meaning and check it again. A software-rendered export can behave differently from the
interactive GPU preview; confirm the actual export environment.

**Ready:** the encoded moving shot meets the brief and fits the measured render budget.

## Use near a release

For a series releasing soon, start with one representative shot in the existing project.
Choose the highest-value uncertainty and prove it before spreading the treatment. Reuse the
validated lighting/material setup where it fits; avoid a pipeline migration for an accent.
Keep each film's evidence, story, and UI demonstrations intact. Add a second advanced effect
only when it contributes a distinct idea and the delivery budget supports it.

Deliver the source, reference frames, encoded test, measured cost, and the fallback with the
normal film handoff. Professional acceptance comes from coherent art direction, truthful
content, clean joins, readable type, stable encoding, and checked sound. An engine name,
shader count, or unreviewed still cannot establish that outcome.

## Sources and refresh

Original synthesis prompted by the supplied ticket brief and the user's near-term film-series
request, October 25, 2026. No source prompt, shader, rig, or media copied. The specific planned
film briefs and runtime remain uninspected until identified.

- [Remotion flickering](https://www.remotion.dev/docs/flickering), Multi-threading issue and
  Why Remotion works this way; [random](https://www.remotion.dev/docs/random), deterministic
  seed and multi-thread discussion. Living docs observed October 25, 2026; reuse rights
  not established. These corroborate frame-order independence, not a mandatory renderer.
- [OfflineAudioContext](https://developer.mozilla.org/en-US/docs/Web/API/OfflineAudioContext),
  MDN contributors, definition and startRendering; living page observed October 25, 2026.
  Documents offline buffer generation; it does not supply a film encoder or timeline mixer.
- [XPBD](https://matthias-research.github.io/pages/publications/XPBD.pdf), Macklin, Müller,
  Chentanez, 2016, Introduction and §2, supports fixed simulation assumptions. Baking,
  checkpoint contents, and shot gating above are our engineering synthesis.
- Three.js [shadow materials](https://threejs.org/docs/pages/Object3D.html) and
  [color management](https://threejs.org/manual/pages/color-management.html), living pages
  observed October 25, 2026. Check the installed version before implementation.

Recheck when the destination's renderer, sampling, solver, aspect ratio, codec, or delivery
platform changes. No film render, listening pass, or paired skill evaluation was run here.

## Imported-asset evidence

The imported-mesh checks are original synthesis, observed October 27, 2026. No upstream
code, prompt, mesh or media is copied. Hunyuan3D-2's
[minimal example](https://github.com/Tencent-Hunyuan/Hunyuan3D-2/blob/f8db63096c8282cb27354314d896feba5ba6ff8a/minimal_demo.py)
creates shape, then texture, then exports GLB; it does not demonstrate a rig or an animated
shot. Its custom Tencent community license and individual file notices need review for the
selected use. The independent Khronos
[glTF schema](https://raw.githubusercontent.com/KhronosGroup/glTF/main/specification/2.0/schema/glTF.schema.json)
separates meshes, materials, skins and animations. It corroborates those distinct components,
not the quality of a generated asset. Living schema, redistribution rights not assessed.
Recheck on generator, format, importer or shot changes. No mesh generation, scene import or
paired skill/control evaluation was run for this refinement.
