"""Exercise the watcher CLI with a local GitHub executable, never a network call."""

import copy
import fcntl
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).with_name("watch_pr.py")
META = {"url": "https://github.com/example/project/pull/7", "state": "OPEN",
        "headRefOid": "a" * 40, "baseRefOid": "b" * 40, "baseRefName": "main",
        "isDraft": False, "mergeStateStatus": "CLEAN", "reviewDecision": "APPROVED",
        "autoMergeRequest": None}
THREAD = {"id": "thread1", "isResolved": False, "isOutdated": False,
          "path": "app.py", "line": 2, "comments": {"totalCount": 1, "nodes": [
              {"id": "reply1", "updatedAt": "2026-10-25T01:00:00Z", "url": "https://example.com/reply"}]}}


def sample(meta=None, checks=None, thread_pages=None):
    meta = meta or META
    pages = thread_pages or [[THREAD]]
    connections = []
    for index, page in enumerate(pages):
        connections.append({"data": {"repository": {"pullRequest": {"reviewThreads": {
            "nodes": page, "pageInfo": {"hasNextPage": index < len(pages) - 1,
                                      "endCursor": str(index)}}}}}})
    comment = {"id": 1, "html_url": "https://example.com/comment", "body": "private comment"}
    review = {"id": 2, "html_url": "https://example.com/review", "body": "private review",
              "state": "CHANGES_REQUESTED", "commit_id": "c" * 40}
    return [{"data": meta}, {"data": [] if checks is None else checks},
            {"data": [[comment], [dict(comment, id=3)]]}, {"data": [[review]]},
            {"data": [[dict(comment, id=4)]]}, {"data": connections}, {"data": meta}]


class WatcherCLI(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.fixture = self.root / "responses.json"
        self.counter = self.root / "counter"
        self.state = self.root / "state"
        executable = self.root / "gh"
        executable.write_text(f"#!{sys.executable}\n" + '''import json, os, pathlib, sys
args = sys.argv[1:]
# Reject every unexpected or mutating CLI command before reading a fixture.
assert args[:2] in (["pr", "view"], ["pr", "checks"]) or args[0] == "api"
if args[0] == "api":
    assert args[1] == "graphql" or args[1].startswith("repos/example/project/")
    assert "--paginate" in args and "--slurp" in args
if args[1] == "graphql":
    assert "mutation" not in " ".join(args)
assert os.environ["GH_HOST"] == "github.com"
path = pathlib.Path(os.environ["RESPONSES"])
counter = pathlib.Path(os.environ["COUNTER"])
i = int(counter.read_text()) if counter.exists() else 0
row = json.loads(path.read_text())[i]
counter.write_text(str(i + 1))
print(json.dumps(row["data"]) if "data" in row else "", end="")
sys.stderr.write(row.get("stderr", ""))
sys.exit(row.get("code", 0))
''')
        executable.chmod(0o700)
        self.env = dict(os.environ, PATH=str(self.root) + os.pathsep + os.environ["PATH"],
                        RESPONSES=str(self.fixture), COUNTER=str(self.counter))

    def run_cli(self, responses, *extra):
        self.fixture.write_text(json.dumps(responses))
        self.counter.unlink(missing_ok=True)
        return subprocess.run([sys.executable, str(SCRIPT), "7", "--repo", "example/project",
                               "--state-dir", str(self.state), *extra],
                              env=self.env, capture_output=True, text=True, timeout=15)

    def test_resume_detects_base_and_paginated_old_findings_without_storing_bodies(self):
        first = self.run_cli(sample(), "--once")
        self.assertEqual(first.returncode, 0, first.stderr)
        event = json.loads(first.stdout)
        self.assertEqual(event["unresolved_threads"], 1)
        self.assertEqual(event["readiness"], "not assessed")
        newer = dict(META, baseRefOid="d" * 40)
        late_thread = copy.deepcopy(THREAD)
        late_thread["id"] = "thread101"
        second = self.run_cli(sample(newer, thread_pages=[[THREAD], [late_thread]]), "--once")
        self.assertEqual(second.returncode, 0, second.stderr)
        event = json.loads(second.stdout)
        self.assertEqual(event["changed"], ["pr", "threads"])
        self.assertEqual(event["unresolved_threads"], 2)
        stored = next(self.state.glob("*.json")).read_text()
        self.assertNotIn("private comment", stored)
        self.assertNotIn("private review", stored)
        state = json.loads(stored)["snapshot"]
        self.assertEqual(len(state["comments"]), 2)
        self.assertEqual(state["reviews"][0]["state"], "CHANGES_REQUESTED")

    def test_failed_or_racing_collection_preserves_previous_success(self):
        self.assertEqual(self.run_cli(sample(), "--once").returncode, 0)
        path = next(self.state.glob("*.json"))
        saved = path.read_bytes()
        cases = [[{"code": 1, "stderr": "HTTP 403"}],
                 sample()[:-1] + [{"data": dict(META, headRefOid="e" * 40)}],
                 sample()[:-2] + [{"data": [{"errors": [{"message": "partial"}]}]}]]
        for responses in cases:
            result = self.run_cli(responses, "--once")
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertEqual(result.stdout, "")
            self.assertEqual(path.read_bytes(), saved)

    def test_no_checks_is_unknown_and_auto_merge_metadata_is_minimal(self):
        meta = dict(META, autoMergeRequest={"enabledAt": "2026-10-25", "mergeMethod": "SQUASH",
                                           "authorEmail": "private", "commitBody": "secret text"})
        responses = sample(meta)
        responses[1] = {"code": 1, "stderr": "no checks reported on the 'feature' branch\n"}
        result = self.run_cli(responses, "--once")
        self.assertEqual(result.returncode, 0, result.stderr)
        event = json.loads(result.stdout)
        self.assertEqual(event["check_count"], 0)
        self.assertEqual(event["readiness"], "not assessed")
        saved = next(self.state.glob("*.json")).read_text()
        self.assertNotIn("secret text", saved)
        self.assertNotIn("authorEmail", saved)

    def test_duplicate_owner_and_corrupt_state_do_not_poll(self):
        self.state.mkdir()
        stem = hashlib.sha256(b"example/project#7").hexdigest()
        with (self.state / (stem + ".lock")).open("a") as handle:
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
            result = self.run_cli([], "--once")
            self.assertEqual(result.returncode, 2)
            self.assertFalse(self.counter.exists())
        path = self.state / (stem + ".json")
        path.write_text("{broken")
        result = self.run_cli([], "--once")
        self.assertEqual(result.returncode, 1)
        self.assertEqual(path.read_text(), "{broken")
        self.assertFalse(self.counter.exists())

    def test_old_inline_edit_wakes_a_resumed_poll_without_once(self):
        self.assertEqual(self.run_cli(sample(), "--once").returncode, 0)
        changed = sample()
        changed[4]["data"][0][0]["body"] = "revised old finding"
        result = self.run_cli(sample() + changed, "--timeout", "10", "--interval", "5")
        self.assertEqual(result.returncode, 0, result.stderr)
        events = [json.loads(line) for line in result.stdout.splitlines()]
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["changed"], ["inline_comments"])
        path = next(self.state.glob("*.json"))
        corrupt = json.loads(path.read_text())
        corrupt["snapshot"]["pr"]["state"] = "corrupted"
        path.write_text(json.dumps(corrupt))
        saved = path.read_bytes()
        result = self.run_cli([], "--once")
        self.assertEqual(result.returncode, 1)
        self.assertFalse(self.counter.exists())
        self.assertEqual(path.read_bytes(), saved)

    def test_bounded_wait_and_terminal_states_are_not_readiness(self):
        waiting = self.run_cli(sample(), "--timeout", "1", "--interval", "5")
        self.assertEqual(waiting.returncode, 3, waiting.stderr)
        for state in ("MERGED", "CLOSED"):
            result = self.run_cli(sample(dict(META, state=state)))
            self.assertEqual(result.returncode, 0, result.stderr)
            event = json.loads(result.stdout)
            self.assertEqual(event["state"], state)
            self.assertEqual(event["readiness"], "not assessed")


if __name__ == "__main__":
    unittest.main()
