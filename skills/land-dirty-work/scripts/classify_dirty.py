"""Classification, clustering, mtime staleness, and content fingerprinting for dirty paths."""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import os
from pathlib import Path

from scan_git import run_git, run_git_bytes

CREDENTIAL_BASENAMES = {
    ".npmrc",
    ".netrc",
    ".envrc",
    ".pypirc",
    ".pgpass",
    "auth.json",
    ".credentials.json",
}
CREDENTIAL_DIR_PARTS = {"secrets", "credentials"}
CREDENTIAL_PREFIXES = ("id_rsa", "id_ed25519", "id_ecdsa")
CREDENTIAL_SUFFIXES = (".pem", ".key", ".p12", ".pfx", ".tfvars", ".kdbx", ".jks")
SECRET_DATA_SUFFIXES = {"", ".json", ".yml", ".yaml", ".toml", ".txt", ".ini", ".cfg", ".env"}
TEMPLATE_SUFFIXES = (".example", ".sample", ".template")
SCRATCH_SUFFIXES = {".log", ".tmp", ".orig", ".rej", ".xcbkptlist"}
SCRATCH_BASENAMES = {"contents.xcworkspacedata", ".ds_store"}
HASH_FULL_BYTES_LIMIT = 2_097_152
SAMPLE_EDGE_BYTES = 65_536
IGNORED_CRED_PATHSPECS = (
    ":(icase,glob)**/.env",
    ":(icase,glob)**/.env.*",
    ":(icase,glob)**/*.pem",
    ":(icase,glob)**/*.key",
    ":(icase,glob)**/*.p12",
    ":(icase,glob)**/*.pfx",
    ":(icase,glob)**/*.tfvars",
    ":(icase,glob)**/*.kdbx",
    ":(icase,glob)**/*.jks",
    ":(icase,glob)**/.npmrc",
    ":(icase,glob)**/.netrc",
    ":(icase,glob)**/.envrc",
    ":(icase,glob)**/.pypirc",
    ":(icase,glob)**/.pgpass",
    ":(icase,glob)**/auth.json",
    ":(icase,glob)**/.credentials.json",
    ":(icase,glob)**/id_rsa*",
    ":(icase,glob)**/id_ed25519*",
    ":(icase,glob)**/id_ecdsa*",
    ":(icase,glob)**/*secret*",
    ":(icase,glob)**/*credential*",
    ":(icase,glob)**/secrets/**",
    ":(icase,glob)**/credentials/**",
)


def is_credential_candidate(rel_path: str) -> bool:
    """Return True when a dirty path looks like local secrets, env config, or key material."""
    p = Path(rel_path)
    if CREDENTIAL_DIR_PARTS.intersection({part.lower() for part in p.parts[:-1]}):
        return True
    base = p.name.lower()
    if base == ".env" or (base.startswith(".env.") and not base.endswith(TEMPLATE_SUFFIXES)):
        return True
    if base in CREDENTIAL_BASENAMES or base.startswith(CREDENTIAL_PREFIXES):
        return True
    if base.endswith(CREDENTIAL_SUFFIXES):
        return True
    if ("secret" in base or "credential" in base) and Path(base).suffix in SECRET_DATA_SUFFIXES:
        return True
    return False


def find_ignored_credentials(worktree_path: Path) -> list[str]:
    """List gitignored credential files using targeted pathspecs (capped at 100 entries)."""
    rc, ign_raw, _ = run_git(
        worktree_path,
        "ls-files",
        "--others",
        "--ignored",
        "--exclude-standard",
        "-z",
        "--",
        *IGNORED_CRED_PATHSPECS,
    )
    if rc != 0 or not ign_raw:
        return []
    return sorted({p for p in ign_raw.split("\0") if p and is_credential_candidate(p)})[:100]


def is_likely_scratch_path(rel_path: str) -> bool:
    """Return True for log/temp/patch leftovers or IDE workspace/macOS scratch artifacts."""
    p = Path(rel_path)
    return p.suffix.lower() in SCRATCH_SUFFIXES or p.name.lower() in SCRATCH_BASENAMES


def find_symlink_paths(worktree_path: Path, paths: list[str]) -> list[str]:
    """Return sorted dirty paths that are filesystem symlinks."""
    return [rel for rel in sorted(set(paths)) if (worktree_path / rel).is_symlink()]


def classify_binary_and_oversized(
    worktree_path: Path, untracked: list[str], threshold: int
) -> tuple[list[str], bool]:
    """Detect oversized untracked files and NUL-byte binaries (capped NUL read past 200 files)."""
    flagged: list[str] = []
    capped = len(untracked) > 200
    for idx, rel_path in enumerate(untracked):
        target = worktree_path / rel_path
        if not target.is_file() or target.is_symlink():
            continue
        try:
            if target.stat().st_size >= threshold:
                flagged.append(rel_path)
                continue
            if idx < 200:
                with target.open("rb") as handle:
                    if b"\x00" in handle.read(8192):
                        flagged.append(rel_path)
        except OSError:
            flagged.append(rel_path)
    return flagged, capped


def compute_mtime_and_clusters(
    worktree_path: Path, paths: list[str], now_ts: float, git_dir: Path | None = None
) -> tuple[dict[str, list[str]], dict[str, int], str | None, float | None, float | None]:
    """Group dirty paths by top-level directory and compute newest dirty modification age."""
    clusters: dict[str, list[str]] = {}
    newest: float | None = None
    missing_dirty = False
    for rel in sorted(set(paths)):
        parts = Path(rel).parts
        key = parts[0] if len(parts) > 1 else "(root)"
        clusters.setdefault(key, []).append(rel)
        target = worktree_path / rel
        try:
            mtime = target.lstat().st_mtime
            if newest is None or mtime > newest:
                newest = mtime
        except OSError:
            missing_dirty = True
            continue
    if paths and git_dir is not None and (newest is None or missing_dirty):
        index_file = git_dir / "index"
        try:
            idx_mtime = index_file.lstat().st_mtime
            if newest is None or idx_mtime > newest:
                newest = idx_mtime
        except OSError:
            pass
    cluster_counts = {k: len(v) for k, v in clusters.items()}
    if newest is None:
        return clusters, cluster_counts, None, None, None
    iso = datetime.fromtimestamp(newest, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    delta_sec = max(0.0, now_ts - newest)
    return clusters, cluster_counts, iso, round(delta_sec / 86400.0, 2), round(delta_sec / 60.0, 1)


def _hash_untracked_entry(hasher: "hashlib._Hash", target: Path, rel: str) -> None:
    """Feed symlink target or file bytes into the dirty fingerprint hash."""
    if target.is_symlink():
        try:
            link_val = os.readlink(target)
        except OSError:
            link_val = "unreadable"
        hasher.update(f"{rel}\0symlink:{link_val}\0".encode("utf-8", errors="replace"))
        return
    if not target.is_file():
        hasher.update(f"{rel}\0missing\0".encode("utf-8", errors="replace"))
        return
    try:
        st = target.stat()
        file_hasher = hashlib.sha256()
        if st.st_size <= HASH_FULL_BYTES_LIMIT:
            with target.open("rb") as handle:
                while chunk := handle.read(65_536):
                    file_hasher.update(chunk)
            hasher.update(f"{rel}\0{st.st_size}\0{file_hasher.hexdigest()}\0".encode("utf-8", errors="replace"))
        else:
            with target.open("rb") as handle:
                file_hasher.update(handle.read(SAMPLE_EDGE_BYTES))
                if st.st_size > SAMPLE_EDGE_BYTES:
                    handle.seek(max(0, st.st_size - SAMPLE_EDGE_BYTES))
                    file_hasher.update(handle.read(SAMPLE_EDGE_BYTES))
            hasher.update(
                f"{rel}\0{st.st_size}\0{st.st_mtime_ns}\0{file_hasher.hexdigest()}\0".encode(
                    "utf-8", errors="replace"
                )
            )
    except OSError:
        hasher.update(f"{rel}\0err\0".encode("utf-8", errors="replace"))


def compute_dirty_fingerprint(
    worktree_path: Path, head_sha: str | None, status_bytes: bytes, untracked: list[str]
) -> tuple[str | None, list[str]]:
    """Build a content hash over HEAD, status, staged/unstaged binary diffs, and untracked contents."""
    hasher = hashlib.sha256()
    hasher.update((head_sha or "").encode("utf-8"))
    hasher.update(b"\0")
    hasher.update(status_bytes)
    hasher.update(b"\0")
    diff_errors: list[str] = []
    rc_staged, staged_diff, staged_err = run_git_bytes(
        worktree_path, "diff", "--no-ext-diff", "--no-textconv", "--full-index", "--binary", "--cached"
    )
    if rc_staged != 0:
        diff_errors.append(f"git diff --cached failed in {worktree_path}: {staged_err or 'exit ' + str(rc_staged)}")
    rc_unstaged, unstaged_diff, unstaged_err = run_git_bytes(
        worktree_path, "diff", "--no-ext-diff", "--no-textconv", "--full-index", "--binary"
    )
    if rc_unstaged != 0:
        diff_errors.append(f"git diff failed in {worktree_path}: {unstaged_err or 'exit ' + str(rc_unstaged)}")
    if diff_errors:
        return None, diff_errors
    hasher.update(staged_diff)
    hasher.update(b"\0")
    hasher.update(unstaged_diff)
    hasher.update(b"\0")
    for rel in sorted(untracked):
        _hash_untracked_entry(hasher, worktree_path / rel, rel)
    return hasher.hexdigest()[:16], []


def cap_list(items: list, max_paths: int) -> list:
    """Truncate list items to max_paths when positive."""
    return items[:max_paths] if max_paths > 0 else items


def count_omitted(parsed: dict, bin_big: list[str], max_paths: int) -> int:
    """Count total entries dropped by --max-paths truncation across dirty categories."""
    if max_paths <= 0:
        return 0
    buckets = (
        parsed["staged"],
        parsed["unstaged"],
        parsed["untracked"],
        parsed["renamed"],
        parsed["deleted"],
        bin_big,
    )
    return sum(max(0, len(lst) - max_paths) for lst in buckets)
