# Import a selected Codex runtime receipt

Use this when a comparison already captured `codex exec --json` output. It is a small
offline adapter into the existing case arm's `timing.json`, not a runner or a new evaluation
format. Run no model and read no private session store to use it. Preserve the raw capture
privately; its digest binds the derived record without copying messages or native IDs.

```sh
python3 <skill-dir>/scripts/import_codex_receipt.py case-output/events.jsonl \
  --exit-code 0 --duration-seconds 12.4 --output case-output/timing.json
```

Supply the native process's observed exit code, not the importer's exit code. Supply elapsed
wall time only when measured; omit the duration flag when unknown. The output must be new.
The helper never runs commands from events, applies a candidate, overwrites existing evidence,
invents a model/version, derives prices or creates `grading.json`/benchmark acceptance.

The importer supports the JSONL event shape in the current official guide: turn start,
completion/failure, error events and completed agent messages. It checks sequence boundaries,
preserves failed/incomplete runtime states, and rejects malformed events or invalid token
counts. An agent-message completion outside an active turn makes the sequence incomplete;
it cannot supply response proof. Unknown event types do not provide turn or grading evidence.
A completed native turn
with absent usage keeps those metrics null; absent duration also stays null. Broken turn
ordering makes aggregate token metrics unknown.

`token_usage` preserves reported input, cached input, output and reasoning-output counts when
present for all completed turns. `total_tokens` is reported input plus output. Cached input
is included in input, not added again; reasoning output is also kept separate rather than
added to output. Failed turns can have no usage, so the stated basis is completed turns,
not an estimate of all failed work. Keep the native client's version and run identity in the
existing comparison manifest; inspect changed event schemas before extending this adapter.

Exit 0 means the selected stream was imported, including a failed or incomplete source run.
Exit 2 means invalid/unreadable input or an output collision. Always inspect `run_status`,
warnings and null metrics. `turn.completed` is runtime evidence only: it does not prove skill
invocation, isolation, a correct artifact, independent grading, a passing control or permission
to apply. The existing [evaluation protocol](evaluation.md#grading) remains the acceptance owner.

## Source and checked scope

Original implementation and synthetic fixtures, observed November 4, 2026. OpenAI's official
[non-interactive guide](https://learn.chatgpt.com/docs/non-interactive-mode), JSON Lines section,
documents `codex exec --json`, turn events and usage fields. It is a living page; reuse rights
were not established and no prose or implementation was copied. The importer consumes its
documented shape, not every historical rollout format. Recheck before adopting another CLI
version or event family. Offline tests establish parsing, privacy of derived output and
preservation only; native execution and skill/control effectiveness were not run.
