# Contributing

Start with the [workflow map](docs/workflows.md) and find the existing owner.
Describe the task, the current failure or gap, and how the change can be checked.
Prefer a focused correction to another overlapping skill.

Read [authoring](docs/authoring.md) for packaging, invocation and evaluation rules.
Keep each bundle independently installable. Preserve licenses and record sources
when adapting material. Keep credentials, personal paths, private project details
and raw agent transcripts out of changes and issue reports.

Run `sh scripts/verify.sh`. For a behavior change, also run the closest meaningful
trial against the final files and say what it proves. Distinguish static checks,
fixture results, native skill selection and real app/media checks. Report failures
and unrun checks explicitly. Preserve existing tests and the destination project's
gates. Add a regression test when it catches a credible, consequential failure
that existing checks miss; do not add tests just to increase coverage.

Use a commit message that describes the change. Keep AI session URLs and assistant
coauthor trailers out of commit metadata. AI-assisted contributions need the same
source, license and verification review as any other change.

For sensitive findings, use the repository's private vulnerability reporting
channel if enabled. Otherwise arrange a private channel with the maintainer
before sharing details. Do not publish secrets, private source or exploit details
in a public issue. No dedicated security response service or response time is promised.
