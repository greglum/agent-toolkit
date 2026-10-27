#!/usr/bin/env python3
"""Snap clip candidates to sentence bounds, filter by duration, suppress overlaps, keep top N.

Standard library only; reads and writes local JSON, makes no network calls.
Input format: references/selection-input.md. Exit 0: written, 2: input or usage error.
"""

import argparse
import json
import math
from pathlib import Path
import sys

TERMINAL = (".", "!", "?", "…")
CLOSERS = "\"')]}”’"
# Advisory only: an opening word that often points back to earlier context.
DANGLING_OPENERS = {
    "and", "but", "so", "because", "which", "that", "this", "these", "those", "it",
    "he", "she", "they", "them", "also", "then", "anyway", "or", "plus",
}


class InputError(ValueError):
    pass


def number(value, field, where):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise InputError(f"{where}: '{field}' must be a number")
    try:
        value = float(value)
    except OverflowError:
        raise InputError(f"{where}: '{field}' is too large") from None
    if not math.isfinite(value):
        raise InputError(f"{where}: '{field}' must be finite")
    return value


def ends_sentence(text):
    return text.rstrip().rstrip(CLOSERS).endswith(TERMINAL)


def load_segments(raw):
    if not isinstance(raw, list) or not raw:
        raise InputError("'segments' must be a non-empty list")
    segments = []
    for i, seg in enumerate(raw):
        where = f"segments[{i}]"
        if not isinstance(seg, dict) or not isinstance(seg.get("text"), str):
            raise InputError(f"{where}: needs start, end, and text")
        start, end = number(seg.get("start"), "start", where), number(seg.get("end"), "end", where)
        if start < 0 or end < start:
            raise InputError(f"{where}: needs 0 <= start <= end")
        segments.append({"start": start, "end": end, "text": seg["text"].strip()})
    segments.sort(key=lambda s: (s["start"], s["end"]))
    return [s for s in segments if s["text"]]


def sentences(segments):
    """Group segments into sentences ended by terminal punctuation.

    Returns (sentences, tail). The tail is trailing text with no closing punctuation, which
    no clip can use; it is returned so the output can record it, or None.
    """
    found, current = [], []
    for seg in segments:
        current.append(seg)
        if ends_sentence(seg["text"]):
            found.append({"start": current[0]["start"], "end": current[-1]["end"],
                          "text": " ".join(s["text"] for s in current)})
            current = []
    tail = None
    if current:
        tail = {"start": current[0]["start"], "end": current[-1]["end"],
                "text": " ".join(s["text"] for s in current)}
    return found, tail


def snap(start, end, sents):
    """Return (first, last) sentence indexes covering [start, end], or None.

    Start moves back to the start of the sentence it falls in, or forward to the next
    sentence when it falls in a gap. End moves forward to the end of its sentence, or back
    to the previous sentence end when it falls in a gap.
    """
    first = next((i for i, s in enumerate(sents) if s["end"] > start), None)
    last = next((i for i in range(len(sents) - 1, -1, -1) if sents[i]["start"] < end), None)
    if first is None or last is None or last < first:
        return None
    return first, last


def overlap_ratio(a, b):
    shared = min(a["end"], b["end"]) - max(a["start"], b["start"])
    shorter = min(a["end"] - a["start"], b["end"] - b["start"])
    return max(0.0, shared) / shorter if shorter > 0 else 0.0


def select(data, count, min_seconds, max_seconds, overlap_threshold):
    if not all(math.isfinite(v) for v in (min_seconds, max_seconds, overlap_threshold)):
        raise InputError("min, max, and overlap must be finite numbers")
    if count < 1 or min_seconds <= 0 or max_seconds < min_seconds or not 0 <= overlap_threshold <= 1:
        raise InputError("need count >= 1, 0 < min <= max, and 0 <= overlap <= 1")
    if not isinstance(data, dict):
        raise InputError("input must be a JSON object")
    sents, tail = sentences(load_segments(data.get("segments")))
    if not sents:
        raise InputError("no sentence boundaries: no segment text ends in . ! or ?")
    raw = data.get("candidates")
    if not isinstance(raw, list) or not raw:
        raise InputError("'candidates' must be a non-empty list")
    seen = set()
    for i, cand in enumerate(raw):
        if not isinstance(cand, dict):
            raise InputError(f"candidates[{i}]: must be an object")
        cid = cand.get("id")
        if not isinstance(cid, str) or not cid.strip():
            raise InputError(f"candidates[{i}]: 'id' must be a non-empty string")
        if cid in seen:
            raise InputError(f"candidates[{i}]: duplicate id '{cid}'")
        seen.add(cid)

    rejected, snapped = [], []
    for i, cand in enumerate(raw):
        where = f"candidates[{i}]"
        base = {"id": cand["id"], "order": i}
        try:
            start = number(cand.get("start"), "start", where)
            end = number(cand.get("end"), "end", where)
            score = number(cand.get("score"), "score", where)
        except InputError as err:
            rejected.append({**base, "rejected_because": f"invalid: {err}"})
            continue
        reason = cand.get("reason")
        base.update(proposed_start=start, proposed_end=end, score=score, reason=reason)
        if not isinstance(reason, str) or not reason.strip():
            rejected.append({**base, "rejected_because": "invalid: no reason given"})
            continue
        if end <= start:
            rejected.append({**base, "rejected_because": "invalid: end is not after start"})
            continue
        span = snap(start, end, sents)
        if span is None:
            rejected.append({**base, "rejected_because": "no complete sentence inside the proposed range"})
            continue
        first, last = span
        # Over the cap: drop trailing sentences, never cut inside one.
        while last > first and sents[last]["end"] - sents[first]["start"] > max_seconds:
            last -= 1
        clip = {**base, "start": sents[first]["start"], "end": sents[last]["end"]}
        clip["duration"] = round(clip["end"] - clip["start"], 3)
        clip["text"] = " ".join(s["text"] for s in sents[first:last + 1])
        if clip["duration"] > max_seconds:
            rejected.append({**clip, "rejected_because": f"longer than {max_seconds:g} s after snapping"})
        elif clip["duration"] < min_seconds:
            rejected.append({**clip, "rejected_because": f"shorter than {min_seconds:g} s after snapping"})
        else:
            opener = clip["text"].split()[0].strip(",.;:!?\"'").lower()
            clip["review_flags"] = (
                [f"opens with '{opener}': check it stands alone"] if opener in DANGLING_OPENERS else [])
            snapped.append(clip)

    kept = []
    for clip in sorted(snapped, key=lambda c: (-c["score"], c["start"], c["order"])):
        same = next((k for k in kept if (k["start"], k["end"]) == (clip["start"], clip["end"])), None)
        clash = same or next((k for k in kept if overlap_ratio(clip, k) > overlap_threshold), None)
        if same is not None:
            rejected.append({**clip, "rejected_because": f"same snapped span as kept '{same['id']}'"})
        elif clash is not None:
            ratio = overlap_ratio(clip, clash)
            rejected.append({**clip, "rejected_because":
                             f"overlaps kept '{clash['id']}' by {ratio:.0%} of the shorter clip"})
        elif len(kept) >= count:
            rejected.append({**clip, "rejected_because": f"outside the top {count}"})
        else:
            kept.append({**clip, "rank": len(kept) + 1})

    for item in kept + rejected:
        item.pop("order", None)
    return {
        "settings": {"count": count, "min_seconds": min_seconds, "max_seconds": max_seconds,
                     "overlap_threshold": overlap_threshold, "sentences_found": len(sents),
                     "shortfall": max(0, count - len(kept)), "unterminated_tail": tail},
        "source": data.get("source"),
        "kept": kept,
        "rejected": rejected,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("input", type=Path)
    parser.add_argument("--out", type=Path, required=True, help="new JSON file; never overwritten")
    parser.add_argument("--count", type=int, required=True, help="clips wanted")
    parser.add_argument("--min-seconds", type=float, required=True)
    parser.add_argument("--max-seconds", type=float, required=True)
    parser.add_argument("--overlap", type=float, default=0.5,
                        help="suppress a clip sharing more than this share of the shorter clip (default 0.5)")
    args = parser.parse_args(argv)
    if args.out.exists():
        print(f"error: {args.out} exists; choose a new output path", file=sys.stderr)
        return 2
    try:
        data = json.loads(args.input.read_text(encoding="utf-8"))
        result = select(data, args.count, args.min_seconds, args.max_seconds, args.overlap)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, InputError) as err:
        print(f"error: {err}", file=sys.stderr)
        return 2
    try:
        text = json.dumps(result, indent=2, allow_nan=False) + "\n"
    except ValueError as err:
        print(f"error: {err}", file=sys.stderr)
        return 2
    try:
        with args.out.open("x", encoding="utf-8") as handle:
            handle.write(text)
    except OSError as err:
        print(f"error: {err}", file=sys.stderr)
        return 2
    print(f"kept {len(result['kept'])} of {len(data['candidates'])}; wrote {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
