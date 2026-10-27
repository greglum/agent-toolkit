# Measuring fit

Read this at step 3. A screenshot suggests; a measurement decides. A break predicted from
source is a lead until it renders.

## Method

- Define one measurement helper in the page once per load and call it after each navigation.
  A client-side route change keeps the page, so one helper can sweep a whole section.
- Reset every scroll position before measuring. A scroller left scrolled by an earlier probe
  reports its rows hundreds of pixels off, and the wrong number survives into the report.
- Quote the viewport (width by height), chrome state, and theme with every number. Take before
  and after figures at the same scroll state.
- Horizontal fit: `document.documentElement.scrollWidth` against `clientWidth`, then each
  scroll container's `scrollWidth` against its `clientWidth`, then each element's right edge
  against its container's right edge less padding.
- Vertical fit: the surface's height against the height budget, and each bounded region's
  `scrollHeight` against `clientHeight`.
- Stability: record the position of content below a search box or result list, type several
  characters, let a refetch land, and measure again. Any movement is a finding.
- Clipped text: compare the element's `scrollWidth` with its `clientWidth`, then confirm the
  full value is reachable by pointer and by keyboard.

## Observation traps

- **Wrong port.** A configured port is a request. If it is taken, the server picks another.
  Read the port it reports before calling the app broken.
- **Setup screens.** A sign-in, missing-credentials, or configuration page means the
  environment is not set up. It is not a layout finding.
- **Default tab only.** Driving routes by URL lands on each page's default tab. Enumerate
  in-page tabs, or state that only defaults were measured.
- **Unstyled harness.** A fixture page that skips the app stylesheet or theme setup leaves
  tokens undefined. Borders and backgrounds then look broken when they are not.
- **Overlay scrollbars.** On systems with overlay scrollbars the page scrollbar takes no
  width, so a box that fits there can overflow where scrollbars take 15 to 17 pixels. Measure
  where scrollbars take space, or subtract the width explicitly.
- **Stale composite.** A screenshot taken right after setting `scrollTop` from script can show
  the old frame. Trust the DOM over the image.
- **Hidden pane.** A background tab or hidden preview may not paint. Animation frames never
  fire and exiting overlays stay mounted. Bring it to the front, or measure synchronously.
- **Stale module.** After a large edit or a redeploy, the open tab can serve old code or dead
  chunk references that crash every route. Hard reload, and compare the served module with the
  file before concluding an edit did nothing.
- **False empty or error.** A first load can return auth errors and render empty states, and
  an HTTP 200 can carry an error body. Confirm real content rendered. Reload once before
  believing a blank page.
- **Synthetic input.** A scripted `.click()` may not open a menu or combobox that listens for
  pointer events. Use real pointer input.
- **Wrong node.** A component ref can point at a wrapper rather than the node on screen.
  Measure from the scroll container that owns the element.
- **Console noise.** Errors from browser extensions are not application errors. Check the
  origin.

## State matrix

Select cases from the actual props, data contracts, and reachable branches before rendering.
Record why each axis applies or is skipped: quantity needs repeated items, variable text needs
a variable source, and a mode needs product support. Combine axes when the code couples them
or a measured failure warrants it; avoid a blind cross product. Include sibling pressure for
resizable or nested panels, not just viewport changes.

Cover every row that applies to the surface, at each box. First list each rendered field with
its real limit from the schema, types, API contract, or domain. Distinguish a verified
unbounded field from an unknown limit. An unknown limit is an evidence gap, not by itself a
UI defect or permission to restrict accepted data. Use plausible values while marking the
maximum unverified; report a defect when a supported value causes an observed failure.

- **Volume:** zero rows; zero because a filter excluded everything (different copy and
  actions); exactly one; enough to scroll several screens; more than one page, so paging,
  grouping, and totals engage together.
- **Shape:** the longest realistic string in every text field, with a wrap or truncate
  decision per field (a truncated fact stays reachable); every nullable field empty at
  once, with the record still identifiable; the largest, smallest, zero, and negative numbers
  and the earliest and latest dates where legal; accented, non-Latin, and emoji text where
  users can enter it; colliding values such as two people with one display name.
- **Lifecycle:** first load, with a placeholder that holds the final layout; refetch while
  reading, keeping scroll, selection, and expanded rows; request failure with a clear message
  and retry; an action in flight; an optimistic update that fails.
- **Permission:** each role that can reach the surface, including read-only. An unexplained
  disabled control is a finding.
- **Reading conditions:** 200% zoom, and right-to-left text where the product supports it.

Reach each state by changing data where the surface receives it: the seed data, an existing
fixture harness, or a throwaway fixture that is removed before the work is handed back. Never
force a break by editing markup or styles. Import the actual component with its existing
providers and tokens. Confirm the intended fixture reached the rendered view; a refetch that
replaces it or missing provider is a harness failure. Hold loading and pending fixtures until
the observer advances them, instead of relying on a short timeout. Keep empty, one, and huge in separate fixtures so
one failure cannot mask another, and recheck every fixture after a fix, the ordinary one
included. Mark a state unreachable when none of those can produce it. Never submit real forms,
mutate real data, deploy, or change permissions to reach a state. Theme and viewport are user
state: record them first and restore them after.
