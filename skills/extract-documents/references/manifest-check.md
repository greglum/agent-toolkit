# Reconcile a prepared local extraction bundle

Use this after installed readers have produced files and a manifest. The bundled checker
compares the independently requested input list with the manifest, checks local file hashes,
and makes failed/unsupported inputs visible. It does not run a converter, read remote URLs,
verify content fidelity, establish page numbers or certify a declared locator mapping.

Keep the project's manifest owner. If its shape differs, derive a temporary check view using
the fields below rather than replacing the project format. The view is a JSON list or an
object with a `sources` list. Paths resolve inside the declared bundle root, including
symlinks; sources and outputs outside it are rejected. Filesystem identity checks also reject
hard-linked originals used as outputs. Preserve original files separately
from outputs. For a corpus held elsewhere, use its existing authorized bundle/root arrangement.

Each entry has:

| Field | Meaning |
| --- | --- |
| `source_id`, `source` | Unique ID and original local file path |
| `source_sha256` | Actual source digest; null only for an unreadable failed/unsupported input |
| `status` | `verified`, `partial`, `failed` or `unsupported` |
| `known_loss`, `errors` | Lists of nonempty descriptions; partial needs loss/uncertainty, failed/unsupported needs a reason |
| `output` | `{ "path": "text/report.md", "sha256": "actual digest" }`, or null when no output exists |
| `tool` | Converter `name` and `version`; version may be null. Tool may be null for failed/unsupported inputs |
| `verification` | `coverage`: `full`, `sampled` or `none`; `locators`: a list of `{ "source": "page 2", "output": "lines 12-18" }` |

Only record page/line/cell relationships actually checked against the original. Use a
source-level locator or an empty list when finer mappings are unknown. A nonempty output
and a converter success do not justify `verified`. Keep options, timestamps, provider
destinations and any richer project provenance in the existing manifest; this helper checks
only the declared subset. An empty verified output, source/output alias or missing required
output is a mismatch.

```sh
python3 <skill-dir>/scripts/check_manifest.py bundle/manifest.json \
  --root bundle --input originals/report.pdf --input originals/table.csv
```

Pass every requested input, including failures; deriving the input list from the manifest
would hide omissions. Exit 0 reports `RECONCILED`, which can include failed or unsupported
sources. Exit 1 reports `MISMATCH`; exit 2 means the manifest or invocation was invalid or
unreadable. Duplicate JSON object keys make the manifest invalid. The checker hashes
only regular files, so an unsupported pipe or device can be accounted for without reading
it. Inspect status counts and reasons before using the bundle. The tool writes only
JSON to stdout and never repairs a manifest or overwrites source/output files.

Original implementation, November 4, 2026. The [provenance](provenance.md) boundary remains:
converter output and checked file accounting are separate from faithful extraction. A local
UTF-8 reader fixture exercises complete input/output accounting; other readers and real
document fidelity remain task-specific checks, not bundled converter support.
