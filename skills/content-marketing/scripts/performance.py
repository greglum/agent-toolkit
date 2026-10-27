"""Compare exported counts only within declared, matching observation cohorts."""

import math
from collections import defaultdict
from datetime import datetime, timedelta
from statistics import median


COHORT = ("platform", "account", "format", "metric", "definition", "scope", "window_hours")
FIELDS = {"content_id", "published_at", "observed_at", "status", "value", "source", *COHORT}
METRICS = {"impressions", "views", "outbound_clicks", "site_sessions"}


def timestamp(value):
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (TypeError, ValueError, AttributeError) as exc:
        raise ValueError("observation timestamps must be ISO 8601 with timezone") from exc
    if parsed.tzinfo is None:
        raise ValueError("observation timestamps need a timezone")
    return parsed


def analyze(observations):
    if not isinstance(observations, list):
        raise ValueError("observations must be a list")
    groups, seen = defaultdict(list), set()
    for i, row in enumerate(observations):
        label = f"observations[{i}]"
        if not isinstance(row, dict) or set(row) != FIELDS:
            raise ValueError(f"{label}: fields must match the observation contract")
        for field in FIELDS - {"value", "window_hours"}:
            if not isinstance(row[field], str) or not row[field].strip():
                raise ValueError(f"{label}.{field}: nonempty text required")
        if row["platform"] not in {"youtube", "linkedin", "website"} or row["metric"] not in METRICS:
            raise ValueError(f"{label}: unsupported platform or count metric")
        if type(row["window_hours"]) is not int or row["window_hours"] <= 0:
            raise ValueError(f"{label}: window_hours must be a positive integer")
        if row["status"] not in {"complete", "partial", "unavailable"}:
            raise ValueError(f"{label}: status must be complete, partial or unavailable")
        value = row["value"]
        if value is not None and (type(value) not in (int, float) or not math.isfinite(value) or value < 0):
            raise ValueError(f"{label}: value must be a finite nonnegative count or null")
        if (row["status"] == "complete" and value is None) or (row["status"] == "unavailable" and value is not None):
            raise ValueError(f"{label}: complete needs a value; unavailable needs null")
        published, observed = timestamp(row["published_at"]), timestamp(row["observed_at"])
        if observed < published:
            raise ValueError(f"{label}: observation precedes publication")
        try:
            end = published + timedelta(hours=row["window_hours"])
        except OverflowError as exc:
            raise ValueError(f"{label}: measurement window exceeds timestamp range") from exc
        if row["status"] == "complete" and observed < end:
            raise ValueError(f"{label}: the complete publication-age window has not elapsed")
        key = tuple(row[field] for field in COHORT)
        identity = (key, row["content_id"])
        if identity in seen:
            raise ValueError(f"{label}: duplicate content observation in the same cohort")
        seen.add(identity)
        groups[key].append(row)

    result = []
    for key, rows in groups.items():
        complete = [r for r in rows if r["status"] == "complete"]
        measured = []
        for row in rows:
            peers = [r["value"] for r in complete if r["content_id"] != row["content_id"]]
            baseline = median(peers) if len(peers) >= 3 else None
            reason = None
            if row["status"] != "complete":
                reason = "incomplete observation"
            elif baseline is None:
                reason = "fewer than three complete peers"
            elif baseline == 0:
                reason = "zero peer median"
            lift = row["value"] / baseline if reason is None else None
            measured.append({**row, "peer_count": len(peers), "peer_median": baseline,
                             "lift": lift, "comparison_limit": reason})
        measured.sort(key=lambda r: (r["lift"] is None, -(r["lift"] or 0), r["content_id"]))
        result.append({"cohort": dict(zip(COHORT, key)), "total": len(rows),
                       "complete": len(complete), "partial": sum(r["status"] == "partial" for r in rows),
                       "unavailable": sum(r["status"] == "unavailable" for r in rows), "rows": measured})
    return result
