# Fallback defaults

Use these only when the project has no token for the decision. They are starting points, not
product policy. Report each one you use as a choice, and prefer adding it to the project's
token file over hard-coding it in a component.

## Duration

| Element | Band |
| --- | --- |
| Press feedback | 100 to 160 ms |
| Tooltip, small popover | 125 to 200 ms |
| Menu, select, dropdown | 150 to 250 ms |
| Dialog, sheet, drawer | 200 to 400 ms; up to 500 ms for large travel |
| Toast | 200 to 400 ms |
| Explanatory or marketing sequence | Longer when the sequence is the content |

Interface responses stay under about 300 ms. A shorter dropdown feels faster at the same
work. After the first tooltip in a group opens, open its neighbors with no delay and no
entrance.

## Easing

| Role | Curve |
| --- | --- |
| Enter, exit, respond to input | Strong decelerate: `cubic-bezier(0.23, 1, 0.32, 1)` |
| Move or morph on screen | Strong symmetric: `cubic-bezier(0.77, 0, 0.175, 1)` |
| Sheet or drawer travel | `cubic-bezier(0.32, 0.72, 0, 1)` |
| Color or hover change | `ease` |
| Constant motion (progress, marquee) | `linear` |

Built-in `ease-out` is weak for deliberate motion. Never use a slow-start curve (`ease-in`)
for an entrance or a response to input; it delays the frame the user is watching. When a
curve outside this table is needed, take it from a published easing collection rather than
inventing control points.

## Springs

- Perceptual form: `{ type: "spring", duration: 0.5, bounce: 0.2 }`. Keep bounce between 0.1
  and 0.3, and use bounce only for gestures and playful moments.
- Physical form, for finer control: stiffness, damping, and mass.
- Springs keep velocity through an interruption, which is why gestures use them.

## Groups and gestures

- Stagger 30 to 80 ms per item. Cap the total sequence: past a handful of items, reveal the
  rest together. A stagger never blocks input.
- Where flick dismissal is intended, use release velocity as well as distance. Tune and
  record the speed threshold on a device. For position-only snap actions, use their declared
  distance threshold. Use the [drag release recipe](recipes.md#drag-release) for settle ownership.
- Past a boundary, resist with increasing friction instead of a hard stop.

## Provenance

Curve values, duration bands, and spring forms adapt Emil Kowalski's published animation
guidance ([emilkowalski/skills](https://github.com/emilkowalski/skills/tree/2d228630ba1446365f614a108cb8252f1feda202),
MIT License, Copyright 2026 Emil Kowalski; observed October 11, 2026, verified against the
catalog notice on November 20, 2026) and the iOS-style drawer curve it cites.
Local departures: the bands are ranges, the project's own tokens outrank every fallback,
scale cannot replace layout, opacity cannot replace hiding semantics, and no universal
spring mandate is imported. Recheck when the project's motion tokens, target runtimes, or
upstream skill defaults change.

The living illustration recipe generalizes the idle-life method of
[rossark-motion-skill](https://github.com/rossark0/rossark-motion-skill/tree/9b20964e32f07f8ac7e2948cd175746fa4a7712f)
(MIT License, Copyright 2026 rossark0; observed October 23, 2026). Local departure: extracts
only the single-clock pure-function loop rules without bundling engine code or project
assets. Recheck when the target rendering owner or upstream guidance changes.
