# UX/UI resource index

Research observed **2026-10-05**. This index catalogs curated web design, component, motion,
and illustration references with usage guidance, observed dates, and material access or
license limits.

Read this index when choosing an external reference, then inspect only the relevant source
pages. This directory is a set of options, not a required toolchain. Start the
implementation with `references/design-synthesis.md` (linked from `SKILL.md`) and the app's
own design owners.

## Start with the design problem

| Stuck on | Start here | Extract |
|---|---|---|
| A working app feels generic or hard to scan | [The Component Gallery](https://component.gallery/), [Mobbin](https://mobbin.com/), [Refero Styles](https://styles.refero.design/) | Task structure, complete flows, density, type roles and grouping |
| Navigation is crowded or unclear | [Navbar Gallery](https://www.navbar.gallery/), [The Component Gallery](https://component.gallery/) | Destination hierarchy, current location and narrow-screen behavior |
| Forms, actions or plan choices are unclear | [Mobbin](https://mobbin.com/), [CTA.gallery](https://www.cta.gallery/), [PricingPages.design](https://pricingpages.design/) | Information needed before acting, commitment, validation and recovery |
| A visual direction is underspecified | [DESIGNmd](https://designmd.ai/what-is-design-md), [Refero Styles](https://styles.refero.design/), [Kage](https://kage.design/) | Concrete principles mapped to existing tokens; observed versus inferred values |
| A public page lacks character | [Minimal Gallery](https://minimal.gallery/), [Land-book](https://land-book.com/), [Awwwards](https://www.awwwards.com/) | Composition, typography, imagery and content rhythm |
| A compatible component needs an implementation reference | [shadcn/ui](https://ui.shadcn.com/docs), [21st.dev](https://21st.dev/), [Shadcnblocks](https://www.shadcnblocks.com/) | Specific source, license, dependency/version fit and state contract |
| Interaction feedback feels rough | [60fps](https://60fps.design/), [MicroKit](https://microkit.co/), [Kinetics](https://kinetics.colorion.co/), [Motion Primitives](https://github.com/ibelick/motion-primitives/blob/main/README.md), [SmoothUI](https://smoothui.dev/) | Trigger, continuity, interruption, final state and reduced-motion alternative |
| A requested expressive effect needs research | [Landing Love](https://www.landing.love/), [Anime.js](https://animejs.com/), [Three.js](https://threejs.org/manual/pages/installation.html) | Purpose, rendering host, fallback, lifecycle and measured app cost |
| Illustration would explain an empty state or feature | [Kitbitz](https://kitbitz.art/), [3dicons](https://3dicons.co/) | A coherent kit, exact item rights, useful meaning and delivery cost |

## 01-13: Discovery, design systems and real patterns

All rows below observed **2026-10-05**.

| # | Resource | Best use, rights, and material limit |
|---|---|---|
| 01 | [Scrolltide](https://www.scrolltide.co/) | Public-page identity and visual moments; paid tiers and terms restrict source redistribution. |
| 02 | [DESIGNmd](https://designmd.ai/what-is-design-md) | Readable `DESIGN.md` examples; community kits carry item-level licenses and unverified quality. |
| 03 | [VibePrompt](https://vibeprompts.dev/) | Task-oriented layout and state prompts; displayed snippet semantics and reuse license were unverified. |
| 04 | [Minimal Gallery](https://minimal.gallery/) | Typography and composition; legal policy restricts gallery screenshots and metadata reuse; inspect original sites. |
| 05 | [Kage](https://kage.design/) | Reference-to-brief analysis examples; AI-generated breakdowns can err and cannot override workflow rules. |
| 06 | [Refero Styles](https://styles.refero.design/) | Visual roles and extracted systems; reconstructed examples are not original production source; terms limit redistribution. |
| 07 | [The Component Gallery](https://component.gallery/) | Cross-system pattern names and rationale; no unified license across linked systems; verify each upstream repo. |
| 08 | [Godly, now Recent](https://recent.design/info) | Broad visual exploration (redirects from `godly.website`); no verified general reuse license; showcase is not app UX proof. |
| 09 | [Awwwards](https://www.awwwards.com/) | Website art direction and evaluation criteria; award scores do not establish usability or accessibility; terms govern media. |
| 10 | [Landing Love](https://www.landing.love/) | Motion and landing-page sequencing; showcase videos do not prove runtime acceptance or grant reuse rights. |
| 11 | [Land-book](https://land-book.com/) | Website composition; Pro features are paid; inspect originals and separate site asset rights. |
| 12 | [Mobbin](https://mobbin.com/) | Shipped app screens and flows; paid account limits full flows; copyright terms govern captured screenshots. |
| 13 | [Hoverstat.es](https://www.hoverstat.es/about/) | Experimental interaction and art direction; novelty requires a clear user task and accessible fallback. |

## 14-18: Specific page and navigation decisions

All rows below observed **2026-10-05**.

| # | Resource | Best use, rights, and material limit |
|---|---|---|
| 14 | [Navbar Gallery](https://www.navbar.gallery/) | Navigation structures (`web-app` tag includes workspace/account patterns); confirm marketing vs signed-in nav fit. |
| 15 | [Footer Design](https://www.footer.design/info) | Footer grouping and closing rhythm; first decide whether a working app needs a footer. |
| 16 | [CTA.gallery](https://www.cta.gallery/) | Action clarity and commitment patterns; promotional conversion claims were unverified. |
| 17 | [Supahero](https://supahero.io/) | Public hero composition (linked with `screensdesign.com`); includes paid promotional placements. |
| 18 | [PricingPages.design](https://pricingpages.design/) | Plan-comparison structure; framed as inspiration, not permission to copy; screenshot prices are not live billing facts. |

## 19-26: Components and blocks

All rows below observed **2026-10-05** (item 19 MCP/proxy rechecked **2026-11-06**).

| # | Resource | Best use, rights, and material limit |
|---|---|---|
| 19 | [21st.dev](https://21st.dev/) | Authorized React component discovery; check individual component licenses separately from proprietary previews/terms (`docs.21st.dev/terms`). See boundary below. |
| 20 | [shadcn/ui](https://ui.shadcn.com/docs) | Owned, composable React source (`MIT`); verify installed Tailwind/primitive version and third-party registry licenses separately. |
| 21 | [Aceternity UI](https://ui.aceternity.com/) | Selective animated blocks; separates free components from paid team/lifetime blocks; check license and bundle cost. |
| 22 | [Magic UI](https://magicui.design/) | Bounded effects and marketing blocks; free `MIT` core and commercial Pro (`magicui.design/license`) are separate. |
| 23 | [Motion Primitives](https://github.com/ibelick/motion-primitives/blob/main/README.md) | Layout continuity details (`MIT` in repo `LICENCE.md`); README labels it beta; inspect source and dependencies. |
| 24 | [Uiverse](https://uiverse.io/) | Isolated CSS/HTML elements (`MIT` in Galaxy repo; site Terms text empty in check); supply native semantics and state yourself. |
| 25 | [SmoothUI](https://smoothui.dev/) | Animated React/shadcn blocks (`MIT`); accessibility matrix is vendor-reported; verify keyboard/focus locally. |
| 26 | [Shadcnblocks](https://www.shadcnblocks.com/) | Compatible shells and sections; bespoke commercial license/terms govern free and paid blocks; check before copying. |

## 27-34: Motion, materials and graphics

All rows below observed **2026-10-05**.

| # | Resource | Best use, rights, and material limit |
|---|---|---|
| 27 | [Kinetics](https://kinetics.colorion.co/) | Motion easing/stiffness previews ([GitHub source](https://github.com/ckissi/kinetics)); MIT footer claim lacked a verified repo license file. |
| 28 | [MicroKit](https://microkit.co/) | Small React/CSS control interactions (`MIT` first-party repo); adapted third-party examples carry separate acknowledgements. |
| 29 | [Liquid Glass by Sam Asante](https://github.com/samasante/liquid-glass) | Headless React optical lens (`MIT`); SVG/WebGL refraction differs across browsers (`BROWSERS.md`); verify image rights and GPU cost. |
| 30 | [Anime.js](https://animejs.com/) | DOM/SVG timelines ([GitHub](https://github.com/juliangarnier/anime)); match versioned API and existing motion owners; verify bundle cost locally. |
| 31 | [Three.js](https://threejs.org/manual/pages/installation.html) | Genuine 3D/spatial scenes (`MIT`); own responsive canvas sizing and explicit GPU texture/geometry disposal. |
| 32 | [Shadertoy](https://www.shadertoy.com/view/MsdBzX) | Procedural shader ideas; terms page was unreachable (`terms`), and authors set per-shader licenses (often noncommercial); check rights first. |
| 33 | [The Book of Shaders](https://thebookofshaders.com/00/) | Fragment shader fundamentals; freely readable text states all rights reserved; treat as learning material only. |
| 34 | [Three.js Journey](https://threejs-journey.com/) | Optional paid 3D/WebGPU course; only select intro lessons are free, and course content rights are separate. |

## 35-36: Illustration assets

All rows below observed **2026-10-05**.

| # | Resource | Best use, rights, and material limit |
|---|---|---|
| 35 | [Kitbitz](https://kitbitz.art/) | Coherent themed kits (nature/cyberpunk titled free `CC0`, full contents unextracted in check); verify item license before download. |
| 36 | [3dicons](https://3dicons.co/) | 3D onboarding/feature icons; mixes free/open-source variants with premium offerings; check selected variant license and small-size legibility. |

## Supplemental reference choices

Observed **2026-10-24**. These extend discovery beyond the 36-site set without refreshing
those older assessments. Public page text was inspected; no paid content, recording playback,
generated output or runtime behavior was tested. Rights to redistribute prompts and media
were not established. Recheck the selected item before use.

| Reference | Use when | Material limit |
| --- | --- | --- |
| [60fps](https://60fps.design/) | A gesture, transition or multi-step interaction needs a sequence reference; its index includes app examples, motion and storyboards | A recording is a behavior reference, not reusable implementation or measured timing; inspect the actual sequence and its rights |
| [Motionin](https://www.motionin.design/) | A requested expressive section needs a prompt/spec reference | Its FAQ describes section prompts/specs and a separate studio service; do not assume a complete website or accepted runtime output from one prompt |
| [Collect UI](https://collectui.com/) | Broader website/interface inspiration is useful | Current homepage describes curated designs; it does not establish captured production flows. For shipped-screen and flow research, start with [Mobbin](https://mobbin.com/) |

## Design tooling references

Observed **2026-10-26** (refreshed **2026-11-25**). Consult these when the task needs machinery
beyond visual inspiration. Source inspection establishes the interfaces below; none of these
external tools were run locally. These are research options, not required installs or
replacements for project design owners.

| Reference | Use when | Material limit |
| --- | --- | --- |
| [UI UX Pro Max](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/tree/28b3b8dee8c976df4fa3e94aed4e092ad43fcb03) | Palette, typography or stack advice needs searchable data and persisted recommendations | MIT source; font and asset rights remain separate. Search can return no match. Stack retrieval is separate from design-system generation; check applicability to the installed stack before adopting advice |
| [Impeccable](https://github.com/pbakaus/impeccable/tree/2fc5e1459e) | A confirmed design-review need calls for a 62-rule Rust static/browser detector (`--sarif`, `--report-unused-ignores`) or live browser variants | Apache-2.0 source (v4.11.1, Nov 26, 2026 UTC). Downloads a self-contained engine binary and installs edit hooks on some paths; live mode's copy-edit Apply can invoke local `codex`/`claude` with sandbox and approval bypass unless `IMPECCABLE_LIVE_COPY_AGENT=chat` or `off` is set. Inspect telemetry (`DO_NOT_TRACK=1`) and hooks before authorized use |
| [Hallmark](https://github.com/Nutlope/hallmark/tree/04977e15f3) | A new landing-page workflow wants Floor/Reflex/Finish browser linting (`sloplint.mjs`), dealt theme materials, or Wikimedia Commons photo attribution | MIT source (v2.0.0, Nov 11, 2026). Browser checks need Puppeteer/Chrome; Wikimedia photo entries carry per-image CC0/CC-BY licenses rather than stock-site terms. Opinionated house rules (eyebrow/word caps) may conflict with an app's existing `DESIGN.md` |
| [Meng To Skills](https://github.com/MengTo/Skills/tree/a5b1d3d28b) | Reference-study workflows (originality audits, stitched full-page captures, Three.js material/camera recipes, SVG spot illustration specs) | MIT source (217 skills, Nov 25, 2026). Broad showcase catalog with uneven verification depth across individual folders; inspect specific skill and demo rights before adapting ideas |

## Agentic UI and motion registries

Observed **2026-11-25**. Source and homepage text were inspected; none were installed or run.
Check free vs. Pro boundaries, token secrets, and hosted endpoints before adoption.

| Reference | Best use | License and material limit |
| --- | --- | --- |
| [affectUI](https://github.com/flohoeller/affectui/tree/f5cced0134) | Zero-dependency single-file React 19 `.tsx` components for agent trees, tool calls, traces, approvals, and chat via shadcn CLI/MCP | 75 free MIT items (`affectui.com`); Pro items require a one-time commercial license (from $249) and `AFFECTUI_TOKEN` env var (never commit tokens) |
| [BoardUI](https://github.com/BoardUI/boardui/tree/c87984b6bb) | React 19 + Tailwind v4 + React Aria design system for dashboards and agentic chat (90 free items, semantic dark tokens, RTL) | MIT free repo; Pro (10 templates + 30 components) uses commercial BoardUI License; React Aria primitives require client modules (`"use client"`) in App Router |
| [beUI](https://github.com/starc007/ui-components/tree/1d7fd24337) | Animated Motion + Tailwind React components (plus [beui-native](https://github.com/starc007/beui-native/tree/ab3e58aa75) for React Native) via shadcn CLI or public MCP (`mcp.beui.dev`) | MIT free repos; Pro tier (`pro.beui.dev`) is commercial and separate |
| [Transitions.dev](https://github.com/Jakubantalik/transitions.dev/tree/ec4d48f5aa) | 48+ UI transition recipes, `transitions-agent` motion scanner/GitHub Action, and Refine tool | Dual license: custom Transitions.dev License on `transitions/` and `skills/` (free commercial product use, no redistribution as competing pack) + MIT tooling; `fix` sends affected files to `api.transitions.dev` (Free 10/mo, Business $59/mo) |
| [Bencho](https://github.com/cabralorenzo/bencho/tree/84dfcee170) | 48 interactive React micro-interaction blocks and 24 Web Audio API synthesized interface sounds via shadcn registry | MIT for repo code (excludes brand, goat mark, and site photos; two sounds notice `cuelume`); Pro (180+ blocks, MCP) is commercial |
| [OriginKit](https://github.com/vellum-ai/originkit/tree/d27526a2e2) | 50 free animated React/Framer components via MCP plugin | MIT MCP repo; fetching source needs a free `cmp_live_...` API key (10 fetches/day limit) |
| [HorizonX](https://horizonx.so/) | Commercial UI kits, animated shaders, textures, Figma files, and MCP | Subscription ($24.99/mo); no public GitHub repo inspected; verify commercial terms before use |

## 21st.dev Magic proxy and request boundary

Checked **2026-11-06**. The [21st MCP guide](https://21st.dev/mcp) covers component search,
source retrieval, installation, generation, and publishing, and its legacy
[Magic MCP proxy](https://github.com/21st-dev/magic-mcp/blob/6b5299e8a83ceffa73d4fc4e148905bb3eeeeb55/src/index.ts)
forwards requests from a local client to 21st's hosted service (ISC license at that commit).
For search, send only a generic description of the needed component. Send project-specific
code or context to hosted generation only when the user has explicitly authorized that data
and provider. Search access does not authorize installing an MCP server, paying for plans
([21st.dev plans](https://21st.dev/plans)), or publishing project code; check item licenses
and [21st.dev terms](https://docs.21st.dev/terms) before adopting any component.

## How to read the evidence

Supplemental motion sources reviewed October 7 UTC, October 6 Pacific, 2026:
[Prompt Motion](https://prompt-motion.com/) and [Oneshotted](https://oneshotted.io/) pair
creator prompts with results; [Motion Prompts](https://motionprompts.dev/developers/) supplies
agent-readable mechanics and composition metadata under noncommercial reuse terms.
Use these to clarify a requested effect, with prompt provenance, rights, and runtime fit checked
at the selected item. Route live state transitions to `ui-motion` and timeline videos to
`motion-film`. Gallery UI footage does not prove working interactions. These supplement the
36-site set; they do not change its October 5 observation date.

The table notes separate inspected first-party facts from analytical risks. Research into
public offerings, documentation, and source is not a DOM/axe audit, performance benchmark,
verified download, paid entitlement check, or successful builder run.

Site counts, plan details, legal terms, integration commands, and URLs can change. Recheck
the selected item and original source before adoption. Keep code, prompt, screenshot, font,
and asset rights separate; a gallery entry does not grant permission to redistribute the
depicted design. This index contains original analysis and direct links; it does not
redistribute site prompts, component catalogs, images, or paid course materials.
