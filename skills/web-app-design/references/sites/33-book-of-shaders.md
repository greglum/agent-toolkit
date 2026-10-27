# 33. The Book of Shaders

**Observed:** 2026-10-05. **Research depth:** targeted search for official chapters/about/license, homepage table of contents, author introduction, running-shader chapter, examples gallery, and first-party repository. Public text was accessible. No shader was executed or reused.

## Purpose and audience

The Book of Shaders is a progressive learning resource by Patricio Gonzalez Vivo and Jen Lowe. It teaches fragment shaders through executable examples and small exercises. The introduction addresses creative coders, game developers, and engineers who already have programming experience plus basic linear algebra and trigonometry. It is useful for understanding an effect rather than asking an agent to imitate a mysterious snippet. [About the book](https://thebookofshaders.com/00/)

The published contents include shader basics, uniforms, shaping functions, color, shapes, matrices, patterns, randomness, noise, cellular noise, and fractional Brownian motion. Some later topics are listed without linked chapters, including image processing, simulations, and 3D techniques. Do not mistake the planned contents for a complete implementation reference. [Current table of contents](https://thebookofshaders.com/)

## Concrete design uses

For a branded web experience, study controlled color blending, restrained procedural texture, repeating geometry, or a subtle animated field. For graphics-heavy products, the exercises can build intuition about coordinate transforms and noise parameters that become real product controls. The examples gallery combines chapter examples with shaders contributed by readers, so provenance can vary across entries. [Examples gallery](https://thebookofshaders.com/examples/)

The running-shader chapter discusses different environments and ways to execute shader code. That makes this a good explanation resource when a team needs to understand why a fragment example requires a rendering host and uniforms. It does not supply a production-ready button, table, or accessible navigation system. An ordinary productivity app should improve its task structure, spacing, typography, and controls before using shader education as a design dependency. [Running your shader](https://thebookofshaders.com/04/)

## Access, integration, and rights

The observed book and examples were publicly readable without a paid course gate. Embedded examples depend on browser graphics capability; adopting their concepts still requires a suitable application renderer and lifecycle handling. No package installation, offline export, or external account setup was performed.

Both the homepage and first-party repository state copyright with all rights reserved. Free reading and public repository access do not establish a general commercial code or content license. Do not ingest the book wholesale into a skill, reproduce chapters, or copy an example without inspecting its exact notice or obtaining permission when needed. Independently contributed examples can require separate checks. [Homepage license section](https://thebookofshaders.com/), [first-party repository](https://github.com/patriciogonzalezvivo/thebookofshaders)

## Use in the design skill

Route here for learning and diagnosis of shader techniques. Ask the agent to explain the relevant principle in original language, keep the direct chapter link, and produce an original bounded implementation only when the requested design needs it. The deliverable should describe how parameters affect appearance and how the rest of the interface remains usable if graphics are unavailable.

**Analytical checks:** GPU load, high-density rendering, moving or flashing patterns, text contrast over graphics, reduced motion, touch input, render-loop cleanup, and context failure. A browser demonstration does not establish accessibility or device acceptance. Recheck current chapter availability, example authorship/license, rendering API compatibility, and measured app performance before borrowing implementation details.
