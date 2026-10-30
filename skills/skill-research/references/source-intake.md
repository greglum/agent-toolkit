# Follow a source without losing the boundary

Use this reference when a round starts from an article, thread, video, or repository with
supporting links. Keep the requested focus; this reference does not start a catalog-wide
round or grant authority to run or install upstream software.

1. Inventory every substantive outbound link from the seed. Record its relationship to the
   claim being assessed. Follow linked evidence far enough to resolve that claim; classify
   navigation, profiles, promotions, duplicates, and unrelated branches separately.
2. Keep a coverage ledger: URL, parent source, content inspected, revision or timestamp,
   access limit, and disposition. A linked repository's README review is not a review of all
   its source. A video title or description is not its transcript or demonstration.
3. Recover primary text through an available browser or official source when direct fetch
   fails. For X posts and Articles, use the [recovery sequence](#x-post-and-article-recovery).
   Note automatic captions, unavailable images, missing demonstrations, and any inferred
   wording. Do not silently substitute a third-party summary for the original.
4. Distinguish author claims, source observations, inference, and measured results. Follow
   implementation details needed for an adopted lesson. Preserve contrary evidence and
   explicit limits on what was run.
5. For tools, distinguish telemetry from operational data transfer. Inspect sync scope,
   pending-event replay, remote commands, token revocation, optional integrations, and build
   prerequisites when those affect a proposed adoption. Do not equate public source or a
   disabled analytics key with a verified private deployment.
6. End with every substantive seed link accounted for as inspected, unavailable, or deferred
   with a reason. Carry unresolved evidence dependencies into the report. Report bounded
   coverage rather than claiming all recursively linked internet content was reviewed.

## X post and Article recovery

A web reader's 403, empty response, or login shell establishes that reader's access limit,
not that the post is unavailable. Use the following sequence for `x.com` and `twitter.com`:

1. Prefer an available browser when the web reader has known X access failures; a new task
   need not rediscover the same 403. Keep the supplied URL in the ledger. For a status URL,
   open `https://x.com/<author>/status/<id>` without share parameters. Preserve a supplied
   direct Article path. Switch away from a failed reader rather than retrying URL spellings.
   If that browser backend is disabled or fails, inspect the available browser/app inventory
   and try another permitted route, including native browser controls such as Safari when
   supported. One backend's failure does not establish that all browsers are unavailable.
   Respect the user's browser restrictions; do not change settings, launch a prohibited
   browser, or route around an approval rejection.
2. Read the rendered accessibility tree or DOM snapshot. An Article can appear in full
   inside its status page. If only a preview appears, follow its visible Article link or
   expansion control. Use the actual destination the page exposes; do not guess Article IDs.
   Accessibility output can truncate a long text node even when the whole post is rendered.
   Inspect screenshots and scroll through the omitted text before claiming full coverage.
3. Confirm author, title or opening text, displayed date, and the end of the body. Read all
   sections, expanding or scrolling as needed. Separate the author's body from replies,
   quoted posts, profile links, and recommendations. Record an unknown display timezone
   rather than inventing one. Text recovery does not establish image or video inspection.
4. Inspect substantive links in the recovered body. Follow visible shortened links to their
   actual destinations and record both when needed. Cite the canonical original post for
   its claims, and the destination source for evidence checked there. Keep a compact ledger
   of the recovery method, body coverage, missing media, and access limits.
5. After available permitted browser routes fail, search once by exact post ID, or by author
   and distinctive title, for an author-published copy. Verify identity and completeness.
   Search snippets, embedded previews, mirrors, and summaries are leads; label any recovered
   copy's provenance and omissions. An unofficial copy alone does not establish a full
   primary-source review. Do not present untested proxy hosts or syndication endpoints as
   established fallbacks. Stop at login or access barriers under the session's authority;
   do not install a scraper or change account access to recover a source.

Finish with primary text recovered, partial coverage, or UNAVAILABLE, naming the failed
reader and fallback used. Keep an unrecovered primary source UNAVAILABLE even when a
secondary account is useful. Ask for supplied text only when missing content blocks the
assessment after these available paths.

These are original intake instructions. The telemetry/synchronization distinction was
checked against HumanLayer's
[Pi documentation at the reviewed revision](https://github.com/humanlayer/humanlayer-pi/blob/f4bd3ed65cfdb8dfea474b4cadce2ed90cc4acbd/README.md).
Observed October 24, 2026. Recheck the actual source and destination before a tool trial;
this reference does not certify the plugin or prescribe it.
