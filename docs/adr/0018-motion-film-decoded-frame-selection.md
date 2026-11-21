# 0018: Select Actual Decoded Video Frames with setpts/select Rather Than fps Resampling

- Status: Accepted
- Date: 2026-11-20

## Context

motion-film/scripts/contact_sheet.py samples video frames at fixed intervals for visual inspection, where ffmpeg's fps filter would synthesize or duplicate frames at invented timestamps.

## Decision

Use `setpts=PTS-STARTPTS,select='isnan(prev_selected_t)+gte(t-prev_selected_t,...)'` to sample actual decoded frames while preserving timestamps relative to the first decoded frame.

## Consequences

Contact sheets reflect authentic decoded frames and real presentation times on both constant- and variable-frame-rate video.

## Code References

- `skills/motion-film/scripts/contact_sheet.py:42`
- `skills/motion-film/scripts/contact_sheet.py:43`
