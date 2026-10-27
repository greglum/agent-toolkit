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
  distance threshold and disable competing inertia instead.
- Past a boundary, resist with increasing friction instead of a hard stop.

## Provenance

Curve values, duration bands, and spring forms follow Emil Kowalski's published animation
guidance (MIT, `emilkowalski/skills` at `2d22863`) and the iOS-style drawer curve it cites.
The bands are deliberately ranges; the project's own system outranks them.
The living illustration recipe generalizes the idle-life method of
[rossark-motion-skill](https://github.com/rossark0/rossark-motion-skill/tree/9b20964e32f07f8ac7e2948cd175746fa4a7712f)
(MIT, copyright 2026 rossark0, reviewed October 23, 2026). No engine code is bundled.
