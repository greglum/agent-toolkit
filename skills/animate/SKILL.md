---
name: animate
description: >-
  Build web UI motion that earns its place: gate purpose and frequency, pick the cheapest
  tool, then set properties, timing, interruption, exit, and reduced motion from project
  tokens. Edits code. Use to animate an element, add a transition, or build a
  find-animation-opportunities row. Grade results with review-animations.
---

# Animate

Turn one motion request, or one ledger row from `find-animation-opportunities`, into an
implementation that passes `review-animations` the first time. Make each decision, state it
in one line, and write the code. Do not offer a menu of options.

Two failures matter, and the first is worse: animating something that should not move, and
animating the right thing with the wrong ingredients.

## Rules

- **The project owns the system.** Use its tokens, primitives, motion runtime, and
  reduced-motion policy. Extend a token set; never add a parallel one. The values in
  [defaults](references/defaults.md) apply only where the project has none, and each default
  you use is reported as a choice.
- **Cheapest tool, no new dependency.** Installing a runtime needs the user's approval. A
  component need (toast, drawer, menu, dialog) goes to the project's existing primitive, not
  a hand-rolled one with an animation on top.
- **Stay in scope.** Change only the files the request or row owns.

## Sequence

1. **Gate.** From a ledger row, purpose and tier are settled; confirm the cited code still
   matches, and stop with a report on drift. From a direct request, name the purpose and the
   frequency tier first. Keyboard-shortcut or constant-tier actions, and motion with no
   purpose, get no animation: say so, offer the non-motion alternative, and finish. Done when
   purpose and tier are stated, or the rejection is written.
2. **Make it correct without motion.** Reserve the space settled content needs, anchor
   overlays to their trigger, and drive pending and done states from the real operation.
   Preserve focus, selection, errors, and retry. Done when every state reads correctly with
   motion disabled.
3. **Pick the tool.** Walk down and stop at the first that fits:

   | Need | Tool |
   | --- | --- |
   | State change you control with a class or attribute; hover, press, toggle | CSS transition |
   | Entry on mount, or animating to and from `display: none` | `@starting-style` with `transition-behavior: allow-discrete`, within the project's browser support |
   | Predetermined or looping motion that must stay smooth while scripts run | CSS animation |
   | One-off programmatic motion without a library | Web Animations API |
   | Route or whole-view state swap | View Transitions API where supported, with an instant fallback |
   | Springs, exit after unmount, shared-element layout, gesture-driven values | The installed runtime |

4. **Choose properties and geometry.**
   - Name each property; never `transition: all`. Prefer `transform` and `opacity`. Name the
     property a utility class actually writes (check the compiled CSS): a utility can set
     `scale` or `translate` rather than `transform`, and the transition then never runs.
   - Anchored overlays scale from their trigger; dialogs stay centered.
   - Enter from a slightly reduced scale with opacity, never from `scale(0)`.
   - Use percentage translation for travel relative to the element's own size.
   - An animated transform must not erase a layout transform already on the element.
   - Where siblings must move (a disclosure), animate the layout deliberately (grid rows or
     an interpolated height) and measure it. Scale cannot stand in for layout.
   - Opacity does not hide. Keep the primitive's hidden, inert, and focus lifecycle.
   - Do not drive many children per frame through an inherited custom property.
5. **Set timing.** Project tokens first, then [defaults](references/defaults.md). Entrances
   and responses to input decelerate; never start slow on a response. On-screen movement uses
   a symmetric curve; constant motion is linear. Use a spring for gestures and values the
   user can reverse mid-flight. Make deliberate phases slow and system responses fast (hold to
   confirm fills slowly; release snaps back).
6. **Handle interruption, exit, and lifecycle.** Rapid triggers retarget from the displayed
   value: transitions or springs, not keyframes that restart. Exit along the entry path. The
   semantic action commits immediately and never waits for an animation. Cancel animations,
   listeners, and observers when their owner unmounts; a stale completion must not overwrite
   newer state.
7. **Ship access with it.** Follow the project's reduced-motion contract. Absent one, remove
   travel and scale and keep a short opacity or color change where it carries meaning. Gate
   hover motion to `(hover: hover) and (pointer: fine)`. Keep focus visible throughout.
8. **Verify, then get it graded.** Run the project's required gates. Run the app through its
   own verification workflow and exercise the change at normal speed, on rapid repeat and
   reversal, with reduced motion, and by keyboard; follow `ui-motion`'s rendered review when
   it is installed. Then invoke `review-animations` on your diff and fix every Block finding.
   Done when the gates pass and the review has no Block, or the blocker is stated with the
   evidence that would settle it.

For common components, start from the matching entry in [recipes](references/recipes.md)
and adapt it to the project's tokens and primitives.

## Output

The code is the deliverable. Then, briefly:

- **Gate:** tier and purpose, or what was rejected and why.
- **Ingredients:** tool, properties, timing source, interruption, reduced-motion variant.
- **Choices:** every default or call made where the project was silent, with confidence,
  least confident first.
- **Feel checks for a human:** what source cannot settle (a crossfade, a spring's bounce,
  a gesture on a real device) and how to check it: 4x slow playback, frame stepping, a phone.
- **Checks:** gates, rendered checks, and review result, each passed, failed, or not run.
