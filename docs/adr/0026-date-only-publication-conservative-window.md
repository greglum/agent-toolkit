# 0026: Apply Conservative End-of-Day Upper Bound to Date-Only Publication Timestamps

- Status: Accepted
- Date: 2026-11-20

## Context

social-research/scripts/lift.py checks whether a post's observation window has elapsed, but some records supply date-only published_at strings without a time component.

## Decision

Add a +1 day buffer whenever published_at lacks a 'T' time separator before computing the observation window end.

## Consequences

Posts published late on a given date are never prematurely treated as having completed their observation window.

## Code References

- `skills/social-research/scripts/lift.py:81`
