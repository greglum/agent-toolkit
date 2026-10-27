# Read a SARIF evidence ledger

Use this when a requested audit includes existing local SARIF scanner reports. This reader
starts no scanner, installs nothing and fetches no URI. It does not confirm vulnerabilities,
apply suppressions or fixes, deduplicate records, or certify a repository as secure.

Run from this skill's folder, using the actual local input path:

```sh
python3 scripts/sarif_review.py report.sarif > review-ledger.json
```

Keep the producer's exit code before displaying or filtering the ledger. Output JSON goes
to stdout. Exit 0 means the supported input was interpreted without an operational or
coverage gap. Findings can still exist. Exit 2 means invalid input, incomplete execution
metadata, failed scan execution, or an unsupported interpretation feature. For a valid but
incomplete input, findings remain in the output with diagnostics. Invalid input produces
an error object and no partial success claim.

The input is one UTF-8 local SARIF 2.1.0 file up to 20 MiB. Duplicate JSON keys and nonfinite
numeric constants, exponent overflow and non-integer invocation exit codes are rejected. Validation covers consumed structure and identity consistency;
this is not a full SARIF JSON-schema validator. Preserve the original input. The output records
its SHA-256, input path, run and result indexes so each candidate can be checked there.

## Interpret the output

- `complete` describes this interpretation and reported scanner execution, not security.
- `execution` is `succeeded`, `failed` or `unknown`. Missing invocation metadata and absent
  results remain gaps. Invocation notifications are retained; error notifications make the
  ledger incomplete. A process exit code alone cannot establish scanner success.
- Every result stays separate, including repeated rules, tools and locations. Driver and
  extension rule identities are kept distinct. No source or artifact URI is opened.
- Levels come from the explicit result, the referenced rule's default, or SARIF's default;
  non-failure records retain their kind and have level `none`.
- Baseline state, suppressions and fingerprints remain evidence. Suppressed records are
  not dropped. All candidate records start as `needs-validation`.
- Indexed artifact locations retain their URI base metadata. This tool does not resolve
  paths against the filesystem or treat a source location as proof of reachability.

Return to the audit's source and reproduction method for confirmation, severity, control
checks and remediation. A scanner's `error` level is not an independently established
vulnerability severity. Inputs and outputs can contain sensitive source text or paths;
keep them in the task's approved private evidence location.

## Explicit limits

Invocation rule and notification configuration overrides, inherited notification descriptor
levels, external-property storage and message-string lookup by ID are not implemented. Those cases set `complete: false`; an inherited severity affected
by possible overrides is `null`, never guessed. Direct message text or Markdown is retained
as untrusted data. Code flows, fixes, attachments and source snippets remain in the original
report, reached through the recorded result index; this ledger is not a lossless converter.
An empty `runs` array is incomplete. Null results mark that run incomplete while retaining
other runs. An index disambiguates duplicate rule IDs; hierarchical result IDs are preserved.
A successful invocation with an explicit empty results
array is interpretable, but does not establish application safety or complete scanner coverage.

## Source and checks

Original standard-library implementation. No Trail of Bits code or prose was copied.
Research leads were inspected at
[Trail of Bits 196a907](https://github.com/trailofbits/skills/blob/196a9073ab10d35bacf111f945e02c00b2c6883a/plugins/static-analysis/skills/sarif-parsing/resources/sarif_helpers.py)
(root CC BY-SA 4.0, observed October 26, 2026). Semantics were checked against
[OASIS SARIF 2.1.0 plus Errata 01](https://docs.oasis-open.org/sarif/sarif/v2.1.0/errata01/os/sarif-v2.1.0-errata01-os-complete.html),
sections 3.4.5, 3.20.14, 3.27.6-10 and 3.54.2. Recheck when adding another SARIF version or
an unsupported feature. The bundled example is synthetic.

```sh
python3 -m unittest discover -s scripts -p 'test_sarif_review.py'
```
