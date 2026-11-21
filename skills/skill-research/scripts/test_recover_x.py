from contextlib import redirect_stdout
import http.client
import io
import json
import unittest
from unittest.mock import patch
import urllib.error
import urllib.request

from recover_x import ApiRedirects, MAX_BYTES, fetch_json, parse_source, read_embed, read_extraction, recover, main


URL = "https://x.com/example/status/2115810209214107833"
SOURCE = parse_source(URL)


def embed(text="A public claim."):
    return {"url": URL, "author_name": "Example", "html":
            '<blockquote><p>' + text + '</p>Author footer and date</blockquote><script>untrusted()</script>'}


class PublicSourceRecovery(unittest.TestCase):
    def test_public_url_boundary_drops_share_data_and_rejects_arbitrary_hosts(self):
        self.assertEqual(parse_source(URL + "?private=discard#fragment")["url"], URL)
        for url in ("http://x.com/example/status/21", "https://x.com.evil.test/example/status/21",
                    "https://credential" + chr(64) + "x.com/example/status/21",
                    "https://x.com:8443/example/status/21"):
            with self.subTest(url=url), self.assertRaises(ValueError):
                parse_source(url)
        request = urllib.request.Request("https://publish.x.com/oembed")
        for target in ("http://127.0.0.1/", "https://api.fxtwitter.com/2/status/21"):
            with self.subTest(target=target), self.assertRaises(ValueError):
                ApiRedirects().redirect_request(request, None, 302, "Found", {}, target)

    def test_embed_keeps_body_links_and_excludes_footer_and_scripts(self):
        data = embed('First line.<br><a href="https://t.co/fixture">Repository</a><script>attack()</script>')
        record = read_embed(data, SOURCE)
        self.assertEqual(record["text"], "First line.\nRepository")
        self.assertEqual(record["links"], ["https://t.co/fixture"])
        data["url"] = "https://x.com/i/web/status/" + SOURCE["id"]
        record = read_embed(data, SOURCE)
        self.assertTrue(any("AUTHOR_UNVERIFIED" in warning for warning in record["warnings"]))

    def test_truncation_and_link_only_article_preview_cannot_be_full_review(self):
        for data, marker in [(embed("A claim that continues…"), "TRUNCATED"),
                             (embed('<a href="https://t.co/article">https://t.co/article</a>'), "LINK_ONLY")]:
            with self.subTest(marker=marker), patch("recover_x.fetch_json", return_value=(data, "digest")):
                result = recover(URL)
                self.assertEqual(result["coverage"], "PARTIAL")
                self.assertFalse(result["full_review"])
                self.assertTrue(any(marker in warning for warning in result["records"][0]["warnings"]))

    def test_mismatched_post_id_never_becomes_evidence(self):
        data = embed()
        data["url"] = "https://x.com/example/status/999"
        with patch("recover_x.fetch_json", return_value=(data, "digest")):
            result = recover(URL)
        self.assertEqual(result["coverage"], "UNAVAILABLE")
        self.assertFalse(result["records"])
        self.assertEqual(result["attempts"][0]["status"], "FAILED")

    def test_secondary_article_preserves_entities_and_stays_secondary(self):
        article = {"id": "2113242613214048257", "title": "Fixture", "content": {
            "blocks": [{"type": "header-two", "text": "Section"}, {"type": "atomic", "text": " "}],
            "entityMap": [{"value": {"type": "MARKDOWN", "data": {"markdown": "Embedded source"}}}]}}
        data = {"code": 200, "status": {"type": "status", "id": SOURCE["id"],
                "text": "https://x.com/i/article/2113242613214048257", "article": article,
                "author": {"screen_name": "example"}}}
        record = read_extraction(data, SOURCE)
        self.assertEqual(record["provenance"], "secondary_extraction")
        self.assertEqual(record["article"]["content"]["entityMap"][0]["value"]["data"]["markdown"],
                         "Embedded source")
        self.assertEqual(record["article_block_text"], "Section\n\n ")
        data["code"] = 404
        with self.assertRaises(ValueError):
            read_extraction(data, SOURCE)
        data["code"] = 200
        for empty_article in (None, {"title": "Preview only", "content": {"blocks": []}},
                              {"content": {"blocks": [{"text": " \n "}]}}):
            data["status"].update(text="", article=empty_article)
            with self.subTest(article=empty_article), self.assertRaises(ValueError):
                read_extraction(data, SOURCE)
        article["content"]["blocks"] = [{"type": "atomic", "text": " "}]
        data["status"]["article"] = article
        record = read_extraction(data, SOURCE)
        self.assertEqual(record["article"], article)
        self.assertEqual(record["provenance"], "secondary_extraction")
        self.assertTrue(any("MARKDOWN_ENTITY" in warning for warning in record["warnings"]))
        for entity in ({"type": "MARKDOWN", "data": {"markdown": " \n "}},
                       {"type": "MEDIA", "data": {"markdown": "Not Markdown"}}):
            article["content"]["entityMap"] = [{"value": entity}]
            with self.subTest(entity=entity), self.assertRaises(ValueError):
                read_extraction(data, SOURCE)

    def test_failed_primary_can_recover_only_through_requested_secondary(self):
        data = {"code": 200, "status": {"type": "status", "id": SOURCE["id"],
                "text": "Remaining public source text.", "author": {"screen_name": "example"}}}
        failure = urllib.error.URLError("DNS unavailable in sandbox")
        with patch("recover_x.fetch_json", side_effect=failure):
            unavailable = recover(URL)
        self.assertEqual(len(unavailable["attempts"]), 1)
        self.assertFalse(unavailable["records"])
        with patch("recover_x.fetch_json", side_effect=[failure, (data, "digest")]):
            recovered = recover(URL, secondary=True)
        self.assertEqual(recovered["coverage"], "PARTIAL")
        self.assertEqual(recovered["attempts"][0]["status"], "FAILED")
        self.assertEqual(recovered["records"][0]["text"], "Remaining public source text.")
        self.assertFalse(recovered["full_review"])

    def test_cli_keeps_markdown_secondary_and_reports_empty_article_failure(self):
        article = {"content": {"blocks": [{"type": "atomic", "text": " "}],
                   "entityMap": [{"value": {"type": "MARKDOWN",
                                  "data": {"markdown": "Fixture source body"}}}]}}
        data = {"code": 200, "status": {"type": "status", "id": SOURCE["id"],
                "text": "", "article": article}}
        for body, expected_exit in (("Fixture source body", 0), (" ", 2)):
            article["content"]["entityMap"][0]["value"]["data"]["markdown"] = body
            output = io.StringIO()
            with self.subTest(body=body), patch("sys.argv", ["recover_x.py", URL, "--secondary"]), \
                    patch("recover_x.fetch_json", side_effect=[
                        urllib.error.URLError("Offline primary unavailable"), (data, "digest")]), \
                    redirect_stdout(output):
                self.assertEqual(main(), expected_exit)
            result = json.loads(output.getvalue())
            self.assertFalse(result["full_review"])
            self.assertEqual(result["attempts"][0]["status"], "FAILED")
            if expected_exit == 0:
                self.assertEqual(result["coverage"], "PARTIAL")
                self.assertEqual(result["records"][0]["provenance"], "secondary_extraction")
                self.assertTrue(any("association is not verified" in warning
                                    for warning in result["records"][0]["warnings"]))
            else:
                self.assertEqual(result["coverage"], "UNAVAILABLE")
                self.assertFalse(result["records"])

    def test_article_id_is_not_sent_to_post_endpoints(self):
        with patch("recover_x.fetch_json", side_effect=AssertionError("Article ID used as post ID")):
            result = recover("https://x.com/i/article/2113242613214048257", secondary=True)
        self.assertEqual(result["coverage"], "NEEDS_ARTICLE_ROUTE")
        self.assertFalse(result["attempts"])

    def test_truncated_http_exception_records_failed_attempt(self):
        class FailingOpener:
            def open(self, request, timeout=25):
                raise http.client.IncompleteRead(b'{"partial":')

        with patch("urllib.request.build_opener", return_value=FailingOpener()):
            result = recover(URL)
        self.assertEqual(result["coverage"], "UNAVAILABLE")
        self.assertFalse(result["records"])
        self.assertEqual(result["attempts"][0]["status"], "FAILED")
        self.assertIn("IncompleteRead", result["attempts"][0]["error"])

    def test_fetch_json_enforces_max_bytes_cap(self):
        class FakeResponse:
            def __init__(self, payload):
                self.payload = payload

            def __enter__(self):
                return self

            def __exit__(self, *args):
                return False

            def read(self, size):
                return self.payload[:size]

        class FakeOpener:
            def __init__(self, payload):
                self.payload = payload

            def open(self, request, timeout=25):
                return FakeResponse(self.payload)

        oversized = b"x" * (MAX_BYTES + 1)
        with patch("urllib.request.build_opener", return_value=FakeOpener(oversized)):
            with self.assertRaises(ValueError):
                fetch_json("https://publish.x.com/oembed?url=https://x.com/example/status/1")
            result = recover(URL)
        self.assertEqual(result["attempts"][0]["status"], "FAILED")
        self.assertIn("1 MiB", result["attempts"][0]["error"])

        valid = json.dumps(embed()).encode("utf-8")
        with patch("urllib.request.build_opener", return_value=FakeOpener(valid)):
            data, digest = fetch_json("https://publish.x.com/oembed?url=https://x.com/example/status/1")
        self.assertEqual(data["url"], URL)
        self.assertTrue(digest)


if __name__ == "__main__":
    unittest.main()
