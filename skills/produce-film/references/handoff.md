# Stage handoff contract

Every stage returns structured paths and receipts rather than prose summaries. The parent
integrator verifies each receipt before starting the next dependent stage.

## 1. Brief and clock -> Asset and film stages

Pass:
- `brief_path`: production brief with thesis, audience, formats, dimensions, fps, duration
  budget, and audio/caption scope
- `clock_path`: frozen cue sheet or `timing.json` (event times in seconds and derived frames)
- `asset_ledger_path`: cleared inputs, origins, rights, and required attributions
- `max_workers`: numeric concurrency cap

## 2. Asset stages (`blender-scene`, `svg-illustration`) -> `motion-film`

Each asset stage returns:
- `artifact_paths`: exported `.glb` / `.blend` / `.svg` / component source and preview stills
- `check_receipts`: `lint_bpy.py` or `lint_svg.py` exit code and JSON summary
- `asset_metadata`: units/scale, pivot/origin, `viewBox` or bounding box, `id` prefix, and
  clock/step interface (for animated SVGs)
- `rights`: asset licenses and required attribution lines
- `unresolved`: any unverified renders or open visual fixes

## 3. `motion-film` -> `repurpose-long-video` and `thumbnail-production`

`motion-film` returns:
- `master_path`: encoded master video path plus container/codec/fps/dimensions/duration
- `source_revision`: repo commit or snapshot ID and editable project path
- `check_receipts`: `probe_export.py`, `check_motion.py`, `contact_sheet.py`, and blind
  critique verdicts (`passed`, `failed`, `unavailable`, `not run`)
- `opening_payoff`: settled title, one-sentence thesis, and opening visual payoff
- `cleared_assets`: asset IDs and stills cleared for covers or cutdowns
- `unresolved`: unrun listening, playback, or platform checks

## 4. `repurpose-long-video` -> `motion-film` and `thumbnail-production`

`repurpose-long-video` returns:
- `edit_list_path`: `edit-list.json` binding every clip to source SHA-256 and in/out times
- `clip_paths` and `caption_paths`: exported short clips and caption sidecars
- `context_verdicts`: pass/extended/dropped status per clip
- `unresolved`: unverified caption, loudness, or visual checks

## 5. Final package -> User handoff for `distribution-draft`

Because `distribution-draft` is explicit-only, `produce-film` never invokes it. Instead,
present this packet so the user can run `/distribution-draft` or `$distribution-draft`:
- Approved thesis, audience, and claims verified against primary records
- Delivered master, cutdown, and cover paths (never claiming they are uploaded)
- Cleared asset attributions and any required AI/synthetic disclosures
- Remaining unverified checks or owner approvals
