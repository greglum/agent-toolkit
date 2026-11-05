#!/usr/bin/env python3
"""Retrieve public X evidence without browser state; never certify full coverage."""

import argparse
from datetime import datetime, timezone
import hashlib
from html.parser import HTMLParser
import json
import re
import urllib.error
import urllib.parse
import urllib.request


X_HOSTS = {"x.com", "www.x.com", "twitter.com", "www.twitter.com", "mobile.twitter.com"}
API_HOSTS = {"publish.x.com", "api.fxtwitter.com"}
MAX_BYTES = 1_048_576


def parse_source(url):
    if not isinstance(url, str):
        raise ValueError("Expected a public X URL string.")
    parts = urllib.parse.urlsplit(url)
    if (parts.scheme != "https" or parts.hostname not in X_HOSTS
            or parts.username or parts.password or parts.port not in (None, 443)):
        raise ValueError("Use a public HTTPS x.com or twitter.com post/Article URL.")
    match = re.fullmatch(r"/([A-Za-z0-9_]{1,15})/status/(\d{2,20})(?:/(?:photo|video)/\d+)?/?", parts.path)
    if match:
        author, identity = match.groups()
        return {"url": f"https://x.com/{author}/status/{identity}",
                "kind": "post", "id": identity, "author": author}
    match = re.fullmatch(r"/i/web/status/(\d{2,20})/?", parts.path)
    if match:
        return {"url": f"https://x.com/i/web/status/{match[1]}",
                "kind": "post", "id": match[1], "author": None}
    match = re.fullmatch(r"/(?:i|[A-Za-z0-9_]{1,15})/article/(\d{2,20})/?", parts.path)
    if match:
        return {"url": f"https://x.com{parts.path.rstrip('/')}",
                "kind": "article", "id": match[1], "author": None}
    raise ValueError("Expected a status URL or an actual Article URL; do not guess IDs.")


class ApiRedirects(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        target = urllib.parse.urlsplit(newurl)
        if (target.scheme != "https" or target.hostname not in API_HOSTS
                or target.hostname != urllib.parse.urlsplit(req.full_url).hostname
                or target.username or target.password or target.port not in (None, 443)):
            raise ValueError("API redirected outside its original public endpoint host.")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def fetch_json(url):
    request = urllib.request.Request(url, headers={"User-Agent": "skill-research/1.0",
                                                 "Accept": "application/json"})
    # This opener has no browser cookie jar or authentication handler.
    with urllib.request.build_opener(ApiRedirects()).open(request, timeout=25) as response:
        raw = response.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise ValueError("Response exceeded the 1 MiB evidence limit.")
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise ValueError("Expected a JSON object from the public endpoint.")
    return data, hashlib.sha256(raw).hexdigest()


class EmbedBody(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.in_body = False
        self.skip = 0
        self.text = []
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self.skip += 1
        elif tag == "p":
            self.in_body = True
        elif self.in_body and not self.skip:
            if tag == "br":
                self.text.append("\n")
            elif tag == "a":
                href = dict(attrs).get("href", "")
                if href.startswith(("https://", "http://")):
                    self.links.append(href)

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self.skip = max(0, self.skip - 1)
        elif tag == "p":
            self.in_body = False
            self.text.append("\n")

    def handle_data(self, data):
        if self.in_body and not self.skip:
            self.text.append(data)


def read_embed(data, source):
    returned = parse_source(data.get("url", ""))
    if returned["kind"] != "post" or returned["id"] != source["id"]:
        raise ValueError("Official embed returned a different post ID.")
    markup = data.get("html")
    if not isinstance(markup, str):
        raise ValueError("Official embed has no HTML text.")
    body = EmbedBody()
    body.feed(markup)
    text = "".join(body.text).strip()
    if not text:
        raise ValueError("Official embed contained no post body.")
    warnings = ["Embed coverage requires review; media, replies and Article bodies are not certified."]
    if text.endswith(("…", "...")):
        warnings.append("TRUNCATED: recover the remaining text before assessing the whole post.")
    if not re.sub(r"https?://\S+", "", text).strip():
        warnings.append("LINK_ONLY: follow the actual destination; it may be an Article.")
    if source["author"] and not returned["author"]:
        warnings.append("AUTHOR_UNVERIFIED: returned URL has no handle; verify attribution.")
    elif source["author"] and returned["author"].lower() != source["author"].lower():
        warnings.append("AUTHOR_CHANGED: verify the returned handle before attribution.")
    return {"provenance": "official_embed", "url": returned["url"],
            "author_name": data.get("author_name"), "author_url": data.get("author_url"),
            "text": text, "links": list(dict.fromkeys(body.links)), "warnings": warnings}


def read_extraction(data, source):
    post = data.get("status")
    if data.get("code") != 200 or not isinstance(post, dict) or post.get("type") != "status":
        raise ValueError("Secondary API returned no available post; inspect its code/tombstone.")
    if str(post.get("id")) != source["id"]:
        raise ValueError("Secondary extraction returned a different post ID.")
    text = post.get("text")
    if not isinstance(text, str):
        raise ValueError("Secondary extraction has no post text.")
    article = post.get("article")
    article_text = []
    has_markdown_body = False
    if article is not None:
        if not isinstance(article, dict) or not isinstance(article.get("content"), dict):
            raise ValueError("Article content shape changed; inspect the raw response.")
        blocks = article["content"].get("blocks")
        if not isinstance(blocks, list):
            raise ValueError("Article has no readable block list.")
        for block in blocks:
            if not isinstance(block, dict) or not isinstance(block.get("text"), str):
                raise ValueError("Invalid Article block; preserve the response for inspection.")
            article_text.append(block["text"])
        entities = article["content"].get("entityMap")
        if any(block.get("type") == "atomic" for block in blocks) and isinstance(entities, list):
            for entity in entities:
                value = entity.get("value") if isinstance(entity, dict) else None
                if not isinstance(value, dict) or value.get("type") != "MARKDOWN":
                    continue
                entity_data = value.get("data")
                markdown = entity_data.get("markdown") if isinstance(entity_data, dict) else None
                if isinstance(markdown, str) and markdown.strip():
                    has_markdown_body = True
    if not text.strip() and not any(block.strip() for block in article_text) and not has_markdown_body:
        raise ValueError("Secondary extraction contained no post or Article body.")
    warnings = ["SECONDARY: corroborate claims against first-party sources; no full-primary review proven.",
                "Inspect raw Article entities, media and links; plain block text can omit embedded content."]
    if has_markdown_body:
        warnings.append("MARKDOWN_ENTITY: inspect raw Markdown and its block association; association is not verified.")
    author = post.get("author") or {}
    if not isinstance(author, dict):
        raise ValueError("Secondary author shape changed.")
    if source["author"] and str(author.get("screen_name", "")).lower() != source["author"].lower():
        warnings.append("AUTHOR_CHANGED: verify the extracted handle before attribution.")
    return {"provenance": "secondary_extraction", "text": text, "author": author,
            "article": article, "article_block_text": "\n\n".join(article_text),
            "links": list(dict.fromkeys(re.findall(r"https?://[^\s<>]+", text))),
            "warnings": warnings}


def recover(url, secondary=False):
    source = parse_source(url)
    result = {"source": source, "observed_at": datetime.now(timezone.utc).isoformat(),
              "coverage": "UNAVAILABLE", "full_review": False, "attempts": [], "records": []}
    if source["kind"] == "article":
        result["coverage"] = "NEEDS_ARTICLE_ROUTE"
        result["next_action"] = "Use the actual Article page, author copy or discovered containing post. Never use its ID as a post ID."
        return result
    endpoint = "https://publish.x.com/oembed?" + urllib.parse.urlencode(
        {"url": source["url"], "omit_script": "1"})
    routes = [(endpoint, read_embed)]
    if secondary:
        routes.append((f"https://api.fxtwitter.com/2/status/{source['id']}", read_extraction))
    for endpoint, reader in routes:
        attempt = {"endpoint": endpoint}
        try:
            data, digest = fetch_json(endpoint)
            attempt["response_sha256"] = digest
            attempt["response"] = data
            record = reader(data, source)
            result["records"].append(record)
            attempt["status"] = "RETRIEVED"
        except (OSError, ValueError, urllib.error.URLError) as error:
            attempt["status"] = "FAILED"
            attempt["error"] = str(error)
            if isinstance(error, urllib.error.HTTPError):
                attempt["http_status"] = error.code
        result["attempts"].append(attempt)
    if result["records"]:
        result["coverage"] = "PARTIAL"
    result["next_action"] = "Read the recovery guide: verify completeness, follow substantive links, and record remaining routes before declaring a blocker."
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url", help="Public X post or actual Article URL")
    parser.add_argument("--secondary", action="store_true",
                        help="Also send the public post ID to FxEmbed; output stays labeled secondary")
    args = parser.parse_args()
    try:
        result = recover(args.url, args.secondary)
    except ValueError as error:
        parser.error(str(error))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["records"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
