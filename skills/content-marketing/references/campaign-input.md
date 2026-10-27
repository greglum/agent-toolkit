# Campaign input and outputs

Use UTF-8 JSON, schema version 1. Unknown fields, duplicate object keys, duplicate claim/item
IDs and duplicate content observations in a cohort fail. No placeholders count as evidence.
The builder is offline: `verified` records the agent's completed source/link check, not a
network check performed by the script.

The [neutral example](../examples/campaign.json) is a synthetic planning fixture, not a
real campaign or performance record. Copy its shape, replace its facts, and add observations
only when authorized exports exist. All fields shown are required; observations may be empty.

## Campaign and claims

| Object | Fields |
| --- | --- |
| Top level | `schema_version`: 1; `campaign`: object; `claims`, `items`, `observations`: lists |
| `campaign` | `id`: public-safe lowercase slug; `audience`, `goal`, `hypothesis`: nonempty text; `owned_site`: HTTPS origin; `review_on`: YYYY-MM-DD; `measurement`: reporting source/action/window; `decision_rule`: repeat/revise/stop criteria chosen before results |
| Each claim | Unique `id`, factual `statement`, public `source_url`, precise `locator`, `checked_at` observation date, `status`: `verified` or `unverified` |

Hypotheses describe what to test, not accomplished results. Claim source links must be public
HTTPS URLs, not private repository paths. Keep a separate private evidence record when needed.

## Channel items

Each item has these fields:

| Field | Contract |
| --- | --- |
| `id` | Unique lowercase slug; used as `utm_content` |
| `platform`, `format` | `youtube`: `video` or `short`; `linkedin`: `post`, `video` or `article`; `website`: `page` |
| `placement` | YouTube: `description`, `profile`, `related_video`; LinkedIn: `post`; website: `link` |
| `title`, `hook`, `cta`, `measure` | Nonempty text. `measure` names the report, metric and elapsed review window |
| `outline` | Nonempty list of concrete steps; no empty lines or unfinished scaffold |
| `claim_ids` | Nonempty list of unique existing claim IDs supporting factual content |
| `destination_url` | Actual public HTTPS destination, or null when not yet available |
| `link_access` | `verified` only after checking both URL and placement access; otherwise `unknown` |

`related_video` is for a Short linking to an actual YouTube watch URL. A Short's description
link, unknown link access or unverified cited claim blocks readiness. The tool does not create
platform text or enforce platform length limits; the rendered fields are creative briefs.

The builder replaces existing UTM fields only on unblocked outbound links to `owned_site`:
`utm_source` is the publishing platform, `utm_medium=social`, `utm_campaign` is the campaign
ID and `utm_content` is the item ID. Unrelated query fields and fragments survive. Other
destinations keep their URL; no attribution is promised there. No personal data in IDs or URLs.

## Observations from authorized exports

Each row records a count over the **first `window_hours` after publication**. A later capture
is valid only if the export filters that exact period. Do not relabel a lifetime count as
seven-day performance just because the post is older than seven days. The builder can verify
elapsed time, not that the export was filtered correctly. Retain the raw export and locator.

```json
{
  "content_id": "post-01",
  "platform": "linkedin",
  "account": "owned-account",
  "format": "post",
  "metric": "outbound_clicks",
  "definition": "Visits to external links including repeats, from the personal post export",
  "scope": "organic-public-link-posts",
  "window_hours": 168,
  "published_at": "2026-10-01T00:00:00Z",
  "observed_at": "2026-10-08T00:00:00Z",
  "status": "complete",
  "value": 12,
  "source": "authorized-export.csv:row-2"
}
```

`metric` is `impressions`, `views`, `outbound_clicks`, or `site_sessions`. Keep the exact
definition: a platform-wide click count may include clicks that are not outbound traffic.
`status` is `complete`, `partial`, or `unavailable`. Complete requires a finite nonnegative
value and the elapsed window; unavailable requires null; partial permits an observed value
or null. Timestamps need timezones. Record one snapshot per content/cohort, not duplicate
captures of the same result. No people, demographics, credentials or raw visitor data.

Cohorts match every field: platform, account, format, metric, definition, scope and window.
For each complete row, its peer median excludes that row and uses at least three complete
peers. A zero median, insufficient peers, or an incomplete row yields no lift, with a reason.
There is no pooled ranking across cohorts and no cap on totals. These are descriptive
comparisons, not confidence levels. Fields are preserved in JSON/CSV; formula-like CSV text
is prefixed with an apostrophe for spreadsheet safety. JSON retains the original strings.

## Review outputs

- `campaign.json`: input digest, campaign, claims, prepared items with status/blockers/links,
  and all cohort results. Keep it with the input and source exports for the next review.
- `brief.md`: readable channel briefs, evidence and measurement limitations. No approvals.
- `performance.csv`: every observation, raw count, peer count/median, lift and comparison limit.

Builds never replace an existing output directory. Validation completes before output is
created. A write failure may leave a partial new directory; inspect it and use a fresh path
after correcting the cause. Nothing is posted, fetched, scheduled or appended to a shared ledger.
