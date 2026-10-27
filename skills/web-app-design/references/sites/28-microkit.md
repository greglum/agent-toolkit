# 28. MicroKit

**Observed:** 2026-10-05. **Research depth:** explicit search for `site:microkit.co micro interactions license`, homepage FAQ, React/CSS catalogs, a complete number-field example, first-party repository, and license. Public source text was accessible. Live behavior and browser acceptance remain untested.

## What it offers

MicroKit supplies small interactions for frontend developers, with live previews and copyable code rather than a required component package. The observed catalog contained 49 interactions, organized by feedback, inputs, and navigation. It offers TypeScript/JavaScript and CSS/Tailwind variants. This suits refinement of a product's controls more directly than wholesale visual-system design. [Homepage and FAQ](https://microkit.co/), [full catalog](https://microkit.co/components)

The React catalog includes sliding tabs, a moving navigation indicator, expanding icon tabs, a nested menu, and a scrub number field. The CSS catalog emphasizes buttons, links, and focus states. Those categories help a future skill route by the interaction being improved. [React patterns](https://microkit.co/components/react), [CSS patterns](https://microkit.co/components/css)

## Concrete patterns and working method

The scrub field is particularly useful for creative tools or settings where users repeatedly tune a numeric value. The inspected implementation distinguishes click-to-type from dragging, clamps a bounded value, supports keyboard steps and modifier speeds, and gives Escape separate cancellation handling. It includes a reduced-motion rule for its boundary nudge. These are source observations, not proof that the control meets every accessibility requirement. [Number-field source](https://microkit.co/components/scrub-number-field)

For routine business apps, sliding active indicators and clear focus feedback are usually easier to justify than pointer-following glow. Expanding icon tabs need a stable accessible name and cannot make label discovery depend on hover. A showcase purchase button's simulated completion state must be replaced by actual pending, success, and failure states from the application. Marketing pages can use more expressive button treatments when the label and hit area remain stable. These are integration judgments based on the catalog, not conversion measurements.

## Dependencies and reuse

The FAQ says 26 observed interactions have no extra dependency, while 23 use `lucide-react`. Inspect each page's installation section rather than assuming those counts remain current. React state, refs, or handlers require a client boundary in Next.js App Router. Tailwind alternatives exist, but installing a second styling system is unnecessary when the app already owns equivalent CSS and tokens. [Installation guidance](https://microkit.co/)

The first-party repository has an MIT license with a copyright and permission-notice requirement. The homepage also acknowledges adaptations from publicly shared examples and Webflow exports, and invites attribution corrections. Keep provenance for adopted code and inspect any separately supplied assets. Public code and registry commands were observed; no package installation or paid purchase was performed. [Repository](https://github.com/henriquegpb/microkit), [license](https://github.com/henriquegpb/microkit/blob/main/LICENSE)

## Use in the design skill

Start with the existing app component. Read one fitting example, extract the state transition, and adapt its motion to the app's tokens and established primitive. Record why the interaction helps the task and which source was used.

**Analytical checks:** keyboard completion and cancellation, screen-reader labels, visible focus, pointer cancellation, touch scrolling, truthful asynchronous status, and reduced-motion behavior. Verify contrast and rendering in the target app. Recheck the per-component dependency list, registry contents, attribution, and license before each adoption.
