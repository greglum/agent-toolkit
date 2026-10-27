# Grouping flags, message format, and doc audits

Load from step 2 when a grouping or message flag is passed, when writing commit messages,
or when changed Markdown meets an available documentation-audit skill.

## Flags

Honor `--message` as the single-commit override and `--no-split` as single-commit mode.
`--split` requires analysis, not artificial groups when only one purpose exists. Preserve
the supplied message override.

## Message format

Use the repository's message convention. Otherwise use `type(scope): subject`, with an
imperative, lowercase subject under 72 characters, no final period, and an optional body
explaining why. Write for a `git log` reader who never saw the session: say what the code now
does differently, and keep review rounds, finding numbers, and session labels out.

## Documentation audits

When changed Markdown and repository documentation-audit skills are both present, briefly
recommend the fitting available audit. This advice does not add an approval stop. Run it
only when requested or required by repository gates, and honor its actual mode and output
contract. Do not assume report paths or a follow-up implementation skill exist.
