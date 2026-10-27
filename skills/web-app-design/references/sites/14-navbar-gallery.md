# 14. Navbar Gallery

Observed: 2026-10-05. Depth: targeted web search, public homepage, web-app collection, and mobile collection. Pages were readable without signing in. Screenshots and linked sites were not exercised in a running browser; this is reference research, with no accessibility or performance measurements.

Research method: searched `site:navbar.gallery navigation design about examples`, opened the official site, and followed the primary pages listed below.

## Purpose and useful evidence

[Navbar Gallery](https://www.navbar.gallery/) concentrates on navigation rather than whole-site mood boards. Its taxonomy includes static or sticky bars, dropdowns, mega menus, sidebars, search, announcement bars, full-screen menus, and breadcrumbs. Entries link to their own reference page and the original website. This makes it useful for designers and developers who have a specific navigation decision to resolve.

The [web-app collection](https://www.navbar.gallery/style/web-app) explicitly discusses workspace switching, user accounts, and deep feature navigation. However, the sampled entries include ToDesktop, Firecrawl, and WorkOS website links. A product-company website can show marketing navigation rather than the signed-in application. The label is a discovery hint, not evidence that the gallery covers every operational state. The separate [mobile collection](https://www.navbar.gallery/mobile-navigation) provides another route for examining narrow-screen navigation.

## Patterns and application fit

Use this resource after identifying the user's destinations and frequency of movement. Compare a persistent sidebar for frequent cross-section work, a compact top bar for a shallow hierarchy, and breadcrumbs for a deep path. Record which information is visible before interaction, how many levels are exposed, and whether local page navigation is distinct from global navigation.

For a working app, the most useful extraction is a relationship: workspace identity near workspace actions, account controls apart from task controls, and current location visible without opening a menu. Those are design questions for our app, not claims that a particular entry has solved them. A large marketing mega menu may be a poor fit for repeated daily tasks; a visually striking full-screen menu can add unnecessary travel between destinations.

Compare desktop and mobile references deliberately. Decide which links stay visible, which collapse, and what remains reachable when labels are long or the user has more workspaces than the example. Avoid simply shrinking the desktop screenshot.

## Reuse, access, and integration

The inspected gallery pages expose reference images and outbound links, not an implementation package or a verified code license. No subscription gate appeared in those pages. No blanket license for reusing screenshots, trademarks, illustrations, or source code was located in the sampled material. Link to the original reference and write an original pattern explanation; do not treat a gallery image as a reusable asset. Browsing requires no application dependency.

## Skill use and checks

The future skill should route navigation work here only when navigation is the actual problem. Select two or three references with different structural answers, then produce a destination map and responsive behavior notes. Implement with the repository's existing navigation primitives and tokens.

Analytical checks: keyboard access to every destination, visible focus, current-page indication, Escape behavior, focus return, touch operation, and header overlap at zoom. Hover-only flyouts and custom full-screen interactions deserve extra inspection. These are possible failure modes to verify locally, not measured defects in this gallery.

Recheck when the gallery taxonomy changes, a selected original site redesigns, a reference link disappears, or copying code/assets becomes part of the proposed implementation.
