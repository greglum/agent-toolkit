# Verification and limitations

## Run the checks

From the clone's root:

```bash
sh scripts/verify.sh
```

This runs the catalog validator, installer and validator tests, and every bundled
Python and JavaScript test suite. Python 3.10+ and Node.js 18+ must be on PATH.
The diagram generator uses Node; media helpers use FFmpeg/ffprobe when exercised
against real media. Optional browser, graphics, document and provider tools are
listed in the selected skill. No provider call or dependency install is part of
this command. Tests use local fixtures and mocked boundaries where appropriate.

The optional repository pre-commit hook adds a staged secret scan and requires
Gitleaks. Keep any existing global hook policy; run these checks
manually or integrate them through the hook owner instead of replacing it blindly.

For a local snapshot secret scan with an installed Gitleaks:

```bash
gitleaks dir . --redact --no-banner
```

For existing Git history, use `gitleaks git . --redact --no-banner`.
A clean scan does not establish the absence of private names or all sensitive data.
The validator also reads a local private-name list when configured, and reports
when that check is skipped. Keep that list outside the clone.

## What the checks establish

| Evidence | Supports | Does not establish |
| --- | --- | --- |
| Catalog validator | Bundle structure, invocation metadata, portability rules, relative links | Native automatic skill selection or successful execution |
| Installer tests | Link, archive and conflict behavior on temporary directories | Every operating system or an existing user's installation |
| Bundled tool tests | The cases asserted by each suite | Every input, optional integration or real-media result |
| Supplied-skill trial | Behavior on its recorded task, model and environment | General superiority over a no-skill control |
| Source or license note | The recorded source and its stated reuse boundary | Current service terms or a license for linked assets |

Use the destination project's source, runtime and human checks for the result you intend
to deliver. These catalog checks do not measure general productivity, model quality or
production readiness.
