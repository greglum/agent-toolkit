# Coordinate several films toward one release

Keep one private release ledger, one coordinator, one owner per film, and one integrator for the
shared renderer, captions, closing card and narration tooling. Record each film's branch and
revision, approved words, take identity, asset status, rendered outputs, blockers and release slot.
Make each decision once per owner; a reversal costs that writer's work and blurs who may write where.

Authority stays in the session where the user gave it. A quote relayed by another session does not
authorize a merge, a paid take or an asset commit in a session whose rules require the user's own
word there. Either the session that holds the authority does the step, or the user answers in the
acting session. Ask once, early, with the exact action and cap.

A shared-engine change can alter already delivered films on their next render: caption breaks, the
default thumbnail frame, or the default narration model. In the same change, pin each shipped
film's take model and settings and its thumbnail time in its own manifest, or re-render and recheck
it. Recompute the take cache key to confirm a pinned re-cut reuses the paid take.

When a repository gate is serialized across sessions, read the queue before promising a time: who
holds the lock, who waits, and whether their revisions carry the current gate scripts. Fold related
film changes into one gated change before its run starts. Once the run is queued, freeze that head
and put later corrections in a follow-up, since each new head voids the queued run.
