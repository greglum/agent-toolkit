#!/usr/bin/env python3
"""Build a local, evidence-linked campaign brief and matched-window measurement report."""

import argparse
import csv
from datetime import date
import hashlib
import io
import json
from pathlib import Path
import re
import sys
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from performance import analyze, COHORT


SLUG = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
FORMATS = {"youtube": {"video", "short"}, "linkedin": {"post", "video", "article"}, "website": {"page"}}
PLACEMENTS = {"youtube": {"description", "profile", "related_video"}, "linkedin": {"post"}, "website": {"link"}}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def fields(obj, expected, label):
    require(isinstance(obj, dict) and set(obj) == set(expected.split()), f"{label}: fields must match the input contract")


def text(value):
    return isinstance(value, str) and bool(value.strip())


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate JSON object key")
        result[key] = value
    return result


def https_url(value, label):
    require(text(value) and not any(c.isspace() or ord(c) < 32 or c in '<>"\\' for c in value),
            f"{label}: public HTTPS URL required")
    try:
        parsed = urlsplit(value)
        port = parsed.port
    except ValueError as exc:
        raise ValueError(f"{label}: invalid HTTPS URL") from exc
    require(parsed.scheme == "https" and bool(parsed.hostname) and not parsed.username
            and not parsed.password and port in (None, 443), f"{label}: public HTTPS URL without credentials required")
    require(not any(k.lower() in {"token", "key", "api_key", "password", "secret", "email"}
                    for k, _ in parse_qsl(parsed.query)), f"{label}: remove sensitive query fields")
    return parsed


def validate(plan):
    fields(plan, "schema_version campaign claims items observations", "plan")
    require(type(plan["schema_version"]) is int and plan["schema_version"] == 1, "schema_version must be 1")
    campaign = plan["campaign"]
    fields(campaign, "id audience goal hypothesis owned_site review_on measurement decision_rule", "campaign")
    require(all(text(v) for v in campaign.values()), "campaign fields must be nonempty text")
    require(SLUG.fullmatch(campaign["id"]), "campaign.id must be a public-safe lowercase slug")
    site = https_url(campaign["owned_site"], "owned_site")
    require(site.path in ("", "/") and not site.query and not site.fragment, "owned_site must be an origin")
    date.fromisoformat(campaign["review_on"])
    require(isinstance(plan["claims"], list) and plan["claims"], "claims must be a nonempty list")
    claims = {}
    for claim in plan["claims"]:
        fields(claim, "id statement source_url locator checked_at status", "claim")
        require(all(text(v) for v in claim.values()), "claim fields must be nonempty text")
        require(SLUG.fullmatch(claim["id"]) and claim["id"] not in claims, "claim IDs must be unique lowercase slugs")
        require(claim["status"] in {"verified", "unverified"}, "claim status must be verified or unverified")
        https_url(claim["source_url"], "source_url")
        date.fromisoformat(claim["checked_at"])
        claims[claim["id"]] = claim
    require(isinstance(plan["items"], list) and plan["items"], "items must be a nonempty list")
    ids = set()
    for item in plan["items"]:
        fields(item, "id platform format placement title hook outline cta destination_url link_access claim_ids measure", "item")
        for name in ("id", "platform", "format", "placement", "title", "hook", "cta", "measure"):
            require(text(item[name]), f"item.{name} must be nonempty text")
        require(SLUG.fullmatch(item["id"]) and item["id"] not in ids, "item IDs must be unique lowercase slugs")
        ids.add(item["id"])
        require(item["platform"] in FORMATS, "unsupported item platform")
        require(item["format"] in FORMATS[item["platform"]], "unsupported platform/format pair")
        require(item["placement"] in PLACEMENTS[item["platform"]], "unsupported platform/placement pair")
        require(text(item["link_access"]) and item["link_access"] in {"verified", "unknown"},
                "link_access must be verified or unknown")
        require(isinstance(item["outline"], list) and item["outline"] and all(text(v) for v in item["outline"]),
                "item.outline must have nonempty steps")
        refs = item["claim_ids"]
        require(isinstance(refs, list) and refs and all(text(r) and r in claims for r in refs)
                and len(refs) == len(set(refs)), "item.claim_ids must name unique existing claims")
        if item["destination_url"] is not None:
            https_url(item["destination_url"], "destination_url")
    return analyze(plan["observations"])


def video_url(url):
    parsed = urlsplit(url)
    if parsed.hostname == "youtu.be":
        identifier = parsed.path.lstrip("/")
    elif parsed.hostname in {"youtube.com", "www.youtube.com"} and parsed.path == "/watch":
        identifier = dict(parse_qsl(parsed.query)).get("v", "")
    else:
        return False
    return re.fullmatch(r"[A-Za-z0-9_-]{11}", identifier) is not None


def prepare_item(item, plan):
    blockers, notes = [], []
    claims = {c["id"]: c for c in plan["claims"]}
    if any(claims[ref]["status"] != "verified" for ref in item["claim_ids"]):
        blockers.append("Verify the cited claims before review")
    url = item["destination_url"]
    if url is None:
        blockers.append("Supply and verify the actual destination URL")
    elif item["platform"] == "youtube" and item["format"] == "short" and item["placement"] == "description":
        blockers.append("Shorts description URLs are not clickable; choose a related video or profile route")
    elif item["placement"] == "related_video" and (item["format"] != "short" or not video_url(url)):
        blockers.append("A Shorts related-video route needs an actual YouTube watch URL")
    if item["link_access"] != "verified":
        blockers.append("Verify the destination and this account's link placement access")
    if url:
        parsed = urlsplit(url)
        site = urlsplit(plan["campaign"]["owned_site"])
        if parsed.hostname == site.hostname and item["platform"] != "website" and not blockers:
            params = [(k, v) for k, v in parse_qsl(parsed.query, keep_blank_values=True) if not k.lower().startswith("utm_")]
            params += [("utm_source", item["platform"]), ("utm_medium", "social"),
                       ("utm_campaign", plan["campaign"]["id"]), ("utm_content", item["id"])]
            url = urlunsplit(parsed._replace(query=urlencode(params)))
            notes.append("Tagged owned-site referral; analytics capture must be verified separately")
        else:
            notes.append("Canonical destination retained; no claim of UTM attribution at this destination")
    return {**item, "url": url, "status": "blocked" if blockers else "ready_for_review",
            "blockers": blockers, "link_notes": notes}


def prose(value):
    return re.sub(r"([\\`*_{}\[\]<>#|])", r"\\\1", " ".join(str(value).split()))


def render(plan, items, groups):
    c = plan["campaign"]
    lines = [f"# Campaign: {prose(c['id'])}", "", "DRAFT. Nothing has been approved, posted or scheduled.", "",
             f"Audience: {prose(c['audience'])}", f"Goal: {prose(c['goal'])}",
             f"Hypothesis, not result: {prose(c['hypothesis'])}", f"Review on: {prose(c['review_on'])}",
             f"Measurement: {prose(c['measurement'])}", f"Decision rule, chosen before results: {prose(c['decision_rule'])}"]
    for item in items:
        lines += ["", f"## {prose(item['id'])}: {item['status']}", "",
                  f"{item['platform']} / {item['format']} / {item['placement']}",
                  f"Title: {prose(item['title'])}", f"Hook: {prose(item['hook'])}", "", "Outline:"]
        lines += [f"- {prose(point)}" for point in item["outline"]]
        lines += ["", f"Call to action: {prose(item['cta'])}", f"Destination: {item['url'] or 'UNAVAILABLE'}",
                  f"Measure: {prose(item['measure'])}", "Claims: " + ", ".join(item["claim_ids"])]
        lines += [f"- BLOCKED: {prose(reason)}" for reason in item["blockers"]]
        lines += [f"- {prose(note)}" for note in item["link_notes"]]
    lines += ["", "## Claim evidence", ""]
    for claim in plan["claims"]:
        lines += [f"- {prose(claim['id'])} ({claim['status']}): {prose(claim['statement'])}",
                  f"  Source: {claim['source_url']}; {prose(claim['locator'])}; checked {prose(claim['checked_at'])}"]
    lines += ["", "## Measurement review", ""]
    if not groups:
        lines += ["No observations supplied. No measured winner or traffic gain can be claimed."]
    for group in groups:
        lines += ["Cohort: " + "; ".join(f"{key}={prose(value)}" for key, value in group["cohort"].items()),
                  f"All records: {group['total']}; complete: {group['complete']}; partial: {group['partial']}; unavailable: {group['unavailable']}."]
        for row in group["rows"]:
            comparison = f"{row['lift']:.3g}x peer median" if row["lift"] is not None else row["comparison_limit"]
            lines.append(f"- {prose(row['content_id'])}: {row['value']} ({row['status']}); {comparison}; peers={row['peer_count']}; source={prose(row['source'])}")
    lines += ["", "Comparisons are descriptive, not causal or statistical confidence. Never combine platform counts into unique people.", ""]
    return "\n".join(lines)


def csv_text(groups):
    stream = io.StringIO(newline="")
    writer = csv.writer(stream)
    columns = ["content_id", *COHORT, "published_at", "observed_at", "status", "value", "source",
               "peer_count", "peer_median", "lift", "comparison_limit"]
    writer.writerow(columns)
    for group in groups:
        for row in group["rows"]:
            cells = []
            for key in columns:
                value = row[key]
                if isinstance(value, str) and value.lstrip().startswith(("=", "+", "-", "@")):
                    value = "'" + value
                cells.append(value)
            writer.writerow(cells)
    return stream.getvalue()


def build(input_path, output):
    raw = input_path.read_bytes()
    plan = json.loads(raw, object_pairs_hook=unique_object, parse_constant=invalid_constant)
    groups = validate(plan)
    items = [prepare_item(item, plan) for item in plan["items"]]
    manifest = {"schema_version": 1, "input_sha256": hashlib.sha256(raw).hexdigest(),
                "campaign": plan["campaign"], "claims": plan["claims"], "items": items, "performance": groups}
    artifacts = {"campaign.json": json.dumps(manifest, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
                 "brief.md": render(plan, items, groups), "performance.csv": csv_text(groups)}
    output.mkdir(parents=True, exist_ok=False)
    for name, content in artifacts.items():
        (output / name).write_text(content, encoding="utf-8")
    return items


def invalid_constant(value):
    raise ValueError("nonfinite JSON number")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--out", type=Path, required=True, help="new local output directory; existing paths are never replaced")
    args = parser.parse_args()
    try:
        items = build(args.input, args.out)
    except (ValueError, OSError) as exc:
        print(f"Campaign not built: {exc}", file=sys.stderr)
        return 1
    print(f"Draft written to {args.out}; {sum(i['status'] == 'blocked' for i in items)} blocked item(s). Nothing published.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
