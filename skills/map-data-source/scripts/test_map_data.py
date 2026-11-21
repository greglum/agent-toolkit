import csv
import json
import os
from pathlib import Path
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parent
ASSETS = SCRIPTS.parent / "assets"
SHOP = ASSETS / "shop"
CLAIMS = ASSETS / "claims.json"
TOOL = SCRIPTS / "map_data.py"


def run(*args, env=None):
    process = subprocess.run([sys.executable, "-B", str(TOOL), *map(str, args)], capture_output=True, text=True,
                             env=env)
    return process.returncode, json.loads(process.stdout), process.stdout


def table(report, name):
    return next(t for t in report["tables"] if t["table"] == name)


def column(item, name):
    return next(c for c in item["columns"] if c["column"] == name)


class MapDataTests(unittest.TestCase):
    def setUp(self):
        scratch = tempfile.TemporaryDirectory()
        self.addCleanup(scratch.cleanup)
        self.root = Path(scratch.name)

    def copy_shop(self):
        target = self.root / "shop"
        shutil.copytree(SHOP, target)
        return target

    def test_survey_reports_drift_absence_and_sentinels(self):
        code, report, _ = run("survey", SHOP)
        self.assertEqual(code, 0)
        lines = table(report, "order_lines")
        self.assertEqual((lines["files"], lines["rows"]), (3, 16))
        last = lines["drift"][-1]
        self.assertEqual(last["missing"], ["channel"])
        self.assertEqual(last["type_changed"], [{"column": "quantity", "from": "integer", "to": "decimal"}])
        self.assertEqual(lines["drift"][0]["added"], ["gift_wrap"])
        channel = column(lines, "channel")
        self.assertEqual((channel["absent_rows"], channel["null"], channel["empty"]), (5, 0, 0))
        products = table(report, "products")
        sentinel = column(products, "weight_g").get("sentinel_candidates", [])
        self.assertEqual([(s["value"], s["count"], s["side"]) for s in sentinel], [(9999, 2, "max")])
        self.assertEqual(column(products, "color")["null_tokens"], {"N/A": 2})
        self.assertNotIn("sentinel_candidates", column(products, "category"))
        retyped = self.write("drift", {"a_1.csv": "id,q\n1,2\n", "a_2.csv": "id,q\n2,2.5\n"})
        self.assertEqual(len(table(run("survey", retyped)[1], "a")["drift"]), 1)
        times = column(lines, "ordered_at")["time"]
        self.assertEqual((times["min"], times["max"]), ("2026-03-01T09:15:00Z", "2026-03-03T12:30:00Z"))

    def test_distinct_cap_reports_exceeds_cap_not_a_number(self):
        code, report, _ = run("survey", SHOP, "--distinct-cap", "5")
        order_id = column(table(report, "order_lines"), "order_id")
        self.assertEqual((code, order_id["distinct"]), (0, "exceeds cap"))
        self.assertEqual(column(table(report, "order_lines"), "line_no")["distinct"], 3)
        self.assertEqual(column(table(run("survey", SHOP)[1], "order_lines"), "order_id")["distinct"], 9)

    def test_keys_reject_obvious_id_and_find_two_column_key(self):
        for source in (SHOP, self.sqlite_copy()):
            code, report, _ = run("keys", source, "--table", "order_lines", "--max-width", "2")
            self.assertEqual(code, 0, source)
            order_id = next(c for c in report["columns"] if c["name"] == "order_id")
            self.assertEqual((order_id["duplicate_groups"], order_id["rows_in_duplicate_groups"]), (6, 13))
            self.assertIn({"columns": ["order_id", "line_no"], "status": "unique", "null_rows": 0}, report["keys"])
            self.assertFalse(any(k["columns"] == ["order_id"] for k in report["keys"]))

    def test_joins_rank_unique_parent_and_measure_fan_out(self):
        code, report, _ = run("joins", SHOP)
        self.assertEqual(code, 0)
        found = {(c["child"], c["parent"]): c for c in report["candidates"]}
        good = found[("order_lines.sku", "products.sku")]
        fan = found[("order_lines.sku", "price_history.sku")]
        self.assertEqual((good["containment"], good["orphan_rows"], good["parent_unique"], good["fan_out"]),
                         (1.0, 0, True, 1.0))
        self.assertEqual((fan["parent_unique"], fan["fan_out"]), (False, 1.5))
        self.assertGreater(good["score"], fan["score"])
        self.assertTrue(all(c["status"] == "candidate" for c in report["candidates"]))

    def test_claims_pass_then_fail_after_planted_orphan(self):
        code, report, _ = run("check-claims", CLAIMS, SHOP)
        self.assertEqual((code, report["status"], report["failed"]), (0, "pass", 0))
        shop = self.copy_shop()
        with open(shop / "order_lines_2026-03-04.csv", "w", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(["order_id", "line_no", "sku", "quantity", "gift_wrap", "ordered_at", "loaded_at"])
            writer.writerow([1010, 1, "SKU-999", 1, "no", "2026-03-04T10:00:00Z", "2026-03-05T02:00:00Z"])
        code, report, _ = run("check-claims", CLAIMS, shop)
        failed = [r for r in report["results"] if r["status"] != "pass"]
        self.assertEqual(code, 1)
        self.assertEqual([(r["id"], r["orphan_rows"]) for r in failed], [("sku-in-products", 1)])
        self.assertEqual(failed[0]["examples"], ["SKU-999"])
        code, report, text = run("check-claims", CLAIMS, shop, "--no-values")
        self.assertEqual((code, report["failed"]), (1, 1))
        self.assertNotIn("SKU-999", text)

    def test_empty_table_vacuous_missing_column_and_empty_cell_fail(self):
        shop = self.copy_shop()
        (shop / "products.csv").write_text("sku,name,category,weight_g,color\n")
        prices = shop / "price_history.csv"
        prices.write_text(prices.read_text().replace("SKU-109,2026-01-01,9.50", "SKU-109,2026-01-01, "))
        claims = self.root / "claims.json"
        claims.write_text(json.dumps({"claims": [
            {"id": "grain", "type": "unique", "table": "products", "columns": ["sku"]},
            {"id": "skus", "type": "not_null", "table": "products", "column": "sku"},
            {"id": "gone", "type": "not_null", "table": "price_history", "column": "currency"},
            {"id": "priced", "type": "not_null", "table": "price_history", "column": "price"}]}))
        code, report, _ = run("check-claims", claims, shop)
        self.assertEqual(code, 1)
        self.assertEqual([r["status"] for r in report["results"]], ["vacuous", "vacuous", "fail", "fail"])
        self.assertEqual(report["results"][3]["null_rows"], 1)

    def test_invalid_input_exits_2(self):
        bad = self.root / "bad.json"
        bad.write_text(json.dumps({"claims": [{"id": "x", "type": "unique_ish", "table": "products"}]}))
        self.assertEqual(run("check-claims", bad, SHOP)[0], 2)
        bad.write_text(json.dumps({"claims": [{"id": "x", "type": "row_count", "table": "products", "min": "10"}]}))
        self.assertEqual(run("check-claims", bad, SHOP)[0], 2)
        self.assertEqual(run("survey", self.root / "missing")[0], 2)

    def write(self, folder, files):
        folder = self.root / folder
        folder.mkdir()
        for name, text in files.items():
            (folder / name).write_text(text)
        return folder

    def claims(self, *claims):
        path = self.root / "c.json"
        path.write_text(json.dumps({"claims": list(claims)}))
        return path

    def test_each_claim_type_fails_on_a_false_claim(self):
        code, report, _ = run("check-claims", self.claims(
            {"id": "r", "type": "range", "table": "order_lines", "column": "quantity", "max": 2},
            {"id": "a", "type": "accepted_values", "table": "order_lines", "column": "channel", "values": ["web"]},
            {"id": "u", "type": "unique", "table": "order_lines", "columns": ["order_id"]},
            {"id": "n", "type": "row_count", "table": "order_lines", "max": 5}), SHOP)
        self.assertEqual((code, [r["status"] for r in report["results"]]), (1, ["fail"] * 4))

    def test_all_null_column_is_vacuous_and_nan_is_out_of_range(self):
        data = self.write("nulls", {"t.csv": "id,code,amt\n1,,\n2,,\n", "n.csv": "id,amt\n1,nan\n2,5\n"})
        code, report, _ = run("check-claims", self.claims(
            {"id": "u", "type": "unique", "table": "t", "columns": ["code"]},
            {"id": "a", "type": "accepted_values", "table": "t", "column": "code", "values": ["x"]},
            {"id": "r", "type": "range", "table": "t", "column": "amt", "min": 0},
            {"id": "f", "type": "range", "table": "n", "column": "amt", "min": 0, "max": 10}), data)
        self.assertEqual([r["status"] for r in report["results"]], ["vacuous"] * 3 + ["fail"])
        self.assertEqual((code, report["results"][3]["not_finite"]), (1, 1))
        empty = self.claims({"id": "e", "type": "accepted_values", "table": "t", "column": "id", "values": []})
        self.assertEqual(run("check-claims", empty, data)[0], 2)

    def test_no_values_suppresses_every_echo_and_header_like_data(self):
        shop = self.copy_shop()
        (shop / "order_lines_2026-03-04.csv").write_text(
            "order_id,line_no,sku,quantity,gift_wrap,ordered_at,loaded_at\n"
            "1010,1,SKU-999,1,no,2026-03-04T10:00:00Z,2026-03-05T02:00:00Z\n")
        (shop / "contacts.csv").write_text("5551234,987654\n5551235,987655\n")
        _, survey, text = run("survey", shop, "--no-values")
        for needle in ("9999", "5551234", "SKU-"):
            self.assertNotIn(needle, text)
        contacts = table(survey, "contacts")
        self.assertIn("header_suspect", contacts["file_detail"][0])
        self.assertEqual([c["column"] for c in contacts["columns"]], ["col_1", "col_2"])
        for name, needles in (("order_lines", ("1003", "SKU-")), ("contacts", ("5551234",))):
            text = run("keys", shop, "--table", name, "--no-values")[2]
            self.assertTrue(all(n not in text for n in needles), name)
        code, joins, text = run("joins", shop, "--no-values")
        self.assertNotIn("SKU-999", text)
        found = {(c["child"], c["parent"]): c for c in joins["candidates"]}
        self.assertEqual(found[("order_lines.sku", "products.sku")]["orphan_rows"], 1)

    def test_keys_are_minimal_and_nullable_sets_are_marked(self):
        scratch = self.root / "tmp"
        scratch.mkdir()
        _, report, _ = run("keys", SHOP, "--table", "order_lines", env={**os.environ, "TMPDIR": str(scratch)})
        sets = [set(k["columns"]) for k in report["keys"]]
        self.assertFalse(any(a < b for a in sets for b in sets))
        self.assertIn({"columns": ["line_no", "sku", "channel"], "status": "unique_with_nulls", "null_rows": 5},
                      report["keys"])
        self.assertEqual(list(scratch.iterdir()), [])

    def test_leading_zero_codes_stay_text_and_mismatch_is_reported(self):
        data = self.write("codes", {
            "zips.csv": "zip,city\n00501,A\n01002,B\n", "people.csv": "id,zip\n1,00501\n2,01002\n",
            "codes.csv": "code,label\n007,a\n008,b\n009,c\n", "refs.csv": "ref,code\n1,7\n2,8\n3,9\n"})
        zip_column = column(table(run("survey", data)[1], "zips"), "zip")
        self.assertEqual((zip_column["type"], "min" in zip_column), ("text", False))
        found = {(c["child"], c["parent"]): c for c in run("joins", data)[1]["candidates"]}
        self.assertEqual(found[("people.zip", "zips.zip")]["containment"], 1.0)
        self.assertEqual(found[("refs.code", "codes.code")]["leading_zero_mismatch"], 3)

    def test_sqlite_generated_columns_are_read(self):
        path = self.root / "g.sqlite"
        db = sqlite3.connect(path)
        db.execute("CREATE TABLE t (a INTEGER, b INTEGER GENERATED ALWAYS AS (a * 2) VIRTUAL)")
        db.executemany("INSERT INTO t (a) VALUES (?)", [(1,), (2,)])
        db.commit()
        db.close()
        self.assertEqual(column(table(run("survey", path)[1], "t"), "b")["max"], 4)
        self.assertEqual([c["name"] for c in run("keys", path, "--table", "t")[1]["columns"]], ["a", "b"])

    def test_accepted_values_match_native_sqlite_numbers(self):
        path = self.root / "r.sqlite"
        db = sqlite3.connect(path)
        db.execute("CREATE TABLE t (grade REAL, code TEXT)")
        db.executemany("INSERT INTO t VALUES (?, ?)", [(2.0, "A"), (3.5, "B")])
        db.commit()
        db.close()
        code, report, _ = run("check-claims", self.claims(
            {"id": "g", "type": "accepted_values", "table": "t", "column": "grade", "values": [2, 3.5]},
            {"id": "x", "type": "accepted_values", "table": "t", "column": "grade", "values": [2]}), path)
        self.assertEqual((code, [r["status"] for r in report["results"]]), (1, ["pass", "fail"]))

    def sqlite_copy(self):
        path = self.root / "shop.sqlite"
        db = sqlite3.connect(path)
        rows = []
        for file in sorted(SHOP.glob("order_lines_*.csv")):
            with open(file, newline="") as handle:
                rows += [(r["order_id"], r["line_no"], r["sku"]) for r in csv.DictReader(handle)]
        db.execute("CREATE TABLE order_lines (order_id INTEGER, line_no INTEGER, sku TEXT)")
        db.executemany("INSERT INTO order_lines VALUES (?, ?, ?)", rows)
        db.commit()
        db.close()
        return path


if __name__ == "__main__":
    unittest.main()
