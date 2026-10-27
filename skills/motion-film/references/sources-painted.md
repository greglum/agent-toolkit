# Painted-material sources

The material-space and redraw-cadence refinement in [genre direction](genres.md) is original
guidance prompted by Tobia Donadon's
[Shorts Animator article](https://x.com/tobiadonadon_/status/2114445880522604545)
and [public product page](https://www.tobiadonadon.com/projects/construct/material/skills/shorts-animator),
observed October 25, 2026. The article displays October 25, 9:55 AM, timezone unspecified.
The public bundle, its implementation and reuse license were not available for review.
No package, prompt, code, media or source prose was copied or installed.

Independent checks:

- Toon Boom's [Harmony 25 Animate Pencil Line Texture Node](https://docs.toonboom.com/help/harmony-25/premium/reference/node/filter/animate-pencil-line-texture-node.html),
  Hold Mode, Hold Value, Random Seed and Offset Types, observed October 25, 2026; page shows
  updated March 26, 2026 and all rights reserved. Separates texture transformation from
  drawing motion and documents different exposure/hold choices. No universal cadence adopted.
- Corrêa, Jensen, Thayer and Finkelstein, [Texture Mapping for Cel Animation](https://media.disneyanimation.com/uploads/production/publication_asset/45/asset/2DTextureMapping_1998.pdf),
  abstract and introduction, retrieved October 25, 2026 from Disney Animation's research
  host. Temporal inconsistency can make paint slide or boil unintentionally. Publication
  year is suggested by the URL, not verified from the inspected paper text; reuse rights
  not established. No warping algorithm or 3D requirement adopted.
- Remotion's [Flickering](https://www.remotion.dev/docs/flickering), Multi-threading issue,
  observed October 25, 2026. Corroborates frame-order independence; page redistribution
  rights not checked. Exposure-index sampling is a local design conclusion from this
  constraint and Toon Boom's hold behavior, not an inspected Shorts Animator implementation.

Recheck when the style, sampling, camera, material coordinates or output profile changes.
The refinement does not bundle a painted-scene renderer or prove rendering speed, revenue,
output quality or behavioral benefit. A paired behavioral trial and local film render were
not run.
