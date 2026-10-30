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


Reviewed October 29, 2026:

- [Jim Manico's Grim Prompter](https://github.com/jmanico/grim-prompter/tree/076ec0d32c9eec0e09bfdee22b57121f49b26022),
  MIT. Inspected the runbook, control evidence definitions, change reviewer and tool credential
  boundaries. Original synthesis adds control evidence states, a bounded baseline-review
  procedure and effective tool-authority tracing. No upstream text, code or schema is bundled.
  Departures: keep the existing audit owner and authority gates; no fixed architecture catalog,
  cumulative JSON contract, installation, or claim of automated analysis or validation.
- [OWASP Threat Modeling Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Threat_Modeling_Cheat_Sheet.html),
  System Modeling, Response and Mitigations, and Review and Validation; and
  [OWASP practical threat modeling](https://devguide.owasp.org/en/04-design/01-threat-modeling/07-practical-threat-modeling/),
  assumptions, ongoing refinement and incremental scope. Independently support the method,
  not the prompt library's accuracy. Living pages, no copied text.
- [MCP tools specification, 2025-11-25](https://modelcontextprotocol.io/specification/2025-11-25/server/tools)
  and [Invariant Labs' April 1, 2025 tool-poisoning experiments](https://invariantlabs.ai/blog/mcp-security-notification-tool-poisoning-attacks).
  Discovery metadata and updates are a separate input surface; the experiments demonstrate
  steering in the tested client, not a vulnerability in every current client. No payloads copied.

Recheck on source, protocol, credential design or baseline-format changes, or when a bounded
trial exposes a missing step. These are procedural refinements; blind/control evaluation
and native automatic selection remain untested.


An October 29, 2026 repository trial reproduced response-status disclosure during dependency
errors and verified a bounded correction with synthetic failures. It also exposed archived
probes in broad implementation search results. The resulting original refinements cover
failure-state response contracts, preserved detection, and current versus carried evidence.
No project code, private findings or payloads are bundled. This supplied-skill run has no
no-skill control and does not establish comparative benefit. Recheck when a real audit or
blind comparison contradicts these procedures.
