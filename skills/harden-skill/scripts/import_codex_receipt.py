#!/usr/bin/env python3
"""Import runtime metrics from a selected codex exec --json stream into timing.json.

Exit 0 imports a valid stream, including failed/incomplete runs; 2 is invalid input.
No model runs, grading, invocation proof or evaluation acceptance are produced.
"""

import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path


TOKEN_FIELDS = ("input_tokens", "cached_input_tokens", "output_tokens", "reasoning_output_tokens")


def import_receipt(raw, exit_code, duration=None):
    events = []
    for number, line in enumerate(raw.decode("utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except ValueError as error:
            raise ValueError(f"line {number}: invalid JSON event") from error
        if not isinstance(event, dict) or not isinstance(event.get("type"), str):
            raise ValueError(f"line {number}: expected an event object with a type")
        events.append(event)
    if not events:
        raise ValueError("empty event stream")
    if duration is not None and (not math.isfinite(duration) or duration < 0):
        raise ValueError("duration must be finite nonnegative seconds")
    counts, usage, warnings = Counter(), [], []
    active, broken_sequence, message, failed = False, False, False, False
    for event in events:
        kind = event["type"]
        counts[kind] += 1
        if kind == "turn.started":
            broken_sequence |= active
            active = True
        elif kind in {"turn.completed", "turn.failed"}:
            broken_sequence |= not active
            active = False
            failed |= kind == "turn.failed"
            if kind == "turn.completed":
                current = event.get("usage")
                if current is not None and not isinstance(current, dict):
                    raise ValueError("turn.completed: usage must be an object or absent")
                values = {}
                for key in TOKEN_FIELDS:
                    value = (current or {}).get(key)
                    if value is not None and (type(value) is not int or value < 0):
                        raise ValueError(f"turn.completed: {key} must be a nonnegative integer or absent")
                    values[key] = value
                if (values["cached_input_tokens"] is not None and values["input_tokens"] is not None
                        and values["cached_input_tokens"] > values["input_tokens"]):
                    raise ValueError("turn.completed: cached input exceeds total input")
                usage.append(values)
        elif kind == "error":
            failed = True
        elif kind == "item.completed":
            item = event.get("item")
            if isinstance(item, dict) and item.get("type") == "agent_message":
                if not active:
                    broken_sequence = True
                else:
                    message |= isinstance(item.get("text"), str) and bool(item["text"].strip())
    if active or broken_sequence or not counts["turn.started"] or not message:
        warnings.append("Stream does not establish a complete turn sequence and nonempty agent response.")
    if not usage or any(value is None for item in usage for key, value in item.items()
                        if key in {"input_tokens", "output_tokens"}):
        warnings.append("Token usage is incomplete; absent metrics remain null.")
    totals = {key: sum(item[key] for item in usage) if usage and all(
        item[key] is not None for item in usage) else None for key in TOKEN_FIELDS}
    if broken_sequence:
        totals = {key: None for key in TOKEN_FIELDS}
    total_tokens = (totals["input_tokens"] + totals["output_tokens"]
                    if totals["input_tokens"] is not None and totals["output_tokens"] is not None else None)
    status = "failed" if failed or exit_code != 0 else (
        "incomplete" if active or broken_sequence or not counts["turn.completed"] or not message else "completed")
    return {"status": "IMPORTED", "harness": "codex exec --json", "run_status": status,
            "process_exit_code": exit_code, "source_sha256": hashlib.sha256(raw).hexdigest(),
            "duration_seconds": duration, "duration_basis": "caller-observed wall time" if duration is not None else None,
            "token_usage": totals, "total_tokens": total_tokens,
            "token_basis": "reported completed turns; cached input is included in input, not added again",
            "turns_started": counts["turn.started"], "turns_completed": counts["turn.completed"],
            "turns_failed": counts["turn.failed"], "agent_message_observed": message,
            "evaluation_acceptance": "not established; grading, arms, isolation and judge evidence are separate",
            "warnings": warnings}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("receipt", type=Path)
    parser.add_argument("--exit-code", type=int, required=True, help="observed native process exit code")
    parser.add_argument("--duration-seconds", type=float, help="observed wall time; absent stays unknown")
    parser.add_argument("--output", type=Path, help="new timing.json; existing files are never overwritten")
    args = parser.parse_args()
    try:
        report = import_receipt(args.receipt.read_bytes(), args.exit_code, args.duration_seconds)
        output = json.dumps(report, indent=2) + "\n"
        if args.output:
            with args.output.open("x", encoding="utf-8") as stream:
                stream.write(output)
        else:
            print(output, end="")
    except (OSError, ValueError) as error:
        print(json.dumps({"status": "UNAVAILABLE", "error": str(error)}))
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
