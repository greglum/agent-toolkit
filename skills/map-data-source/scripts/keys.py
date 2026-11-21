"""keys: minimal unique column sets up to a width, from exact SQL counts on the whole table."""
import re
from itertools import combinations

from column_profile import clip

ID_NAME = re.compile(r"(^id$|_id$|^id_|code$|key$|number$|_no$|^no$)", re.I)


def keys(ws, table, max_width, max_combos, show):
    rows = ws.scalar("SELECT COUNT(*) FROM %s" % table.sql)
    names = list(table.columns)
    columns = [_column(ws, table, name, rows, show) for name in names]
    out = {"table": table.name, "rows": rows, "columns": columns, "keys": [], "max_width": max_width}
    notes = ws.input_notes([table.name])
    if notes:
        out["input_notes"] = notes[table.name]
    if rows == 0:
        out["status"] = "vacuous"
        out["note"] = "no rows: every column set is trivially unique, so no key is proven"
        return out
    distinct = {n: c["distinct"] + (1 if c["null_rows"] else 0) for n, c in zip(names, columns)}
    found, checked, skipped = [], 0, 0
    for width in range(1, max_width + 1):
        for combo in combinations(names, width):
            if any(set(key) <= set(combo) for key in found):
                continue
            product = 1
            for name in combo:
                product *= distinct[name]
            if product < rows:
                skipped += 1
                continue
            if checked >= max_combos:
                out["truncated"] = "stopped at --max-combos %d; wider sets unchecked" % max_combos
                break
            checked += 1
            groups, dup_rows = _duplicates(ws, table, combo)
            if groups == 0:
                found.append(combo)
                null_rows = _null_rows(ws, table, combo)
                out["keys"].append({
                    "columns": [clip(c) for c in combo],
                    "status": "unique" if null_rows == 0 else "unique_with_nulls",
                    "null_rows": null_rows,
                })
        if "truncated" in out:
            break
    out["sets_checked"], out["sets_skipped_by_cardinality"] = checked, skipped
    if "truncated" in out:
        out["status"] = "truncated: %d sets found before the limit; the search is incomplete" % len(out["keys"])
    else:
        out["status"] = "found" if out["keys"] else "no unique set up to width %d" % max_width
    return out


def _column(ws, table, name, rows, show):
    col = table.col(name)
    nulls = ws.scalar("SELECT COUNT(*) FROM %s WHERE %s IS NULL" % (table.sql, col))
    distinct = ws.scalar("SELECT COUNT(DISTINCT %s) FROM %s" % (col, table.sql))
    groups, dup_rows = _duplicates(ws, table, (name,))
    item = {"name": clip(name), "null_rows": nulls, "distinct": distinct, "duplicate_groups": groups,
            "rows_in_duplicate_groups": dup_rows}
    if groups:
        top = ws.db.execute(
            "SELECT %s, COUNT(*) FROM %s GROUP BY %s HAVING COUNT(*) > 1 ORDER BY 2 DESC LIMIT 3"
            % (col, table.sql, col)).fetchall()
        item["top_duplicates"] = [{"value": clip(v, show) if v is not None else None, "rows": n} for v, n in top]
        if ID_NAME.search(name) and rows:
            item["warning"] = "named like an identifier but not unique"
    return item


def _duplicates(ws, table, combo):
    cols = ", ".join(table.col(c) for c in combo)
    groups, dup_rows = ws.db.execute(
        "SELECT COUNT(*), COALESCE(SUM(n), 0) FROM (SELECT COUNT(*) AS n FROM %s GROUP BY %s HAVING n > 1)"
        % (table.sql, cols)).fetchone()
    return groups, dup_rows


def _null_rows(ws, table, combo):
    where = " OR ".join("%s IS NULL" % table.col(c) for c in combo)
    return ws.scalar("SELECT COUNT(*) FROM %s WHERE %s" % (table.sql, where))
