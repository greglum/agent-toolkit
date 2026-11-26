# Migration traps

Check each row against the migration scripts, safety guards, and reconciler before trusting a
passing run.

| Trap | What goes wrong | What to enforce |
| --- | --- | --- |
| Silent skipped tables | Tables with no copy rule are never staged, yet the reconciler checks only loaded tables and prints PASS. | Require every source table to appear in `table_mappings` or `dropped_tables` with a concrete reason. |
| Production vs dev schema drift | Migration code assumes the newest dev column exists in production, failing or reading nulls at cutover. | Pin the deployed source schema revision and read optional columns defensively when drift is possible. |
| Local-only guard bypass | Destructive or local-only checks inspect only `host` / `PGHOST`, missing `hostaddr`, `service`, `PGHOSTADDR`, or `PGSERVICE`. | Check every driver connection-target alias and environment fallback before allowing destructive actions. |
| Row-value leakage in logs | Default database error verbosity prints failing `DETAIL` tuples, and small mismatch reports print inline row values. | Set `VERBOSITY=terse` on load/check sessions and report key digests and counts instead of inline row text. |
| Dict collapse on folded keys | Storing extracts as `{key: hash}` silently overwrites duplicate or folded source rows and compares an arbitrary hash. | Compare sorted hash lists (multisets) per key unless `allow_fold: true` is declared with expected folded counts. |
| Count-only check misses | Matching row counts pass when a coalesce picks the wrong foreign key or when chunked text drops newlines or clips slugs. | Include foreign keys and canonical payload or content hashes in every per-key extract check. |
| Unscoped column inventory | Querying `information_schema.columns` by table name alone merges same-named tables from other schemas. | Filter column inventory by explicit `source_schema` and check all copied, transformed, and dropped columns. |
| Split cutoff clocks | Source and target checks each evaluate `now()`, so rows crossing a retention boundary during the run cause false mismatches. | Read one pinned cutoff timestamp once and pass it into both source and target queries. |
| Active-row guards vs restore | Restorable soft-deleted or cancelled rows violate strict active-parent checks during bulk copy, or cyclic FKs fail non-deferrable loads. | Account for restorable deleted/cancelled rows in copy rules and verify deferrable constraints and app dependency order. |
