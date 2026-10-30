# Offline screenshot review

Use when a real design question needs a portable comparison and human feedback. Reuse the
project's capture rig; this tool does not take screenshots, generate alternatives, measure
usability, verify capture metadata or authorize a selected design. Keep the current surface
first as the baseline. Compare the same content, viewport, theme and UI state.

Place one JSON manifest beside the authorized PNG, JPEG or WebP files:

```json
{
  "version": 1,
  "title": "Compare the project list",
  "question": "Which layout makes the next action easier to find?",
  "context": {
    "viewport": {"width": 1280, "height": 800},
    "theme": "light",
    "state": "same three synthetic projects, no selection"
  },
  "variants": [
    {"id": "current", "label": "Current list", "image": "current.png", "image_size": {"width": 1280, "height": 800}, "source_revision": "baseline commit or content identity"},
    {"id": "compact", "label": "Compact list", "image": "compact.png", "image_size": {"width": 1280, "height": 800}, "source_revision": "candidate commit plus dirty-diff identity when needed"}
  ]
}
```

Use actual capture identities. Unknown provenance must be stated as unknown, never invented.
The shared context is a declaration, not a check that the screenshots match. Capture each
comparison context separately. The digest binds metadata and image bytes, not authenticity.
Record intrinsic image dimensions in `image_size`, separately from the CSS viewport (a
high-density capture may differ). Dimensions reserve image space; export also checks them
against the decoded image. Image paths must stay inside the manifest folder and cannot contain symlinks. The manifest
is limited to 64 KiB, one to eight variants, 8 MiB per image and 24 MiB total image bytes.

```sh
python3 scripts/review_variants.py comparison.json review.html
```

Run from the installed bundle or use the script's full path. The command creates a new
HTML file and refuses overwrites. It reads no provider settings and makes no network calls.
Open the HTML locally. Screenshots, source identities and declared context work without
JavaScript. With scripts enabled, select a variant, add notes and download review JSON.
Confirm that the browser saved the file before closing the tab. Notes are not persisted.
A malformed image or mismatched image dimensions keep export disabled; correct the source and rebuild to a new file.

The HTML embeds images; the review JSON contains metadata, image hashes, selection and notes,
without image bytes or original filesystem paths. Both can contain private information.
Inspect before sharing. A preference is feedback, not permission to implement or publish.

## Verification

Run `python3 -m unittest discover -s scripts -p 'test_variant_review.py'` from the bundle.
For the rendered check, use existing Playwright and axe-core installations:

```sh
node scripts/check-variant-browser.mjs /path/to/playwright/index.mjs /path/to/axe.min.js /path/to/new-evidence-folder
```

No dependencies are installed. The browser check uses Playwright's bundled Chromium or an
explicit `CHROME_PATH`, rejecting installed Google Chrome. It checks synthetic fixtures,
offline export, no-script comparison, keyboard controls, narrow/wide light/dark geometry,
focus and axe results. Its artifacts prove that fixture only, not your screenshots' quality
or the design's effect on real users. Keep browser evidence outside the repository.

## Source scope

Original implementation; no upstream code, prompts or media copied. The review-board idea
was assessed against [gstack's design comparison](https://github.com/garrytan/gstack/tree/d9b0d60082cca70d41522206b4301d790236f451/design/src),
MIT, observed October 27, 2026. This tool deliberately omits generation, feedback servers,
galleries, uploads and provider choice. Recheck the local contract if capture metadata,
review export or supported image formats change.
