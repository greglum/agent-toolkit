# Timing defaults

Read this when writing the scene contract, setting holds or eases, or reviewing pace. These
numbers are defaults taken from public motion skills, not measurements made here. The owner's
motion tokens, a measured reference, and the actual voice take outrank them. Record any value
you change and why in the storyboard or manifest.

## Holds and reading windows

- Start a reading window when the words are fully legible, not when their entrance begins.
- Hold a line about 0.5 s plus 0.3 s per word. Never go below 0.6 s per three words. Hold the
  last line at least 2 s and an end card at least 2.5 s. A one or two word chapter line can
  hold for less when the next shot keeps it on screen.
- Give each read its own window. Start the next message after the current one is read.
- Text and UI that have landed stay still. Idle breathing, floating, pulsing, or a slow push
  added late in a scene draws the eye away from the read.
- Hold the payoff fully in frame for a beat before anything leaves.
- In review, flag any stretch over about 3 s where nothing new appears, outside a planned
  hold or a UI action the viewer is following.

## Still beat before the payoff

Leave 0.3 to 0.75 s of stillness between an action and its result, then play the result at
normal speed. The pause lets the viewer predict the result; the result then confirms or
corrects them. Use it once per beat that matters, not on every step.

## Eases by role

- Arrivals decelerate on a long-tailed ease-out, for example `cubic-bezier(0.16, 1, 0.3, 1)`.
- Exits accelerate away.
- Camera moves and color floods ease at both ends.
- Linear is only for constant rates: progress, rotation, a steady scroll.
- Interpolate scale and camera zoom perceptually (in log space). Linear scale looks slower as
  it grows. Do not zoom in and then straight back out.
- Text, data, and camera settle without overshoot (critically damped). Small UI objects may
  use a light spring, damping ratio about 0.75 to 0.85. Opacity and color never overshoot.
- One ease and one duration on every element reads as generated. Vary them by role.

## Exits, stagger, and overlap

- An exit is one continuous motion, about 50 to 75% of its entrance's duration.
- At a moving cut, the incoming half may be the longer one so speed matches across the seam.
- Stagger words 60 to 120 ms apart and list items 40 to 80 ms apart. Keep a whole cascade
  under about 0.5 s. Start the next element when the previous one is 30 to 50% done.
- Bring in the main object first and its supporting label about 0.1 s later.
- With three or more animated elements, keep at most a third of them moving at once.
- Reposition a settled group slow, fast, slow: a short ramp, a quick middle, and a tail at
  least three times the ramp. Reveal new content during the fast middle.

## Counted numbers and clicks

- A counted number starts on the word that names it, eases out with no overshoot, rounds on
  every frame, sits in a fixed-width box with its unit and tabular digits, and holds its
  sourced final value.
- A demonstrated click: the cursor arrives and rests 0.2 to 0.4 s, presses for about 100 ms,
  and the result starts within 0.1 to 0.27 s.

## Moving cuts

Cut a move at its fastest frame. Match axis, direction, and speed on both sides: mirror the
ease (ease-in out of the outgoing shot, ease-out into the incoming one). On a zoom, the scale
must change in the same direction on both sides. A change of direction needs a visible cause.
Check the result with the consecutive-frame strip in [capture and export review](render-review.md#frames-and-handoffs).

## Narration sets the clock

When a scene is narrated, its duration comes from the measured take, and the picture reveals
each part on the word that names it. The script budget and that reveal rule live in
[narration](narration.md#write-the-script). Trim words before stretching motion.
