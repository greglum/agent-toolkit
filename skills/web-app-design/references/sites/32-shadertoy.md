# 32. Shadertoy

**Observed:** 2026-10-05. **Research depth:** explicit searches including `site:shadertoy.com terms license shaders`; attempted homepage, how-to, terms, and representative shader pages; inspected indexed first-party shader text and the official Three.js integration manual. Direct Shadertoy fetches returned 402. That fetch status does not prove an actual payment requirement. Current terms and live previews were not verified.

## Purpose and available evidence

Shadertoy is a browser shader editor and community gallery for procedural graphics. Indexed shader pages expose GLSL help and inputs such as viewport resolution, elapsed time, mouse state, and texture channels. Their examples are fragment programs rather than complete accessible UI components. The site's own text was available through search results, even though direct pages could not be inspected fully. [Representative first-party shader page](https://www.shadertoy.com/view/MsdBzX)

The official Three.js manual explains how to adapt Shadertoy output into a Three.js shader, including its entry point, uniforms, and texture inputs. This is useful primary integration guidance from the runtime maintainer. It also shows why copying shader text into an unrelated renderer without handling the host contract is insufficient. [Three.js integration manual](https://threejs.org/manual/pages/shadertoy.html)

## Patterns and best-fit use

Use the gallery to understand procedural color, noise, raymarching, fluid-like imagery, lighting, and animated backgrounds. A future design pass can borrow the visual principle, then implement an original effect appropriate to its own layout and performance budget. The useful outcome might be a static asset or a subtle canvas accent rather than a continuously rendering full-screen scene.

For working apps, shaders are most defensible when the product needs visual simulation, spatial exploration, or graphics authoring. A marketing hero can justify decorative motion if content remains readable and the page still works without the effect. These are analytical recommendations; this research did not measure user outcomes, motion quality, or rendering cost on any shader.

## Reuse and integration constraints

Shader authors can specify individual rights. This research could not confirm the site's current default license because the terms page was inaccessible. Search surfaced noncommercial-license warnings, and the Three.js manual contains a sample with a noncommercial attribution/share-alike notice. That sample does not prove a blanket rule for today's entire gallery. Treat commercial reuse as unresolved until the exact shader, author notice, included textures, and current terms have been inspected. [Terms endpoint, inaccessible in this run](https://www.shadertoy.com/terms), [sample-specific notice](https://threejs.org/manual/pages/shadertoy.html)

Embedding a shader can require uniform updates, input assets, multiple passes, a render loop, and a compatible GPU API. Public viewing and reusable code rights are separate questions. Login, API availability, export features, and paid access were not verified. Do not add an account or bypass an access challenge as part of ordinary inspiration gathering.

## Use in the design skill

Record a reference URL and explain the effect in original language. Choose original implementation or clearly permitted source; never assume public visibility supplies permission.

**Analytical checks:** GPU load, high-density canvas cost, mobile capability, flashing/motion, readable overlays, offscreen rendering, context failure, and a static fallback. Keep meaningful labels and controls in accessible DOM. Recheck site access, current terms, item-specific rights, texture permissions, renderer compatibility, and the actual target-device cost before adoption.
