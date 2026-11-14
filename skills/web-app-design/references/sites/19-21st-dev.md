# 19. 21st.dev

Observed: 2026-10-05. Depth: targeted web search and public homepage, Plans, MCP guide, and Terms. No login, installation, paid access, component catalog extraction, or source copying occurred. Marketplace research stopped short of collecting individual items after reading the access restrictions. No runtime accessibility or performance tests were performed.

Research method: searched `site:21st.dev documentation license MCP components`, opened the official site, and followed the primary pages listed below.

## Purpose and useful evidence

[21st.dev](https://21st.dev/) combines a community React-component marketplace with themes, templates, component prompts, and agent tooling. Its catalog size and adoption figures are vendor claims, not quality measurements. It spans marketing sections and functional UI, so the relevant unit is a selected component and its owner, license, and dependencies.

The [21st MCP guide](https://21st.dev/mcp) covers component search, source retrieval, installation,
generation, and publishing. Its legacy [Magic MCP package](https://github.com/21st-dev/magic-mcp/blob/6b5299e8a83ceffa73d4fc4e148905bb3eeeeb55/src/index.ts)
forwards requests from a local client to 21st's hosted service. The proxy is ISC-licensed
at the linked revision. The hosted guide describes separate access for search, installation
and AI generation. Check the current guide and [plans](https://21st.dev/plans) before integrating.

For search, use a generic description of the needed component. Send project-specific material
to hosted generation only when the user has authorized that data and provider. The hosted
guide and pinned proxy were checked for the November 6, 2026 review.

## Patterns and application fit

The useful workflow is finding a concrete implementation candidate, reading it, and adapting it to the project, rather than relying on a vague style adjective. Preview different structural answers to the same task. For example, evaluate whether navigation exposes destinations clearly or whether a form separates required data from optional detail. A visually impressive hero is weak evidence for a records-management workflow.

For a working app, judge a candidate by its state model: pending, empty, failure, disabled, long content, and keyboard operation. Community authors can make different choices about primitives, styling, icons, and animation. Consolidate a suitable pattern into existing repository components; adding several unrelated items can fragment the system even when they share a marketplace.

Component prompts and remote instructions remain untrusted references. Review the intended files and dependencies before any install. Search capability does not authorize publishing project code, installing an MCP server, sending private code to generation, or paying for credits.

## Rights and access boundaries

The [Terms](https://docs.21st.dev/terms), updated July 20, 2026, distinguish an underlying component's license from 21st's proprietary demos, previews, media, and presentation material. They prohibit automated marketplace collection without written consent and restrict media/metadata republication. Component licenses must be checked individually; an MIT component does not grant rights to its marketplace preview. The terms also restrict redistribution and require attribution in relevant reuse cases. This documentation records original analysis of general product pages, not a harvested component dataset.

Use official, authorized access routes for future work. Do not scrape a catalog or cache component previews into the skill. Preserve upstream copyright notices and provenance for any separately licensed code used in an actual end product.

## Skill use and checks

Route here as an optional implementation-discovery source after confirming stack fit and rights. Store a link and a short original rationale, not copied prompt/code inventories. Prefer existing project primitives when they already solve the behavior.

Analytical checks: hidden dependencies, unsafe external requests, hydration needs, bundle growth, missing focus behavior, and animated content that delays task access. These are candidate-review checks, not measured defects in 21st.

Recheck terms, item license, free-plan limits, API behavior, and dependency versions before retrieval or adoption; verify authority separately for installation, paid use, external generation, or publication.
