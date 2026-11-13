# Live browser films

Read this when the film plays in the viewer's browser from source: a title sequence, a
product film or an opening that hands over to a working page. The scene contract, reading
windows, critique loop and render review still apply. This reference adds what changes when
no media file exists and the viewer's device does the rendering. It supplies no engine.

## Decide live or rendered

Choose per film, then per shot. Record the choice and its reason in the brief.

- Play live when the film must respond to the viewer, show live data, end on a working
  page, stay sharp at any zoom, or ship inside a host that serves one small page.
- Render to video when the look depends on light transport: real reflections, refraction,
  depth of field, motion blur. A drawn or shaded imitation of those reads as illustration.
  Follow [material and mechanism shots](material-3d.md) and prove one hero still before
  committing a film to a 3D scene.
- A rendered film needs a host that serves media, a poster, and a plan for the seam where
  video meets the live page. Check the destination's size and request limits first.

Done when the brief names the delivery, the host limits and the reason.

## Drive everything from one clock

One number, film time, sets the whole picture. Read it from a monotonic clock in one place.

- Every shot is a pure function of film time. The same time draws the same picture after
  any seek, pause, skip or replay. Nothing reads what was drawn before.
- Declare each cut time once. Derive visibility, captions, progress and skip targets from
  those values.
- Hiding the page pauses the clock. Returning resumes from the same film time.
- Skip, replay and resize set the time or rebuild the tracks. They never patch state.
- Effects with history follow [seekable simulations](simulations.md): write position as a
  closed form of age with a fixed seed.
- Keep the capture hook in the same code path as playback: set the time, draw, read the frame.

Done when a frame drawn after a backward seek matches the same time reached by playing.

## Frame by orientation

Compose each shot for the window it is in, from one shot list.

- Write a framing as a window in the subject's own units, centred on a named point, plus the
  room captions take. Compute translation and scale from the viewport at build time.
- Give portrait and landscape their own window per shot. A portrait close-up fits width; a
  landscape one fits height. Rebuild on resize and on rotation.
- Keep one caption area height across neighbouring shots so the picture's edge holds still.
- Name the clearance for anything near an edge in pixels, and measure it at the narrowest
  supported width and with browser bars showing.
- Scale type with the frame's short side. Text sized for a phone is too small on a laptop.

Done when every shot's subject, caption and controls are measured inside the frame at each
supported width, in both orientations.

## Open on the viewer's tap

When the film starts on a tap, the tap is the first cut.

- The poster is the film at time zero, on the same elements. Starting is a change of clock,
  never a swap of pictures.
- The object under the finger responds within 100 ms, where the finger landed, with no fade
  and no black frame between the tap and the first shot.
- Build everything the first second needs before the poster shows: tracks, layers, canvases.
  The tap handler only starts the clock.
- Guard the second tap. A double tap must not skip the opening.
- The control is a real button with a visible focus state and a keyboard path. Replay returns
  to the same poster and behaves the same way.
- Nothing plays before the gesture. Without JavaScript the end state shows.

Done when a real-time capture shows the first changed frame within 100 ms of the pointer
event and no frame between poster and first shot is blank.

## Draw from reference photos

A drawn subject that must read as a real object starts from photographs, not memory.

- Collect references with one job each: overall proportion, one material, one detail at the
  closest framing the film uses. Record source, date and rights. Keep maker names and marks
  out of the drawing.
- Write a drawing specification from them: parts, proportions, one light direction, the tone
  each surface takes facing toward and away from the light. Label each value measured,
  estimated or chosen.
- Review the drawing at the film's closest framing, side by side with the reference, before
  timing any shot that depends on it.
- A reviewer who cannot view images reports that, and the references stay unverified.

Done when each close-up has a reference, a specification entry and a side-by-side check.

## Keep playback on the compositor

- Animate transform and opacity only. Measure geometry once at build, never during playback.
- Promote the few layers that move, before they move. Each promoted layer costs memory in
  proportion to its pixel area at device scale; count them.
- A value written into a drawing every frame repaints the layer that holds it. Give a moving
  part its own small layer instead of editing a large scaled one.
- A promoted layer may keep the scale it was first drawn at. After a large scale change,
  check edge sharpness at device pixel ratio on the target device. If it is soft, drop the
  layer hint for one frame at the cut so the layer is drawn again, and measure that frame.
- Animations the browser plays can stay smooth while script is busy; values set from script
  each frame cannot. Where the clock allows, play tracks from a shared start time and set
  time directly only to seek.
- No filter, backdrop filter or large blend layer without a trace that shows the cost.

Done when a trace of the heaviest shot shows no layout or paint during playback, or each
remaining paint is named and measured.

## Verify in real time

Frozen frames prove what a time looks like. They do not prove pace, smoothness, the cut or
the tap. Run both.

1. Frame-interval log. Play the film end to end with no frozen clock. Log each animation
   frame's timestamp and film time. Report median, 99th percentile and maximum interval, and
   every interval over 1.5 display frames with the film time it fell on. Repeat with CPU
   throttling. Record device or emulation, pixel ratio and whether rendering was software.
2. Boundary screencast. Record the screen in real time across the tap and each cut. Map each
   recorded frame to film time from the page's own log. Inspect the frames on both sides of
   every boundary for a blank, a half-moved layer, a double exposure or a late caption.
   Log every control's opacity on each frame across each hand-off. In one production a
   frozen-clock sweep missed an end-card control that faded in, vanished and faded in again;
   only the per-frame log in real time showed it.
3. Projected travel. Time a 3D turn by its geometry on screen, such as the free edge's
   position, which moves with the cosine of the angle, not by the rotation angle. A lid whose
   rotation eased over 800 ms still read as a 200 to 300 ms snap, because most of its visible
   travel happened in a short span of angle.
4. Response time. Measure pointer event to first changed frame.
5. Repeat cycles. Replay several times, skip from every shot, rotate, hide and return. The
   end state matches and one loop is running.
6. A real phone. Emulation and headless software rendering do not establish phone playback.
   Without a device run, report phone playback as unverified.

A model reviewing its own film checks stills. Rhythm between frames is outside what a still
shows, so timing errors pass frame review. Ask the builder to list what it computed, what it
estimated and what it could not verify without watching.

Done when each check has a recorded result, or is listed as unrun with the reason.

## Sources and limits

Original guidance, written November 11, 2026, from one production: a short vector product
film played in a phone browser from a single page, whose final cuts ran about 31 to 35
seconds. No upstream code, prompts or media copied. Sources were rechecked November 12, 2026.

- Chris Harrelson, ["Re-rastering composited layers on scale change"](https://developer.chrome.com/blog/re-rastering-composite),
  Chrome for Developers, September 22, 2016, page licensed CC BY 4.0: from Chrome 53,
  `will-change: transform` holds a fixed bitmap under script-driven scale changes, and
  removing it for a frame forces a fresh draw; CSS animations and Web Animations are excluded.
  A paused animation whose time is set by script is covered neither way, so the rule above
  says to check. Current Chrome and Safari behaviour was not measured here.
- web.dev, ["Animations and performance"](https://web.dev/articles/animations-and-performance)
  and ["Stick to compositor-only properties and manage layer count"](https://web.dev/articles/stick-to-compositor-only-properties-and-manage-layer-count),
  last updated August 8, 2014 and March 20, 2015, observed November 11, 2026, CC BY 4.0: transform and opacity skip layout and
  paint, browser-played animations usually run on the compositor thread, and every layer
  costs memory.
- Karo Zieminski, ["Claude Fable 5.2 for designers: 7 tests, every prompt"](https://productwithattitude.com/articles/claude-fable-5-2-design-motion-tests-prompts),
  Product with Attitude, November 9, 2026, no reuse license established: one author's seven
  launch-day tests, which note that the model cannot watch whether a timing reads right.
  Supports the real-time checks, not a general capability claim.
- Mavday, ["Blender MCP and AI agents"](https://mavday.com/ai-engineering/blender-mcp-ai-agents),
  October 29, 2026, no reuse license established: a headless test placed every part within
  its measured tolerance yet the design came out basic, because an agent that cannot see its
  render cannot judge how it looks. Supports proving a hero still before choosing a rendered route.

Recheck when the target browsers, the host's limits or the capture tooling change. No paired
skill and control evaluation was run. The 100 ms tap threshold and the 1.5 frame interval
flag are chosen values from that one production, not measured thresholds of perception.
