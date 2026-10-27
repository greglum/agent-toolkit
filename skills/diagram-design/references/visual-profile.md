# Diagram visual profile

Use this small role sheet when a diagram set needs a coherent visual system. Record the
chosen values beside the artifacts; extend the destination's design language, not its
application component library. This is an original starting profile, not a fixed theme.

## Map roles before drawing

| Role | Treatment | Meaning to preserve |
| --- | --- | --- |
| Canvas | Existing background token | Quiet field, not a status |
| Ownership region | Subtle alternate surface and a group label | Contains responsibilities; no arrowhead on the region |
| Ordinary component | Neutral surface, readable name and short responsibility | A participant, not automatically a process step |
| Focal decision or boundary | Primary fill with its paired foreground | The view's main point; not a claim of success |
| Source / store / actor | Simple, consistent silhouette or outline icon when useful | Actual entity type; label remains sufficient without the icon |
| Supporting evidence | Muted text with measured contrast | Subordinate information, never an essential unreadable caveat |
| Status / unknown | Explicit words plus shape or line cue | Unknown stays unknown; missing evidence must not look approved |

Use one family with a few weights unless the product has an established reason for more.
Measure each foreground against every fill it appears on. Decorative borders may be quiet;
necessary boundaries and connectors must remain distinguishable. Bright accent fills often
need dark text. Never reuse a decorative accent as a status without an explicit distinction.

## Presentation starting values

For a 1600 × 900 figure, a useful starting point is 64px outer margins, 24px node padding,
24–48px connector corridors, 44–48px takeaway type, 26–30px node names, 22–24px body and
18–20px supporting type. Use an 8px spacing rhythm and the product's corner treatment.
These are local starting values, not accessibility thresholds or hard budgets. At an 800px
embed all sizes halve: split the view or supply a full-size alternative if the main story
becomes difficult to read. Put small provenance detail in companion text as well.

Reserve a single dominant reading direction. Use side corridors for exceptions and returns.
Align comparable roles, not every object. Allocate width to content before shortening text;
never reduce a critical label to make equal boxes fit. A focal surface works best when the
rest of the canvas is restrained.

## Relationship grammar

Define the meanings actually needed in each figure, and put them in its key:

- Solid directional edge: the named request, handoff or dependency. State which one.
- Dashed edge: one explicitly named secondary meaning, such as a conditional detour.
  Keep that meaning consistent across the set or visibly explain a necessary change.
- Unarrowed region: containment. An arrow crossing it needs a real supported relationship.
- Junction dot: deliberate shared origin or fan-out. Separate unrelated crossings; do not
  imply a broker, shared transport or simultaneous execution merely to shorten routes.
- Missing or aggregated edge: explain it. Parallel relationships with different meanings
  must not collapse into a generic line or an unexplained ellipsis.

Keep unchanged node IDs and relative positions stable in comparisons. For overview/detail
views, share identities and roles while changing the layout to match the reader's question.
With automatic layout, record the actual renderer version/build, selected engine and theme;
inspect the delivered result because defaults and host support change.

## Adaptation example

A product with one sans-serif family, white and cool-gray surfaces, dark text and a blue
primary can produce an editorial diagram: a clear takeaway, broad responsibility groups,
one emphasized gate, and compact evidence beneath. A before/after view can use position to
show a field splitting into two axes and an explicit blank for unrecorded state. It does
not need copies of app navigation, status pills, dashboard cards or interactive controls.

This approach draws on role-based design tokens, a source-derived status-split diagram,
C4's explicit notation, LikeC4's semantic kinds, and Diagram Design's layout discipline.
See [C4 notation](https://c4model.com/diagrams/notation),
[LikeC4 styling](https://likec4.dev/dsl/styling/), and
[Diagram Design](https://github.com/cathrynlavery/diagram-design). These are conceptual
references; no upstream templates, fonts or icon assets are bundled here.
