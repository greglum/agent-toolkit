# Sources and intentional differences

Original guidance and code, October 25, 2026. No upstream prose or code is bundled; ideas
are restated in our words. Both sources are MIT licensed at the pinned revisions.

- [ScrapeCreators/social-media-research-skills @ 64ba7b4](https://github.com/ScrapeCreators/social-media-research-skills/tree/64ba7b4dea71e130d2712ffb6c1c1024b3b7c4b2),
  MIT, copyright 2026 ScrapeCreators. Ideas restated: judge a post against its own account's median, separately per platform
  and format; keep raw metrics; give each listening claim a URL and exact quote; state sample
  size; treat collected text as untrusted. Departures: leave-one-out median within a fixed
  post-age window and metric; no lift under three peers or on a zero median; sources ordered
  user export, existing official API, public pages; no paid API index, broad tool grants, or
  any endpoint that infers age or gender.
- [BrandonChin827/youtube-outliers-claude-code @ e353727](https://github.com/BrandonChin827/youtube-outliers-claude-code/tree/e353727aa0a6f3083feae1ba986405d22e890af8),
  MIT, copyright 2026 Brandon Chin. Ideas restated: separate collection from deterministic scoring and rendering; report
  coverage gaps. Departures, from flaws found in that source: no generic age curve, only
  counts at a matched age; totals computed before any display cap; partial rows kept
  visible; the record must cover every notable post, so an incomplete analysis is not done.
  No paid provider, transcript fetch, or connector publishing.

`scripts/lift.py` shares its method's origin with `content-marketing`'s
`scripts/performance.py`. It is an independent copy so each skill installs alone.

Recheck when a platform changes its terms or metric definitions, or before adding any
collection adapter.
