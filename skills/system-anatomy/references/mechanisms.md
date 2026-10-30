# Model a physical mechanism

Use this branch for moving physical parts and calculated physical readouts. Keep the main
skill's source, interaction and delivery checks. A cutaway alone does not require a solver.

## State the model's purpose

Distinguish illustrative movement, constrained kinematics and predictive simulation. A
kinematic model explains possible positions; it does not establish forces, temperature,
pressure, wear or real-world performance. Name the intended question and valid input range.
Keep fictional machines and assumed dimensions visibly labeled on the artifact.

Record each consequential parameter's value, unit, source locator and status: measured,
specified, estimated or illustrative. A photograph can guide shape without establishing
hidden dimensions. Record the equations and assumptions that connect input to output.
Give independent inputs and constraints explicitly; use one degree of freedom only when
the mechanism supports it. Keep visual separation and camera position outside the physical
model so inspecting a part cannot change a calculated result.

**Ready:** a reader can identify what the model explains, its assumptions and what it
cannot predict.

## Calculate before rendering

Keep pose calculations independent of drawing code. Return the coordinates and quantities
the drawing, readouts and schematic consume. Derive dependent dimensions once and round at
the display boundary. For example, a module-4 mm, 32-tooth pinion has a 64 mm pitch radius;
a half-turn rack travel is about 201.062 mm, not exactly 201 mm.

Check the equations against an independently calculated pose or known limiting case. For
links and joints, verify lengths, mating points and permitted motion across the input range,
including intermediate positions. State tolerances and units. A synchronized chart proves
agreement with its model, not agreement with a real machine. Physical prediction needs
reference measurements appropriate to its intended use, kept separate from code verification.
Surface an infeasible input instead of clamping geometry into an apparently valid pose.

If the model needs time integration, declare initial conditions and time-step limits. For requested
film delivery, pass the model/parameter revision, units, assumptions, assets and explicit-time
render interface to the available film workflow. Keep sound and encoding out of the model.
No film skill, deployment or auto-playing tour is a prerequisite for an interactive figure.

**Ready:** numerical checks hold across the declared range and every displayed quantity
has a derivation or an explicit illustrative label.

## Start from the bundled slider-crank

From the catalog root, build into a new destination:

```bash
node skills/system-anatomy/scripts/build-mechanism.mjs /tmp/slider-crank.html
```

Open that file directly in a browser. The builder refuses to replace an existing file.
It inlines the example's model, controls and styles. The page needs no server, dependency
install, remote font or runtime request. The bundle works when installed alone.

The example uses an ideal planar slider-crank with an illustrative 40 mm crank radius and
120 mm rod. A native angle control changes the pose and numerical readouts together. Part
selection highlights a component and explains its role. Reset restores the quarter-turn
pose. The initial drawing and equations remain useful with JavaScript disabled. The example
has no automatic motion or force model, needs no graphics acceleration and makes no
fabrication claim.

For crank radius r, rod length L and angle theta, the crank pin is
`(r cos(theta), r sin(theta))` and the slider coordinate is
`r cos(theta) + sqrt(L² - r² sin²(theta))`. The model uses the right-hand assembly branch
and requires `L > r > 0`, with angles from 0 to 360 degrees. At 0 and 180 degrees the
slider coordinates are 160 and 80 mm; at 90 degrees the coordinate is about 113.137 mm.
Displacement uses the 0-degree position as its origin.

The pure model lives in `scripts/slider-crank.mjs`; the fixed example shell and controls
live in `assets/slider-crank/`. Adapt those files to a concrete mechanism. The command
builds this illustrative example only; it supplies no general physics engine.
Use the destination project's existing renderer when it already meets the requested job.

**Done:** the delivered figure includes its model limits and parameter provenance; numerical
and interaction checks pass on the actual output; requested exports have their own evidence.

## Provenance

Original implementation of standard slider-crank geometry, with original code and prose.
[Teardown](https://github.com/elvarofficial/teardown/tree/e7e668cd44f48ba79a3c575e9f55c7e194d26eef),
MIT, observed October 30, 2026, supplied the capability comparison and shared-model example.
This bundle includes no upstream code, prompts, geometry, fonts or media. Independent checks drew on
[NASA's modeling definitions](https://public.ksc.nasa.gov/mns/ms-definitions/) and
[verification guidance](https://www.grc.nasa.gov/www/wind/valid/tutorial/verassess.html).
Living-page reuse rights remain unknown; this procedure uses original words.
Recheck when the mechanism, intended use, equations, runtime or source revision changes.
