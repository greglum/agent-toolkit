# 0024: Follow SARIF 2.1.0 Tool Component Addressing and Permit Descriptorless Rule IDs

- Status: Accepted
- Date: 2026-11-20

## Context

security-audit/scripts/sarif_review.py validates SARIF 2.1.0 files where reportingDescriptorReference semantics for toolComponent and rule descriptors are subtle.

## Decision

Default component lookups to tool.driver, resolve explicit toolComponent.index against tool.extensions (and guid across driver + extensions), and accept id-only rule references that have no matching embedded rule descriptor.

## Consequences

Valid SARIF outputs from scanners that emit extension indexes or id-only rule references are parsed faithfully without false InvalidSarif failures.

## Code References

- `skills/security-audit/scripts/sarif_review.py:101`
- `skills/security-audit/scripts/sarif_review.py:111`
