# Design synthesis

Use this when translating references into a buildable direction. The repository decides
its own scales and primitives. The questions below sharpen choices within those owners.

## A brief an implementer can use

Keep this compact; omit fields that the current design owner already settles.

| Decision | Record |
|---|---|
| User and task | Who uses this, how often, and what they need to accomplish |
| Improvement | The concrete friction or opportunity the design addresses |
| Direction | A plain name and the few visual choices that make it distinct |
| References | Exact screen/page, observation date, what was actually visible, adopted idea, why it fits these users, evidence limits |
| Composition | Reading order, dominant content, primary action, grouping, density |
| Type and geometry | Existing font roles, type/spacing tokens, alignment, width, wrapping |
| Surfaces and color | Background hierarchy, boundaries, accent/semantic roles, focus |
| Interaction | State ownership, feedback, overlays, recovery, purposeful motion |
| Adaptation | What changes at supported widths and themes; what remains accessible |
| Proof | Relevant states and the rendered, accessibility, and source checks |

For example, a project triage surface might use a compact workbench direction: the next
action leads, a scannable project list carries the content, and detail opens in the existing
panel. One reference informs row hierarchy, another shows a filtering flow. The app's
current table, tokens, and focus behavior implement it. This is a reasoning example, not
a template to impose on every dashboard.

Say exactly what the reference teaches. “Dense rows separate identity from metadata through
type weight and alignment” is actionable. “Make it premium like that site” leaves the
agent to invent all the consequential choices.

Before building, ask whether the same brief for another product would yield the same
direction. If it would, the direction is generic; revise that part.

## Arrival paths

For a public landing or detail page, record the known incoming link or visitor question,
the promise it makes, the first useful evidence on the destination, and the available next
step. Use verified content and working routes; keep acquisition goals in private planning
when the project requires it. If the incoming source is unknown, label that assumption.

Inspect the exact destination at a phone width, including its hash, query, and any first-visit
overlay. A matching headline is insufficient if the example, action, or section is hidden
behind an intro or several screens of repeated explanation. Keep supporting proof near the
claim it supports and preserve direct access to the promised task.

A campaign for one offer can prioritize one action. A homepage, portfolio, or reference hub
may serve several legitimate intents; give them a clear hierarchy rather than forcing a
sales funnel, invented proof, or mandatory FAQ into the page. Validate reachability and
comprehension separately from any unmeasured conversion claim.

## Controlled comparison

Use alternatives to settle a real question, such as whether a dense list needs grouped rows
or a separate details pane. Keep the content, viewport, theme, and state constant; vary the
structural decision being tested. Include the current surface as the baseline. A sketch or
short comparison can settle an obvious choice; render candidates when geometry or interaction
is what remains uncertain. Do not generate variants for an already settled local correction.

For a portable screenshot comparison with human feedback, build the optional
[offline review board](variant-review.md). It embeds supplied images and capture/source
identities; it does not capture screens, generate variants, or validate their claims.

Judge each candidate by the task: what can the user find, compare, or act on without opening
another view or decoding a truncated label? Preserve required information and actions while
changing their emphasis. Record the chosen direction and its tradeoff in the existing brief,
then carry it through connected screens. Later feedback should refine that direction unless
it changes the brief. A self-review is design evidence, not a measured usability study.

## Component adoption check

Use this before copying a gallery component, running its registry installer, or adding an
effect runtime. Inspect the exact candidate and its dependencies, not just the showcase:

- **Rights:** identify the license for the component, demo, fonts, and assets separately.
  A repository's CLI license may not cover the components it distributes.
- **Fit:** check framework/version, styling and token ownership, primitive substrate,
  rendering environment, and transitive dependencies. Similar-looking APIs do not establish
  compatibility. Reimplement a small visual idea in the existing primitive when that is simpler.
- **Behavior:** trace keyboard, focus, dismissal, controlled state, and relevant failure paths.
  Determine which semantics belong to the host app and which the candidate actually supplies.
- **Cost:** inspect listeners, frame loops, cleanup, reduced motion, and fallback behavior.
  Keep important content and actions available if an optional effect cannot render.

For an effect that depends on an experimental browser feature or GPU context, test the
supported path and the path with that capability unavailable. A flag-enabled demo does not
prove ordinary browser support. Check that visible controls still receive pointer and
keyboard input after scrolling and zooming; drawn pixels can diverge from DOM hit regions.
Verify readable content and usable actions in the fallback, not just the absence of errors.

Finish with an explicit disposition: reuse the compatible component, adapt only the idea,
or reject it with a reason. An installer, screenshot, or accessibility claim is not proof
of those contracts. Keep source pins and detailed attribution in the research record.

## Craft that survives real content

**Hierarchy.** Build the reading order around the user's question. Put the current object,
status, and next action where users look first. Give the dominant content most of the useful
space. Establish hierarchy through size, weight, grouping, and alignment before adding color.

**Typography.** Reuse font roles with clear differences between page titles, section labels,
body content, and metadata. Give headings useful wording and room to wrap. Align comparable
numbers and use tabular numerals where the font supports them. Legible secondary text helps
scanning; making it faint or tiny makes the user work harder.

**Spacing and density.** Create a rhythm from the existing spacing scale. Tighten within a
group and open the space between groups. Match density to frequency and content: daily
workflows benefit from scannable information, while a decision or introduction may need
more breathing room. Check short, long, missing, and translated content rather than tuning
only to a tidy fixture.

**Surfaces.** Use background changes, dividers, or containers to express grouping and
interaction. A container earns its boundary by holding a meaningful unit. Consistent edge
treatment and alignment often provide polish without extra shadows or effects. Maintain
the same visual meaning in dark mode; inspect actual composited colors for transparency.

**Color and icons.** Give accents a job, preserve semantic roles, and express statuses with
text as well as color. Use the current icon family with consistent geometry. Pair unfamiliar
actions with labels; visual novelty should not force users to decode basic controls.

**Detail.** Tune row baselines, control heights (matched across a shared row), label
proximity, truncation, scroll boundaries, empty-state proportions, and popover anchoring. These details carry the
direction after the first impression. Confirm hover, focus, active, disabled, and pending
states on the controls that changed.

**States.** Keep user input on failure, give actionable inline errors, and focus the first
invalid field. Keep reader position and useful existing data during refresh. Completion
follows the operation's actual state, not a visual timer.

**Motion.** Keep everyday actions immediate and retarget interrupted transitions correctly.
Shaders, 3D, blur, and scroll choreography must justify their loading and interaction cost.

## Fit the surface to its job

| Surface | Design around | References worth seeking | Verify beyond a tidy screenshot |
|---|---|---|---|
| App shell/navigation | Current location, frequent destinations, growing names | Active, collapsed, overflow and narrow navigation states | Keyboard order, focus, deep links, scroll and long labels |
| Dashboard | A question, comparison, exception or next action | Real product screens with similar data shapes | Missing/stale values, units, chart labels, readable tables and drill-down |
| List/table | Scanning, comparing, filtering, selecting and acting | Dense data interfaces and complete filtering flows | Long rows, empty filters, sort/selection state, pagination and row actions |
| Form/settings | Decisions and input in a sensible order | Complete validation, saving and recovery flows | Preserved input, inline errors, first invalid focus, pending and failed save |
| Detail/workbench | The object and its useful context | Master/detail, panels and long-content layouts | Back/context preservation, permissions, overflowing content and overlays |
| Chat/assistant | Reading, composing, responding and inspecting results | Real multi-turn conversations and artifact workflows | Drafts, streaming/cancel/error, long code/tables, scroll position and input focus |
| Landing/pricing | Understand the offer, assess trust, choose a next step | Relevant website composition, pricing and CTA examples | Truthful claims, meaningful links, narrow layout, accessible motion and forms |
| Expressive experience | An explicitly requested brand or interactive story | Relevant motion/3D/shader references | Loading, reduced motion, keyboard, fallback and measured performance |

On working and reading surfaces, a reference contributes type, palette, density, and one
signature move, not its layout wholesale. Choose a pattern because it handles the content and
behavior. A familiar grid, sidebar, hero, gradient, or serif can be right when the brief calls
for it. Taste is the fit between those choices; a universal visual ban simply creates another
default.

## Deriving a design record

Use when asked to create or update `DESIGN.md` from an existing product. Documenting the
system alone authorizes no product restyling. Preserve its existing format and accepted
decisions; do not introduce a token schema or exporter merely to write the record.

Select the product first, especially in a monorepo. Trace its active design guidance,
imported tokens and themes, shared primitives, then representative rendered consumers.
Exclude unused packages, proposals, examples and legacy styles. For each proposed rule or
value, keep a source locator, product/theme scope, and whether it is explicit intent, a
shared implementation, or a rendered observation in the task's evidence record.

Repeated literals alone do not establish a token scale, brand intent, or prohibition.
Preserve existing semantic names and aliases. Keep local exceptions scoped; report conflicts
with governing guidance instead of silently turning the implementation into the rule.

With only a public URL, label the document a reconstructed draft. Exact values need computed
styles or loaded CSS connected to rendered elements; screenshots establish appearance.
Scope observations to inspected pages, viewports and states. Do not infer private token
names, component ownership or rationale. If rendering is unavailable, report that limit and
leave unsupported values out.

Finish with a document diff that preserves accepted decisions, source-linked evidence for
new rules, and the project's existing documentation checks. Run an installed schema/export
validator only when that format is already the project's contract. Check lint findings
separately from export success: an exporter can emit output despite source errors, and a
successful lint exit can leave warnings. Review the actual token changes and unresolved
findings; unchanged finding counts do not prove that accepted values were preserved.
Export success does not establish source validity, visual fidelity or design intent.

Provenance: original synthesis after reviewing ibelick's
[create-design-md](https://github.com/ibelick/ui-skills/blob/59193a75432e5f41c6980f53b9e6a7bd56919947/skills/create-design-md/SKILL.md),
MIT, observed October 25, 2026. No upstream text, schema or implementation is bundled.
Recheck when the project's documentation contract or selected source changes.

## Applying a design contract

Use this when implementing a `DESIGN.md` or brand spec in the product.

1. **Rules before values.** Skim the headings, then read the frontmatter and every rule
   section (do and don't lists, known gaps, iteration notes) in full; a stated rule beats your
   default.
2. **Inventory the contract.** Note its colors and their states, type families and scale with
   any named substitutes, geometry (radius, elevation, control heights), focus treatment, and
   every prohibition, before touching code.
3. **Map onto the existing owner.** Put each value in the repository's token source, wherever
   it lives (a CSS file, a theme module, runtime injection). A value without a slot gets a named
   token in that owner, never a literal at the call site. Restyle through component variants
   and keep their names. Note any derived value, such as a dark mode the contract omits.
4. **Name type styles outside the color namespace.** With Tailwind and `tailwind-merge`, an
   unknown `text-*` size can be merged away as a color next to `text-muted-foreground`; check
   the project's merge config or use a distinct utility name.
5. **Turn each prohibition into a check** and run it before finishing.
6. **Test the mapping with the named recipes.** Confirm each component recipe the contract names
   can be built from tokens and variants alone; one that needs a raw value exposes a gap.

Report the mapping and each deliberate deviation (substituted fonts, derived values, a hover
kept where the spec omits it), with the contrast results from the [rendered
checks](rendered-checks.md).

A design system page, when requested, proves the contract: foundations, then components,
then compositions. Show color as role pairs with measured contrast before the raw palette.
Open each component with its typical case in real content. Primitives get a variant by state
matrix; composed components get a typical example plus edge cases (long, empty, error,
loading). Render the easiest-to-break rules as do and don't pairs, and end with one realistic
screen built only from tokens and components. Exhaustive combinations belong in tests.

## A reusable request

Adapt this to the task rather than filling every blank by assumption:

> Use $web-app-design on [surface] for [users and task]. Preserve [design owners and
> behavior contracts]. Use [references, or research a small relevant set] to improve
> [concrete friction]. Explain the adopted choices, implement the requested states, and
> verify [viewport/theme/journey scope] in the running app. Report missing evidence.

The request specifies a result and boundaries. It does not require an external builder,
marketplace package, purchased prompt, or a new design system.
