# 0012: Prevent FIFO TOCTOU Blocking on Input Reads and Defer Unreadable Source Validation to Manifest Reconciliation

- Status: Accepted
- Date: 2026-11-20

## Context

extract-documents/scripts/check_manifest.py hashes untrusted local paths where a path could be swapped to a FIFO between an is_file() check and open(), and corpora may include legitimately unreadable sources recorded as failed or unsupported.

## Decision

Open input files with os.O_RDONLY | os.O_NONBLOCK and verify stat.S_ISREG(os.fstat(fd).st_mode) before reading, and catch OSError while gathering source identities so unreadable files are validated against their declared failed/unsupported manifest status downstream.

## Consequences

The manifest verifier cannot be hung by a FIFO TOCTOU race and accurately reconciles corpora containing failed or unsupported unreadable inputs.

## Code References

- `skills/extract-documents/scripts/check_manifest.py:25`
- `skills/extract-documents/scripts/check_manifest.py:75`
