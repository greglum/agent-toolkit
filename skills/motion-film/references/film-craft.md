# Live action and animated film craft

Use this branch for narrative shorts, recurring characters, and animation combined with
recorded footage. Keep the production record, scene contract, rights ledger and export checks
owned by motion-film. This branch supplies direction and review methods, not a video generator.

## Stage a filmable action

Translate each story beat into an observable change: what the subject wants, what it does,
what resists it, and what changes afterwards. Give each shot one dominant action chain.
Choose framing, camera movement, light and duration to make that change visible. A sequence
of explanatory cards does not by itself establish character action or a requested live-action
performance. Identify whether the brief needs filmed actors, generated photorealistic footage,
animated characters, or recorded footage with animated graphics before choosing assets.

For each location, sketch the performers, important props, camera side and action line.
Record screen positions, travel direction and eyelines. Define the space exposed by a reverse
angle before producing it. Keep the camera on a coherent side of the action unless the cut
deliberately re-establishes geography. Reject a shot whose camera and performer paths cannot
fit its duration. Finish when the shot's beginning, action and ending can be staged with the
available assets, and its connection to the neighboring shots is explicit.

## Keep identity and story state

For a recurring animated or generated character, retain one accepted identity reference and
the design details that must persist. Test an important angle or lighting change before
producing the sequence. Check which reference inputs the selected tool actually accepts;
text descriptions and a fixed seed do not guarantee stable identity.

Track only continuity fields relevant to the shot: costume, hair, distinctive marks, prop
owner and hand, object position and condition, story day, and the last event that changed
them. Changes such as a wet coat drying or an object breaking follow story order even when
shots are produced out of order. Compare later takes with the accepted identity reference,
as well as adjacent takes. Chaining from the previous frame can carry its errors forward.

For recorded actors, preserve the source performance and select compatible takes. For a
generated performance, inspect turns, occlusion, contact and expression in motion. Keep a
coherent take when a replacement only improves sharpness while changing identity. Repair a
local defect only when the intended identity and action remain recoverable; otherwise select
or produce a replacement within the existing generation authority and budget.

Finish when each retained shot agrees with the character reference and its story-state
record. A still cannot settle acting, lip sync, flicker or contact through an occlusion.

## Combine animation and footage

Give each animated layer a role: an object in the scene, a mark following a filmed subject,
or an editorial graphic fixed to the screen. Screen graphics can stay still while the camera
moves. A layer meant to inhabit the scene needs compatible tracking, perspective, occlusion,
light and contact. Record its attachment and inspect the start, strongest movement and end.

Cut for a visible cause or reaction. Match movement direction across a continuous action;
use a deliberate re-establishing shot when changing geography. Check both sides of each cut
at normal speed and frame by frame. Keep explanatory text readable without covering the
performance that carries the beat. A successful encode or attractive contact sheet does not
complete performance, playback or listening review.

## Sources and limits

Original wording, curated November 3, 2026. Source ideas were reviewed at these revisions:

- [zhangzhangco, plan-camera-shots](https://github.com/zhangzhangco/film-production-skills/blob/47b2a6a432235e716fa2aa0d08eefae76fdb34fd/skills/plan-camera-shots/SKILL.md)
  and its field guide: spatial baselines, dominant action, executable camera paths and
  targeted continuity checks. Repository LICENSE is MIT, copyright 2026 zhangzhangco.
  Retained the useful direction without its shared JSON envelopes or a seven-skill pipeline.
- [Maurice Holda / Nagacash, character-continuity](https://github.com/Nagacash/character-continuity-skill/blob/97757802b607dbd1c1e850aca3ed1b1c9f362624/skills/character-continuity/SKILL.md)
  and `references/continuity-sheet.md`: compare with accepted identity, track prop changes
  and story order, and plan unseen reverse-angle space. The entrypoint declares CC-BY-4.0
  while the root LICENSE declares MIT. No text, templates, scripts or media copied;
  resolve that discrepancy before vendoring. Fixed take counts, duration recipes, and
  provider capability claims were not adopted.

No external runner, model, paid service or authentication is installed by these instructions.
The sources do not establish local generation capability or measured quality gains.
Recheck when changing the production method, conditioning interface, reference assets or
source revision. Static catalog validation and a single illustrative film cannot establish
general character continuity or a behavioral improvement over a no-skill control.
