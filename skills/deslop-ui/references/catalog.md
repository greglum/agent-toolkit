# Pattern catalog

Named patterns, grouped by layer. Each names the tell, why it reads as generated, and the
decision that replaces it. Sources: the Fountain Institute's seven tells (Humble), SmoothUI's
"AI design slop" and its closed-loop argument, the design-anti-slop three-layer catalog
(Agrawal), and GenDesigns' fifteen mistakes, read 2026-09-25; Anthropic's frontend-design
skill (`41bbe19`), read 2026-10-07; the rest is practice.

A page pops through hierarchy, one confident accent, real numbers, and purposeful space; it
looks generated through decoration.

## Visual

| Id | Tell | Why it reads as generated | Decision that replaces it |
|---|---|---|---|
| V1 | Purple, indigo, or violet-to-cyan gradients on buttons, headings, backgrounds | The most common gradient in tech marketing; the model's default for "innovative" | One accent from the product's palette; gradients only where the brand system defines one |
| V2 | Gradient-filled headline text (`bg-clip-text text-transparent`) | Marketing hero shorthand | Solid ink, hierarchy from size and weight |
| V3 | Radial glow, aurora, or `blur-3xl` blobs behind content | Learned as "premium dark mode" from gaming and crypto sites | A flat surface; depth from borders and one or two tonal steps |
| V4 | Glassmorphism (`backdrop-blur` cards, translucent borders, neon rims) | Photographs well, ranks well, means nothing | Opaque cards with the system's border and shadow scale |
| V5 | Neon or five-plus saturated colors with none in charge | High-chroma-on-dark overrepresented in "modern UI" data | A color budget: neutrals, one accent, semantic state colors only |
| V6 | Uniform `rounded-2xl`/`3xl` on every box | No cost function for radius | The system's two or three radius steps, larger only for the outermost container |
| V7 | Heavy `shadow-xl`/`2xl` on flat content | Shadow read as polish | Shadow only for things that float (menus, dialogs); content sits on borders |
| V8 | Emoji as icons, bullets, or section markers | Marketing copy's visual punctuation | One icon set at one stroke weight, or no icon |
| V9 | Sparkle or magic-wand icons on features that are not AI | "AI equals sparkle" | The icon that names the action, or none |
| V10 | Rainbow side tabs and colored left borders on every card | Active-state color applied everywhere with no budget | Color only where it encodes state; the rest neutral |
| V11 | A colored dot beside every status | "Status equals dot" pattern-matched from dev tools | A labelled pill or plain text; a dot only with a label and a single meaning |
| V12 | Bounce, pulse, scale, or glow on every hover | Motion read as delight | Motion only where it explains a change; reduced-motion honored |
| V13 | Icon stamps: an icon in a tinted rounded square before every heading | The generated feature-card default | Icon only when it disambiguates; otherwise the heading alone |
| V14 | Stock photography or 3D clay illustration with no relation to the data | Filler | Real content, a real chart, or space |
| V15 | Template chrome: an eyebrow label over every heading, middle-dot meta strings, an arrow appended to every link | Page-builder furniture repeated by habit | Labels and arrows only where they carry information, in the system's type roles |

## Structural

| Id | Tell | Why | Decision |
|---|---|---|---|
| S1 | Four KPI cards in a row on every dashboard whether or not four numbers matter | The generated dashboard opener | Only numbers that support a decision, in scan order, with context or drill-down where useful |
| S2 | Three-box feature grid, six identical cards each with icon, heading, two lines | Symmetry without content | Cards sized by their content; a list when the items are a list |
| S3 | Cards inside cards inside cards | Container rule applied recursively | One container per group; sections separated by space or a rule |
| S4 | Uniform everything: every section the same height, gap, and shape | No hierarchy of importance | The primary task gets the height and width; secondary readings fold |
| S5 | Generic sidebar plus top bar that could belong to any SaaS | The layout mean | Navigation named in the product's vocabulary, grouped by the user's jobs |
| S6 | A hero band on a working screen | Marketing pattern in a tool | A one-line masthead with the actions the user came for |
| S7 | Decorative charts: a sparkline or donut that answers no question | Chart as texture | Charts that answer a named question, with the axis and unit, or none |
| S8 | Bento grid for its own sake | Apple marketing shorthand | A grid that follows reading order and data relationships |
| S9 | Logo soup, fake testimonial carousels, "trusted by" rows | Landing-page filler | Remove, or one verifiable proof |
| S10 | Modal for everything | Easiest container to generate | Inline edit, a drawer for a record, a modal only for a decision |
| S11 | Numbered 01/02/03 markers on content that is not a sequence | Order implied for decoration | Numbers only for steps or real order |

## Conceptual

| Id | Tell | Why | Decision |
|---|---|---|---|
| C1 | Aspirational-empty headlines ("Unlock your potential", "Work smarter") | Says nothing about this product | A headline that states what the page holds or does |
| C2 | Verb slop: empower, leverage, seamless, effortless, robust, supercharge, elevate | Marketing verbs in interface copy | Plain verbs that name the action |
| C3 | Generic sections: "Features", "Insights", "Overview" as headings over unrelated content | Structure without a subject | Headings that name the content ("Overdue projects") |
| C4 | Fake specificity: numbers with no source, avatars with no people, quotes with no author | Placeholder shapes shipped as content | Real data, labelled fixtures, or nothing |
| C5 | No point of view: every option equal weight, no default, no recommendation | The page refuses to decide | A default, a primary action, an order |
| C6 | Missing functional states: no empty, loading, error, or permission state | The happy path is all the generator drew | Every state the journey has, with the next step in it |
| C7 | Portability failure: the screen would work unchanged for any product | Sampled from the mean | Vocabulary, examples, and numbers that only this product has |
| C8 | Exclamation marks, "Welcome back!", "Oops!", "Awesome!" | Chat register in a tool | Statements: "Welcome, Cara", "Saved", "Upload failed because…" |
| C9 | Explaining the obvious ("Click the button below to continue") | Copy filling space | Remove |
| C10 | One action renamed across its flow ("Publish", then "Success!") | Each string written alone | One verb for the action, its pending label, and its confirmation |

## Acceptance bar

Apply these checks on every requested screen, theme, viewport, and state. The explicit brief
and existing design system govern acceptance. The catalog suggests inspection leads, not
universal aesthetic bans; preserve justified brand choices and explain exceptions. Mark
uninspected or source-only cells unverified.

1. Color follows the product's palette and communicates action, state, or approved brand intent.
2. Hierarchy is legible with color removed: size, weight, and position say what matters first.
3. Gradients, glow, blur, glass, and illustration serve a documented product or brand purpose.
4. Typography, radius, depth, and shadow use the existing token system consistently.
5. Icons follow the product's vocabulary and system, with a clear semantic or brand purpose.
6. Containers reflect real grouping or interaction; inspect needless nesting and wrappers.
7. Layout follows the user's task and reading order, not a template: the primary surface has
   useful space its task needs; KPI counts exist because a decision needs them, with context or
   drill-down where the underlying data and task support it.
8. Every chart answers a named question with truthful data and units, axes, or scales where
   its representation requires them.
9. Interface copy follows the product's voice and rules: specific nouns, plain verbs, and
   useful empty, error, and loading states. Use `deslop` if available; otherwise audit directly.
10. Vocabulary, numbers, and examples fit this product. Shared primitives and familiar
    interaction patterns are valid when they serve the task.
