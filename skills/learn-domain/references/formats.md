# Domain notes formats

The checker reads these exact formats. Put the four sections in one file or split them across
files; pass every file to the checker together. Section headings are level-2 headings named
`Sources`, `Glossary`, `Primer` and `Questions`. A section ends at the next level-1 or
level-2 heading. The checker needs all four sections, each with at least one entry. A missing
section is `missing_section` and an empty one is `vacuous`.

In `Sources`, `Glossary` and `Questions`, the checker reads every table row in the section,
including rows after a blank line. Any other non-blank line there is `untabled_prose`: put
claims in the primer, not under a table.

## Status values

Every glossary row and primer claim carries exactly one status. Spell it as shown.

| Status | Use it when |
| --- | --- |
| `Checked` | You read the claim at the cited place in the source. Needs a valid locator. |
| `Reported` | A source states it, but you did not confirm it at a precise place, or the source only claims it. |
| `Analysis` | Your own reasoning from the cited sources. Cite the sources it rests on. |
| `Open` | Unknown or disputed. Cite the question ID that will settle it, or the source that raised it. |

## References and locators

A reference is a source ID (`S1`) or a question ID, optionally followed by a locator. Question
IDs are `Q<n>` (`Q2`) or `Q-<slug>-<n>` (`Q-lots-02`, as map-data-source writes them). A
question ID alone only supports `Open`.

A locator is one or more of these, separated by spaces:

- a section: `§4.2`, `section 3`, `chapter 2`, `clause 5.1`, `appendix B`
- a page: `p. 12`, `pp. 4-6`
- a line: `line 40`, `lines 12-18`
- a timestamp: `12:30` or `01:02:03`
- a URL fragment: `#grading-rules`
- a table, figure or similar: `table 3`, `figure 2`, `rule 7.3`, `slide 4`, `sheet Lots`, `row 9`, `step 2`
- a quoted heading: `"Moisture limits"`

Free text such as `see manual` or `it is in there` is not a locator. `Checked` without a valid
locator is `checked_without_locator`; any other reference with free text after the ID is
`bad_locator`. Commas separate references, so a locator cannot contain a comma: write
`S1 p. 4 table 2`, not `S1 p. 4, table 2`.

## Sources

| Column | Rule |
| --- | --- |
| ID | `S` plus a number, unique. |
| Source | Title and version. |
| Kind | One of `internal`, `standard`, `regulator`, `rulebook`, `vendor`, `peer-reviewed`, `practitioner`. |
| Date | Exactly `YYYY`, `YYYY-MM` or `YYYY-MM-DD`. With no date, write `accessed YYYY-MM-DD`. |
| Locator | A URL (`https://...`) or a path with a `/` or a file extension. Write a local path as plain text or a code span, never a Markdown link. |
| Proves | What this source can establish on its own authority. Write `none` if nothing. |
| Claims | What it states but cannot establish. Write `none` if nothing. |

## Glossary

Columns: `Term`, `Meaning`, `Not`, `Avoid`, `Units`, `Source`, `Status`. `Term`, `Meaning`,
`Source` and `Status` must be filled. Use `-` for an empty `Not`, `Avoid` or `Units` cell.
`Source` holds references without brackets, separated by commas. `Avoid` lists synonyms to
avoid, separated by commas. Each term appears once and no avoided word is also a term.

## Primer

Use these level-3 headings: `How it works`, `Entities and processes`, `Metrics and traps`,
`Newcomer mistakes`. Only level-3 headings are headings here; a level-4 or deeper heading
is a claim and needs a tag. Every other non-blank line is a claim:

```text
- Claim text. [S1 §4.2; Checked]
- Claim resting on two sources. [S2 rule 7.3, S3 §5; Analysis]
- First sentence. [S1 p. 3; Checked] Second sentence. [S2 §1; Reported]
```

The tag is a bracket holding references, a semicolon, then the status. It contains no `|`,
so it fits in a table cell. Each sentence needs its own tag right after it: two sentences
before one tag is `multi_sentence_claim`, and text after the last tag is `uncited_claim`.
A sentence break is a `.`, `!` or `?` followed by a space and a capital letter, so avoid
abbreviations such as `e.g. The` inside a claim. Table header and separator rows are exempt.

Wrap a long bullet by indenting the next line; the checker joins an indented line to the
line directly above. An unindented line, a nested bullet, or an indented line after a blank
line is a new claim and needs its own tag.

## Questions

Columns: `ID`, `Rank`, `Question`, `Decision`, `Evidence`, `Answerer`. All must be filled.
`Rank` is a unique positive integer in ASCII digits, 1 first. `Evidence` starts with one kind:

- `conflict:` two or more sources disagree. Cite at least two source IDs.
- `gap:` the sources are silent.
- `data:` an observation in the data, such as an unexplained code.
- `standard:` a standard interview prompt.

Name the answerer by role, such as `Intake supervisor`. An email, an `@handle`, or two
capitalized words with no role word (such as `Jane Doe`) is `answerer_not_role`.

## Avoided synonyms

The checker flags any listed avoided synonym in a primer claim, a glossary meaning or a
question, matched as a whole word or phrase with an optional plural `s` or `es`, ignoring
case. Other inflections are not matched. To mention a wrong term on purpose, such as in
`Newcomer mistakes`, put it in a code span: `` `batch` ``.

The checker does not read question `Decision` or `Evidence` cells for avoided synonyms, nor
any text outside the four sections.

## Example

```markdown
## Sources

| ID | Source | Kind | Date | Locator | Proves | Claims |
| --- | --- | --- | --- | --- | --- | --- |
| S1 | Grading standard, rev. 2 | standard | 2025-03-01 | https://standards.example.org/g | Grade rules | Prices |

## Glossary

| Term | Meaning | Not | Avoid | Units | Source | Status |
| --- | --- | --- | --- | --- | --- | --- |
| Lot | Cocoons from one tray on one day | Not a shipment | batch | count | S1 §2 | Checked |

## Primer

### How it works

- Each lot gets one grade. [S1 §3; Checked]
```
