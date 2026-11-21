"""Classify raw values and profile one column in a single streaming pass.

Every count here is exact. The bounded structures are the distinct-value sets: past the cap
they are dropped and the column reports "exceeds cap" instead of a number.
"""
import hashlib
import re
from datetime import datetime, timezone

NULL_TOKENS = {"na", "n/a", "null", "none", "nan", "nil", "-", "?", "#n/a", "missing", "unknown"}
INTEGER = re.compile(r"^[+-]?(0|[1-9]\d*)$")
DECIMAL = re.compile(r"^[+-]?((0|[1-9]\d*)(\.\d*)?|\.\d+)([eE][+-]?\d+)?$")
LEADING_ZERO = re.compile(r"^0\d+$")
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
DATETIME = re.compile(r"^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}(:\d{2}(\.\d+)?)?(Z|[+-]\d{2}:?\d{2})?$")
LOAD_HINT = re.compile(r"(load|ingest|insert|etl|extract|import|sync|batch|received|_dw)", re.I)
NINES = re.compile(r"^-?9{2,}(\.0+)?$")
DATA_LIKE = re.compile(r"^[+-]?[\d.,]+$|@")
TEXT_CAP = 80
MAX_DIGITS = 15


def clip(value, show=True):
    """Echo a value from the data, capped; untrusted, so never long and never followed."""
    if not show:
        return "<suppressed>"
    text = value if isinstance(value, str) else str(value)
    return text if len(text) <= TEXT_CAP else text[:TEXT_CAP] + "..."


def looks_like_data(name):
    """A header cell that looks like a value (a number or an email-like token)."""
    return bool(DATA_LIKE.search(str(name).strip()))


def as_text(value):
    """Canonical text for a raw value from any reader; None stays None."""
    if value is None or isinstance(value, str):
        return value
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    if isinstance(value, bytes):
        return "blob:" + hashlib.sha256(value).hexdigest()
    return str(value)


def parse_time(text):
    """Return a sortable UTC-or-naive datetime and whether it was timezone-aware."""
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    if len(text) > 19 and text[-5] in "+-" and text[-3] != ":":
        text = text[:-2] + ":" + text[-2:]
    moment = datetime.fromisoformat(text.replace(" ", "T", 1))
    if moment.tzinfo is None:
        return moment, False
    return moment.astimezone(timezone.utc).replace(tzinfo=None), True


def _digits(text):
    return sum(ch.isdigit() for ch in text.split("e")[0].split("E")[0])


def kind(value):
    """Classify one raw value: null, empty, token, integer, decimal, boolean, date, datetime, json, text.

    Digit strings with a leading zero, or more digits than a float holds, are text: codes and
    identifiers must never be coerced to numbers.
    """
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int):
        return "integer" if len(str(abs(value))) <= MAX_DIGITS else "text"
    if isinstance(value, float):
        return "decimal"
    if isinstance(value, (list, dict)):
        return "json"
    if isinstance(value, bytes):
        return "blob"
    text = value.strip()
    if not text:
        return "empty"
    if text.lower() in NULL_TOKENS:
        return "token"
    if INTEGER.match(text):
        return "integer" if _digits(text) <= MAX_DIGITS else "text"
    if DECIMAL.match(text):
        return "decimal" if _digits(text) <= MAX_DIGITS else "text"
    if text.lower() in ("true", "false"):
        return "boolean"
    if DATE.match(text) or DATETIME.match(text):
        try:
            parse_time(text)
        except ValueError:
            return "text"
        return "date" if DATE.match(text) else "datetime"
    return "text"


def merge_types(kinds):
    """Most specific type covering a set of value kinds, or 'mixed'; None when no values."""
    seen = set(kinds) - {"null", "empty", "token"}
    if not seen:
        return None
    if len(seen) == 1:
        return next(iter(seen))
    if seen <= {"integer", "decimal"}:
        return "decimal"
    if seen <= {"date", "datetime"}:
        return "datetime"
    return "mixed"


class Extremes:
    """Exact count of the two smallest and two largest distinct numeric values."""

    def __init__(self):
        self.low = []
        self.high = []

    @staticmethod
    def _add(slots, number, better):
        for slot in slots:
            if slot[0] == number:
                slot[1] += 1
                return
        slots.append([number, 1])
        slots.sort(key=lambda s: s[0], reverse=not better)
        del slots[2:]

    def add(self, number):
        self._add(self.low, number, True)
        self._add(self.high, number, False)

    def sentinels(self):
        """Repeated extreme values that look like codes rather than measurements. Leads only.

        Reason text never contains the value, so suppressing the value suppresses it everywhere.
        """
        found = []
        if not self.low:
            return found
        lo, hi = self.low[0], self.high[0]
        for value, count, second, other_end, side in (
            (hi[0], hi[1], self.high[1][0] if len(self.high) > 1 else None, lo[0], "max"),
            (lo[0], lo[1], self.low[1][0] if len(self.low) > 1 else None, hi[0], "min"),
        ):
            if count < 2 or second is None:
                continue
            reasons = []
            if NINES.match(as_text(value)):
                reasons.append("all-nines code")
            if value < 0 and side == "min" and second >= 0:
                reasons.append("only negative value in an otherwise non-negative column")
            if abs(value - second) > abs(second - other_end) > 0:
                reasons.append("gap to the next value exceeds the span of all other values")
            if reasons:
                found.append({"value": value, "count": count, "side": side, "why": reasons})
        return found


class Distinct:
    """Exact distinct count up to a cap, then None."""

    def __init__(self, cap):
        self.cap, self.values, self.exceeded = cap, set(), False

    def add(self, value):
        if not self.exceeded:
            self.values.add(value)
            if len(self.values) > self.cap:
                self.exceeded, self.values = True, set()

    def report(self):
        return "exceeds cap" if self.exceeded else len(self.values)


class ColumnProfile:
    def __init__(self, name, distinct_cap):
        self.name = name
        self.cap = distinct_cap
        self.kinds = {}
        self.tokens = {}
        self.present = 0
        self.leading_zero = 0
        self.raw = Distinct(distinct_cap)
        self.normalized = Distinct(distinct_cap)
        self.extremes = Extremes()
        self.time_low = self.time_high = None
        self.aware = {"naive": 0, "aware": 0}

    def add(self, raw):
        self.present += 1
        k = kind(raw)
        self.kinds[k] = self.kinds.get(k, 0) + 1
        if k in ("null", "empty"):
            return
        exact = as_text(raw)
        self.raw.add(exact)
        text = exact.strip()
        if k == "token":
            self.tokens[text] = self.tokens.get(text, 0) + 1
            return
        self.normalized.add(text)
        if LEADING_ZERO.match(text):
            self.leading_zero += 1
        if k in ("integer", "decimal"):
            self.extremes.add(int(text) if k == "integer" else float(text))
        elif k in ("date", "datetime"):
            moment, aware = parse_time(text)
            self.aware["aware" if aware else "naive"] += 1
            if self.time_low is None or moment < self.time_low[0]:
                self.time_low = (moment, text)
            if self.time_high is None or moment > self.time_high[0]:
                self.time_high = (moment, text)

    def type(self):
        return merge_types(self.kinds)

    def report(self, absent, show):
        values = sum(c for k, c in self.kinds.items() if k not in ("null", "empty", "token"))
        out = {
            "column": clip(self.name),
            "type": self.type(),
            "kinds": dict(sorted(self.kinds.items())),
            "rows_present": self.present,
            "absent_rows": absent,
            "null": self.kinds.get("null", 0),
            "empty": self.kinds.get("empty", 0),
            "null_tokens": {(clip(k) if show else "suppressed_%d" % i): v
                            for i, (k, v) in enumerate(sorted(self.tokens.items()), 1)},
            "values": values,
            "distinct": self.raw.report(),
            "distinct_normalized": self.normalized.report(),
        }
        if self.raw.exceeded or self.normalized.exceeded:
            out["distinct_cap"] = self.cap
        if self.leading_zero:
            out["leading_zero_values"] = self.leading_zero
        if self.extremes.low:
            out["min"], out["max"] = self.extremes.low[0][0], self.extremes.high[0][0]
            if not show:
                out["min"] = out["max"] = "<suppressed>"
            sentinels = self.extremes.sentinels()
            if sentinels:
                for item in sentinels:
                    item["value"] = item["value"] if show else "<suppressed>"
                out["sentinel_candidates"] = sentinels
        if self.time_low:
            out["time"] = {
                "min": clip(self.time_low[1], show),
                "max": clip(self.time_high[1], show),
                **self.aware,
                "role_hint": "load time? confirm" if LOAD_HINT.search(self.name) else "event or other time; confirm",
            }
            if self.aware["naive"] and self.aware["aware"]:
                out["time"]["warning"] = "mixes naive and timezone-aware values"
        return out
