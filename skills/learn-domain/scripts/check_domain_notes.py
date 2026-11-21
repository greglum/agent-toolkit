#!/usr/bin/env python3
"""Check domain notes (sources, glossary, primer, questions) written in references/formats.md.

Usage: check_domain_notes.py FILE.md [FILE.md ...]
Exit 0: no findings. Exit 1: findings. Exit 2: invalid input. Output is JSON on stdout.
"""
import json
import re
import sys
from pathlib import Path

if sys.version_info < (3, 10):
    print(json.dumps({"error": f"Python 3.10 or later is required; this is {sys.version.split()[0]}"}))
    sys.exit(2)

STATUSES = {"Checked", "Reported", "Analysis", "Open"}
KINDS = {"internal", "standard", "regulator", "rulebook", "vendor", "peer-reviewed", "practitioner"}
EVIDENCE_KINDS = ("conflict", "gap", "data", "standard")
SECTIONS = {"sources": "sources", "source map": "sources", "glossary": "glossary",
            "primer": "primer", "questions": "questions"}
PRIMER_PARTS = ("how it works", "entities and processes", "metrics and traps", "newcomer mistakes")
COLUMNS = {
    "sources": ("id", "source", "kind", "date", "locator", "proves", "claims"),
    "glossary": ("term", "meaning", "not", "avoid", "units", "source", "status"),
    "questions": ("id", "rank", "question", "decision", "evidence", "answerer"),
}
ROLE_WORDS = {"lead", "manager", "analyst", "clerk", "supervisor", "engineer", "owner", "team", "officer",
              "director", "head", "expert", "specialist", "steward", "admin", "operator", "auditor", "desk",
              "architect", "scientist", "counsel", "planner", "coordinator", "controller", "superintendent",
              "chief", "administrator", "advisor", "researcher", "developer", "designer", "inspector",
              "accountant", "treasurer", "underwriter", "actuary", "broker"}
H2 = re.compile(r"^ {0,3}#{1,2}\s+(.*?)\s*#*\s*$")
H3 = re.compile(r"^ {0,3}###\s+(.*?)\s*#*\s*$")
SEPARATOR = re.compile(r"^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)*\|?\s*$")
CELL_SPLIT = re.compile(r"(?<!\\)\|")
QID = r"Q(?:[0-9]+|-[A-Za-z0-9_]+(?:-[A-Za-z0-9_]+)*-[0-9]+)"
ID = rf"(?:S[0-9]+|{QID})(?![\w-])"
TAG = re.compile(rf"\[\s*({ID}[^\[\];]*);\s*([^\[\]]*?)\s*\]")
BARE_REF = re.compile(rf"\[\s*{ID}[^\[\];]*\]")
REF = re.compile(rf"^({ID})\s*(.*)$")
SOURCE_ID = re.compile(r"(?<![\w-])S[0-9]+(?![\w-])")
LOCATOR_TOKEN = (r"(?:§\s*[\w.-]+|pp?\.\s*[0-9]+(?:-[0-9]+)?|(?:line|lines|l\.)\s*[0-9]+(?:-[0-9]+)?"
                 r"|[0-9]{1,2}:[0-9]{2}(?::[0-9]{2})?|#[\w.-]+|\"[^\"]+\""
                 r"|(?:table|figure|fig\.|rule|section|chapter|clause|slide|sheet|cell|row|appendix|annex|step|item)"
                 r"\s+[\w.-]+)")
LOCATOR = re.compile(rf"^{LOCATOR_TOKEN}(?:\s+{LOCATOR_TOKEN})*$", re.IGNORECASE)
DATE = re.compile(r"^(?:accessed\s+)?[0-9]{4}(?:-[0-9]{2}(?:-[0-9]{2})?)?$", re.IGNORECASE)
URL_OR_PATH = re.compile(r"^(?:https?://\S+|[\w.~/-]*/[\w.~/-]+|[\w.~-]+\.[A-Za-z0-9]{1,5})$")
SENTENCE_BREAK = re.compile(r"[.!?]\s+(?=[A-Z])")
CODE_SPAN = re.compile(r"`[^`]*`")
LIST_MARKER = re.compile(r"^([-*+]|[0-9]+[.)])\s")
EMAIL = re.compile(r"[^\s@]+@[^\s@]+\.[A-Za-z]{2,}|(?<!\w)@\w+")
TWO_NAMES = re.compile(r"^[A-Z][a-z]+(?:\s+[A-Z]\.)?\s+[A-Z][a-z'-]+$")
EMPTY = {"", "-", "n/a", "none"}


class InputError(ValueError):
    pass


def short(text):
    text = " ".join(str(text).split())
    return text if len(text) <= 80 else text[:77] + "..."


def cells(line):
    body = line.strip()
    if body.startswith("|"):
        body = body[1:]
    if body.endswith("|") and not body.endswith("\\|"):
        body = body[:-1]
    return [c.strip().replace("\\|", "|") for c in CELL_SPLIT.split(body)]


def sections(text):
    """Return [(section name, [(line number, line)])] for each recognized level-2 section."""
    current, lines, found = None, [], []
    for number, line in enumerate(text.splitlines(), 1):
        heading = H2.match(line)
        if heading:
            if current:
                found.append((current, lines))
            current, lines = SECTIONS.get(heading.group(1).strip().lower()), []
        elif current:
            lines.append((number, line))
    if current:
        found.append((current, lines))
    return found


def empty(value):
    return value.strip().lower() in EMPTY


class Checker:
    def __init__(self):
        self.findings, self.sources, self.terms, self.questions = [], {}, {}, {}
        self.claims, self.prose = [], []
        self.seen_parts, self.seen_sections, self.primer_claims, self.ranks = set(), set(), 0, set()

    def add(self, check, file, line, detail):
        self.findings.append({"check": check, "file": file, "line": line, "detail": short(detail)})

    def tables(self, name, path, lines):
        """Read every table row in a section. Untabled prose is a finding."""
        rows, index = [], None
        for i, (number, line) in enumerate(lines):
            text = line.strip()
            if not text or text.startswith("<!--") or H3.match(line) or SEPARATOR.match(line):
                continue
            if not text.startswith("|"):
                self.add("untabled_prose", path, number, text)
                continue
            if i + 1 < len(lines) and SEPARATOR.match(lines[i + 1][1]):
                header = [c.lower() for c in cells(line)]
                missing = [c for c in COLUMNS[name] if c not in header]
                if missing:
                    raise InputError(f"{path}:{number}: {name} table lacks columns {missing}")
                index = {c: header.index(c) for c in COLUMNS[name]}
                continue
            if index is None:
                raise InputError(f"{path}:{number}: {name} row comes before any table header")
            row = cells(line)
            rows.append((number, {c: (row[j] if j < len(row) else "") for c, j in index.items()}))
        if index is None:
            raise InputError(f"{path}: section {name} has no table")
        return rows

    def refs(self, file, line, text, status, where):
        """Validate a reference list against a status."""
        if status not in STATUSES:
            if not status:
                self.add("missing_status", file, line, f"{where} has no status")
            else:
                self.add("invalid_status", file, line, f"{where} status {status!r} is not one of {sorted(STATUSES)}")
            status = None
        parts = [p.strip() for p in text.split(",") if p.strip()]
        if not parts:
            self.add("missing_source", file, line, f"{where} cites no source")
            return
        parsed = []
        for part in parts:
            match = REF.match(part)
            if not match:
                self.add("bad_reference", file, line, f"{where} reference {part!r} is not S<n> or a question ID")
                continue
            parsed.append((match.group(1), match.group(2).strip()))
            self.claims.append((file, line, match.group(1)))
        if status and status != "Open" and parsed and all(r.startswith("Q") for r, _ in parsed):
            self.add("question_ref_not_open", file, line, f"{where} cites only questions but is {status}")
        for ref, locator in parsed:
            valid = bool(LOCATOR.match(locator))
            if status == "Checked" and ref.startswith("S") and not valid:
                self.add("checked_without_locator", file, line, f"{where} is Checked but {ref} has no valid locator")
            elif locator and not valid:
                self.add("bad_locator", file, line, f"{where} locator {locator!r} after {ref} is not a locator")

    def read_sources(self, file, rows):
        for line, row in rows:
            sid = row["id"]
            if not re.fullmatch(r"S[0-9]+", sid):
                self.add("bad_id", file, line, f"source ID {sid!r} is not S<n>")
                continue
            if sid in self.sources:
                self.add("duplicate_id", file, line, f"source {sid} is defined twice")
            self.sources[sid] = line
            if row["kind"].lower() not in KINDS:
                self.add("source_unknown_kind", file, line, f"{sid} kind {row['kind']!r} is not one of {sorted(KINDS)}")
            if not DATE.match(row["date"].strip()):
                self.add("source_missing_date", file, line, f"{sid} date {row['date']!r} is not YYYY, YYYY-MM or YYYY-MM-DD")
            if not URL_OR_PATH.match(row["locator"].strip().strip("`")):
                self.add("source_missing_locator", file, line, f"{sid} locator {row['locator']!r} is not a URL or path")
            if any(row[c].strip() in ("", "-") for c in ("proves", "claims")):
                self.add("source_missing_scope", file, line, f"{sid} must say what it proves and only claims")

    def read_glossary(self, file, rows):
        for line, row in rows:
            term = row["term"].strip()
            if not term:
                self.add("glossary_missing_term", file, line, "row has no term")
                continue
            key = term.lower()
            if key in self.terms:
                self.add("duplicate_term", file, line, f"term {term!r} is defined twice")
            avoid = [a.strip() for a in row["avoid"].split(",") if not empty(a)]
            self.terms[key] = (file, line, term, avoid)
            if empty(row["meaning"]):
                self.add("glossary_missing_meaning", file, line, f"{term!r} has no meaning")
            else:
                self.prose.append((file, line, row["meaning"], key))
            self.refs(file, line, "" if empty(row["source"]) else row["source"], row["status"].strip(), f"term {term!r}")

    def read_questions(self, file, rows):
        for line, row in rows:
            qid = row["id"]
            if not re.fullmatch(QID, qid):
                self.add("bad_id", file, line, f"question ID {qid!r} is not Q<n> or Q-<slug>-<n>")
                continue
            if qid in self.questions:
                self.add("duplicate_id", file, line, f"question {qid} is defined twice")
            self.questions[qid] = line
            rank = row["rank"].strip()
            if not re.fullmatch(r"[1-9][0-9]*", rank) or int(rank) in self.ranks:
                self.add("question_bad_rank", file, line, f"{qid} rank {rank!r} is not a unique positive integer")
            else:
                self.ranks.add(int(rank))
            for column in ("question", "decision", "answerer"):
                if empty(row[column]):
                    self.add(f"question_missing_{column}", file, line, f"{qid} has no {column}")
            answerer = row["answerer"].strip()
            words = {w.lower() for w in re.findall(r"[A-Za-z]+", answerer)}
            if EMAIL.search(answerer) or (TWO_NAMES.match(answerer) and not words & ROLE_WORDS):
                self.add("answerer_not_role", file, line, f"{qid} answerer looks like a person, not a role")
            self.prose.append((file, line, row["question"], None))
            evidence = row["evidence"].strip()
            if empty(evidence):
                self.add("question_missing_evidence", file, line, f"{qid} names no evidence")
                continue
            kind = evidence.split(":", 1)[0].strip().lower() if ":" in evidence else ""
            if kind not in EVIDENCE_KINDS:
                self.add("question_evidence_kind", file, line, f"{qid} evidence must start with one of {list(EVIDENCE_KINDS)}")
            elif kind == "conflict" and len(set(SOURCE_ID.findall(evidence))) < 2:
                self.add("conflict_needs_two_sources", file, line, f"{qid} conflict cites fewer than two sources")
            for sid in SOURCE_ID.findall(evidence):
                self.claims.append((file, line, sid))

    def read_primer(self, file, lines):
        claims = []
        for i, (number, line) in enumerate(lines):
            if not line.strip() or line.lstrip().startswith("<!--"):
                continue
            heading = H3.match(line)
            if heading:
                self.seen_parts.add(heading.group(1).strip().lower())
                continue
            if SEPARATOR.match(line):
                if claims and claims[-1][0] == lines[i - 1][0]:
                    claims.pop()
                continue
            joined = i > 0 and lines[i - 1][1].strip() and not LIST_MARKER.match(line.lstrip())
            if line[:1] in (" ", "\t") and claims and joined and not line.lstrip().startswith("|"):
                claims[-1][1] += " " + line.strip()
                continue
            claims.append([number, line.strip()])
        self.primer_claims += len(claims)
        for number, text in claims:
            self.prose.append((file, number, text, None))
            tags = list(TAG.finditer(text))
            if not tags:
                check = "missing_status" if BARE_REF.search(text) else "uncited_claim"
                self.add(check, file, number, text)
                continue
            start = 0
            for tag in tags:
                if SENTENCE_BREAK.search(CODE_SPAN.sub("x", text[start:tag.start()]).strip()):
                    self.add("multi_sentence_claim", file, number, "each sentence needs its own tag")
                self.refs(file, number, tag.group(1), tag.group(2), "claim")
                start = tag.end()
            if re.search(r"[A-Za-z0-9]", text[start:]):
                self.add("uncited_claim", file, number, f"text after the last tag: {text[start:]}")

    def cross_checks(self):
        for file, line, ref in self.claims:
            if ref.startswith("S") and ref not in self.sources:
                self.add("unknown_source", file, line, f"{ref} is not in the source map")
            if ref.startswith("Q") and ref not in self.questions:
                self.add("unknown_question", file, line, f"{ref} is not in the question list")
        avoided = {}
        for key, (file, line, term, avoid) in self.terms.items():
            for word in avoid:
                if word.lower() in self.terms:
                    self.add("avoid_is_term", file, line, f"{term!r} avoids {word!r}, which is also a glossary term")
                avoided.setdefault(word.lower(), term)
        for file, line, text, owner in self.prose:
            plain = CODE_SPAN.sub(" ", TAG.sub(" ", text))
            for word, term in avoided.items():
                if re.search(r"(?<![\w-])" + re.escape(word) + r"(?:e?s)?(?![\w-])", plain, re.IGNORECASE):
                    self.add("avoided_synonym_used", file, line, f"uses {word!r}; the glossary term is {term!r}")
        counts = {"sources": len(self.sources), "glossary": len(self.terms),
                  "questions": len(self.questions), "primer": self.primer_claims}
        for name in ("sources", "glossary", "primer", "questions"):
            if name not in self.seen_sections:
                self.add("missing_section", None, None, f"no {name} section found")
            elif not counts[name]:
                self.add("vacuous", None, None, f"the {name} section has no entries")
        if "primer" in self.seen_sections:
            for part in PRIMER_PARTS:
                if part not in self.seen_parts:
                    self.add("missing_primer_section", None, None, f"primer has no '{part}' heading")


def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        raise InputError("usage: check_domain_notes.py FILE.md [FILE.md ...]")
    checker, parsed = Checker(), []
    for arg in argv:
        try:
            text = Path(arg).read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as error:
            raise InputError(f"{arg}: cannot read ({error.__class__.__name__})")
        parsed.append((arg, sections(text)))
    if not any(found for _, found in parsed):
        raise InputError("no Sources, Glossary, Primer or Questions section in the input")
    order = {"sources": 0, "glossary": 1, "questions": 2, "primer": 3}
    work = sorted(((order[name], file, name, lines) for file, found in parsed for name, lines in found),
                  key=lambda item: item[0])
    for _, file, name, lines in work:
        checker.seen_sections.add(name)
        if name == "primer":
            checker.read_primer(file, lines)
        else:
            getattr(checker, f"read_{name}")(file, checker.tables(name, file, lines))
    checker.cross_checks()
    findings = sorted(checker.findings, key=lambda f: (f["file"] or "", f["line"] or 0, f["check"]))
    report = {"status": "findings" if findings else "clean",
              "counts": {"sources": len(checker.sources), "terms": len(checker.terms),
                         "questions": len(checker.questions), "primer_claims": checker.primer_claims},
              "findings": findings}
    print(json.dumps(report, indent=2))
    return 1 if findings else 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except InputError as error:
        print(json.dumps({"error": str(error)}))
        sys.exit(2)
    except Exception as error:
        print(json.dumps({"error": f"unexpected {error.__class__.__name__}: {short(error)}"}))
        sys.exit(2)
