---
name: fit-surface
description: >-
  Audit or fix one web surface across viewport widths, chrome, themes, and states in the
  running app (overflow, clipping, worst-case text). Audits edit nothing. Not for new
  design (web-app-design), AI-slop UI (deslop-ui), motion (ui-motion, review-animations),
  model-chosen UI (bounded-generative-ui), or launch harnesses (app-verifier).
compatibility: Needs a way to load the running app at chosen viewport sizes and read DOM measurements, such as browser automation or a headless browser script. Without it, source fixes can proceed but rendered fit is reported unverified.
---

# Fit surface

Make one existing page, tab, table, panel, or dialog fit every box it can render in, with
every kind of data it will meet. Respect the requested mode; an unclear request is an audit. Audit mode measures and reports;
it changes no application or design files. Edit mode fixes confirmed defects and rechecks
them. Preserve the repository's design system, primitives, and library choices.

## Procedure

1. **Derive the boxes.** If a named target path does not exist or contains no web UI surface,
   stop and report the gap instead of guessing scope. Read the repository's instructions and its design owner: the design
   document, layout guidance, app shell, and tokens. Record the supported viewport range, the
   design target, the floor, the height budget, every chrome state that changes width (such as
   a sidebar open or collapsed, or a docked panel), and the shipped themes. Compute the usable
   box for each width and chrome state: viewport minus chrome minus the page scrollbar where
   scrollbars take space. A narrow container inside a wide viewport, such as a dialog or
   drawer, is its own box. If the repository states no range, propose one and label it
   assumed. Done when a box table lists every width and chrome state with its usable width,
   and each value cites a source or is labeled assumed.

2. **Get the surface rendering.** Find the repository's no-login fixture harness, component
   specimen page, or seeded local entry before declaring rendering unavailable. Cover every
   view (in-page tabs, expanded rows, menus, dialogs, and drawers, not just routes) and
   follow the observation traps and state-setup rules in [measuring](references/measuring.md).
   Load dense, realistic data; never submit forms, mutate real data, or change permissions.
   A sandbox can stop a browser from starting; record the error without weakening the
   sandbox and report rendered fit as unverified. Done when every listed view renders real
   content, or the blocker is recorded and rendered fit is marked unverified.

3. **Measure the matrix.** Read [measuring](references/measuring.md) for the method, traps,
   and state matrix. For phone, tablet, or installed-web-app surfaces, also use [mobile
   fit](references/mobile-fit.md). Use the bundled [browser collector](references/browser-collector.md)
   for repeatable geometry evidence when the existing rig supports it. For each box, chrome
   state, and theme, start static geometry checks at a recorded scroll position, then
   compare document `scrollWidth` with `clientWidth`, each scroller's scroll size with its
   client size, and element edges with their container's edges. Check height against the
   budget. Quote the viewport with every number. Then drive the data states that apply. A
   narrow request still measures every box its fix can reach; a data state that cannot change
   size may be skipped with that reason. Done when every matrix cell has a
   measurement or a stated reason it has none.

4. **Find each floor.** For every overflow, name what sets the minimum width and compare it
   with the box in pixels. A table's floor is the sum of its declared column widths, whatever
   the box. Other floors come from fixed widths, unwrapped strings, and flex children that
   cannot shrink. Done when each overflow has a measured floor, a box width, and the owning
   source location.

5. **Fix at the owning layer.** In audit mode, propose fixes and skip to step 7. In edit
   mode, fix the shared primitive or token before adding a per-page override, and say which
   layer changed. Edit mode does not authorize commits, pushes, or dependency installs. Apply these rules:
   - Key floors to the container's width, with a container query or the repository's
     equivalent, so they step down when chrome narrows the box. A viewport breakpoint cannot
     see chrome.
   - Declare the order in which columns give way. The identifying column and the facts the
     reader came for never give way.
   - Keep every hidden or clipped fact reachable through a tooltip that also opens on
     keyboard focus, a detail view, or a summary.
   - Keep the horizontal scroll a dense comparison grid needs. Keep each row's identity and
     key total in view while it scrolls. Propose scroll for any other table only where the
     design owner allows it.
   - Reserve scrollbar space where it affects layout and keep result geometry stable during
     typing and refetching within the recorded height budget. Use fixed-height scrolling only
     when the design owner calls for it; otherwise choose suitable minimum or maximum sizing.
     Recheck reflow and control reachability in short viewports and at supported zoom levels.
   Done when every confirmed overflow in the requested surface has a fix in its owning layer,
   each one outside it is reported with its floor and a proposed fix, and the give-way order
   is written down.

6. **Recheck affected cells.** Re-measure every box, chrome state, theme, and data state the
   change can reach, including other callers of a changed primitive. Match initial conditions
   for before and after checks; preserve action-produced scroll for interaction continuity
   as described in the measurement method. If a fix causes a regression in another viewport,
   chrome state, theme, data state, or caller, revert or narrow it before continuing. Run the
   repository's required gates. Restore the original theme and viewport. Done when each
   affected cell passes with numbers, or each failure is listed with its measurement.

7. **Report.** Give the box table, then the matrix with every cell marked covered, skipped
   with a reason, or unreachable. List findings with viewport, chrome state, theme, measured
   numbers, and location. For edit mode, add each fix and its layer, the give-way order, and
   exact gate commands with their exit statuses. List choices made where the repository was
   silent, with confidence, least confident first. Source-only work means rendered fit is
   unverified; separate passed, failed, unavailable, and unrun checks explicitly. Done in audit
   mode when the box table, matrix, and findings are delivered without editing app files; done
   in edit mode when affected cells pass (or remaining failures are listed with measurements),
   required repository gates pass with command/exit receipts, and every cell is accounted for.

## Provenance

Generalized from one product's repeated viewport-fit and state-stress work. Read
[sources](references/sources.md) only when reviewing provenance or updating this method.
