# Animated line art and reference matching

Read this when building an animated SVG illustration, living line-art card, or matching the
motion timing of a cleared reference clip.

## Hand-inked figure craft

- **Local figure coordinates:** author each character in a consistent local coordinate space
  (for example feet anchored on one baseline `y` and facing `+x`) and place instances into the
  scene with a single group transform. Proportions, pen weight, and stride math stay coherent.
- **Open-stroke limbs:** drawing a limb as a paper-filled band bounded by two slightly curved
  ink strokes that stay open at the ends reads as hand-inked rather than rigid vector tubes.
- **Skeleton before clothing:** solve hip, knee, and ankle positions first, even under a coat
  or skirt, then attach hems and sleeves to those joints so garments open and close with the
  stride. Hang scarves, bags, and lanterns on damped springs or pendulums.
- **Planted feet:** match horizontal translation speed to the gait stride and period (`speed *
  scale * dt`) so stance feet do not skate across the ground. To speed up a day/night scene,
  compress character arrival schedules rather than accelerating walk cycles into a blur.
- **Palette inversion for time of day:** keep ink on `currentColor` and paper fills on one
  dedicated class (while marking solid-color garments explicitly) so a single palette update can
  shift a scene cleanly from warm daylight to dark indigo night with glowing windows.

## Stepped-clock verification

Background tabs, preview panes, and headless browsers throttle `requestAnimationFrame`. Never
rely on wall-clock playback alone to judge frame craft:

1. Support a freeze parameter (such as `?t=1.25`) and a debug mode (`?debug`) that disables the
   rAF loop and exposes a fixed-step function (`window.__step(seconds)`) advancing in `1/60` s
   increments.
2. Capture a zoomed frame strip centered on each moving figure or interactive prop across one
   full stride or reaction (start, contact, peak, follow-through, settle).
3. Check the strip for planted feet, hip rise over stance and dip at double support, clothing
   overlap, leading-limb draw order, prop attachment, and return to idle after interaction.
4. Sweep key palette states (day, dusk, flip transition, night, dawn) and verify ink contrast
   holds across every settled state.

## Measuring a reference clip

When matching the timing of a cleared reference clip:

1. Probe `r_frame_rate`, `avg_frame_rate`, and `nb_frames` with `ffprobe`. Most social clips
   are variable-frame-rate (VFR); resample by time (`-vf fps=30` or `fps=60`) before indexing
   frames. Never mix decoded frame indices (`select` / `trim=start_frame`) with rawvideo
   nominal-fps padding, which can double or skew measured speed.
2. Measure independent loop periods per moving part (legs, body sway, secondary props) by
   comparing cropped frame differences across lags; identical limbs can create a false half-cycle
   match, so confirm full-cycle alignment using arms or asymmetric props.
3. Overlay a translucent red render of your SVG over the cropped reference frame at matching
   timestamps to check alignment at both the opening and late in the loop so drift is caught.
4. Keep originality boundaries strict: measuring timing and proportions to match feel does not
   authorize shipping the reference's characters or story as new work.

## Sources and recheck triggers

Original synthesis observed November 25, 2026. No upstream code, assets, or prose copied:

- `JDhruv14/line-art-animation` at `c43d698913` (MIT, 2026-11-10): `SKILL.md`,
  `references/verify.md`, `references/matching.md`, `scripts/clip.ts`, `scripts/capture.ts`
  (open-stroke limbs, planted-foot gait, day/night `currentColor` inversion, `?debug` stepping,
  VFR time-resampling and period/overlay measurement).
- `MengTo/Skills` at `a5b1d3d28b` (MIT, 2026-11-25): `agent-skills/illustration/README.md`
  (SVG file contract, scoped ID prefixes, palette linting, zoomed vector inspection).
- `rough-stuff/rough` at `56a2762171` (MIT, 2023-11-20): sketchy SVG/Canvas primitive concepts
  (roughness, bowing, hachure fills).
- W3C WAI WCAG 2.2.2 (Pause, Stop, Hide) and `prefers-reduced-motion` guidance for animated SVG
  and `<feTurbulence>` filter cost limits.

Recheck when browser SVG filter support, WCAG guidance, or destination SVG sanitizer contracts
change.
