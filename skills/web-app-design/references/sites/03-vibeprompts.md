# 03. VibePrompt

Observed: **2026-10-05**. Depth: explicit domain search; public catalog, dashboard category, and data-table example inspected, including displayed prompt, Tailwind markup, and JavaScript. A targeted license/terms search returned no authoritative license page. No rendered preview audit was run.

Search method: searches scoped to `vibeprompts.dev` checked application patterns and legal/license information; catalog navigation led to a dashboard example whose displayed code was inspected directly.

## What it offers

VibePrompt is a searchable collection of layout prompts and copyable Tailwind snippets. It spans marketing sections and working-app patterns: authentication, onboarding, navigation, dashboards, and utility widgets. The public catalog was accessible without signing in or paying during this review. Public availability does not establish open-source licensing. [Catalog](https://vibeprompts.dev/)

The [dashboard collection](https://vibeprompts.dev/dashboards/) includes task-oriented surfaces such as inbox split views, incident boards, approval queues, cost exploration, and logs. This is more relevant to application UX than a catalog consisting entirely of decorative heroes.

## Useful patterns and working method

Use its descriptive pattern names to sharpen an underspecified request. “Make this dashboard modern” becomes a concrete choice: overview, investigation workbench, operational queue, or split-view inbox. Different tasks need different information order and controls. Browse the nearest pattern, then describe the user's decision and the data it requires before choosing a layout.

The inspected [data-table example](https://vibeprompts.dev/dashboards/dashboards-data-table-with-toolbar/) has search, sort direction, a result count, and a no-match state. The useful lesson is that a toolbar must have behavior and feedback. A search box that does nothing, or a table that loses all context after filtering, is unfinished UI even if its borders and typography look polished.

For our apps, retain the existing table, query, form, and routing owners. Translate the reference into requirements instead of introducing a second standalone snippet. Specify whether search is server-side, how sorting interacts with pagination, whether filters persist in the URL, and what permissions govern actions. A small demonstration with local rows cannot answer those application questions.

Suggested workflow:

1. Choose a pattern that matches the task and data density.
2. List the required states and real actions beside the visual principles.
3. Map them to existing primitives and APIs.
4. Implement with real labels, loading/error feedback, and relevant empty-state recovery.
5. Verify search and sort semantics with realistic data as well as visual layout.

## Source, dependencies, and reuse

The example exposes plain HTML with Tailwind classes and direct DOM JavaScript. It is not a React integration or an authenticated data layer. Copying it into a component app without adaptation could bypass established state ownership and introduce global IDs or event wiring that behaves poorly when instances repeat. [Example source](https://vibeprompts.dev/dashboards/dashboards-data-table-with-toolbar/)

No permissive code or prompt license was verified. Record this as **unknown**, not MIT or unrestricted commercial use. This library stores links and original analysis only. Before incorporating exact source, establish the item's license or obtain suitable permission. No paid access or external integration was observed for the inspected pages.

## Quality considerations and skill use

Source inspection found sortable headings implemented with click listeners and a search field without an explicit label in the displayed snippet. These are concerns to repair through semantic buttons, accessible sort state, and a label; they are not results of a browser accessibility audit. Also check live announcements, focus visibility, horizontal overflow, keyboard operation, and how dense records behave at zoom. Performance was not measured.

Skill role: quick pattern and state discovery, followed by implementation through the app's own system. Recheck licensing before source reuse, the selected example when behavior is relied upon, and the available catalog when a relevant pattern cannot be found.
