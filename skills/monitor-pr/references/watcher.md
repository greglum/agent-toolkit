# Event watcher

Run by absolute script path, with an explicit target:

```bash
python3 <skill-dir>/scripts/watch_pr.py 24 --repo owner/repo --once
python3 <skill-dir>/scripts/watch_pr.py 24 --repo owner/repo --timeout 300
```

The first observation emits the current snapshot summary, including existing unresolved
threads. Subsequent runs compare persistent state and emit only changed categories. It watches
head/base/state, draft/auto-merge, merge state, review decision, checks, review submissions,
comments, and thread/reply changes. It paginates top-level comments, reviews, inline comments
and thread states; body hashes detect edits without persisting reply text. It reports base
movement without computing file overlap. Inspect affected source after that event.

This is a notifier. It does not classify merge readiness, discover protection rules, prove
checks executed, review code, resolve threads, write to GitHub, or schedule future turns.
`gh pr checks --watch --required` is a simpler native choice for a CI-only request.

State uses `~/.local/state/skills/monitor-pr/`, or `--state-dir <directory>`. It contains PR
identities, URLs, timestamps and hashes, not comment bodies or credentials. It is private local
metadata, written atomically. One OS lock per target prevents duplicate watchers within that
state directory. All owners must use the same directory; this is not a cross-machine lock.
Corrupt or incompatible state fails visibly. Preserve it and use a new directory to rebaseline.
A crash between output and save can replay an event; notifications are not exactly-once.

Exit codes: `0` initial snapshot (`--once`), an event, or terminal merged/closed state;
`3` deadline reached without a new event; `1` access, API, schema, race or state error;
`2` invalid arguments or another watcher holds the lock; `130` interrupted. No exit code means
ready to merge. A failure preserves the prior successful snapshot. A head/base change during
collection rejects that sample. GitHub cannot supply an atomic multi-API snapshot; re-read
live gates before acting. A transient failure ends this bounded run; inspect rate limits and
retry through the owning task with backoff rather than spawning a second poller.

Use the command runner's asynchronous handle for longer runs. The timeout bounds polling;
each API request also has a timeout. No daemon or recurring task is installed.
