# Offline design reference tool

Use the bundled [recipe search](../scripts/design_reference.py) when a design brief needs a
concrete starting direction. It searches twelve original task recipes, calculates declared
opaque sRGB role-pair contrast, and produces a draft JSON or Markdown brief. It needs Python
3.10+ and the bundled [corpus](../assets/design-recipes.json). No network, package, font or
model call is involved.

Read the project's accepted design rules first. These candidates do not replace accepted
tokens, justify product-specific aesthetic claims, or prove a running app is accessible.

## Search, inspect, draft

Resolve `<skill-dir>` to this installed skill's directory; the script finds its bundled
corpus relative to itself. Results include matched terms, stable IDs, original rationale,
composition and type roles, color-role candidates, pair calculations and source provenance.

```sh
python3 <skill-dir>/scripts/design_reference.py validate
python3 <skill-dir>/scripts/design_reference.py search "dense inventory table sorting" --limit 2
python3 <skill-dir>/scripts/design_reference.py draft "incident monitoring dashboard" --format markdown --output candidate-brief.md
python3 <skill-dir>/scripts/design_reference.py draft "workbench" --format json
python3 <skill-dir>/scripts/design_reference.py contrast '#ab6400' '#fefbe9'
```

The last example fails normal-text AA: its ratio is about 4.43295, not 4.5. Ratios are
compared before display rounding. `--kind large` uses 3:1 only for qualifying large text;
`--kind ui` uses 3:1 for applicable [non-text component or graphical contrast](https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html). The caller must
determine whether a criterion applies. This is not an automatic semantic or size classifier.

The [monitoring example](../examples/monitoring-brief.md) is a synthetic draft. It shows the
complete artifact, including unresolved product mapping. Output files use exclusive creation:
an existing path, including an existing symbolic link, is an error. The tool has no overwrite
option. Save a fresh candidate and review it before changing any accepted product file.

A no-match search returns `status: no-match`, an empty results list and no selected default.
For example, `search "quantum tokamak accelerator"` abstains. Search uses recipe IDs, titles
and explicit tags, not shared instruction prose. Scores order local candidates; they are not
probabilities or measured relevance ratings. `--limit` is from 1 through 12. An exact recipe
ID receives priority.

## Evidence and boundaries

Color checking accepts opaque `#RGB` and `#RRGGBB` values only. It does not infer transparency,
CSS variables, P3 colors, gradients, text sizes, user preferences or rendered backgrounds.
Resolve supported colors through the app's existing owners, or use the repository's browser
and accessibility setup for unsupported values. Both foreground and background must describe
the actual pair in use before the result supports a product claim.

Exit codes:

- `0`: valid corpus, search/draft completed (including no match), or contrast pair passes.
- `1`: contrast pair fails the selected threshold.
- `2`: invalid input/corpus, unsupported color, read/write failure or existing output path.

The corpus is original curation. Sources establish color mathematics and token/reference
semantics; they do not establish that these recipes or colors improve usability. Palette
values and recipe wording were not copied from upstream datasets. Type roles name existing
product fonts rather than downloading or licensing a new font.

Search/generation separation and preserved draft output were informed by
[UI UX Pro Max](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/tree/28b3b8dee8c976df4fa3e94aed4e092ad43fcb03)
(MIT; observed October 26, 2026). The implementation is original standard-library Python.
Contrast uses the current W3C sRGB luminance formula and WCAG 2.2 thresholds linked in the
corpus. No upstream source code or fonts are bundled.

## Maintain the corpus

Use `--corpus path.json` before the command to validate or trial a candidate dataset without
replacing the installed one. Schema version 1 requires unique recipe/source IDs, dated HTTPS
source locators and rights, nonempty tags/rationale/composition/type roles, valid opaque hex
role values, and passing declared role pairs. Validation checks the actual full-precision
pair results; it is not a DTCG schema validator.

Keep each recipe's use and exclusion clear, and add query terms only when they describe that
recipe. Preserve the distinction between original curation and source-supported claims. After
changing retrieval or data, run the bundled CLI tests and try a realistic query not used while
editing plus an unrelated no-match query. Verify candidate roles, content, focus and layout
in the actual product before accepting a draft direction.
