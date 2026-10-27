# Lift input contract

UTF-8 CSV with exactly these columns, in any order. One row per post per metric.

| Column | Contract |
| --- | --- |
| `account` | Public handle or channel name of the account that published the post |
| `platform` | Lowercase platform name, such as `youtube`, `linkedin`, `x`, `tiktok`. Uppercase is rejected |
| `format` | The platform's own format in lowercase, such as `video`, `short`, `post`, `article`, `reel`. Uppercase is rejected |
| `post_id` | Stable post identifier; unique within its cohort |
| `url` | Public `https://` link to the post |
| `published_at` | `YYYY-MM-DD[THH:MM[:SS]][Z]`, read as UTC. No offsets or fractions. A date alone counts the window from the end of that day |
| `observed_at` | When you read the value, in the same format. Not before `published_at` |
| `age_window` | Post age the value was counted at: `48h`, `7d` and so on. `1d` and `24h` match. No `lifetime` |
| `metric` | One count definition per name, such as `views`, `likes`, `comments`, `shares` |
| `value` | Raw nonnegative number as read; empty only when `status` is `unavailable` |
| `status` | `complete`, `partial` (count incomplete or window not yet elapsed), or `unavailable` |
| `source` | Where the row came from: `export` (user file), `api` (official API or analytics), or `page` (public page) |

A cohort is one account, platform, format, metric and age window. Only rows in the same
cohort are compared. A row's lift is its value over the median of the cohort's other
complete rows; there is no lift under 3 such peers or on a zero median. If a source only
shows a current total, record the post's real age window, or mark the row `partial`; do not
convert totals with a growth curve.

The script rejects missing or extra columns, empty required cells, uppercase `platform` or
`format`, non-HTTPS URLs, unparsed dates, an `observed_at` before `published_at`, a `complete`
row observed before `published_at` plus its age window, open-ended windows, an unknown
`source`, negative or non-numeric values, a value on an unavailable row, and a duplicate post
within a cohort. Fix the input and rerun into a new directory.

## Outputs

- `lift.json`: input SHA-256, row count, and per cohort its totals by status and every row
  with its cells, `peer_count`, `peer_median`, `lift`, and `excluded` (the reason no lift
  was given).
- `lift.md`: one section per cohort, scored rows by lift with raw values and source, then
  every unscored row with its reason. `--top` limits only this table; totals and the JSON
  keep every row.

`lift.json` keeps text cells as read; only `age_window` is normalized to hours. In `lift.md`, text cells starting with `=`,
`+`, `-` or `@` gain a leading `'` so a spreadsheet will not run them, and Markdown control
characters are escaped.
