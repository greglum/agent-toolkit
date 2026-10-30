#!/usr/bin/env python3
"""Build an offline screenshot review board. No installs, uploads or overwrites."""

import argparse
import base64
import hashlib
import html
import json
import re
import sys
from pathlib import Path

MAX_IMAGE_BYTES = 8 * 1024 * 1024
MAX_TOTAL_BYTES = 24 * 1024 * 1024
ID = re.compile(r"[A-Za-z][A-Za-z0-9_-]{0,63}\Z")


def text(value, label, limit):
    if not isinstance(value, str) or not value.strip() or len(value) > limit:
        raise ValueError(f"{label} must be nonempty text of at most {limit} characters")
    return value


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON field: {key}")
        result[key] = value
    return result


def image_type(data):
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if data.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if data.startswith(b"RIFF") and data[8:12] == b"WEBP":
        return "image/webp"
    raise ValueError("use a PNG, JPEG or WebP image; active formats are not accepted")


def comparison_context(value):
    if not isinstance(value, dict) or set(value) != {"viewport", "theme", "state"}:
        raise ValueError("context needs exactly viewport, theme and state")
    viewport = value["viewport"]
    if not isinstance(viewport, dict) or set(viewport) != {"width", "height"} or any(
        type(size) is not int or not 1 <= size <= 16384 for size in viewport.values()
    ):
        raise ValueError("viewport needs integer width and height from 1 to 16384 CSS pixels")
    return {"viewport": viewport, "theme": text(value["theme"], "theme", 100),
            "state": text(value["state"], "state", 1000)}


def read_image(root, value):
    relative = Path(text(value, "image", 4096))
    image = root / relative
    if relative.is_absolute() or not image.resolve().is_relative_to(root):
        raise ValueError("image must stay inside the manifest folder")
    if any((root / Path(*relative.parts[:i])).is_symlink()
           for i in range(1, len(relative.parts) + 1)) or not image.is_file():
        raise ValueError("image must be a regular file, with no symbolic links in its path")
    with image.open("rb") as handle:
        return handle.read(MAX_IMAGE_BYTES + 1)


def build(manifest_path):
    manifest_path = Path(manifest_path)
    with manifest_path.open("rb") as handle:
        raw = handle.read(65537)
    if len(raw) > 65536:
        raise ValueError("manifest exceeds 64 KiB")
    manifest = json.loads(raw, object_pairs_hook=unique_object)
    fields = {"version", "title", "question", "context", "variants"}
    if not isinstance(manifest, dict) or set(manifest) != fields or type(manifest["version"]) is not int or manifest["version"] != 1:
        raise ValueError("manifest needs exactly version: 1, title, question, context and variants")
    title = text(manifest["title"], "title", 200)
    question = text(manifest["question"], "question", 2000)
    context = comparison_context(manifest["context"])
    variants = manifest["variants"]
    if not isinstance(variants, list) or not 1 <= len(variants) <= 8:
        raise ValueError("variants must contain one to eight entries; put the baseline first")
    records, cards, seen, total = [], [], set(), 0
    for entry in variants:
        if not isinstance(entry, dict) or set(entry) != {"id", "label", "image", "image_size", "source_revision"}:
            raise ValueError("each variant needs exactly id, label, image, image_size and source_revision")
        key = text(entry["id"], "id", 64)
        if not ID.fullmatch(key) or key in seen:
            raise ValueError("variant ids must be unique letters, numbers, underscores or hyphens, starting with a letter")
        seen.add(key)
        label = text(entry["label"], "label", 200)
        revision = text(entry["source_revision"], "source_revision", 300)
        size = entry["image_size"]
        if not isinstance(size, dict) or set(size) != {"width", "height"} or any(
            type(value) is not int or not 1 <= value <= 32768 for value in size.values()
        ):
            raise ValueError("image_size needs integer width and height from 1 to 32768 pixels")
        data = read_image(manifest_path.parent.resolve(), entry["image"])
        total += len(data)
        if len(data) > MAX_IMAGE_BYTES or total > MAX_TOTAL_BYTES:
            raise ValueError("images exceed 8 MiB each or 24 MiB in total")
        mime = image_type(data)
        digest = hashlib.sha256(data).hexdigest()
        records.append({"id": key, "label": label, "source_revision": revision,
                        "image_size": size, "mime": mime, "sha256": digest})
        image = f"data:{mime};base64," + base64.b64encode(data).decode("ascii")
        safe_label = html.escape(label)
        baseline = ' <span>(baseline)</span>' if len(records) == 1 else ''
        cards.append(f'''<article><h2>{safe_label}{baseline}</h2>
<p>Source: <code>{html.escape(revision)}</code></p>
<img src="{image}" alt="{safe_label}" width="{size["width"]}" height="{size["height"]}">
<div class="feedback" hidden>
<label class="choice"><input type="radio" name="preferred" value="{key}" required>Prefer {safe_label}</label>
<label for="notes-{key}">Notes for {safe_label}</label>
<textarea id="notes-{key}" name="notes-{key}" maxlength="10000" autocomplete="off"></textarea></div>
<details><summary>Image identity</summary><code>{digest}</code></details></article>''')
    identity = {"version": 1, "title": title, "question": question, "context": context,
                "baseline": records[0]["id"], "variants": records}
    digest = hashlib.sha256(json.dumps(identity, sort_keys=True, ensure_ascii=True).encode()).hexdigest()
    payload = {**identity, "board_sha256": digest}
    # Untrusted JSON never becomes markup, including closing script tags in labels.
    encoded = json.dumps(payload, ensure_ascii=True).replace("<", "\\u003c")
    viewport = context["viewport"]
    capture = f'{viewport["width"]} × {viewport["height"]} CSS pixels; {context["theme"]}; {context["state"]}'
    template = Path(__file__).resolve().parent.parent / "assets/variant-review.html"
    values = {"TITLE": html.escape(title), "QUESTION": html.escape(question),
              "CONTEXT": html.escape(capture), "CARDS": "\n".join(cards),
              "IDENTITY": digest, "REVIEW_DATA": encoded}
    # One pass prevents user text resembling a placeholder from being substituted again.
    rendered = re.sub(r"__(TITLE|QUESTION|CONTEXT|CARDS|IDENTITY|REVIEW_DATA)__",
                      lambda match: values[match.group(1)], template.read_text())
    return rendered, digest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    try:
        rendered, digest = build(args.manifest)
        with args.output.open("x", encoding="utf-8") as handle:
            handle.write(rendered)
    except (OSError, ValueError, RecursionError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    print(json.dumps({"output": str(args.output), "board_sha256": digest, "browser_checks": "NOT RUN"}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
