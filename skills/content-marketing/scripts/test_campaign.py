"""Exercise artifact delivery and materially harmful input/comparison boundaries."""

import copy
import csv
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from urllib.parse import parse_qs, urlsplit


SCRIPT = Path(__file__).with_name("campaign.py")
EXAMPLE = SCRIPT.parent.parent / "examples" / "campaign.json"


def observation(identifier, value, **changes):
    return {"content_id": identifier, "platform": "linkedin", "account": "owned-account",
            "format": "post", "metric": "outbound_clicks", "definition": "External visits including repeat clicks",
            "scope": "organic-public", "window_hours": 168, "published_at": "2026-10-01T00:00:00Z",
            "observed_at": "2026-10-08T00:00:00Z", "status": "complete", "value": value,
            "source": "export.csv:row-2", **changes}


class CampaignTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.plan = json.loads(EXAMPLE.read_text())
        self.plan["claims"][0]["status"] = "verified"
        for item in self.plan["items"]:
            item["link_access"] = "verified"

    def run_cli(self, plan=None, *, raw=None, output="result"):
        input_path = self.root / "input.json"
        input_path.write_text(raw if raw is not None else json.dumps(plan if plan is not None else self.plan))
        out = self.root / output
        result = subprocess.run([sys.executable, str(SCRIPT), str(input_path), "--out", str(out)],
                                capture_output=True, text=True)
        return result, out

    def test_complete_path_preserves_counts_cohorts_links_and_raw_evidence(self):
        self.plan["items"][0]["destination_url"] = "https://example.com/workflow?filter=a&utm_source=old#demo"
        self.plan["observations"] = [observation("a", 10), observation("b", 20),
                                     observation("c", 30), observation("d", 80),
                                     observation("partial", 9999, status="partial"),
                                     observation("missing", None, status="unavailable"),
                                     observation("youtube", 100000, platform="youtube", format="video")]
        result, out = self.run_cli()
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads((out / "campaign.json").read_text())
        self.assertEqual(data["performance"][0]["total"], 6)
        rows = {r["content_id"]: r for r in data["performance"][0]["rows"]}
        self.assertEqual((rows["d"]["peer_count"], rows["d"]["peer_median"], rows["d"]["lift"]), (3, 20, 4))
        self.assertIsNone(rows["partial"]["lift"])
        self.assertIsNone(data["performance"][1]["rows"][0]["lift"])
        url = urlsplit(data["items"][0]["url"])
        self.assertEqual(parse_qs(url.query), {"filter": ["a"], "utm_source": ["linkedin"],
                         "utm_medium": ["social"], "utm_campaign": ["demo-workflow"],
                         "utm_content": ["linkedin-lesson"]})
        self.assertEqual(url.fragment, "demo")
        self.assertIn("What a passing check", (out / "brief.md").read_text())
        with (out / "performance.csv").open(newline="") as stream:
            self.assertEqual(len(list(csv.DictReader(stream))), 7)

    def test_missing_proof_destinations_and_nonclickable_short_stay_blocked(self):
        self.plan["claims"][0]["status"] = "unverified"
        self.plan["items"][0]["destination_url"] = None
        self.plan["items"][1]["format"] = "short"
        result, out = self.run_cli()
        self.assertEqual(result.returncode, 0, result.stderr)
        items = json.loads((out / "campaign.json").read_text())["items"]
        self.assertEqual([i["status"] for i in items], ["blocked", "blocked"])
        self.assertTrue(any("not clickable" in b for b in items[1]["blockers"]))
        self.assertNotIn("utm_", items[1]["url"])

    def test_canonical_video_and_internal_site_links_do_not_get_attribution_tags(self):
        self.plan["items"][0]["destination_url"] = "https://www.youtube.com/watch?v=abcdefghijk"
        self.plan["items"][1].update(platform="website", format="page", placement="link")
        result, out = self.run_cli()
        self.assertEqual(result.returncode, 0, result.stderr)
        items = json.loads((out / "campaign.json").read_text())["items"]
        self.assertEqual(items[0]["url"], "https://www.youtube.com/watch?v=abcdefghijk")
        self.assertEqual(items[1]["url"], "https://example.com/workflow")

    def test_rejects_corrupt_or_incomplete_input_before_output_exists(self):
        cases = []
        for field in ("claim_ids", "outline"):
            plan = copy.deepcopy(self.plan)
            plan["items"][0][field] = []
            cases.append(plan)
        no_rule = copy.deepcopy(self.plan)
        del no_rule["campaign"]["decision_rule"]
        cases.append(no_rule)
        for changes in ({"value": float("nan")}, {"value": True},
                        {"value": None}, {"observed_at": "2026-10-02T00:00:00Z"},
                        {"published_at": "2026-10-01"}):
            plan = copy.deepcopy(self.plan)
            plan["observations"] = [{**observation("a", 12), **changes}]
            cases.append(plan)
        duplicate = copy.deepcopy(self.plan)
        duplicate["observations"] = [observation("a", 10), observation("a", 10)]
        cases.append(duplicate)
        for index, plan in enumerate(cases):
            with self.subTest(index=index):
                result, out = self.run_cli(plan, output=f"bad-{index}")
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse(out.exists())
        result, out = self.run_cli(raw='{"schema_version": 1, "schema_version": 1}', output="duplicate-key")
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(out.exists())

    def test_window_definition_scope_and_account_never_pool_and_zero_is_not_missing(self):
        self.plan["observations"] = [observation("a", 0), observation("b", 0), observation("c", 0),
                                     observation("d", 10), observation("lifetime", 10000, window_hours=24),
                                     observation("broad", 10000, definition="All clicks"),
                                     observation("paid", 10000, scope="paid"),
                                     observation("other", 10000, account="another-account")]
        result, out = self.run_cli()
        self.assertEqual(result.returncode, 0, result.stderr)
        groups = json.loads((out / "campaign.json").read_text())["performance"]
        self.assertEqual(len(groups), 5)
        row = next(r for r in groups[0]["rows"] if r["content_id"] == "d")
        self.assertEqual(row["comparison_limit"], "zero peer median")
        self.assertEqual(groups[0]["complete"], 4)

    def test_spreadsheet_formula_content_is_inert_and_existing_artifacts_survive(self):
        self.plan["observations"] = [observation("=HYPERLINK(1)", 10, source="\t=1+1")]
        result, out = self.run_cli()
        self.assertEqual(result.returncode, 0, result.stderr)
        with (out / "performance.csv").open(newline="") as stream:
            row = next(csv.DictReader(stream))
        self.assertEqual(row["content_id"], "'=HYPERLINK(1)")
        self.assertEqual(row["source"], "'\t=1+1")
        original = (out / "brief.md").read_bytes()
        result, _ = self.run_cli()
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual((out / "brief.md").read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
