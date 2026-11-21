# 0031: Anchor Relative Target Paths in deslop-ui Scanner

Status: Accepted
Date: 2026-11-20

## Context

`skills/deslop-ui/scripts/ui-tells.sh` passes user-supplied file and directory paths to `find` and `perl`. POSIX `find` has no `--` end-of-options marker, so a relative path starting with `-` is parsed as an option or expression. Perl's two-argument `open` / diamond operator also interprets leading or trailing special characters (such as `-` or `|`) in filenames magically.

## Decision

Prefix every non-absolute target path with `./` before passing it to `find`, `grep`, and `perl`.

## Consequences

- Dash-named files and directories are treated strictly as paths rather than `find` flags or magic `perl` streams.
- Absolute paths (starting with `/`) pass through unchanged.

## Code References

- `skills/deslop-ui/scripts/ui-tells.sh:16`
