# Existing Remotion projects

Read this only when the project already uses Remotion or the task explicitly chooses it.

- Read the installed version and project scripts first. Consult matching official APIs or the
  project's maintained Remotion skills for the relevant composition, timing, media, text
  measurement, and rendering operation. [Official agent skill docs](https://www.remotion.dev/docs/ai/skills)
  describe the maintained source. A current upstream example may depend on newer APIs.
- Drive scene visuals from Remotion's frame/timeline model. Independently running CSS
  animations, transitions, timer-driven state, or unseeded randomness do not reproduce a
  requested frame reliably. Resolve root and scene-relative timing through the installed API;
  moving a frame hook across a sequence boundary can change what it means.
  Derive seconds-to-frames calculations from the active composition's fps, including
  starts, trims, duration, and premounting. Preserve intended seconds when fps changes.
- Write motion helpers as pure functions of composition or scene time. Take layout targets
  from captured rects or exported layout constants; a ref or state read during render can
  give the same frame different values depending on seek history. Draw strokes with
  `pathLength={1}` so no length is measured, and reveal filled areas with a clip.
- Compute a `spring()` config's damping ratio, damping / (2 sqrt(stiffness x mass)), before
  using it, and hold it to the overshoot rules in [timing defaults](timing.md#eases-by-role).
  `overshootClamping` only cuts the value at the target, so the motion stops abruptly; raise
  damping instead. Check how the installed `interpolate` applies easing over several keys:
  in 4.0.535 one easing applies to each segment, so motion stops at every key, and an
  easing per segment is accepted.
- Register the requested compositions with correct dimensions, fps, duration, and props.
  When Studio editing is part of the task, preserve independently editable source nodes and
  the installed version's authoring conventions. Live-UI performance advice about transform
  syntax does not automatically govern Studio editability.
  When extracting a scene for its own editable timeline, carry its required fonts, styles,
  context, props, and readiness with it; the parent is absent in a standalone preview.
  Register the same scene component with intended props, then open it directly in a fresh
  Studio preview before opening its parent to expose missing initialization.
  If editable delivery is promised, test actual editing, saving and reopening through
  [studio handoff](production.md#verify-an-editable-studio-handoff); selectable nodes alone
  do not establish that edits survive into the requested export.
- Use the supported readiness and asset-loading mechanisms. Measure with actual fonts and
  delivery bounds. Verify scene overlap and total runtime after adding transitions or a
  playback-rate change; nominal clip durations alone may not describe the resulting timeline.
- Keep preview and export distinct. An explicit export request continues through rendering
  and encoded-output inspection. Use a local preview for interactive review when that is the
  requested deliverable.

These are routing and verification rules, not a bundled Remotion runtime or copied API manual.
They do not install packages, upgrade the project, choose a cloud renderer, or establish a
third-party software license.
