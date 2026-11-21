# 0003: Reuse harden-skill's Dependency-Free YAML Frontmatter Parser in Catalog Checks

- Status: Accepted
- Date: 2026-11-20

## Context

scripts/check.py validates every skill bundle's YAML frontmatter while keeping the repository completely free of third-party Python dependencies.

## Decision

Import the existing dependency-free frontmatter and bundle-inspection helpers directly from skills/harden-skill/scripts/inspect_skill.py rather than duplicating parser logic or requiring PyYAML.

## Consequences

Catalog validation and harden-skill enforce identical frontmatter semantics with zero external installs, creating a deliberate internal dependency from scripts/check.py onto skills/harden-skill/scripts/inspect_skill.py.

## Code References

- `scripts/check.py:47`
