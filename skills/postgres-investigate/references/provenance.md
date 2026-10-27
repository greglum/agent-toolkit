# Provenance

Observed October 10, 2026. This is an original workflow informed by source research;
no upstream prose, code, or SQL recipes were copied.

- [Supabase agent skills at c9be0e9](https://github.com/supabase/agent-skills/tree/c9be0e931b7930f7d02126d04774d904c381e7d7),
  [MIT license](https://github.com/supabase/agent-skills/blob/c9be0e931b7930f7d02126d04774d904c381e7d7/LICENSE):
  narrow symptom routing for plans, connections, and row security. This skill replaces
  blanket tuning recipes with disprovable causes, actual-role checks, and measured comparisons.
- [PostgreSQL CREATE POLICY documentation](https://www.postgresql.org/docs/current/sql-createpolicy.html):
  consulted to check new-row validation when `WITH CHECK` is omitted. The URL tracks the
  current release; use the affected database's version when applying this guidance.

Recheck when PostgreSQL, the pooler, role configuration, or an upstream recipe changes,
or before adopting external SQL. Attribution records research, not runtime validation.
