---
name: monitor-pr
description: Monitor an existing GitHub pull request for CI, review, thread, head and base changes. Use when asked to watch or babysit a PR; verify findings and report readiness separately from event notifications.
compatibility: Requires authenticated GitHub CLI and Python 3.10+ on macOS or Linux for the bundled watcher. Without them, use an available read-only PR connector and report monitoring limits. No installation, provider setup, or durable background scheduling is automatic.
---

# Monitor a pull request

Deliver an evidence-based PR handoff. Watching authorizes reads of the identified PR;
fixes, pushes, replies, thread resolution and merging retain their own task authority.
Read [watcher usage](references/watcher.md) before running the bundled tool.

## Bind and observe

Resolve the repository and PR number, actual head/base repositories, branches and full SHAs.
Read repository delivery rules and current checks, reviews and unresolved threads first.
Record who owns monitoring and the requested stop: a time window, next event, readiness,
or an authorized merge. Use one watcher for this PR. Do not kill another owner's watcher.

Prefer a harness-native PR event subscription when it can deliver these events and has a
known stop/unsubscribe operation. Otherwise run `scripts/watch_pr.py` by absolute path.
Keep its process handle and resume state. Wait through the harness's running-command tool;
ending a turn does not establish that a generic harness will wake you later. Report a
bounded handoff when durable wake-up is unavailable. Stop the subscription/process on handoff.

## Reconcile each event

Re-read the relevant live evidence; an event is a prompt to inspect, never approval.
Trace each bot or human finding to current source and the requested behavior. Keep stable
finding identities and record fixed, dismissed with evidence, unresolved or unverifiable.
Carry older unresolved findings forward. A finding's age does not establish that it was fixed.
Honor repository review requirements rather than hardcoding which bot matters.

Within existing fix authority, make the smallest complete correction, run affected gates,
and push only to the identified destination when authorized. Refresh head-bound evidence
after a push. Reuse unchanged evidence only when its context remains valid. Report unrelated
failures separately. Decline unrelated scope growth with a reason in the local record.

For authorized public replies or thread resolution, read [comment checks](references/comments.md).
Do not post status chatter or treat a request to monitor as permission to message others.

## Verify the handoff

Check the live head and base again. Account for pending or missing required checks, current
required approvals, unresolved findings, draft status, mergeability and repository queue rules.
A skipped or neutral check may satisfy GitHub policy without proving its tests ran. Unknown
protection, incomplete review coverage, or an unknown merge state stays unknown. Check base
changes for invalidated proof even when there is no textual conflict.

If asked to leave the PR unmerged, inspect auto-merge and queue membership. Stop before an
authorized write that could trigger an existing automatic merge unless the user has authorized
preventing that merge or settled the conflict. Do not disable someone else's queue entry silently.

Report the PR URL, exact head/base, observed events, finding dispositions, proof, and one of:
ready under the verified repository gates, waiting, blocked, merged, or closed. Include any
unavailable/unrun checks and the watcher exit reason. Merge only with existing authority for
this PR, through normal protection, after a fresh gate check; verify the resulting merge.

Source context and recheck triggers: [sources](references/sources.md).
