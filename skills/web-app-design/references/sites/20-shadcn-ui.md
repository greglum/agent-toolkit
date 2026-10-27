# 20. shadcn/ui

Observed: 2026-10-05. Depth: targeted web search, official homepage, Introduction, Manual Installation, Data Table guide, and repository MIT license. Public docs were readable. No CLI command ran, component was installed, or browser acceptance check occurred.

Research method: searched `site:ui.shadcn.com docs installation license`, opened the official site, and followed the primary pages listed below.

## Purpose and useful evidence

The [Introduction](https://ui.shadcn.com/docs) presents shadcn/ui as modifiable component code plus a distribution platform for building a project's own component library. Composition and inspectable source are central to that model. It is a practical implementation foundation for a compatible React app, rather than a guarantee that the app's overall information architecture is designed.

The observed [manual setup guide](https://ui.shadcn.com/docs/installation/manual) uses Tailwind CSS, import aliases, theme variables, helper dependencies, and `components.json`. Current defaults have changed over time. Existing projects should preserve their established primitive family, tokens, component APIs, and package versions rather than copying today's setup over an older working installation.

The [Data Table guide](https://ui.shadcn.com/docs/components/base/data-table) is especially relevant to working apps. It describes composing a table with TanStack Table for sorting, filtering, pagination, visibility, row actions, and selection. At observation it uses TanStack Table v9 and exposes Base UI, React Aria, and Radix variants. Those version and primitive choices must be checked against the receiving repository.

## Patterns and application fit

The strongest lesson is to compose a feature around real behavior and use consistent primitives. Tables, dialogs, fields, tabs, empty states, sidebars, and menus support repeated operational work better than a catalog of decorative landing effects. Use the relevant component documentation to clarify interaction contracts; use visual inspiration separately to choose hierarchy, density, and character.

A data table is not complete because rows render. Establish stable identity, server/client sorting ownership, page reset behavior, selected-row scope, and what the user can do after failure. The guide's sample data is an instructional example, not proof that those decisions fit a real large dataset. Extend the project's responsible layer instead of generating another generic table abstraction for a single screen.

Modifiable source also means maintenance responsibility. Track the upstream source and local customization when useful, keep custom behavior in clear owners, and review updates intentionally. Copying files removes neither dependency vulnerabilities nor future compatibility work.

## Reuse and integration

The official [repository license](https://github.com/shadcn-ui/ui/blob/main/LICENSE.md) is MIT and requires preserving copyright and permission notices in copies or substantial portions. Separately sourced registries, images, fonts, icons, and packages keep their own licenses. shadcn/ui's license does not automatically cover every third-party registry distributed through its CLI.

The inspected core docs were freely accessible. Adoption requires stack and architectural fit. Replacing a token system, adding Tailwind to another styling architecture, or switching primitive families is a material design-system change that needs the appropriate authority. Reading examples alone adds no dependency.

## Skill use and checks

Use existing shadcn/ui components first when the app already owns them. Resolve exact-version API questions from official docs and current source. The future skill should map the proposed screen to existing primitives, then shape typography, spacing, content, and state behavior coherently.

Analytical checks: labels, focus management, keyboard conventions, contrast after theming, overflow at zoom, table semantics, and loading/error states. Vendor accessibility positioning is not proof that a customized screen passes axe or manual use.

Recheck setup defaults, primitive family, upstream source, and dependency versions before adding or updating components. Validate the rendered application after adaptation.

## Update: DESIGN.md workflow (2026-10-09)

The official `shadcn` agent skill (`shadcn-ui/ui` at `2d3f1cd`) now applies a `DESIGN.md` to a shadcn app: it picks a style by geometry (`vega` classic, `nova` compact with hairlines, `maia` soft and generous, `lyra` boxy, `mira` dense, `luma` rounded with soft elevation, `rhea` a compact `luma`, `sera` editorial), maps tokens and component variants, and builds a design system page with pinned states and live contrast pairs. Its scaffold path (`init`, `add --all`) suits a new showcase app. For an existing app, use the general method in [applying a design contract](../design-synthesis.md#applying-a-design-contract) and the installed `shadcn` skill for component rules. [Source](https://github.com/shadcn-ui/ui/tree/2d3f1cd436b18ea12f24130de4df781355925b08/skills/shadcn).
