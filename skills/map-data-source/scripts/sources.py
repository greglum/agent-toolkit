"""Find tables in a path and read their rows; stage file tables into a temporary SQLite file.

A path is a SQLite database file, one CSV/TSV/JSONL file, or a directory searched recursively.
Files whose relative paths differ only in digits (dates, part numbers) and whose headers
overlap form one logical table, so a table keeps its name when a new dated file arrives.
"""
import csv
import json
import os
import re
import sqlite3
import tempfile
from pathlib import Path

from column_profile import looks_like_data

EXTENSIONS = {".csv": ",", ".tsv": "\t", ".jsonl": None, ".ndjson": None}
SQLITE_MAGIC = b"SQLite format 3\x00"
BATCH = 1000
HEADER_OVERLAP = 0.5
REPORTED_NOTES = ("ragged_rows", "bad_lines", "duplicate_headers", "header_suspect", "delimiter_warning",
                  "empty_file")


class InputError(ValueError):
    pass


def quote(name):
    return '"' + str(name).replace('"', '""') + '"'


def natural(text):
    return [int(part) if part.isdigit() else part for part in re.split(r"(\d+)", text)]


def is_sqlite(path):
    try:
        with open(path, "rb") as handle:
            return handle.read(16) == SQLITE_MAGIC
    except OSError:
        return False


def connect_readonly(path):
    uri = Path(path).resolve().as_uri() + "?mode=ro"
    try:
        db = sqlite3.connect(uri, uri=True)
        db.execute("SELECT count(*) FROM sqlite_master").fetchone()
    except sqlite3.Error as error:
        raise InputError("cannot open SQLite database read-only: %s" % error) from None
    return db


def sqlite_tables(db):
    rows = db.execute(
        "SELECT name, type FROM sqlite_master WHERE type IN ('table','view') "
        "AND name NOT LIKE 'sqlite_%' ORDER BY name").fetchall()
    return [(name, kind) for name, kind in rows]


def sqlite_columns(db, table):
    """All readable columns, generated ones included; hidden virtual-table columns left out."""
    return [row for row in db.execute("PRAGMA table_xinfo(%s)" % quote(table)) if row[6] != 1]


def logical_name(pattern):
    parts = [re.sub(r"[^A-Za-z0-9]+", "_", part.replace("#", "")).strip("_") for part in pattern.split("/")]
    return "_".join(p for p in parts if p) or "table"


def peek_header(file):
    """Column names of a file without reading it all; [] when unreadable or empty."""
    try:
        with open(file, newline="", encoding="utf-8-sig") as handle:
            delimiter = EXTENSIONS[file.suffix.lower()]
            if delimiter is not None:
                return next(csv.reader(handle, delimiter=delimiter), [])
            for line in handle:
                if line.strip():
                    row = json.loads(line)
                    return list(row) if isinstance(row, dict) else []
    except (OSError, UnicodeDecodeError, csv.Error, json.JSONDecodeError):
        pass
    return []


def _overlap(a, b):
    a, b = set(a), set(b)
    return len(a & b) / len(a | b) if a | b else 1.0


def discover(path):
    """Return {table name: {"pattern", "files": [(path, relative path)]}} for files or a directory."""
    root = Path(path)
    if root.is_file():
        if root.suffix.lower() not in EXTENSIONS:
            raise InputError("unsupported file type %r; use CSV, TSV, JSONL or SQLite" % root.suffix)
        files, base = [root], root.parent
    elif root.is_dir():
        files = [p for p in root.rglob("*") if p.is_file() and p.suffix.lower() in EXTENSIONS
                 and not any(part.startswith(".") for part in p.relative_to(root).parts)]
        base = root
    else:
        raise InputError("path not found: %s" % path)
    files.sort(key=lambda p: natural(p.relative_to(base).as_posix()))
    patterns = {}
    for file in files:
        relative = file.relative_to(base).with_suffix("").as_posix()
        patterns.setdefault(re.sub(r"\d+", "#", relative) + file.suffix.lower(), []).append(file)
    if not patterns:
        raise InputError("no CSV, TSV or JSONL files under %s" % path)
    tables = {}
    for pattern in sorted(patterns):
        groups = []
        for file in patterns[pattern]:
            header = peek_header(file)
            match = next((g for g in groups if _overlap(g[0], header) >= HEADER_OVERLAP), None)
            if match:
                match[1].append(file)
            else:
                groups.append((header, [file]))
        for index, (_, members) in enumerate(groups):
            stem = pattern.rsplit(".", 1)[0]
            if index:
                stem = members[0].relative_to(base).with_suffix("").as_posix()
            name = logical_name(stem)
            while name in tables:
                name += "_2"
            tables[name] = {"pattern": pattern, "files": [(f, f.relative_to(base).as_posix()) for f in members]}
    return tables


def read_file(file, notes, show=True):
    """Yield one dict per row. Header problems and bad lines are counted in notes."""
    delimiter = EXTENSIONS[file.suffix.lower()]
    try:
        handle = open(file, newline="", encoding="utf-8-sig")
    except OSError as error:
        raise InputError("cannot read %s: %s" % (file.name, error)) from None
    with handle:
        try:
            if delimiter is None:
                yield from _jsonl(handle, notes, show)
            else:
                yield from _delimited(handle, delimiter, notes, show)
        except UnicodeDecodeError:
            raise InputError("%s is not UTF-8 text" % file.name) from None
        except csv.Error as error:
            raise InputError("%s: %s" % (file.name, error)) from None


def _delimited(handle, delimiter, notes, show):
    reader = csv.reader(handle, delimiter=delimiter)
    header = next(reader, None)
    if header is None:
        notes["empty_file"] = True
        notes["header"] = []
        return
    if any(looks_like_data(cell) for cell in header):
        notes["header_suspect"] = "first row looks like data; the file may have no header"
        if not show:
            header = ["col_%d" % (i + 1) for i in range(len(header))]
    if len(header) == 1 and delimiter == "," and re.search(r"[;|]", header[0]):
        notes["delimiter_warning"] = "one column found and the header contains ; or |; check the delimiter"
    seen, names = {}, []
    for raw in header:
        name = raw.strip() or "unnamed"
        seen[name] = seen.get(name, 0) + 1
        if seen[name] > 1:
            notes.setdefault("duplicate_headers", []).append(name)
            name = "%s__%d" % (name, seen[name])
        names.append(name)
    notes["header"] = names
    for cells in reader:
        if not cells:
            continue
        if len(cells) != len(names):
            notes["ragged_rows"] = notes.get("ragged_rows", 0) + 1
        yield {name: (cells[i] if i < len(cells) else None) for i, name in enumerate(names)}


def _jsonl(handle, notes, show):
    names = notes.setdefault("header", [])
    renamed = {}
    for line in handle:
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            row = None
        if not isinstance(row, dict):
            notes["bad_lines"] = notes.get("bad_lines", 0) + 1
            continue
        if not show:
            row = {renamed.setdefault(k, "col_%d" % (len(renamed) + 1)) if looks_like_data(k) else k: v
                   for k, v in row.items()}
            if renamed:
                notes["header_suspect"] = "some keys look like data and were renamed"
        for key in row:
            if key not in names:
                names.append(key)
        yield row


def input_notes(notes):
    """Per-file reader problems worth carrying into every report; column names left out."""
    found = {}
    for file, items in notes.items():
        kept = {k: v for k, v in items.items() if k in REPORTED_NOTES and k != "duplicate_headers"}
        if items.get("duplicate_headers"):
            kept["duplicate_headers"] = len(items["duplicate_headers"])
        if kept:
            found[file] = kept
    return found


class Table:
    def __init__(self, name, sql, columns, kind, files=()):
        self.name, self.sql, self.kind, self.files = name, sql, kind, list(files)
        self.columns = columns

    def col(self, name):
        if name not in self.columns:
            raise KeyError(name)
        return self.columns[name]


class Workspace:
    """One SQLite connection holding every table of a source; staged copies are deleted on close."""

    def __init__(self, path, show=True):
        self.path, self.show, self.tables, self.notes, self._temp = Path(path), show, {}, {}, None
        if self.path.is_file() and is_sqlite(self.path):
            self.db = connect_readonly(self.path)
            for name, kind in sqlite_tables(self.db):
                columns = {row[1]: quote(row[1]) for row in sqlite_columns(self.db, name)}
                self.tables[name] = Table(name, quote(name), columns, kind)
            if not self.tables:
                self.db.close()
                raise InputError("SQLite database has no tables")
        else:
            groups = discover(self.path)
            handle, self._temp = tempfile.mkstemp(suffix=".sqlite", prefix="map-data-")
            os.close(handle)
            self.db = sqlite3.connect(self._temp)
            try:
                for index, (name, group) in enumerate(groups.items()):
                    self._stage(name, "t%d" % index, group["files"])
            except BaseException:
                self.close()
                raise

    def _add_column(self, sql, columns, key):
        columns[key] = "c%d" % len(columns)
        self.db.execute("ALTER TABLE %s ADD COLUMN %s TEXT" % (sql, columns[key]))

    def _stage(self, name, sql, files):
        columns, notes = {}, {}
        self.db.execute("CREATE TABLE %s (rowid_ INTEGER PRIMARY KEY)" % sql)
        for file, relative in files:
            file_notes = notes.setdefault(relative, {})
            batch, order = [], list(columns)
            for row in read_file(file, file_notes, self.show):
                if any(key not in columns for key in row):
                    if batch:
                        self._insert(sql, columns, order, batch)
                        batch = []
                    for key in row:
                        if key not in columns:
                            self._add_column(sql, columns, key)
                    order = list(columns)
                batch.append([_stage_value(row.get(key)) for key in order])
                if len(batch) >= BATCH:
                    self._insert(sql, columns, order, batch)
                    batch = []
            if batch and order:
                self._insert(sql, columns, order, batch)
            for key in file_notes.get("header", []):
                if key not in columns:
                    self._add_column(sql, columns, key)
        self.db.commit()
        self.notes[name] = notes
        self.tables[name] = Table(name, sql, columns, "file_group", [f for f, _ in files])

    def _insert(self, sql, columns, order, batch):
        names = ", ".join(columns[key] for key in order)
        marks = ", ".join("?" for _ in order)
        self.db.executemany("INSERT INTO %s (%s) VALUES (%s)" % (sql, names, marks), batch)

    def table(self, name):
        if name is None:
            if len(self.tables) == 1:
                return next(iter(self.tables.values()))
            raise InputError("choose a table with --table; found: %s" % ", ".join(sorted(self.tables)))
        if name not in self.tables:
            raise InputError("no table %r; found: %s" % (name, ", ".join(sorted(self.tables))))
        return self.tables[name]

    def input_notes(self, names=None):
        found = {n: input_notes(self.notes.get(n, {})) for n in (names or self.notes)}
        return {n: v for n, v in found.items() if v}

    def rows(self, table):
        """Stream rows as dicts keyed by display column name."""
        names = list(table.columns)
        if not names:
            return
        cursor = self.db.execute("SELECT %s FROM %s" % (", ".join(table.columns[n] for n in names), table.sql))
        for values in cursor:
            yield dict(zip(names, values))

    def scalar(self, query, params=()):
        return self.db.execute(query, params).fetchone()[0]

    def close(self):
        self.db.close()
        if self._temp:
            os.unlink(self._temp)


def _stage_value(raw):
    """Empty and whitespace-only cells become NULL; codes and tokens stay as values."""
    if raw is None:
        return None
    if isinstance(raw, str):
        return raw if raw.strip() else None
    if isinstance(raw, bool):
        return "true" if raw else "false"
    if isinstance(raw, (list, dict)):
        return json.dumps(raw, sort_keys=True)
    if isinstance(raw, float) and raw.is_integer():
        return str(int(raw))
    return str(raw)
