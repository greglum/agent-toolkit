# 0025: Fetch Public External Endpoints Using an Isolated Opener Without Cookies or Auth Handlers

- Status: Accepted
- Date: 2026-11-20

## Context

skill-research/scripts/recover_x.py retrieves public X post/article JSON endpoints and must never leak local browser sessions or ambient credentials.

## Decision

Build a dedicated urllib.request.build_opener(ApiRedirects()) with no cookie jar or authentication handlers and strict same-host HTTPS redirect enforcement.

## Consequences

Public endpoint fetches stay strictly unauthenticated and cannot inadvertently attach user cookies or follow redirects to untrusted hosts.

## Code References

- `skills/skill-research/scripts/recover_x.py:56`
