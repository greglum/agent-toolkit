---
name: deslop
description: Remove AI tells from prose in docs, READMEs, and web UI copy (labels, messages, i18n strings). Run the tells and Vale scripts, rewrite plainer, then check. Audit mode reports and changes nothing. Use to de-slop, humanize, plain-language, or de-AI text. Not for simplifying code; use simplify-code.
license: MIT
compatibility: Bundled scanners require POSIX shell and standard text tools. Vale, humanizer, and no-ai-slop are optional; unavailable helpers leave their checks unrun.
metadata:
  version: "1.0.0"
---

# Deslop

Outcome: the text says the same things in plainer words with no AI tells. Every
fact, command, path, link target, placeholder, and required phrase survives, and
the project's own checks still pass.

Two modes, from no-ai-slop. **Audit** reports tells with file:line and a proposed
fix and changes nothing; use it when asked to check, scan, or audit, and as the
first pass over UI copy in code. **Edit** applies the rewrite; use it when asked
to fix, rewrite, simplify, humanize, or deslop. An audit ends with an offer to edit.

When available, use three helpers: the `humanizer` skill (the rewrite),
the `no-ai-slop` skill's `eval.md` (the check), and Vale through `scripts/lint.sh`
(the mechanical pass). `scripts/tells.sh` folds stop-slop's quick checks into one
grep. Load `humanizer` and `no-ai-slop` when the steps below name them; their
SKILL.md files stay the source of truth for the patterns. Resolve bundled scripts from
this skill's directory and target paths from the destination repository. Check helper
availability first. If a helper is missing, continue direct prose review against the
user's voice and project rules, and name its check as unrun. Do not install tools or
invent external evaluation results. A cold Vale cache can run `vale sync` and download
style packages; inspect that setup and its destinations before execution, within the
session's existing authority.

## Procedure

1. **Scope.** List the target files and read each one in full. Read applicable
   repository instructions and record existing changes. Keep edits within the requested
   files or copy surface. Before touching
   prose, record three things:
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
   before list. In audit mode, this plus a read for the patterns tells.sh cannot
   grep (forced triads, repeated openings, one-line closers) is the report.
3. **Rewrite** with available `humanizer` in file mode, or direct prose judgment: mark tells strongest first, draft,
   check the five survivors (a not-X-but-Y contrast, a one-line closer, a dash,
   a triad, a bold label), then write the final text. A bold label earns its place when
   it states a claim ("Keys stay private"), not when it names a topic followed by
   fragments. Do not swap tells for telegraphic fragments, dropped articles or verbs,
   or arrows standing in for sentences. Prose changes only. For
   UI copy, apply [references/ui-copy.md](references/ui-copy.md) alongside.
4. **Check** with available `no-ai-slop`: answer each item in its `eval.md` pass or fail.
   A fail means fix the draft and check again. If absent, reread for clear language and
   preserved facts, and report a direct check without claiming its external rubric passed.
5. **Re-run step 2.** Give each remaining hit a disposition: fixed, or kept with
   the reason. Reasons that hold: a domain or product word, a quoted example, a
   claim-form heading or label ("Releases are verified"), a state adjective
   ("is enabled"), an identifier in code. Vale's Readability grades are
   advisory for technical writing.
6. **Verify.** Run required project gates and relevant existing checks. Preserve
   snapshot/test update gates and render changed screens where applicable. Re-grep the required phrases
   and anchors from step 1. Confirm `git diff` shows prose-only changes.
7. **Report.** What changed, grouped by tell; before and after counts from the
   scripts when scans completed; dispositions for kept hits; each check run with its result; any
   check you could not run, named as unrun.

## Completion

Done when every available helper check passes or its remaining hits carry a
disposition, required project gates pass, and you have delivered the report.
Unavailable helpers stay unrun, with a direct-review result and its limits;
missing or failed scans leave their counts unavailable, never zero. In audit mode, done when the report lists every hit with
file, line, quoted text, the tell, and a proposed fix, and offers the edit.

## Scripts

- `scripts/tells.sh FILE...` greps the strongest tells in any text or source
  file and prints file:line hits grouped by tell. Exit 1 on a strong hit, 0
  otherwise, 2 on usage or a scan failure. Strong tells justify an edit on one sighting; weak tells need
  company from other tells in the same passage.
- `scripts/lint.sh [--all] FILE.md...` runs Vale with write-good, proselint,
  and Readability from a cache directory, so no repository gains a config file.
  E-Prime is off because the humanizer prefers is, are, and has; spelling is
  off because technical writing is full of product and code words. Exit 2 on setup failure,
  with an install hint when Vale is absent (`brew install vale`).
