# Security coverage lanes

Select lanes from the actual system map. For each applicable lane, record the invariant,
source and observation, method, disposition, and untested states. Follow requests through
all relevant layers; a browser restriction such as CORS is not server authorization.

| Lane | Trace and challenge |
|---|---|
| Identity and isolation | Session/token creation, validation, expiry, revocation, object ownership on every read/write, administrator scope, cross-tenant IDs, cache keys and response leakage |
| Inputs and outputs | Parser limits and content types, injection sources and sinks, path/URL allowlists, redirects and SSRF, output encoding, file upload/extraction bounds, Unicode/canonical forms |
| State and concurrency | Atomic quotas and reservations, replay, idempotency, double-spend, expiration races, partial writes, cleanup, retry and rollback behavior |
| Browser and public delivery | Script and markup sinks, CSP and headers on each serving path, external links, cache-sensitive responses, source maps and embedded secrets, privacy promises versus shipped assets |
| APIs and availability | Server-enforced authorization and limits, bypass origins, request/body/token caps, timeouts, concurrency and backpressure, amplification, per-project worst-case cost and kill-switch behavior |
| Infrastructure and data | IAM/OIDC conditions and resource scope, public storage/network paths, encryption, key/secret lifecycle, log redaction and retention, backups and recovery, source configuration versus observed deployment |
| CI and supply chain | Untrusted PR execution, workflow permissions, action/dependency pins and advisories, install hooks, artifact provenance/digests, release branch binding, deploy target checks, public package exposure |
| AI and external tools | Prompt and model-output trust boundaries, tool allowlists and argument validation, provider inputs, data egress, generated code execution, token/call budgets, credentials and model authority; discovery metadata and definition updates, including steering other tools; caller identity through handler to downstream principal and effective resource/operation grants; shared credentials and which runtimes can obtain them |

For scanners, record version, configuration, rules, paths, advisory observation date, and
result or failure. Use tools already owned by the project when suitable. Scanner download,
configuration changes, and uploading source are separate choices subject to task authority.
Avoid treating missing optional tools as a reason to skip source analysis.

A coverage row can be PASS only for an assertion the method can establish. For example,
source review can establish that a handler checks a bearer token; it cannot establish that
all deployed routes reach that handler. Keep that deployment claim in its own row.

For tool integrations, distinguish advertised read-only behavior from enforced backend
authority. Map credential references without reading secret values. A shared identity
increases the possible blast radius but does not alone prove an exploitable path. Check
which attacker capability can reach broader authority and which independent control stops it.


## Response contracts under failure

When an endpoint promises response privacy or fail-closed behavior, compare the relevant
identity and input states during dependency errors, timeouts and exhausted resources as
well as normal operation. Check status, body and headers; keep timing and failures outside
the handler's control explicit. Use synthetic failures in the closest existing harness.

When a fix normalizes error responses, preserve the intended detection path. Verify the
emitted event and configured metric/alarm separately from actual delivered notification.
A uniform success response must not turn an outage into an unobserved failure.
