#!/usr/bin/env python3
"""Map an unfamiliar data source: survey, keys, joins and check-claims. JSON on stdout.

survey <path>                      tables, columns, types, nulls, sentinels, time ranges, drift
keys <path> [--table T]            minimal unique column sets, exact counts
joins <path>                       candidate foreign keys by value overlap, never confirmed
check-claims <claims.json> <path>  re-check saved claims; exit 1 when any fails or is vacuous

<path> is a SQLite file, one CSV/TSV/JSONL file, or a directory of them. Sources are read
only; file tables are staged in a temporary SQLite file that is deleted afterwards.
Exit 0 ok, 1 findings (check-claims), 2 invalid input.
"""
import argparse
import json
import sqlite3
import sys

if sys.version_info < (3, 10):
    print(json.dumps({"error": "Python 3.10 or later is required"}))
    sys.exit(2)

from claims import check, load
from joins import joins
from keys import keys
from sources import InputError, Workspace
from survey import survey


class Parser(argparse.ArgumentParser):
    def error(self, message):
        self.exit(2, json.dumps({"error": "invalid arguments: " + message}) + "\n")


def positive(text):
    value = int(text)
    if value < 1:
        raise argparse.ArgumentTypeError("must be at least 1")
    return value


def fraction(text):
    value = float(text)
    if not 0 < value <= 1:
        raise argparse.ArgumentTypeError("must be in (0, 1]")
    return value


def parser():
    top = Parser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    top.add_argument("--no-values", action="store_true",
                     help="suppress every value echoed from the data (examples, extremes, sentinels)")
    sub = top.add_subparsers(dest="command", required=True, parser_class=Parser)
    common = Parser(add_help=False)
    common.add_argument("--no-values", action="store_true", default=argparse.SUPPRESS,
                        help="same as the top-level flag")
    s = sub.add_parser("survey", parents=[common])
    s.add_argument("path")
    s.add_argument("--distinct-cap", type=positive, default=50000,
                   help="exact distinct counts up to this many per column, then 'exceeds cap'")
    k = sub.add_parser("keys", parents=[common])
    k.add_argument("path")
    k.add_argument("--table")
    k.add_argument("--max-width", type=positive, default=3)
    k.add_argument("--max-combos", type=positive, default=5000)
    j = sub.add_parser("joins", parents=[common])
    j.add_argument("path")
    j.add_argument("--min-containment", type=fraction, default=0.5)
    j.add_argument("--top", type=positive, default=50)
    c = sub.add_parser("check-claims", parents=[common])
    c.add_argument("claims")
    c.add_argument("path")
    return top


def run(args):
    show = not args.no_values
    if args.command == "survey":
        return survey(args.path, args.distinct_cap, show), 0
    claims = load(args.claims) if args.command == "check-claims" else None
    ws = Workspace(args.path, show)
    try:
        if args.command == "keys":
            return keys(ws, ws.table(args.table), args.max_width, args.max_combos, show), 0
        if args.command == "joins":
            return joins(ws, args.min_containment, args.top, show), 0
        report = check(ws, claims, show)
        return report, 0 if report["status"] == "pass" else 1
    finally:
        ws.close()


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        report, code = run(args)
    except (InputError, sqlite3.Error) as error:
        print(json.dumps({"error": str(error)}))
        return 2
    except Exception as error:
        print(json.dumps({"error": "%s: %s" % (type(error).__name__, error)}))
        return 2
    print(json.dumps(report, indent=2, default=str))
    return code


if __name__ == "__main__":
    sys.exit(main())
