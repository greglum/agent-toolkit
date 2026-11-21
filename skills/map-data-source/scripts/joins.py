"""joins: candidate foreign keys found by value overlap. Every result is a candidate, never confirmed.

For each child column and parent column of compatible type in different tables, report
containment of child values in the parent, orphan rows, whether the parent side is unique,
and the fan-out factor a join would cause.
"""
from column_profile import ColumnProfile, clip

KEYISH = {"integer", "text", "mixed", "date"}
CODES = {"integer", "text", "mixed"}
DIGITS = "%s <> '' AND %s NOT GLOB '*[^0-9]*'"
LOW_CARDINALITY = 10


def _compatible(a, b):
    if a not in KEYISH or b not in KEYISH:
        return False
    return a == b or ("mixed" in (a, b) and {a, b} <= {"integer", "text", "mixed"})


def _columns(ws, table):
    profiles = {name: ColumnProfile(name, 1) for name in table.columns}
    for row in ws.rows(table):
        for name, raw in row.items():
            profiles[name].add(raw)
    out = {}
    for name, col in table.columns.items():
        nonnull = ws.scalar("SELECT COUNT(%s) FROM %s" % (col, table.sql))
        distinct = ws.scalar("SELECT COUNT(DISTINCT %s) FROM %s" % (col, table.sql))
        out[name] = {"type": profiles[name].type(), "nonnull": nonnull, "distinct": distinct,
                     "leading_zero": profiles[name].leading_zero}
    return out


def joins(ws, min_containment, top, show):
    stats = {name: _columns(ws, table) for name, table in ws.tables.items()}
    found = []
    for child_name, child in ws.tables.items():
        for parent_name, parent in ws.tables.items():
            if child_name == parent_name:
                continue
            for c, cs in stats[child_name].items():
                for p, ps in stats[parent_name].items():
                    zeros = (cs["leading_zero"] or ps["leading_zero"]) and {cs["type"], ps["type"]} <= CODES
                    if cs["distinct"] and ps["distinct"] and (zeros or _compatible(cs["type"], ps["type"])):
                        item = _measure(ws, child, c, cs, parent, p, ps, min_containment, show)
                        if item:
                            found.append(item)
    found.sort(key=lambda x: (-x["score"], -x["matched_distinct"], x["child"], x["parent"]))
    out = {"candidates": found[:top], "candidates_total": len(found), "min_containment": min_containment,
           "status": "candidates only; confirm each with a document, an owner or a business rule"}
    notes = ws.input_notes()
    if notes:
        out["input_notes"] = notes
    return out


def _measure(ws, child, c, cs, parent, p, ps, min_containment, show):
    cc, pc = child.col(c), parent.col(p)
    in_parent = "SELECT %s FROM %s WHERE %s IS NOT NULL" % (pc, parent.sql, pc)
    matched = ws.scalar("SELECT COUNT(DISTINCT %s) FROM %s WHERE %s IN (%s)" % (cc, child.sql, cc, in_parent))
    zero_only = 0
    if cs["leading_zero"] or ps["leading_zero"]:
        trimmed = "SELECT LTRIM(%s, '0') FROM %s WHERE %s" % (pc, parent.sql, DIGITS % (pc, pc))
        zero_only = ws.scalar(
            "SELECT COUNT(DISTINCT %s) FROM %s WHERE %s AND LTRIM(%s, '0') IN (%s) AND %s NOT IN (%s)"
            % (cc, child.sql, DIGITS % (cc, cc), cc, trimmed, cc, in_parent))
    if not matched and not zero_only:
        return None
    containment = matched / cs["distinct"]
    if max(containment, (matched + zero_only) / cs["distinct"]) < min_containment:
        return None
    orphan_where = "%s IS NOT NULL AND %s NOT IN (%s)" % (cc, cc, in_parent)
    orphans = ws.scalar("SELECT COUNT(*) FROM %s WHERE %s" % (child.sql, orphan_where))
    joined = ws.scalar(
        "SELECT COALESCE(SUM(g.m), 0) FROM %s AS c JOIN (SELECT %s AS k, COUNT(*) AS m FROM %s "
        "WHERE %s IS NOT NULL GROUP BY %s) AS g ON c.%s = g.k"
        % (child.sql, pc, parent.sql, pc, pc, cc))
    matched_rows = cs["nonnull"] - orphans
    parent_unique = ps["distinct"] == ps["nonnull"]
    fan_out = round(joined / matched_rows, 3) if matched_rows else None
    weight = 1.0 if parent_unique else 0.5
    score = round(containment * weight * min(1.0, cs["distinct"] / LOW_CARDINALITY), 3)
    flags = []
    if not parent_unique:
        flags.append("parent side not unique: a join multiplies matched child rows by about %s" % fan_out)
    if cs["distinct"] < LOW_CARDINALITY:
        flags.append("few distinct child values: overlap may be coincidence")
    if orphans:
        flags.append("orphans: an inner join drops %d child rows" % orphans)
    if zero_only:
        flags.append("leading_zero_mismatch: %d distinct child values match only after trimming leading zeros; "
                     "fix the type upstream, never by casting silently" % zero_only)
    item = {
        "child": "%s.%s" % (child.name, clip(c)),
        "parent": "%s.%s" % (parent.name, clip(p)),
        "status": "candidate",
        "score": score,
        "containment": round(containment, 4),
        "child_distinct": cs["distinct"],
        "matched_distinct": matched,
        "child_rows_nonnull": cs["nonnull"],
        "orphan_rows": orphans,
        "parent_unique": parent_unique,
        "parent_rows_nonnull": ps["nonnull"],
        "fan_out": fan_out,
        "same_name": c.lower() == p.lower(),
        "leading_zero_mismatch": zero_only,
        "flags": flags,
    }
    if orphans and show:
        rows = ws.db.execute("SELECT DISTINCT %s FROM %s WHERE %s LIMIT 3" % (cc, child.sql, orphan_where))
        item["orphan_examples"] = [clip(v) for (v,) in rows]
    return item
