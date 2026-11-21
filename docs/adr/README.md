# Architecture Decision Records

This directory records non-obvious architectural, security, privacy, compatibility, and licensing decisions for the skills catalog and its verification tools.

## When to add an ADR instead of a code comment

Repository checks (`scripts/check_comments.py`) enforce a zero-new-comment ratchet across tracked code files. Keep code self-explanatory and move lasting rationale here:

- Add an ADR (`docs/adr/NNNN-<slug>.md`) when a change introduces or relies on a non-obvious design tradeoff, security or privacy boundary, external tool or platform constraint, compatibility floor, statistical guard, or third-party licensing rule that future maintainers must preserve.
- Use module and function docstrings in Python, clear symbol names, and `SKILL.md` or `references/` files for usage instructions and local contracts.
- Keep inline directives (`# noqa`, `# type: ignore`, `# shellcheck`, `// eslint-disable`) in source files only when required by a linter or type checker.
- Never add explanatory prose comments to `.py`, `.sh`, `.js`, `.ts`, `.mjs`, `.cjs`, or `.githooks/pre-commit` files.

## Index

1. [0001: Use One Offline Verification Entrypoint and Isolate Git Hook Environment Variables](./0001-hermetic-verification-and-hook-isolation.md)
2. [0002: Enforce Public Export Snapshot Boundaries via Isolated Bare Clones and Preflight Checks](./0002-public-export-snapshot-boundaries.md)
3. [0003: Reuse harden-skill's Dependency-Free YAML Frontmatter Parser in Catalog Checks](./0003-zero-dependency-shared-frontmatter-parser.md)
4. [0004: Maintain Python 3.10 Standard-Library Compatibility Across Catalog Scripts](./0004-python-310-compatibility-floor.md)
5. [0005: Preserve Installed Copies, Deduplicate Symlinked Harness Roots, and Support Direct Single-Harness Installs](./0005-installer-symlink-safety-and-harness-layout.md)
6. [0006: Use Ordered Regex Heuristics as Verifiable Leads and Ordered Deny-by-Default Redaction](./0006-ponytail-heuristic-cues-and-redaction-boundaries.md)
7. [0007: Deduplicate Claude Events Globally and Parse Codex Completed User Items Without Double-Counting](./0007-session-transcript-dedup-and-parsing-invariants.md)
8. [0008: Probe Blocked Directories via scandir() Because macOS Sandboxes Permit stat()](./0008-macos-sandbox-directory-listing-probe.md)
9. [0009: Keep deslop/tells.sh Limited to Short Pattern Keywords and Track Third-Party Attribution](./0009-deslop-third-party-licensing-boundary.md)
10. [0010: Preflight Explicit Headless Browsers Independently per Bundle and Reject Installed Google Chrome](./0010-headless-browser-preflight-and-chrome-ban.md)
11. [0011: Restore Keyboard Focus After DOM Rebuilds and Record Hidden Shadow/Frame Omissions Before Render Filtering](./0011-ui-accessibility-and-dom-omission-invariants.md)
12. [0012: Prevent FIFO TOCTOU Blocking on Input Reads and Defer Unreadable Source Validation to Manifest Reconciliation](./0012-toctou-safe-file-opening-and-manifest-reconciliation.md)
13. [0013: Model Evidence Graph Edges as Consumer-to-Dependency and Surface Non-Observed Paths as Leads](./0013-evidence-graph-semantics-and-scope.md)
14. [0014: Emit Structured JSON and Exit 2 on Unexpected Errors Across Audit CLIs](./0014-structured-json-exit-code-2-on-unexpected-error.md)
15. [0015: Use Canonical Text UDF Comparisons, Finite-Number Guards, and 15-Digit Float Thresholds in Data Profiling](./0015-map-data-source-canonical-comparison-and-numeric-safety.md)
16. [0016: Anonymize Data-Like Headers Under --no-values and Always Clean Up Temporary SQLite Staging Files](./0016-map-data-source-no-values-privacy-and-staging.md)
17. [0017: Keep Raw GitHub Diagnostics and Comment Bodies Out of PR Watcher State and Pin GH_HOST](./0017-monitor-pr-security-and-state-invariants.md)
18. [0018: Select Actual Decoded Video Frames with setpts/select Rather Than fps Resampling](./0018-motion-film-decoded-frame-selection.md)
19. [0019: Delegate Git Alternates Resolution to count-objects and Refuse Untrusted Clean Filters or Submodule Recursion](./0019-git-cleanup-safe-read-only-inventory.md)
20. [0020: Require Independent Human Review for Confirmed Retro Evidence and Restrict Marker Advancement to Tracked Runs](./0020-retro-history-confidence-and-marker-invariants.md)
21. [0021: Document External Agent Harness Context Limits, Precedence Rules, and Mirror/Ancestor Index Semantics](./0021-harness-context-budget-constants-and-rules.md)
22. [0022: Hold Friction Markers on Blocked Stores and Cap Sessions Oldest-First for Forward Progress](./0022-retro-friction-windowing-and-gap-invariants.md)
23. [0023: Strip Git Trailing Tab on Spaced Diff Headers and Blame Smallest Files First Within Line Budget](./0023-git-diff-and-blame-budget-invariants.md)
24. [0024: Follow SARIF 2.1.0 Tool Component Addressing and Permit Descriptorless Rule IDs](./0024-sarif-component-and-rule-resolution.md)
25. [0025: Fetch Public External Endpoints Using an Isolated Opener Without Cookies or Auth Handlers](./0025-unauthenticated-public-fetch-opener.md)
26. [0026: Apply Conservative End-of-Day Upper Bound to Date-Only Publication Timestamps](./0026-date-only-publication-conservative-window.md)
27. [0027: Preserve Unrounded Calibration Thresholds, Strict Upper Bounds, and Nanosecond Duration Rounding](./0027-telemetry-threshold-calibration-and-precision.md)
28. [0028: Use Exclusive File and Directory Creation So Prior Evidence Is Never Silently Overwritten](./0028-exclusive-evidence-output-creation.md)
29. [0029: Index Only Recipe ID, Title, and Tags in Design Reference Search](./0029-design-reference-search-field-scope.md)
30. [0030: Escape JSON Script Breakouts and Render HTML Templates in a Single Regex Pass](./0030-html-template-xss-and-single-pass-rendering.md)
31. [0031: Anchor Relative Target Paths in deslop-ui Scanner](./0031-deslop-ui-dash-path-anchoring.md)
