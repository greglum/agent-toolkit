"""Contract and planted-defect regression tests for context_inventory.py."""

from __future__ import annotations

import json
import os
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(os.environ.get("RETRO_SCRIPTS_DIR", Path(__file__).resolve().parent))
SCRIPT = SCRIPTS_DIR / "context_inventory.py"


GIT_ENV = {
    **os.environ,
    "GIT_CONFIG_GLOBAL": os.devnull,
    "GIT_CONFIG_NOSYSTEM": "1",
    "GIT_AUTHOR_NAME": "t",
    "GIT_AUTHOR_EMAIL": "t@localhost",
    "GIT_COMMITTER_NAME": "t",
    "GIT_COMMITTER_EMAIL": "t@localhost",
}


def git(repo: Path, *args: str) -> str:
    proc = subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True, text=True, env=GIT_ENV)
    return proc.stdout.strip()


def init_repo(repo: Path) -> None:
    repo.mkdir(parents=True, exist_ok=True)
    git(repo, "init", "-q", "-b", "main")


class ContextInventoryTests(unittest.TestCase):
    def run_inventory(self, repo: Path, *extra: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, "-B", str(SCRIPT), "--repo", str(repo), "--ref", "HEAD", *extra],
            capture_output=True,
            text=True,
            env=env,
            check=False,
        )

    def test_chain_reads_the_ref_and_one_file_per_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            init_repo(repo)
            (repo / "sub").mkdir()
            (repo / "AGENTS.md").write_text("r" * 100, encoding="utf-8")
            (repo / "sub/AGENTS.override.md").write_text("o" * 40, encoding="utf-8")
            (repo / "sub/AGENTS.md").write_text("a" * 900, encoding="utf-8")
            git(repo, "add", ".")
            git(repo, "commit", "-qm", "init")
            (repo / "AGENTS.md").write_text("r" * 50_000, encoding="utf-8")
            proc = self.run_inventory(repo, "--codex-max-bytes", "150")
            self.assertEqual(proc.returncode, 0, proc.stderr)
            chains = {c["dir"]: c for c in json.loads(proc.stdout)["codex_chains"]}
            self.assertEqual(chains["sub"]["files"], ["AGENTS.md", "sub/AGENTS.override.md"])
            self.assertEqual(chains["sub"]["bytes"], 100 + 2 + 40)
            self.assertEqual(chains["sub"]["status"], "near")
            self.assertEqual(chains["."]["status"], "ok")

    def test_non_positive_codex_max_bytes_is_rejected(self) -> None:
        """Planted-defect regression: 0 or negative --codex-max-bytes must fail instead of falling back or skewing %."""
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            init_repo(repo)
            (repo / "AGENTS.md").write_text("hello\n", encoding="utf-8")
            git(repo, "add", ".")
            git(repo, "commit", "-qm", "init")
            for bad in ("0", "-10"):
                proc = self.run_inventory(repo, "--codex-max-bytes", bad)
                self.assertNotEqual(proc.returncode, 0, bad)

    def test_git_check_ignore_error_is_not_swallowed(self) -> None:
        """Planted-defect regression: git check-ignore exit > 1 must fail rather than report gitignored=False."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = root / "repo"
            init_repo(repo)
            (repo / "AGENTS.md").write_text("See [missing](docs/nope.md).\n", encoding="utf-8")
            git(repo, "add", ".")
            git(repo, "commit", "-qm", "init")

            fake_bin = root / "bin"
            fake_bin.mkdir()
            real_git = subprocess.run(["which", "git"], capture_output=True, text=True, check=True).stdout.strip()
            wrapper = fake_bin / "git"
            wrapper.write_text(
                f"#!/bin/sh\n"
                f"for arg in \"$@\"; do\n"
                f"  if [ \"$arg\" = \"check-ignore\" ]; then\n"
                f"    echo 'fatal: simulated check-ignore error' >&2\n"
                f"    exit 128\n"
                f"  fi\n"
                f"done\n"
                f"exec {real_git} \"$@\"\n",
                encoding="utf-8",
            )
            wrapper.chmod(wrapper.stat().st_mode | stat.S_IXUSR)
            env = {**os.environ, "PATH": f"{fake_bin}:{os.environ.get('PATH', '/usr/bin:/bin')}"}
            proc = self.run_inventory(repo, env=env)
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("check-ignore failed", proc.stderr)

    def test_claude_chains_imports_hop_limit_missing_and_code_ignore(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            init_repo(repo)
            (repo / "docs").mkdir()
            (repo / "sub").mkdir()
            (repo / "CLAUDE.md").write_text(
                "Load @docs/h1.md and @docs/missing.md.\n"
                "Ignore `@scope/pkg` and:\n"
                "```\n@docs/not_imported.md\n```\n",
                encoding="utf-8",
            )
            (repo / "docs/h1.md").write_text("@h2.md", encoding="utf-8")
            (repo / "docs/h2.md").write_text("@h3.md", encoding="utf-8")
            (repo / "docs/h3.md").write_text("@h4.md", encoding="utf-8")
            (repo / "docs/h4.md").write_text("@h5.md", encoding="utf-8")
            (repo / "docs/h5.md").write_text("leaf", encoding="utf-8")
            (repo / "sub/CLAUDE.md").write_text("x" * 40_005, encoding="utf-8")
            git(repo, "add", ".")
            git(repo, "commit", "-qm", "init")

            proc = self.run_inventory(repo)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            data = json.loads(proc.stdout)
            chains = {c["dir"]: c for c in data["claude_chains"]}
            root_chain = chains["."]
            self.assertEqual(root_chain["reads"], "claude-md")
            self.assertEqual(
                root_chain["missing_imports"],
                [{"source": "CLAUDE.md", "target": "docs/missing.md"}],
            )
            self.assertEqual(
                root_chain["imports_past_hop_limit"],
                [{"source": "docs/h4.md", "target": "docs/h5.md"}],
            )
            sub_files = {f["path"]: f for f in chains["sub"]["files"]}
            self.assertTrue(sub_files["sub/CLAUDE.md"]["on_demand_over_char_cut"])

    def test_missing_paths_escaping_symlinks_skill_mirrors_and_ancestor_index(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            parent = Path(tmp).resolve()
            (parent / ".codegraph").mkdir()
            git(parent, "init", "-q", "-b", "main")
            git(parent, "config", "user.name", "t")
            git(parent, "config", "user.email", "t@localhost")
            (parent / "seed.txt").write_text("1\n", encoding="utf-8")
            git(parent, "add", "seed.txt")
            git(parent, "commit", "-qm", "parent")

            repo = parent / "child_repo"
            init_repo(repo)
            (repo / ".gitignore").write_text("src/ignored.py\n", encoding="utf-8")
            (repo / "src").mkdir()
            (repo / "src/real.py").write_text("x = 1\n", encoding="utf-8")
            (repo / "AGENTS.md").write_text(
                "See [broken](missing.md), [link](escape_link.md), and `src/ignored.py` and `src/gone.py`.\n",
                encoding="utf-8",
            )
            os.symlink("../../outside.md", repo / "escape_link.md")
            os.symlink("/etc/passwd", repo / "abs_link.md")
            skill_body = "---\nname: demo\ndescription: Demo skill\n---\n\nBody text here.\n"
            (repo / ".agents/skills/demo").mkdir(parents=True)
            (repo / ".claude/skills/demo").mkdir(parents=True)
            (repo / ".agents/skills/demo/SKILL.md").write_text(skill_body, encoding="utf-8")
            (repo / ".claude/skills/demo/SKILL.md").write_text(skill_body, encoding="utf-8")
            git(repo, "add", ".")
            git(repo, "commit", "-qm", "child")

            proc = self.run_inventory(repo)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            data = json.loads(proc.stdout)

            missing = {(m["target"], m["kind"]): m["gitignored"] for m in data["missing_paths"]["items"]}
            self.assertEqual(missing[("missing.md", "link")], False)
            self.assertEqual(missing[("escape_link.md", "link")], False)
            self.assertEqual(missing[("src/ignored.py", "code_span")], True)
            self.assertEqual(missing[("src/gone.py", "code_span")], False)

            self.assertEqual(data["skills"]["count"], 1)
            self.assertEqual(len(data["skills"]["mirrors"]), 1)
            self.assertEqual(data["code_index"]["in_this_checkout"], [])
            self.assertEqual(data["code_index"]["nearest_ancestor_index"]["levels_up"], 1)
            self.assertEqual(data["code_index"]["nearest_ancestor_index"]["indexes"], [".codegraph"])


if __name__ == "__main__":
    unittest.main()
