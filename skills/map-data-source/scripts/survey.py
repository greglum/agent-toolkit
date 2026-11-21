"""survey: tables, rows, columns, types, nulls, sentinel candidates, time ranges and schema drift."""
from column_profile import ColumnProfile, clip, merge_types, kind
from sources import connect_readonly, discover, is_sqlite, quote, read_file, sqlite_columns, sqlite_tables


def survey(path, distinct_cap, show):
    from pathlib import Path
    source = Path(path)
    if source.is_file() and is_sqlite(source):
        return {"source_kind": "sqlite", "tables": _sqlite(source, distinct_cap, show)}
    groups = discover(source)
    tables = [_group(name, group, distinct_cap, show) for name, group in groups.items()]
    return {"source_kind": "files", "tables": tables, "header_twins": _twins(tables)}


def _profiles(rows, profiles, distinct_cap):
    count = 0
    for row in rows:
        count += 1
        for name, raw in row.items():
            if name not in profiles:
                profiles[name] = ColumnProfile(name, distinct_cap)
            profiles[name].add(raw)
    return count


def _group(name, group, distinct_cap, show):
    profiles, files, total = {}, [], 0
    for file, relative in group["files"]:
        notes, kinds = {}, {}

        def tracked(rows):
            for row in rows:
                for column, raw in row.items():
                    seen = kinds.setdefault(column, {})
                    k = kind(raw)
                    seen[k] = seen.get(k, 0) + 1
                yield row

        rows = _profiles(tracked(read_file(file, notes, show)), profiles, distinct_cap)
        total += rows
        header = notes.pop("header", [])
        files.append({"file": clip(relative), "rows": rows, "columns": header,
                      "types": {c: merge_types(kinds.get(c, {})) for c in header}, **notes})
    out = {
        "table": name,
        "kind": "file_group",
        "pattern": clip(group["pattern"]),
        "files": len(files),
        "rows": total,
        "columns": [p.report(total - p.present, show) for p in profiles.values()],
        "drift": _drift(files),
    }
    for item in files:
        item["columns"] = [clip(c) for c in item["columns"]]
        item["types"] = {clip(c): t for c, t in item["types"].items()}
    out["file_detail"] = files
    if total == 0:
        out["warning"] = "no rows; every uniqueness or relationship claim would pass vacuously"
    return out


def _drift(files):
    """Compare each file with the first: added, missing and type-changed columns."""
    if len(files) < 2:
        return []
    base = files[0]
    changes = []
    for item in files[1:]:
        added = [c for c in item["columns"] if c not in base["types"]]
        missing = [c for c in base["columns"] if c not in item["types"]]
        changed = [{"column": clip(c), "from": base["types"][c], "to": t} for c, t in item["types"].items()
                   if c in base["types"] and base["types"][c] and t and base["types"][c] != t]
        if added or missing or changed:
            changes.append({"file": item["file"], "against": base["file"], "added": [clip(c) for c in added],
                            "missing": [clip(c) for c in missing], "type_changed": changed})
    return changes


def _twins(tables):
    """Separate tables with identical column sets: maybe one table split by an unusual name."""
    by_columns = {}
    for table in tables:
        key = tuple(sorted(c["column"] for c in table["columns"]))
        if key:
            by_columns.setdefault(key, []).append(table["table"])
    return [names for names in by_columns.values() if len(names) > 1]


def _sqlite(path, distinct_cap, show):
    db = connect_readonly(path)
    tables = []
    try:
        for name, object_kind in sqlite_tables(db):
            info = sqlite_columns(db, name)
            names = [row[1] for row in info]
            declared = {row[1]: row[2] for row in info}
            primary = [row[1] for row in sorted(info, key=lambda r: r[5]) if row[5]]
            generated = [clip(row[1]) for row in info if row[6] in (2, 3)]
            profiles = {n: ColumnProfile(n, distinct_cap) for n in names}
            cursor = db.execute("SELECT %s FROM %s" % (", ".join(quote(n) for n in names), quote(name)))
            rows = _profiles((dict(zip(names, values)) for values in cursor), profiles, distinct_cap)
            columns = []
            for column in names:
                report = profiles[column].report(rows - profiles[column].present, show)
                report["declared_type"] = clip(declared[column])
                columns.append(report)
            foreign = [{"from": clip(r[3]), "to_table": clip(r[2]), "to": clip(r[4])}
                       for r in db.execute("PRAGMA foreign_key_list(%s)" % quote(name))]
            table = {"table": clip(name), "kind": object_kind, "rows": rows, "columns": columns,
                     "declared_primary_key": [clip(p) for p in primary], "declared_foreign_keys": foreign,
                     "generated_columns": generated}
            if rows == 0:
                table["warning"] = "no rows; every uniqueness or relationship claim would pass vacuously"
            tables.append(table)
    finally:
        db.close()
    return tables
