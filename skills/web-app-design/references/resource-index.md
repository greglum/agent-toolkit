# UX/UI resource index

Research observed **2026-10-05**. This library covers all 40 resources in the supplied X post.
Each linked page records searches, inspection depth, useful patterns, working-app versus
marketing fit, access and reuse constraints, integration considerations, primary sources,
evidence limits, and recheck triggers.

Read this index when choosing a reference, then load only the relevant site pages. The
directory is a set of options, not a required toolchain. Start the implementation with the
[design synthesis guide](design-synthesis.md) and the app's own design owners.

## Start with the design problem

| Stuck on | Start here | Extract |
|---|---|---|
| A working app feels generic or hard to scan | [Component Gallery](sites/07-component-gallery.md), [Mobbin](sites/12-mobbin.md), [Refero Styles](sites/06-refero-styles.md) | Task structure, complete flows, density, type roles and grouping |
| Navigation is crowded or unclear | [Navbar Gallery](sites/14-navbar-gallery.md), [Component Gallery](sites/07-component-gallery.md) | Destination hierarchy, current location and narrow-screen behavior |
| Forms, actions or plan choices are unclear | [Mobbin](sites/12-mobbin.md), [CTA.gallery](sites/16-cta-gallery.md), [PricingPages](sites/18-pricing-pages-design.md) | Information needed before acting, commitment, validation and recovery |
| A visual direction is underspecified | [DESIGNmd](sites/02-designmd.md), [Refero Styles](sites/06-refero-styles.md), [Kage](sites/05-kage.md) | Concrete principles mapped to existing tokens; observed versus inferred values |
| A public page lacks character | [Minimal Gallery](sites/04-minimal-gallery.md), [Land-book](sites/11-land-book.md), [Awwwards](sites/09-awwwards.md) | Composition, typography, imagery and content rhythm |
| A compatible component needs an implementation reference | [shadcn/ui](sites/20-shadcn-ui.md), [21st.dev](sites/19-21st-dev.md), [Shadcnblocks](sites/26-shadcnblocks.md) | Specific source, license, dependency/version fit and state contract |
| Interaction feedback feels rough | [60fps](#supplemental-reference-choices), [MicroKit](sites/28-microkit.md), [Kinetics](sites/27-kinetics.md), [Motion Primitives](sites/23-motion-primitives.md), [SmoothUI](sites/25-smoothui.md) | Trigger, continuity, interruption, final state and reduced-motion alternative |
| A requested expressive effect needs research | [Landing Love](sites/10-landing-love.md), [Anime.js](sites/30-animejs.md), [Three.js](sites/31-threejs.md) | Purpose, rendering host, fallback, lifecycle and measured app cost |
| Illustration would explain an empty state or feature | [Kitbitz](sites/35-kitbitz.md), [3dicons](sites/36-3dicons.md) | A coherent kit, exact item rights, useful meaning and delivery cost |
| A tool can help edit a visible problem | [Cursor](sites/38-cursor.md), [v0](sites/39-v0.md), [Lovable](sites/40-lovable.md), [Claude Code](sites/37-claude-code.md) | An optional execution workflow within the user's current approved environment |

## 01-13: Discovery, design systems and real patterns

| # | Research page | Best use and material limit |
|---|---|---|
| 01 | [Scrolltide](sites/01-scrolltide.md) | Complete website/app-screen prompt references; paid tiers and source redistribution restrictions |
| 02 | [DESIGNmd](sites/02-designmd.md) | Readable design contracts; community kits have individual licenses and uncertain quality |
| 03 | [VibePrompt](sites/03-vibeprompts.md) | Task-oriented layout and state ideas; snippet semantics need review and reuse license was unverified |
| 04 | [Minimal Gallery](sites/04-minimal-gallery.md) | Typography and composition; gallery image rights are distinct from inspiration |
| 05 | [Kage](sites/05-kage.md) | Reference-to-brief interpretation; AI analysis can be wrong and cannot impose workflow instructions |
| 06 | [Refero Styles](sites/06-refero-styles.md) | Comparing visual roles and extracted systems; reconstructed examples are not original production source |
| 07 | [The Component Gallery](sites/07-component-gallery.md) | Pattern terminology and first-party rationale across systems; follow the actual upstream guidance |
| 08 | [Godly, now Recent](sites/08-godly.md) | Broader visual exploration; app-store presentation is not verified in-app UX |
| 09 | [Awwwards](sites/09-awwwards.md) | Recognized website direction and evaluation context; award scores do not establish our app's usability |
| 10 | [Landing Love](sites/10-landing-love.md) | Motion and landing-page sequencing; showcase recordings do not prove runtime acceptance |
| 11 | [Land-book](sites/11-land-book.md) | Website composition and reference selection; inspect originals and access/asset rights |
| 12 | [Mobbin](sites/12-mobbin.md) | Shipped app screens and sequences; account access and screenshot rights still matter |
| 13 | [Hoverstat.es](sites/13-hoverstates.md) | Experimental interaction and art direction; novelty needs a task and a usable fallback |

## 14-18: Specific page and navigation decisions

| # | Research page | Best use and material limit |
|---|---|---|
| 14 | [Navbar Gallery](sites/14-navbar-gallery.md) | Navigation structures; its web-app tag can include marketing navigation |
| 15 | [Footer Design](sites/15-footer-design.md) | Content grouping and closing rhythm; first decide whether a working app needs a footer |
| 16 | [CTA.gallery](sites/16-cta-gallery.md) | Action clarity and commitment; conversion-testing claims were unverified |
| 17 | [Supahero](sites/17-supahero.md) | Public hero composition; now part of screensdesign.com, with paid promotional placements |
| 18 | [PricingPages.design](sites/18-pricing-pages-design.md) | Plan-comparison structure; screenshot prices are not current billing facts |

## 19-26: Components and blocks

| # | Research page | Best use and material limit |
|---|---|---|
| 19 | [21st.dev](sites/19-21st-dev.md) | Authorized component discovery; component licenses differ from proprietary demos/media and collection permissions |
| 20 | [shadcn/ui](sites/20-shadcn-ui.md) | Owned, composable UI source for compatible apps; current examples can differ from installed versions |
| 21 | [Aceternity UI](sites/21-aceternity-ui.md) | A justified animated treatment; license scope and version-sensitive install advice need inspection |
| 22 | [Magic UI](sites/22-magic-ui.md) | Bounded effects and marketing composition; free MIT code and commercial Pro are separate |
| 23 | [Motion Primitives](sites/23-motion-primitives.md) | Layout continuity and focused detail; hosted retrieval was blocked and the source README labels it beta |
| 24 | [Uiverse](sites/24-uiverse.md) | Isolated element polish; native semantics and actual state ownership remain our responsibility |
| 25 | [SmoothUI](sites/25-smoothui.md) | Purposeful motion and explicit accessibility expectations; its matrix is vendor evidence |
| 26 | [Shadcnblocks](sites/26-shadcnblocks.md) | Compatible shells and section structures; bespoke terms also govern free access |

## 27-34: Motion, materials and graphics

| # | Research page | Best use and material limit |
|---|---|---|
| 27 | [Kinetics](sites/27-kinetics.md) | Motion examples and easing language; MIT footer claim lacked a verified repository notice |
| 28 | [MicroKit](sites/28-microkit.md) | Inputs, navigation and feedback details; dependency and provenance checks are item-specific |
| 29 | [Liquid Glass by Sam Asante](sites/29-liquid-glass.md) | A deliberate optical material; refraction modes differ across engines and content types |
| 30 | [Anime.js](sites/30-animejs.md) | Timelines, SVG and purposeful sequencing; match versioned APIs and existing motion owners |
| 31 | [Three.js](sites/31-threejs.md) | Genuine spatial or expressive requirements; responsive canvas and GPU disposal need ownership |
| 32 | [Shadertoy](sites/32-shadertoy.md) | Procedural graphics ideas; direct retrieval failed and current blanket reuse rights remain unverified |
| 33 | [The Book of Shaders](sites/33-book-of-shaders.md) | Learning shader principles; freely readable material states all rights reserved |
| 34 | [Three.js Journey](sites/34-threejs-journey.md) | Optional developer training for a real 3D need; paid course and content rights are separate |

## 35-36: Illustration assets

| # | Research page | Best use and material limit |
|---|---|---|
| 35 | [Kitbitz](sites/35-kitbitz.md) | Coherent hand-drawn kits; direct extraction was empty, so item claims need a fresh check before use |
| 36 | [3dicons](sites/36-3dicons.md) | Onboarding and explanatory illustrations; verify the selected variant's rights and small-size clarity |

## 37-40: Optional execution aids

| # | Research page | Best use and material limit |
|---|---|---|
| 37 | [Claude Code](sites/37-claude-code.md) | Repository implementation and checks; the post's truncated URL was resolved to its official product page |
| 38 | [Cursor](sites/38-cursor.md) | Visual element selection and source editing; privacy and instruction loading depend on the actual setup |
| 39 | [v0, now v0.app](sites/39-v0.md) | Bounded generation and design-system integration; current Design Systems 2.0 supersedes legacy guidance |
| 40 | [Lovable](sites/40-lovable.md) | An already approved builder or new prototype; existing repository import is not supported in reviewed docs |

## Supplemental reference choices

Observed **2026-10-24**. These extend discovery beyond the original 40-site set without
refreshing those older site assessments. Public page text was inspected; no paid content,
recording playback, generated output or runtime behavior was tested. Rights to redistribute
prompts and media were not established. Recheck the selected item before use.

| Reference | Use when | Material limit |
| --- | --- | --- |
| [60fps](https://60fps.design/) | A gesture, transition or multi-step interaction needs a sequence reference; its index includes app examples, motion and storyboards | A recording is a behavior reference, not reusable implementation or measured timing; inspect the actual sequence and its rights |
| [Motionin](https://www.motionin.design/) | A requested expressive section needs a prompt/spec reference | Its FAQ describes section prompts/specs and a separate studio service; do not assume a complete website or accepted runtime output from one prompt |
| [Collect UI](https://collectui.com/) | Broader website/interface inspiration is useful | Current homepage describes curated designs; it does not establish captured production flows. For shipped-screen and flow research, start with [Mobbin](sites/12-mobbin.md) |

## How to read the evidence

Supplemental motion sources reviewed October 7 UTC, October 6 Pacific, 2026:
[Prompt Motion](https://prompt-motion.com/) and [Oneshotted](https://oneshotted.io/) pair
creator prompts with results; [Motion Prompts](https://motionprompts.dev/developers/) supplies
agent-readable mechanics and composition metadata under noncommercial reuse terms.
Use these to clarify a requested effect, with prompt provenance, rights, and runtime fit checked
at the selected item. Route live state transitions to `ui-motion` and timeline videos to
`motion-film`. Gallery UI footage does not prove working interactions. These supplement the
original 40-site set; they do not change its October 5 observation date.

The pages separate inspected first-party facts from recommendations and analytical risks.
Research into public offerings, documentation, and source is not a DOM/axe audit, performance
benchmark, verified download, paid entitlement check, or successful builder run. An access
error belongs to the research tool's observation; it does not by itself prove a payment gate
or that a service is unavailable to users.

Site counts, plan details, legal terms, integration commands, and URLs can change. Recheck
the selected item and original source before adoption. Keep code, prompt, screenshot, font,
and asset rights separate; a gallery entry does not grant permission to redistribute the
depicted design. This library contains original analysis and direct links; it does not
redistribute site prompts, component catalogs, images, or paid course materials.
