# Recipes

Starting points for common components. Replace each literal value with the project's token
and each hand-built element with the project's primitive. The `--ease-*` and `--dur-*` names
below are placeholders for whatever the project calls them.

## Press feedback

```css
.pressable { transition: transform 140ms var(--ease-out); }
.pressable:active { transform: scale(0.97); }
```

Keep the scale subtle (0.95 to 0.98). Skip it on constant-tier controls.

## Anchored overlay: menu, popover, select

```css
.menu {
  transform-origin: var(--transform-origin); /* the primitive's trigger-side origin */
  transition: opacity 180ms var(--ease-out), transform 180ms var(--ease-out),
    display 180ms allow-discrete, overlay 180ms allow-discrete;
}
.menu:not([data-open]) { opacity: 0; transform: scale(0.96); }
@starting-style { .menu[data-open] { opacity: 0; transform: scale(0.96); } }
```

Use the primitive's open attribute and origin variable. Dismissal, focus return, and inert
state stay with the primitive.

## Tooltip

Delay the first open in a group (the project's hover-intent delay). Once one is open, open
neighbors instantly with no entrance so scanning a toolbar stays fast.

## Dialog

Fade the backdrop. Enter the panel from `scale(0.96)` and opacity, centered. Exit faster
than the entrance. Focus moves on open, not when the animation ends.

## Sheet or drawer

```css
.sheet { transition: transform 320ms var(--ease-drawer); }
.sheet:not([data-open]) { transform: translateY(100%); }
```

Percentage travel follows the sheet's own height. Leave along the same edge it entered.

## Toast

Transitions, not keyframes, so a burst of toasts retargets instead of restarting. Enter
and leave from the stack's edge with translate and opacity. Swiping out follows the pointer,
then finishes from the displayed position using the component's dismissal and inertia policy.

## Disclosure (accordion, collapsible)

```css
.panel { display: grid; grid-template-rows: 0fr; transition: grid-template-rows 220ms var(--ease-out); }
.panel[data-open] { grid-template-rows: 1fr; }
.panel > .inner { overflow: hidden; }
```

Siblings must move, so this animates layout on purpose. Measure it on the longest real
content. Where supported, `interpolate-size: allow-keywords` with `height: auto` is an
alternative.

## List insert and remove

Enter from a small offset with opacity. On removal, collapse the row's space after it fades,
or the list jumps. Skip the motion entirely on frequent-tier lists.

## Group stagger

```css
.item { animation: rise 260ms var(--ease-out) both; animation-delay: calc(var(--i) * 40ms); }
@keyframes rise { from { opacity: 0; transform: translateY(6px); } }
```

Set `--i` per item and cap it so late items share the last delay. Content is interactive
while it arrives.

## Selection indicator

Move one indicator element with `transform` between measured positions, or use the runtime's
shared-layout feature. For a color change under the indicator, a clipped duplicate of the
active label avoids a muddy crossfade.

## Hold to confirm

```css
.hold .fill { clip-path: inset(0 100% 0 0); transition: clip-path 200ms var(--ease-out); }
.hold:active .fill { clip-path: inset(0 0 0 0); transition: clip-path 2s linear; }
```

The slow fill is the user's deliberate phase; release snaps back fast. Commit the action
from the timer that matches the fill, and give keyboard users an equivalent path.

## Drag release

Follow the pointer one-to-one while held, using the owning primitive's pointer capture.
Define the commit threshold, snap destinations, cancellation and inertia policy first.
On release, settle from the displayed position to the chosen destination; use velocity when
the interaction calls for a flick or momentum, and disable competing inertia for a
position-only snap. Preserve page scrolling on its intended axis, cancel a tap that becomes
a drag, release capture on completion or cancellation, and keep equivalent actions available
without dragging. Ignore extra touch points after the drag begins.

This distinction is informed by [Jakub Krehel's swipe example](https://jakub.kr/work/drag-gesture)
and [Motion's drag guide](https://motion.dev/docs/react-drag), observed October 23, 2026.
Publication dates and article reuse rights were not established. No example code or thresholds
are copied; the destination and inertia policy belong to the product.

## Crossfade that will not settle

When two states visibly overlap mid-fade after timing is tuned, a brief small blur on both
(a few pixels) can merge them. Blur is paint work; check cost on the target devices.

## Living illustration

For a drawn SVG or canvas subject on a rare-tier surface, such as an empty state or
onboarding art. Give each subject one clock and compute every part as a pure function of its
time. Split layers at their pivots and rotate each at its pivot. Run idle loops on seeded
phases with periods that divide the loop length, so the loop closes without a jump. Frame 0
is a finished drawing, and reduced motion freezes there. Pause the clock when the subject is
off screen or the page is hidden. Frequent-tier chrome around it stays still.

## View transition

```js
if (!document.startViewTransition) update();
else document.startViewTransition(update);
```

Name only the elements whose identity should carry across. The update itself must work
with no transition at all.
