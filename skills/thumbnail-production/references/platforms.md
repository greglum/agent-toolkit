# Platform limits and release review rules

Read this before producing final platform exports or reviewing post-release thumbnail tests.
Platform limits and Studio controls change over time; verify the target account's current
upload surface before delivery.

## Export and upload rules

- **YouTube long-form:** use a 16:9 composition. Check the current recommended export size
  separately from the experiment threshold. A variant below 1280 by 720 downscales the
  whole test set. Eligible Studio accounts can compare up to three choices concurrently.
  Hold the title fixed for a thumbnail-only test.
- **YouTube Shorts:** use a separate vertical composition for the custom thumbnail upload
  documented for desktop Studio. Verify the actual account control and current limits.
  Shorts are outside the long-form A/B test.
- **LinkedIn:** distinguish a native video thumbnail from a post image or linked-page preview.
  Desktop native video upload has a thumbnail control; check the actual account and composer.
  Match the intended video's shape and inspect feed cropping. A YouTube export is not proof
  of LinkedIn fit, and a cover is not the same as the opening frame during autoplay.

## Release and A/B test metrics

- YouTube thumbnail tests evaluate watch time rather than CTR alone; inconclusive and
  same-performance outcomes are valid results.
- High views on another creator's video do not isolate the thumbnail's effect.
- Keep LinkedIn results separate and do not claim equivalent native thumbnail testing.

## Dates and recheck triggers

- YouTube documentation checked November 5, 2026:
  [desktop uploads and export sizes](https://support.google.com/youtube/answer/72431?co=GENIE.Platform%3DDesktop&hl=en)
  and [A/B tests](https://support.google.com/youtube/answer/16391400).
- LinkedIn documentation checked October 26, 2026:
  [LinkedIn native video](https://www.linkedin.com/help/linkedin/answer/a7486279).
- Recheck trigger: verify current dimensions, file-size caps, A/B slot counts, and desktop
  composer controls whenever preparing a release package or after platform UI changes.
