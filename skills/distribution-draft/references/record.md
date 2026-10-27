# Draft record and ledger row

Show one record per draft at the gate. The ledger row keeps the same shape, without `text` for
dropped drafts and without `claims` locators that point at private files.

```yaml
source:
  key: PR#42            # normalized URL, path@commit, or PR number
  locator: repository path or URL
  owner_confirmed: true
platform: linkedin      # or x
text: the draft as shown
count: {value: 245, limit: from platform docs or unconfirmed, method: platform rule}
link: {url: source link, placement: body or reply, or omitted: reason}
claims:
  - text: one claim the draft makes
    locator: file:line or section
flags: []               # must be empty at the gate
deslop: checks run and result, or unrun
decision: pending       # accepted, edited, or dropped
decided_at: ISO-8601 timestamp
```
