"""check-claims: re-check saved dictionary claims against current data.

A claim that fails, or whose table or column is gone, is a finding (exit 1). A claim on a
table with no rows is "vacuous", also a finding: an empty refresh must not pass silently.
Only a malformed claims file is invalid input (exit 2).
"""
import json
import math

from column_profile import as_text, clip, parse_time
from sources import InputError

FIELDS = {
    "unique": {"columns"},
    "not_null": {"column"},
    "accepted_values": {"column", "values"},
    "range": {"column"},
    "relationship": {"column", "to_table", "to_column"},
    "row_count": set(),
}
EXAMPLES = 3


def load(path):
    try:
        with open(path, encoding="utf-8") as handle:
            data = json.load(handle)
    except (OSError, json.JSONDecodeError) as error:
        raise InputError("cannot read claims file: %s" % error) from None
    claims = data.get("claims") if isinstance(data, dict) else None
    if not isinstance(claims, list) or not claims:
        raise InputError("claims file needs a non-empty 'claims' list")
    ids = set()
    for index, claim in enumerate(claims):
        where = "claim %d" % index
        if not isinstance(claim, dict) or claim.get("type") not in FIELDS:
            raise InputError("%s: type must be one of %s" % (where, ", ".join(sorted(FIELDS))))
        missing = ({"id", "table"} | FIELDS[claim["type"]]) - claim.keys()
        if missing:
            raise InputError("%s: missing %s" % (where, ", ".join(sorted(missing))))
        _types(claim, where)
        if claim["id"] in ids:
            raise InputError("%s: duplicate id %r" % (where, claim["id"]))
        ids.add(claim["id"])
        if claim["type"] in ("range", "row_count") and "min" not in claim and "max" not in claim:
            raise InputError("%s: %s needs min, max or both" % (where, claim["type"]))
        if claim["type"] == "unique" and (not isinstance(claim["columns"], list) or not claim["columns"]):
            raise InputError("%s: columns must be a non-empty list" % where)
        if claim["type"] == "accepted_values" and (not isinstance(claim["values"], list) or not claim["values"]):
            raise InputError("%s: values must be a non-empty list" % where)
    return claims


def _number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _types(claim, where):
    """Reject wrong field types here, so a bad claims file exits 2 instead of crashing later."""
    text = [k for k in ("id", "table", "column", "to_table", "to_column") if k in claim]
    if any(not isinstance(claim[k], str) for k in text):
        raise InputError("%s: %s must be strings" % (where, ", ".join(text)))
    if "columns" in claim and not all(isinstance(c, str) for c in claim["columns"] or [0]):
        raise InputError("%s: columns must be a non-empty list of strings" % where)
    bounds = [claim[k] for k in ("min", "max") if k in claim]
    if claim["type"] == "row_count" and not all(_number(b) for b in bounds):
        raise InputError("%s: row_count min and max must be numbers" % where)
    if claim["type"] == "range" and not (all(_number(b) for b in bounds) or all(isinstance(b, str) for b in bounds)):
        raise InputError("%s: range min and max must both be numbers or both ISO times" % where)
    need = claim.get("min_containment", 1.0)
    if not _number(need) or not 0 < need <= 1:
        raise InputError("%s: min_containment must be a number in (0, 1]" % where)


def check(ws, claims, show):
    results = [_one(ws, claim, show) for claim in claims]
    failed = sum(r["status"] == "fail" for r in results)
    vacuous = sum(r["status"] == "vacuous" for r in results)
    out = {"status": "pass" if not failed and not vacuous else "findings", "claims_total": len(results),
           "failed": failed, "vacuous": vacuous, "results": results}
    notes = ws.input_notes()
    if notes:
        out["input_notes"] = notes
    return out


def _one(ws, claim, show):
    out = {"id": clip(claim["id"]), "type": claim["type"], "table": clip(claim["table"])}
    table = ws.tables.get(claim["table"])
    if table is None:
        return {**out, "status": "fail", "reason": "table not found"}
    names = claim.get("columns") or [claim[k] for k in ("column",) if k in claim]
    gone = [n for n in names if n not in table.columns]
    if gone:
        return {**out, "status": "fail", "reason": "column not found: %s" % ", ".join(clip(n) for n in gone)}
    rows = ws.scalar("SELECT COUNT(*) FROM %s" % table.sql)
    out["rows"] = rows
    if claim["type"] == "row_count":
        ok = claim.get("min", rows) <= rows <= claim.get("max", rows)
        return {**out, "status": "pass" if ok else "fail", "expected": {k: claim[k] for k in ("min", "max") if k in claim}}
    if rows == 0:
        return {**out, "status": "vacuous", "reason": "table has no rows; the claim proves nothing"}
    if claim["type"] in ("unique", "accepted_values", "range"):
        filled = " AND ".join("%s IS NOT NULL" % table.col(n) for n in names)
        if not ws.scalar("SELECT COUNT(*) FROM %s WHERE %s" % (table.sql, filled)):
            return {**out, "status": "vacuous", "reason": "no non-null values; the claim proves nothing"}
    return {**out, **CHECKS[claim["type"]](ws, table, claim, show)}


def _verdict(bad, **counts):
    return {"status": "fail" if bad else "pass", **counts}


def _unique(ws, table, claim, show):
    cols = [table.col(c) for c in claim["columns"]]
    nonnull = " AND ".join("%s IS NOT NULL" % c for c in cols)
    groups, rows = ws.db.execute(
        "SELECT COUNT(*), COALESCE(SUM(n), 0) FROM (SELECT COUNT(*) AS n FROM %s WHERE %s GROUP BY %s HAVING n > 1)"
        % (table.sql, nonnull, ", ".join(cols))).fetchone()
    nulls = ws.scalar("SELECT COUNT(*) FROM %s WHERE NOT (%s)" % (table.sql, nonnull))
    return _verdict(groups, duplicate_groups=groups, rows_in_duplicate_groups=rows, null_rows_not_checked=nulls)


def _not_null(ws, table, claim, show):
    nulls = ws.scalar("SELECT COUNT(*) FROM %s WHERE %s IS NULL" % (table.sql, table.col(claim["column"])))
    return _verdict(nulls, null_rows=nulls)


def _accepted_values(ws, table, claim, show):
    col = table.col(claim["column"])
    accepted = {as_text(v) for v in claim["values"]}
    ws.db.create_function("map_data_accepted", 1, lambda value: as_text(value) in accepted, deterministic=True)
    where = "%s IS NOT NULL AND NOT map_data_accepted(%s)" % (col, col)
    bad = ws.scalar("SELECT COUNT(*) FROM %s WHERE %s" % (table.sql, where))
    out = _verdict(bad, rows_outside=bad)
    if bad:
        values = ws.db.execute("SELECT DISTINCT %s FROM %s WHERE %s LIMIT %d" % (col, table.sql, where, EXAMPLES))
        out["examples"] = [clip(v, show) for (v,) in values]
    return out


def _range(ws, table, claim, show):
    low, high = claim.get("min"), claim.get("max")
    timed = isinstance(low, str) or isinstance(high, str)
    convert = (lambda v: parse_time(as_text(v).strip())[0]) if timed else (lambda v: float(v))
    try:
        low = convert(low) if low is not None else None
        high = convert(high) if high is not None else None
    except (TypeError, ValueError):
        raise InputError("claim %r: min and max must both be numbers or both ISO times" % claim["id"]) from None
    below = above = unparseable = not_finite = 0
    examples = []
    col = table.col(claim["column"])
    for (raw,) in ws.db.execute("SELECT %s FROM %s WHERE %s IS NOT NULL" % (col, table.sql, col)):
        try:
            value = convert(raw)
        except (TypeError, ValueError):
            unparseable += 1
            continue
        if not timed and not math.isfinite(value):
            not_finite += 1
        elif low is not None and value < low:
            below += 1
        elif high is not None and value > high:
            above += 1
        else:
            continue
        if len(examples) < EXAMPLES:
            examples.append(clip(raw, show))
    out = _verdict(below + above + unparseable + not_finite, below_min=below, above_max=above,
                   unparseable=unparseable, not_finite=not_finite)
    if examples:
        out["examples"] = examples
    return out


def _relationship(ws, table, claim, show):
    parent = ws.tables.get(claim["to_table"])
    if parent is None or claim["to_column"] not in parent.columns:
        return {"status": "fail", "reason": "relationship target not found"}
    cc, pc = table.col(claim["column"]), parent.col(claim["to_column"])
    in_parent = "SELECT %s FROM %s WHERE %s IS NOT NULL" % (pc, parent.sql, pc)
    distinct = ws.scalar("SELECT COUNT(DISTINCT %s) FROM %s" % (cc, table.sql))
    if not distinct:
        return {"status": "vacuous", "reason": "child column has no values"}
    matched = ws.scalar("SELECT COUNT(DISTINCT %s) FROM %s WHERE %s IN (%s)" % (cc, table.sql, cc, in_parent))
    where = "%s IS NOT NULL AND %s NOT IN (%s)" % (cc, cc, in_parent)
    orphans = ws.scalar("SELECT COUNT(*) FROM %s WHERE %s" % (table.sql, where))
    need = claim.get("min_containment", 1.0)
    containment = matched / distinct
    out = _verdict(containment < need, containment=round(containment, 4), min_containment=need, orphan_rows=orphans)
    if orphans:
        values = ws.db.execute("SELECT DISTINCT %s FROM %s WHERE %s LIMIT %d" % (cc, table.sql, where, EXAMPLES))
        out["examples"] = [clip(v, show) for (v,) in values]
    return out


CHECKS = {"unique": _unique, "not_null": _not_null, "accepted_values": _accepted_values,
          "range": _range, "relationship": _relationship}
