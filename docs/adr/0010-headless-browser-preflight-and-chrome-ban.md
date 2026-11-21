# 0010: Preflight Explicit Headless Browsers Independently per Bundle and Reject Installed Google Chrome

- Status: Accepted
- Date: 2026-11-20

## Context

Browser verification scripts in diagram-design, fit-surface, and web-app-design must remain independently installable per skill bundle. Launching installed Google Chrome on macOS grows the persistent keychain on every launch (Chromium issue 577651758), which can stall TLS and gh.

## Decision

Duplicate the small CHROME_PATH preflight check inside each skill's browser verification script, resolve symlinks/aliases and reject installed Google Chrome paths before creating output evidence directories or launching Playwright, and require Playwright's bundled Chromium, Chrome for Testing, or chrome-headless-shell.

## Consequences

Each skill installs cleanly without cross-skill imports, invalid browser configurations fail fast before touching output directories, and macOS keychains are protected from Chromium issue 577651758.

## Code References

- `skills/diagram-design/scripts/check-browser.mjs:11`
- `skills/diagram-design/scripts/check-browser.mjs:22`
- `skills/fit-surface/scripts/check-browser.mjs:10`
- `skills/fit-surface/scripts/check-browser.mjs:21`
- `skills/web-app-design/scripts/check-variant-browser.mjs:12`
