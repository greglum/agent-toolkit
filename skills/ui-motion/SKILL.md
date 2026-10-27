---
name: ui-motion
description: >-
  Fix or diagnose existing application motion: loading continuity, state handoffs, overlay
  lifecycles, interruptible gestures, or animations that stutter under load, with rendered
  checks. Preserve tokens and real state. New motion: find-animation-opportunities, then
  animate; grading a diff: review-animations; videos: motion-film.
---

# UI motion

Make changes of state easier to understand while keeping the application responsive.
Respect the requested mode: an audit produces findings; an implementation changes and verifies
the agreed surfaces. In audit mode, use the change steps below to inspect the current behavior
and propose fixes; change no application or design files. Preserve the repository's design
and library decisions.

## Procedure

1. **Trace the interaction.** Read the applicable design guidance, motion policy, tokens, UI
   primitives, and verification workflow. Follow the actual state from the initiating action
   through pending, settled, error, and interrupted states. Record the user's task, the proposed
   purpose of motion, and how often it occurs. Remove motion that only delays repeated work or
   moves information the user is trying to read. Done when each proposed transition has a
   concrete purpose and an owning state or component.
   When a reference video, gallery effect, or vague motion brief needs translation, read
   [reference to interaction](references/reference-to-motion.md) before choosing its mechanics.
2. **Choose the owner.** Reuse the component's existing lifecycle and animation mechanism.
   Extend the shared primitive when the same invariant applies to its callers. Prefer native
   CSS transitions or browser animation APIs for simple motion; use an installed runtime when
   its capabilities are needed and allowed here. A film-only runtime exception does not extend
   to the rest of an application. When a spec or design file hands off motion, reproduce its
   values exactly and leave unspecified elements static. Finish this step with one responsible
   layer and the existing tokens and tooling that will implement it.
   When a visual timeline or animation editor participates, follow the
   [studio round trip](references/visual-editors.md) to verify the saved source.
3. **Fix geometry and state first.** Reserve the space content needs before crossfading it.
   Keep pending and settled layouts compatible, overlays anchored to their trigger, and reader
   position stable through refreshes. Drive loading and completion from the actual operation;
   a decorative timer cannot declare success or turn an unknown task into numeric progress.
   Preserve focus, selection, errors, retry, and interaction during a visual handoff. Done when
   the states are correct and readable without motion.
4. **Add only the useful transition.** Name animated properties. Prefer transform and opacity
   where they fit; measure an intentional layout or paint exception. Reuse the product's
   duration and easing tokens. Match the path and origin to the state change. An animated
   transform must not erase a layout transform on the same element. Rapid toggles and gestures
   must retarget from the displayed state instead of jumping to a stale start or waiting for
   the previous animation. Keep semantic actions immediate.
   Tie animations, listeners, observers, and pending callbacks to the owning lifecycle; cancel
   or dispose them when that owner leaves. A stale completion must not overwrite newer state.
   For continuous canvas or GPU effects, also check visibility suspension and resource teardown
   in [performance diagnosis](references/performance.md), even without reported stutter.
   Completion means normal, reversed, and repeated actions all reach the authoritative final state.
5. **Verify in the running application.** Follow the checks in [rendered
   review](references/rendered-review.md). Inspect the applicable normal and reduced motion
   paths, supported viewports and themes, keyboard and pointer behavior, and interrupted states.
   Use the repository's UI test setup for DOM measurements and axe-core where it exists. Run the
   required source gates. In implementation mode, fix confirmed defects and recheck the affected
   conditions. In audit mode, report them with locations, evidence, and proposed fixes.
6. **Report the evidence.** Name the purpose, owner, and material change or audit finding.
   Include measured results, checks and their status, and any unverified behavior. Report
   material implementation choices where the source was silent, with confidence, least
   confident first. An audit finishes with findings, inspected scope, and unverified conditions.
   An implementation finishes when requested behavior and required checks pass, or the remaining
   blocker and the evidence needed to settle it are explicit. Source-only review leaves rendered
   acceptance unverified.

## Accessibility and performance

- Follow the product's reduced-motion contract. Static changes or gentler transitions can
  preserve meaning; a generic fade must not override a deliberate policy that removes motion.
  Check the computed cascade as well as the class or media query.
- Keep focus indicators and keyboard actions usable throughout motion. Use the existing
  accessible overlay primitive for focus, dismissal, and mounting; visual animation does not
  replace those semantics.
- Scope hover motion to the appropriate pointer capability. Touch and keyboard users still
  need visible state feedback.
- For stutter, dropped frames, or motion that slows under load, use [performance
  diagnosis](references/performance.md) before changing drivers or adding compositor hints.
  A transform, opacity animation, or screenshot alone does not prove smooth frame delivery.
