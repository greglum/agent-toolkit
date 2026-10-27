# Method sources

Reviewed 2026-10-20. Independently written for Claude Code and Codex; no upstream text,
code, prompts, schemas, or agents are bundled. Recheck source and license when upstream
changes or a real run demonstrates a gap. These references describe methods, not authority.

- [Cloudflare security-audit-skill](https://github.com/cloudflare/security-audit-skill/tree/c1c8a8c1471069fb0e188eeaff69b8e8db6564a8),
  MIT. Use its whole-system mapping, independent candidate verification, and explicit coverage
  limits. Keep findings tied to original evidence. Departures: no fixed worker topology,
  mandatory scanner installation, special output framework, or universal sandbox recipe.
  Use available isolation and record its actual limits.
- [Trail of Bits skills](https://github.com/trailofbits/skills/tree/5c99c03fb8a9ea568432ecbcba5d86e9f4ac2bf0),
  root CC BY-SA 4.0. Study false-positive challenges, bounded variant searches, and matching
  remediation to the actual vulnerable path. Summarize ideas independently; do not copy
  share-alike prose into this catalog. Existing local review and variant-search owners remain.
- [OpenAI security best practices](https://github.com/openai/skills/tree/49f948faa9258a0c61caceaf225e179651397431/skills/.curated/security-best-practices)
  and [security threat model](https://github.com/openai/skills/tree/49f948faa9258a0c61caceaf225e179651397431/skills/.curated/security-threat-model),
  each Apache-2.0 at the skill's license file. Use source-grounded assets, attacker capabilities,
  trust boundaries, and prioritized remediation. Departures: discover stack and repository
  gates instead of bundling broad framework advice or imposing an extra approval interview.
- [Sentry security review](https://github.com/getsentry/skills/blob/f57ada2d0b640406ea7e25b11d636c530e77c58b/skills/security-review/SKILL.md),
  root Apache-2.0, with separate reference notices. Look beyond the initial reporting scope
  for effective upstream guards. Departure: authenticated attackers remain in scope; no
  reference text or OWASP notices are imported.
