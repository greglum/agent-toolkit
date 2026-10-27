# 07. The Component Gallery

Observed: **2026-10-05**. Depth: targeted search; homepage, about page, tabs catalog, and the linked GOV.UK tabs guidance inspected. A guessed dialog route failed; the tabs route worked. No components were installed and no rendered audit was run.

Search method: searches scoped to `component.gallery` checked the catalog's purpose and pattern guidance; tabs navigation led to first-party GOV.UK usage documentation for a concrete comparison.

## What it offers

The Component Gallery indexes interface patterns across real design systems. Entries connect a component name with source documentation and metadata such as framework, usage guidance, code examples, accessibility, research, and maintenance concerns. It is a comparison and discovery resource, not one unified drop-in component library. [Homepage](https://component.gallery/), [About](https://component.gallery/about/)

Its creator warns that popularity is not proof that a pattern is correct and recommends consulting research and usage rationale. This makes the resource particularly relevant to working apps, where choosing the right interaction often matters more than adding visual novelty. [About and rationale](https://component.gallery/about/)

## Useful patterns and working method

Start with the problem: switching related content, selecting many records, navigating a hierarchy, or showing progress. Search the relevant component name, compare approaches, and follow the most relevant first-party documentation. The gallery helps establish terminology as well as design options, which improves a brief and makes code review more precise.

The inspected [tabs catalog](https://component.gallery/components/tabs/) connects to multiple systems, including GOV.UK. Its [original tabs guidance](https://design-system.service.gov.uk/components/tabs/) explains when sections can be hidden safely and when sequential reading or comparison makes tabs a poor choice. This is the kind of decision evidence the skill should preserve: why the pattern suits the task, and what would make it unsuitable.

For a sleek working app, use the gallery to strengthen interaction structure before polishing surfaces. A coherent table, form, or navigation component with clear state feedback is a better foundation than a collection of unrelated attractive snippets. The same resource can guide marketing elements, but its distinctive value is operational UI and mature pattern rationale.

Suggested workflow:

1. Name the user's task and expected information relationship.
2. Find the nearest component family and compare two relevant systems.
3. Read their usage and accessibility guidance at the original source.
4. Reuse the app's existing primitive where it already covers the pattern.
5. Adapt the visual treatment through repository tokens and verify the interaction.

## Source, integration, and reuse

The public gallery required no account or payment during this review. Browsing introduces no runtime dependency. The site's own Astro, Airtable, and hosting choices are implementation details of the gallery, not recommendations for our app. [Site implementation notes](https://component.gallery/about/)

An “open source” tag means the linked project is presented that way; it does not grant a single license across the catalog. Inspect the exact upstream repository, version, license, and asset/font terms before copying code. Also distinguish framework compatibility from visual compatibility. Adding an unrelated React library merely because a reference uses it can increase ownership and bundle costs without improving the task.

## Quality considerations and skill use

Accessibility metadata is a discovery aid, not proof that a chosen customization passes our application's audit. Analytical risks include outdated links, unmaintained examples, inappropriate pattern transfer, and styling changes that remove focus or contrast from otherwise sound primitives. No live keyboard, screen-reader, contrast, or performance results are claimed here.

Skill role: primary pattern-selection reference for forms, navigation, dense lists, tables, and complex states. Recheck upstream guidance and maintenance status before code adoption, and the original source whenever catalog metadata conflicts with the current implementation.
