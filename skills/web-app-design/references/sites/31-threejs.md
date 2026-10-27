# 31. Three.js

**Observed:** 2026-10-05. **Research depth:** explicit search for `site:threejs.org documentation license`, official installation/responsive/cleanup/Shadertoy manuals, and first-party license. The homepage returned 503, but official manuals and repository text were accessible. No GPU rendering or app integration was tested.

## Purpose and fit

Three.js is an implementation resource for browser 3D experiences. The installation manual describes JavaScript modules and a canvas-oriented project with separately loaded textures, audio, and models. It supports npm/build-tool use and a CDN/import-map path, recommending the former for most users. Existing projects should retain their own build tool rather than adopt the tutorial's Vite setup wholesale. [Installation manual](https://threejs.org/manual/pages/installation.html)

For a working app, its strongest uses are spatial data, product configuration, scientific scenes, or manipulation of genuinely three-dimensional objects. For marketing, it can support an interactive product scene or a branded visual feature. These are design-fit judgments. Ordinary navigation, forms, and business tables rarely need a scene engine merely to look contemporary.

## Concrete implementation lessons

The responsive manual distinguishes CSS display size from the canvas drawing-buffer size and updates the camera's aspect ratio when necessary. It also explains how high pixel density increases drawing work. A future skill should treat responsive sizing as part of the scene's ownership, not solve it by scaling a fixed screenshot or assuming a desktop canvas will fit a phone. [Responsive design](https://threejs.org/manual/pages/responsive.html)

The cleanup manual states that resources such as textures, geometry, and materials need explicit disposal. Removing a mesh from the scene does not by itself free all associated GPU allocations. This matters for route changes, tab switching, and repeated model loads in a working app. Keep creation, resize handling, render scheduling, and teardown together in the responsible integration layer. [Cleanup manual](https://threejs.org/manual/pages/cleanup.html)

The Shadertoy manual demonstrates translating a shader into Three.js and discusses uniforms, texture inputs, and the difference between fullscreen fragment art and a normal scene. Shader snippets are a starting point requiring adaptation, not a drop-in React component. [Three.js and Shadertoy](https://threejs.org/manual/pages/shadertoy.html)

## Rights, dependencies, and access

The first-party license is MIT and requires copyright and permission notices in copies or substantial portions. That software license does not automatically cover every third-party model, photograph, texture, font, or shader used in a demo. Keep an asset-specific rights record. Public manuals and source were accessible without a paid subscription. [License](https://github.com/mrdoob/three.js/blob/dev/LICENSE)

Three.js adds a rendering runtime plus whatever loaders, controls, asset decoding, or React bindings the chosen scene needs. Only introduce those dependencies when the app's actual task justifies them. Match core/addon versions and check the project's current renderer/browser contract before adopting examples. [Installation and addons](https://threejs.org/manual/pages/installation.html)

## Use in the design skill

Require a clear reason for 3D and a usable HTML alternative for the surrounding task. Prototype one bounded scene, then measure the real application's loading and interaction behavior.

**Analytical checks:** keyboard access to meaningful actions, descriptive alternatives for visual data, touch controls, reduced motion, loading/error states, context loss, paused rendering offscreen, disposal, and performance on required devices. Recheck version compatibility, asset rights, browser capability, and actual frame/loading cost whenever the scene or dependency changes.
