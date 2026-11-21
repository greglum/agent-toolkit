# 0029: Index Only Recipe ID, Title, and Tags in Design Reference Search

- Status: Accepted
- Date: 2026-11-20

## Context

web-app-design/scripts/design_reference.py ranks curated UI recipes against user queries, while every recipe contains shared instructions, rationale, and accessibility prose.

## Decision

Restrict search indexing strictly to each recipe's id, title, and tags, excluding shared prose fields.

## Consequences

Common accessibility or instruction vocabulary present across all recipes does not dilute or distort search relevance.

## Code References

- `skills/web-app-design/scripts/design_reference.py:135`
