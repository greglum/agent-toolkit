# Tactile 3D surfaces

Read when a web brief calls for deformable objects, tearing, foil, embossing, or another
material interaction. Extend the app's existing scene and state owners. These are design
and implementation checks, not a bundled simulator or a measured material model.

## Turn the visual brief into invariants

Map each requested effect to its geometry, input, state transition, material cue, and visible
proof. Separate fixed requirements from tunable starting values. Resolve row/segment counts,
coordinate origin, units, seam position, and cut thresholds before constructing a mesh.
A highly specific prompt can still contain conflicting numbers.

Keep application success with the actual operation. A physical completion in a demo changes
only demo state; tearing, snapping, or a sound cannot verify payment, access, or server work.
Keep the useful DOM action available with keyboard, touch, reduced motion, or unavailable GPU.

**Ready:** every effect has an owner and an observable result, with numeric conflicts resolved.

## Prove topology before finishing the material

For breakable surfaces, inspect both the triangle index graph and constraint graph. A texture
hole changes visibility; it does not disconnect welded triangles or remove a spring.
Represent the two sides with independently movable boundary vertices and no triangles spanning
a severed region. Give each remaining cross-boundary constraint an explicit relationship to
the intact material it represents. Remove all affected structural, diagonal, and long-range
bending links when that material breaks. A column number alone can miss diagonal or multi-hop
bridges. After full separation, the pieces must have no remaining mechanical connection.

Use a plain material to inspect partial separation, endpoints, back face, and full release
before adding foil or particles. If a diagnostic lattice is requested, draw actual active
constraints and computed strain from the solver. Keep diagnostics separate from the final view.

Run simulation with a fixed timestep and bounded catch-up work, independent of display refresh.
Reset accumulated time after suspension. Specify iterations per simulation step, damping,
pinning, scale, and mass assumptions together. Treat stiffness constants as tuning for that
solver and resolution; they do not establish a paper weight or measured material response.
Use an existing solver when it fits; consider compliant constraints only when the required
stiffness behavior justifies their cost.

**Ready:** partial and full separation work in plain shading without hidden bridges or
refresh-rate-dependent behavior.

## Keep input, rendering, and feedback in agreement

Raycast against current geometry and bounds. Choose a drag plane or depth rule and convert
pointer targets into the solver's coordinates. Arbitrate flex, cut, pull, and camera gestures;
capture the active pointer and release on cancellation. Process the swept path between samples
so fast movement cannot skip a narrow cut target. Derive progress and one-time feedback from
committed break events; repeated input cannot break or announce the same link twice.

Update changed position buffers, normals, and bounds as needed. Keep back-face UV orientation
and normal direction coherent through flips. Use built-in physical materials for ordinary
iridescence when sufficient; preserve a specifically requested custom shader. Define each
packed texture channel and its sampling space. Keep non-color masks out of sRGB conversion,
and handle output color conversion in custom materials. Check emboss and fine glitter at the
actual pixel scale rather than only in a large still.

Keep the visible silhouette and shadow caster consistent. Shader-only deformation and alpha
cutouts need matching shadow-pass treatment; CPU-updated geometry alone does not solve custom
fragment discard. For WebGL directional/spot shadows, inspect customDepthMaterial; for point
lights, inspect customDistanceMaterial. Name an approximate contact shadow as an approximation.

Start or resume interactive audio from a user gesture. Provide mute and visual feedback, bound
voices and gain, and release owned nodes and GPU resources on teardown. Suspension must preserve
the operation's real state. Reuse the app's existing motion lifecycle for hide/restore behavior.

**Ready:** gesture, mesh, counter, sound, and shadow agree during interaction and after reset.

## Acceptance probes

Use the repository's existing browser rig and gates. Check the affected cases:

- Partial cut, both tear directions, fast drag, canceled drag, and full release.
- Reset during interaction and after release, with restored positions, previous positions,
  constraints, counters, and pending feedback; repeat without growing resource use.
- Front/back readability, moving edge and shadow, and close-up shading at delivery scale.
- Different refresh rates, narrow touch layout, keyboard path, muted audio, reduced motion,
  hide/restore, unsupported graphics, and context loss where the runtime supports recovery.

Record measured frame cost, browser/device, resolution, pixel ratio, solver settings, and
shadow settings. Vertex count alone is not a performance budget. Recheck typography and focus
outside the canvas with the normal DOM/accessibility checks. Report unrun probes separately.

## Evidence and refresh

Original synthesis from an unattributed user-supplied ticket prompt, reviewed October 25,
2026. Its reported success, code, demo, and reuse rights were not verified; no prompt copied.
Technical references, also observed October 25:

- [XPBD](https://matthias-research.github.io/pages/publications/XPBD.pdf), Macklin, Müller,
  Chentanez, 2016, Introduction and §2: timestep/iteration coupling. Paper rights remain with
  its authors/publisher; no implementation copied.
- [Fix Your Timestep](https://gafferongames.com/post/fix_your_timestep/), Glenn Fiedler,
  June 10, 2004, fixed-step accumulator and bounded catch-up discussion. Copyrighted article;
  method restated without code.
- Three.js [BufferGeometry](https://threejs.org/docs/pages/BufferGeometry.html),
  [Object3D shadow materials](https://threejs.org/docs/pages/Object3D.html),
  [physical materials](https://threejs.org/docs/pages/MeshPhysicalMaterial.html),
  [color management](https://threejs.org/manual/pages/color-management.html), and
  [cleanup](https://threejs.org/manual/pages/cleanup.html). Living docs; Context7 r186
  BufferAttribute/custom-geometry reference checked; MIT license at r186 inspected.
- MDN [pointer capture](https://developer.mozilla.org/en-US/docs/Web/API/Pointer_events),
  [audio policy](https://developer.mozilla.org/en-US/docs/Web/API/Web_Audio_API/Best_practices),
  and [WebGL budgets](https://developer.mozilla.org/en-US/docs/Web/API/WebGL_API/WebGL_best_practices).
  Living documentation used as references; no prose or code copied.

Recheck against the destination's installed Three.js version, renderer, shader pipeline,
input devices, or any changed material/tear requirement. No runtime benchmark is established.
