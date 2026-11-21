---
name: deslop
description: Remove AI tells from prose in docs, READMEs, and i18n or UI copy strings (de-slop, humanize, plain-language, de-AI), keeping facts intact. Audits report without editing. Not for visual or layout UI audits (deslop-ui), factual doc drift (docs-sync), social drafting (distribution-draft), or code refactoring (simplify-code).
license: MIT
compatibility: Bundled scanners require POSIX shell and standard text tools (grep, awk, sed, wc, tr). Vale, optional prose-rewrite or prose-rubric skills, and network access for Vale style sync are optional; unavailable helpers leave their checks unrun.
metadata:
  version: "1.0.0"
---

# Deslop

Outcome: the text says the same things in plainer words with no AI tells. Every
fact, command, path, link target, placeholder, and required phrase survives, and
the project's own checks still pass.

Two modes. **Audit** reports tells with file:line and a proposed fix and changes nothing;
use it when asked to check, scan, or audit, and as the first pass over UI copy in code.
**Edit** applies the rewrite; use it when asked to fix, rewrite, simplify, humanize, or
deslop. An audit ends with an offer to edit.

When available, use optional prose-rewrite or prose-rubric skills alongside Vale through
`scripts/lint.sh` (mechanical style checks) and `scripts/tells.sh` (the bundled mechanical
grep subset; optional external skills supplement semantic review). Resolve bundled scripts
from this skill's directory and target paths from the destination repository. Check helper
availability first. If a helper is missing, continue direct prose review against the user's
voice and project rules, and name its check as unrun. Do not install tools or invent
external evaluation results. On a cold Vale cache, `scripts/lint.sh` fails closed unless
`--sync` is passed after confirming network download authority for Vale style packages. Read
[sources and Vale notes](references/sources.md) only when reviewing upstream provenance or
Vale rule configuration.

## Procedure

1. **Scope.** List the target files and read each one in full. If targets are missing, empty,
   binary, generated artifacts, or non-prose code with no copy surface, refuse and stop
   before scanning. Read applicable repository instructions and record existing changes. Keep
   edits within the requested files or copy surface. Before touching prose, record three things:
   - Required phrases and anchors. Grep the repository's tests and docs for
     exact phrases the target contains (`grep -rn "same task" tests docs`) and
     for inbound links to its headings (`grep -rn "README.md#" docs`). A test
     that greps prose fails on a line wrap, so keep those phrases whole.
   - Untouchable content: code blocks, inline code, commands, paths, YAML
     frontmatter, data, link targets. In source files, everything outside
     string literals, plus the placeholders inside them; read
     [references/ui-copy.md](references/ui-copy.md) for that branch.
   - Register. Technical, reference, and error text stays neutral and plain.
     Product and marketing copy keeps the writer's voice. A writing sample from
     the user overrides both.
2. **Mechanical pass.** Run available `scripts/tells.sh FILES` on every target, and
   available `scripts/lint.sh FILES` on Markdown and text targets. Keep the output as the
   before list. In audit mode, pair this with a read for patterns `tells.sh` cannot grep
   (forced triads, repeated openings, one-line closers), skip Steps 3 through 6, and jump
   directly to Step 7.
3. **Rewrite** with an optional prose-rewrite skill if available, or direct prose judgment: mark tells strongest first, draft,
   check the five survivors (a not-X-but-Y contrast, a one-line closer, a dash,
   a triad, a bold label), then write the final text. A bold label earns its place when
   it states a claim ("Keys stay private"), not when it names a topic followed by
   fragments. Do not swap tells for telegraphic fragments, dropped articles or verbs,
   or arrows standing in for sentences. Prose changes only. For
   UI copy, apply [references/ui-copy.md](references/ui-copy.md) alongside.
4. **Check** with an optional prose-rubric skill if available, or direct prose review:
   confirm clear language, preserved facts, and accurate meaning. A fail means fix the draft
   and check again. When no external rubric skill is available, report the direct check
   without claiming an external rubric passed.
5. **Re-run step 2.** Give each remaining hit a disposition: fixed, or kept with
   the reason. Reasons that hold: a domain or product word, a quoted example, a
   claim-form heading or label ("Releases are verified"), a state adjective
   ("is enabled"), an identifier in code. Vale's Readability grades are
   advisory for technical writing.
6. **Verify.** Run required project gates and relevant existing checks. Preserve
   snapshot/test update gates and render changed screens where applicable. Re-grep the required phrases
   and anchors from step 1. Confirm `git diff` shows prose-only changes. If any gate or
   required-phrase grep fails after multi-file edits, repair or revert the offending edit
   before reporting.
7. **Report.** In edit mode: what changed, grouped by tell; before and after counts from
   scripts when scans completed; dispositions for kept hits; each check run with its result;
   and any check that could not run, named as unrun. In audit mode: list every hit with file,
   line, quoted text, the tell, and a proposed fix, plus scanner counts/status, and offer
   the edit.

## Completion

Done when every available check passes or its remaining hits carry a disposition, required
project gates pass, and you have delivered the Step 7 report. Unavailable helpers stay
unrun, with a direct-review result and its limits; missing or failed scans leave their
counts unavailable, never zero. In audit mode, done when the Step 7 audit report is
delivered and offers the edit.

## Scripts

- `scripts/tells.sh FILE...` greps the strongest tells in any text or source
  file and prints file:line hits grouped by tell. Exit 1 on a strong hit, 0
  otherwise, 2 on usage or a scan failure. Strong tells justify an edit on one sighting; weak tells need
  company from other tells in the same passage.
- `scripts/lint.sh [--all] [--sync] FILE.md...` runs Vale from a cache directory using the
  bundled config (no repository gains a config file). On a cold cache it exits 2 without
  downloading until `--sync` is passed after user confirmation for network access. Exit 2
  also reports missing Vale or setup failure (see Vale install docs if absent).
