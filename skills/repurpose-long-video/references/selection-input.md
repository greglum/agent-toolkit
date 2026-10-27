# Selection input and output

`scripts/select_clips.py` reads one JSON object and writes a new JSON file. It uses the
Python standard library only and makes no network calls. It checks timing and overlap;
it cannot judge whether a clip stands alone or keeps its meaning.

## Input

```json
{
  "source": {"file": "talk-2026-10-01.mp4", "sha256": "...", "duration": 3721.4},
  "segments": [
    {"start": 12.40, "end": 12.71, "text": "The"},
    {"start": 12.71, "end": 13.05, "text": "point"},
    {"start": 13.05, "end": 13.60, "text": "is."}
  ],
  "candidates": [
    {"id": "w2-03", "start": 1204.0, "end": 1251.5, "score": 82,
     "reason": "Complete answer to why the cache failed, with the fix"}
  ]
}
```

- `source`: optional. Copied to the output unchanged so the result names its source.
- `segments`: the merged transcript in source seconds. Each item has `start`, `end`, and
  `text`. Words or phrases both work. Merge overlapping windows first and remove the
  duplicated words from each overlap; duplicates corrupt sentence grouping.
- A sentence ends at a segment whose text ends in `.`, `!`, `?`, or an ellipsis, allowing a
  closing quote or bracket. A transcript with no such punctuation is an input error: add
  punctuation with the existing transcriber's option, or mark boundaries by hand.
  Abbreviations such as "Mr.", "e.g.", or "U.S." also count as sentence ends, so a clip
  can open mid-sentence: check the opening words of every kept clip.
- `candidates`: a unique, non-empty string `id`, `start` and `end` in source seconds, a
  numeric `score` (higher is better), and a non-empty `reason`. A missing or duplicate id
  is an input error. Use ids that name the window, so a clip can be traced back.

## Command

```bash
python3 -I <skill>/scripts/select_clips.py candidates.json --out selection-01.json \
  --count 5 --min-seconds 20 --max-seconds 60 --overlap 0.5
```

`--count`, `--min-seconds`, and `--max-seconds` are required: take them from the brief or
the destination's current limits. `--overlap` defaults to 0.5. Minimum, maximum, and
overlap must be finite. The output path must not exist. Exit 0 means written; exit 2 means an input or usage error, with nothing written.

## Rules applied, in order

1. **Snap.** The start moves back to the start of the sentence it falls in, or forward to
   the next sentence when it falls in a gap. The end moves forward to the end of its
   sentence, or back to the previous sentence end in a gap. A range with no whole sentence
   is rejected.
2. **Cap.** Over `--max-seconds`, whole trailing sentences are dropped until it fits. A
   single sentence over the cap is rejected. Under `--min-seconds` is rejected.
3. **Suppress.** In score order (ties: earlier start, then input order), a clip whose
   shared time with an already kept clip exceeds `--overlap` of the shorter clip is
   rejected, naming the kept clip. A clip whose snapped span equals a kept clip's is
   always rejected, even at `--overlap 1`.
4. **Top N.** After `--count` clips are kept, the rest are rejected as outside the top N.

## Output

`kept` lists clips in rank order with `id`, `rank`, `proposed_start`, `proposed_end`,
snapped `start` and `end`, `duration`, `score`, `reason`, `text`, and `review_flags`.
A flag marks an opening word such as "and", "but", "this", or "they" that often points
to earlier context; it is advisory and English-only. `rejected` lists every other
candidate with `rejected_because`. `settings` records the limits used, the number of
sentences found, `shortfall` (clips wanted minus clips kept, at least 0), and
`unterminated_tail`: the start, end, and text of trailing transcript with no closing
punctuation, which no clip can use, or null. Snapping can move a start back and an end
forward by most of a sentence, so read the snapped text, not the proposal.
