# React Native and Expo motion

Use the existing native motion and navigation owners. This branch implements the requested
interaction; it does not install packages or migrate the app's architecture.

## Procedure

1. **Bind the native stack.** Read the lockfile, app configuration, motion tokens, component
   primitives and verification commands. Record React Native, Expo SDK if present,
   Reanimated, Worklets and Gesture Handler versions, architecture, platforms and build mode.
   Check the matching documentation before choosing an API. Reanimated 4 requires the New
   Architecture; its compatibility table assumes the latest patch in each minor, so inspect
   the installed package's compatibility data for an older patch. Expo Go, a development
   client and a release build provide different evidence. Do not upgrade to make a recipe fit.
2. **Gate the request.** Name its purpose and expected frequency. Keep repeated input and
   semantic actions immediate; retain native navigation conventions. Remove decorative delay
   where it adds no meaning. Define the authoritative pending, success, error and cancelled
   states before motion. Preserve the existing press, scroll, focus and accessibility owners.
3. **Choose the smallest existing mechanism.**

   | Need | Starting owner |
   | --- | --- |
   | Navigation, platform sheet or keyboard-following surface | Existing navigator or native primitive and its supported options |
   | Simple value transition | Existing core Animated or installed motion runtime |
   | Gesture or scroll tracking with custom release behavior | Existing UI-runtime gesture and animation integration |
   | Layout change | Existing layout mechanism, measured in the target view hierarchy |

   Core Animated's native driver supports non-layout properties such as transform and opacity.
   Use one driver consistently for each animated value. Its direct-event support includes
   scroll events; it does not cover PanResponder bubbling events. This limitation does not
   justify replacing working native-driven animations throughout the app. When an approved
   dependency is needed in Expo, resolve it through that SDK's installation guidance rather
   than taking an arbitrary latest package. Verify preset/plugin and native-build setup for
   that version; do not add a second Babel plugin from an unrelated example.
4. **Keep continuous motion with its runtime.** With Reanimated, derive animated styles from
   shared values rather than React state each frame. Read and write shared values in handlers,
   effects or animation callbacks, never component render. Use the installed version's
   compiler-compatible access API when React Compiler is enabled. Keep continuous gesture
   updates on the UI runtime. Schedule a semantic result back to the React Native runtime at
   a meaningful boundary, using its supported bridge API and a function defined in that
   runtime's scope. Avoid per-frame cross-runtime calls.
5. **Define the gesture handoff.** At activation, capture the currently displayed position and
   cancel or retarget its previous animation. Apply movement relative to that position.
   Define release by the product's distance and velocity policy, with bounds and a reachable
   snap destination. Define cancellation separately: a scroll taking over, navigation or a
   second touch must not accidentally commit a destructive action. Preserve scroll-axis
   arbitration and an equivalent accessible action. Commit once; a cancelled or stale
   completion cannot commit again. Dispose listeners and animations when their owner leaves.
6. **Preserve geometry and access.** Prefer transforms and opacity where they express the
   change, but measure required layout animation rather than substituting a scale that leaves
   sibling geometry wrong. Reuse native layout measurements for dynamic content; check large
   text, safe areas, keyboard appearance and rotation. An invisible view can still intercept
   input or accessibility focus: keep the primitive's visibility and dismissal semantics.
   Follow system and product reduced-motion settings, including a static result where called
   for. Reanimated's useReducedMotion reports the startup setting and does not rerender on a
   later setting change. If live changes must update the UI, use the app's settings owner or
   React Native AccessibilityInfo's reduceMotionChanged subscription, with cleanup. Optional
   haptics accompany a meaningful event and never replace visible or accessible feedback.
7. **Verify the actual interaction.** Run the project's source and native build gates. Exercise
   press, drag, release, cancellation, rapid reversal, repeated navigation and unmount during
   motion. Check reduced motion both at launch and while the app is running, large text,
   screen-reader actions and the supported platforms. Use a release build on a representative
   supported device for frame delivery, gesture feel and haptic timing. Simulator and mocked
   tests can establish narrower behavior; neither proves device performance. Report each
   unrun dimension. Finish when the requested behavior and required gates pass, or name the
   concrete blocker and evidence needed to resolve it.

## Sources and limits

Original procedure; no upstream code or wording copied. The native runtime and gesture
questions were assessed against Emil Kowalski's
[animate-expo](https://github.com/emilkowalski/skills/blob/c8a79627b59d72d764d6ab6f2c87c09a48169833/skills/animate-expo/SKILL.md),
MIT, copyright 2026 Emil Kowalski. Local departures retain existing runtimes, SDK constraints,
platform navigation and static reduced-motion policies; no universal timings are imported.

Official documentation checked November 4, 2026:

- React Native, [native driver and caveats](https://reactnative.dev/docs/animations#using-the-native-driver)
  and [AccessibilityInfo events](https://reactnative.dev/docs/accessibilityinfo#addeventlistener).
- Expo, [Reanimated setup](https://docs.expo.dev/versions/latest/sdk/reanimated/).
- Software Mansion, [compatibility](https://docs.swmansion.com/react-native-reanimated/docs/guides/compatibility/),
  [shared values](https://docs.swmansion.com/react-native-reanimated/docs/core/useSharedValue/),
  [worklets](https://docs.swmansion.com/react-native-reanimated/docs/guides/worklets/) and
  [reduced motion](https://docs.swmansion.com/react-native-reanimated/docs/device/useReducedMotion/).

Context7 checks used Reanimated 4.7.1, React Native 0.87.1 and Expo 58.0.0 source IDs. Living
pages may document newer releases. Recheck installed versions, architecture and these API
contracts before implementation or after an SDK upgrade. Documentation establishes API
behavior, not tested app performance or a measured benefit from this skill.
