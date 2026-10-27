# UI copy

The branch of the deslop procedure for text that lives in application source:
JSX text and string props (`label`, `placeholder`, `title`, `alt`, `aria-label`),
i18n catalogs (JSON, YAML, PO, ICU), validation and error messages, empty
states, toasts, tooltips, button labels, headings, notification and email
templates, and CLI output. Start in audit mode; apply on approval, or at once
when the request already says to edit.

## Find the strings

- Catalog first: use the repository's catalog layout and source-locale setting to find
  the requested keys. Search text with `rg` or the available equivalent; treat matches
  as leads and inspect catalogs in full. Edit only the requested copy surface.
- Then source: `grep -rn -E '>[^<{]{12,}<|(label|placeholder|title|alt|aria-label)=\"[^\"]{6,}\"' --include='*.tsx' --include='*.jsx' --include='*.vue' --include='*.svelte' src` finds inline text.
- Run `scripts/tells.sh` on the matched files. A hit inside an identifier
  (`leverageRatio`, `fosterId`) is code, not copy; disposition it as kept.

## Preserve, byte for byte

- Interpolation and ICU: `{name}`, `{{count}}`, `%s`, `%1$d`, `${x}`,
  `{count, plural, one {# item} other {# items}}`, `{gender, select, ...}`.
  Move a placeholder inside a sentence if the sentence needs it; never rename,
  drop, or add one.
- Keys, IDs, `data-*` values, route names, and the catalog's structure and order.
- Markup inside strings: tags, entities, `\n`, leading and trailing spaces.
- Other locales. Change the source locale; list the sibling catalogs whose
  entries now need translation. A machine translation is never a deliverable.
- The string's width class. A button label stays a one- to three-word verb
  phrase; a tooltip stays one sentence; a table header stays one or two words.
  A longer replacement can wrap a button or truncate a cell.

## Write it like this

- Sentence case for everything except product names.
- Second person, present tense: "Save your changes", "You have 3 unread messages".
- A control names its action: "Save", "Delete project", "Send invite". The
  destructive verb appears on the destructive button.
- One term per concept across the app. Build the glossary from the catalog
  before editing ("project" or "app", "sign in" or "log in", "remove" or
  "delete") and use the term the codebase already prefers.
- A status states what happened: "Saved", "3 files uploaded", "Invite sent".
- An error names what happened and the next step: "Upload failed because the
  file is over 25 MB. Choose a smaller file." A generic error names where to
  get help. Use numerals, and state the limit.
- An empty state says what belongs here and how to add it: "No projects yet.
  Create one to get started."
- A confirmation names the object and the consequence: "Delete 'Q3 report'?
  This cannot be undone."
- Punctuation: a period on a full sentence, none on a label or heading, one
  question mark on a confirmation, no exclamation marks.
- `aria-label` describes the control for a screen reader ("Close dialog"), and
  matches the visible label when one exists.

## Verify

- Run required typecheck, lint, and existing tests. Review copy-only snapshot changes
  under the repository's update gate; do not replace expected output to hide a regression.
- Render each changed screen and read the new strings in place. Confirm that
  buttons, table cells, and badges still fit at the narrowest supported width.
- Run the repository's accessibility check (axe, for example) on screens where an `aria-*` value or heading changed.
- The report lists each changed key or line with before and after text, the
  tell it removed, and the locales that now need translation.
