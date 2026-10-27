# Sources and local departures

Original wording and code, October 25, 2026. No upstream code, prompts, or prose copied.

## Upstream

- [Anil-matcha/AI-Youtube-Shorts-Generator at 70c5fa9](https://github.com/Anil-matcha/AI-Youtube-Shorts-Generator/tree/70c5fa96984cbc35b3b76a981a81c676117370ec),
  commit dated October 22, 2026, observed October 25, 2026. MIT License, copyright 2026
  Anil Chandra Naidu Matcha. Read from a blobless clone; nothing was installed or run.
- Ideas adopted, restated: split a long transcript into overlapping windows so a moment at
  a boundary survives; ask for about twice the wanted candidates so suppression has room;
  score each candidate with a one-line reason; drop a candidate that overlaps a
  higher-scored one past a threshold; take the top N; reframe with a crop window that
  follows the largest detected subject with smoothing and starts from the frame centre.
- The catalog's October 23, 2026 source review identified long-video clipping as a
  distinct workflow. The upstream link above preserves the source for this bundle.

## Local departures

- **Rights first.** Upstream downloads from a video platform by URL. This skill works only
  on media the user owns or has licensed, and never downloads without rights and terms.
- **No provider choice.** Upstream defaults to a hosted service with keys for
  transcription, ranking, and clipping, and names specific models. This skill uses the
  project's existing tools and names none; a paid or hosted call needs the user's authority.
- **No virality score.** Upstream ranks on predicted viral potential. Here the score is the
  agent's judged fit to the brief with a stated reason, and no reach is promised.
- **Sentence snapping in code.** Upstream asks the model not to cut mid-sentence. Here
  `select_clips.py` snaps every candidate to sentence bounds and enforces the duration range
  after snapping, so a request alone is not trusted.
- **Overlap measured against the shorter clip.** Upstream compares shared time with the
  lower-scored candidate's own length. Measuring against the shorter clip is symmetric and
  also catches a long clip that swallows a short one.
- **Context and claims check.** Added: each clip is read against the surrounding transcript
  for a meaning changed by the cut.
- **Reframe hold, shot resets, and frame review.** Upstream smooths across the whole clip.
  Here the crop holds through brief misses, falls back to centre or a fit, resets at shot
  cuts, and every clip's frames are checked for cut-off subjects and on-screen text.
- **Originals and outputs kept.** Upstream writes fixed output names and deletes
  intermediates. Here outputs go to new paths with an edit list, and nothing is overwritten.

## Recheck

Recheck when the upstream selection or reframe logic changes, when the project's
transcriber changes its word-timing output, or when a destination changes its vertical
format limits.
