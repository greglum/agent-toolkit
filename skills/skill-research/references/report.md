# Round report and upkeep

## Report

Write one dated file, `YYYY-MM-DD-<topic>.md`, beside the other round reports. Sections:

1. **Title and status.** Date, branch and base SHA, window, lanes run, and who chose the changes.
2. **Method and limits.** How sources were read, blocked hosts, what counts as recency, and what
   was not run.
3. **Sources.** One row each: URL, pinned SHA, date, license, idea in our words, disposition.
   For tools/artifacts, include the source/local capability matrix, implementation versus
   instruction-only coverage, functional advantages and actionable gaps. State which missing
   functions were built and which still need work; procedural edits do not imply feature parity.
4. **Applied changes.** Owner file, the change, the failure it prevents, the source, and the
   proof (checker, blind run with control, or untested). Include minor refinements and cleanup;
   for zero adoptions, name the owners checked and why no supported fix remained.
5. **Gaps, retained, and rejected.** Each with a reason or the owner that already covers it. This
   may live in the Sources disposition column instead of its own section.
6. **Validation.** Commands run and results. Single runs are labeled as single runs, never as
   pass rates.
7. **Process lessons.** What wasted effort, what a lane got wrong, what had to be rechecked, and
   any lesson seen in an earlier report too (cite it).
8. **Not done and recheck triggers.** Unread leads, unverified claims, owner decisions, and the
   event that should prompt each recheck.

## Upkeep in the same change

- Add or update one registry row per author reviewed, adopted or not, with the new "last
  reviewed" link and what was drawn on.
- Add a dated section to the source index that links the report.
- Add the report to the README's research list, and a "Choose a workflow" row for any new skill.
- Update vendored-skill pins separately from the review record, and only after the installer
  action they describe has run.
