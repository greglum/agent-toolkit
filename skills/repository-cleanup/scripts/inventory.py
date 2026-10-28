#!/usr/bin/env python3
"""Read local Git evidence. Never fetch, reset, prune or delete resources."""
import argparse
import ast
import datetime
import json
import os
from pathlib import Path
import subprocess


class Inventory:
    def __init__(self, repo):
        self.repo = repo
        self.errors = []

    def git(self, *args, repo=None, require_no_diagnostics=False):
        target = str(repo or self.repo)
        result = subprocess.run(
            ["git", "-C", target, *args], capture_output=True,
            env={**os.environ, "GIT_OPTIONAL_LOCKS": "0"},
        )
        if result.returncode or (require_no_diagnostics and result.stderr):
            self.errors.append({"repo": target, "args": list(args),
                                "status": result.returncode,
                                "error": os.fsdecode(result.stderr).strip()})
            return None
        return os.fsdecode(result.stdout)

    def object_storage(self, common):
        directory = self.git("rev-parse", "--path-format=absolute", "--git-path", "objects")
        # Native Git resolves relative, chained and environment alternates. Diagnostics can
        # report an unavailable lender even when count-objects exits zero.
        counts = self.git("-c", "core.quotePath=true", "count-objects", "-v",
                          require_no_diagnostics=True)
        alternates = [] if counts is not None else None
        for line in (counts or "").splitlines():
            if line.startswith("alternate: "):
                value = line.removeprefix("alternate: ")
                # With quotePath=true, Git quotes non-ASCII bytes as C octal escapes.
                path = os.fsdecode(ast.literal_eval(value).encode("latin-1")) if value.startswith('"') else value
                alternates.append(path)
        return {
            "directory": directory.strip() if directory is not None else None,
            "common_alternates_file": str(Path(common) / "objects/info/alternates"),
            "effective_alternates_file": str(Path(directory.strip()) / "info/alternates") if directory is not None else None,
            "alternate_object_directories": alternates,
            "environment_alternates_present": bool(os.environ.get("GIT_ALTERNATE_OBJECT_DIRECTORIES")),
            "environment_object_directory_present": bool(os.environ.get("GIT_OBJECT_DIRECTORY")),
            "outside_borrowers": "unknown: lender inspection cannot enumerate outside borrowers",
        }

    def ancestry(self, head, base):
        value = self.git("rev-list", "--left-right", "--count", f"{base}...{head}")
        if value is None:
            return None
        behind, ahead = map(int, value.split())
        return {"behind": behind, "ahead": ahead, "tip_reachable_from_base": ahead == 0}

    def worktrees(self, base):
        raw = self.git("worktree", "list", "--porcelain", "-z")
        trees, current = [], {}
        for field in (raw or "").split("\0"):
            if not field:
                if current:
                    trees.append(current)
                    current = {}
                continue
            key, _, value = field.partition(" ")
            current[key] = value if value else True
        if current:
            trees.append(current)
        for tree in trees:
            path = tree["worktree"]
            tree["activity"] = "unknown: inspect processes and harness ownership separately"
            if tree.get("bare"):
                continue
            if not Path(path).is_dir():
                tree["inspection"] = "unavailable: missing path"
                self.errors.append({"repo": path, "error": "missing worktree path"})
                continue
            status = self.git("status", "--porcelain=v1", "-z", "--untracked-files=all", repo=path)
            fields = iter((status or "").split("\0"))
            changes = []
            for field in fields:
                if not field:
                    continue
                change = {"status": field[:2], "path": field[3:]}
                if "R" in field[:2] or "C" in field[:2]:
                    change["source"] = next(fields, "")
                changes.append(change)
            tree["changes"] = changes if status is not None else None
            ignored = self.git("ls-files", "--others", "--ignored", "--exclude-standard",
                               "--directory", "--no-empty-directory", "-z", repo=path)
            tree["ignored_paths"] = ignored.rstrip("\0").split("\0") if ignored else ([] if ignored is not None else None)
            modules = self.git("submodule", "status", repo=path)
            tree["submodules"] = modules.splitlines() if modules is not None else None
            if tree.get("HEAD"):
                tree["ancestry"] = self.ancestry(tree["HEAD"], base)
        return trees

    def collect(self, base_ref):
        common = self.git("rev-parse", "--path-format=absolute", "--git-common-dir")
        if common is None:
            return {"errors": self.errors, "complete": False}
        storage = self.object_storage(common.strip())
        base = self.git("rev-parse", "--verify", f"{base_ref}^{{commit}}")
        if base is None:
            return {"object_storage": storage, "errors": self.errors, "complete": False}
        base = base.strip()
        raw = self.git("for-each-ref", "--format=%(refname)%00%(objectname)%00%(upstream)%00%(symref)",
                       "refs/heads", "refs/remotes")
        refs = []
        for line in (raw or "").splitlines():
            name, sha, upstream, symbolic = line.split("\0")
            refs.append({"ref": name, "sha": sha, "upstream": upstream or None,
                         "symbolic": symbolic or None,
                         "ancestry": self.ancestry(sha, base) if not symbolic else None})
        remotes = (self.git("remote") or "").splitlines()
        stash_ref = self.git("for-each-ref", "--format=%(refname)", "refs/stash")
        stashes = self.git("reflog", "show", "--format=%gd%x00%H%x00%gs", "refs/stash") if stash_ref else ""
        recovery = self.git("for-each-ref", "--format=%(refname)%00%(objectname)")
        result = {
            "observed_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "repo": str(Path(self.repo).resolve()), "common_dir": common.strip(),
            "base_ref": base_ref, "base_sha": base, "object_storage": storage,
            "remote_evidence": "cached only; reconcile live refs, PRs and protections separately",
            "remotes": remotes, "refs": refs, "worktrees": self.worktrees(base),
            "stashes": [dict(zip(("ref", "sha", "subject"), line.split("\0", 2)))
                        for line in (stashes or "").splitlines()],
            "other_refs": [dict(zip(("ref", "sha"), line.split("\0")))
                           for line in (recovery or "").splitlines()
                           if not line.startswith(("refs/heads/", "refs/remotes/", "refs/tags/"))],
        }
        result["errors"] = self.errors
        result["complete"] = not self.errors
        return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True)
    parser.add_argument("--base", required=True, help="Verified base ref or full commit SHA")
    args = parser.parse_args()
    result = Inventory(args.repo).collect(args.base)
    print(json.dumps(result, indent=2, ensure_ascii=True))
    return 0 if result["complete"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
