# Handoff contract

`onboard-data` sends each child the same kinds of input and expects the same kinds of result.
A child that returns less is recorded as incomplete in the index. Missing input is stated, not
guessed.

## What onboard-data sends

To `learn-domain`, each pass:

- Scope: the goals and decisions from Intake, and which sections to run in this pass.
- Sources: the document locations, and in the second pass the data dictionary paths.
- Artifact folder: the `domain/` subfolder of the onboarding folder.
- Privacy limits: fields, people or records that must not appear in notes.
- Prior open questions: none in the first pass. In the second pass, every open question from
  `map-data-source` with its ID, its `data:` evidence and the location it came from.

To `map-data-source`, for each data location:

- Scope: the folder or SQLite file, and confirmation that access is read-only.
- Artifact folder: the `data/` subfolder, with one subfolder per location when there are several.
- Privacy limits: as above. When any limit applies, the tool runs with `--no-values`.
- Glossary path: optional from the first domain pass (omit when First domain pass did not run), so column meanings use the domain's terms.
- Prior open questions: domain questions that the data might answer.

## What onboard-data expects back

From each child:

- Artifact paths: every file written, relative to the onboarding folder.
- Checker results: the checker name, its exit code, and any failures listed. The first
  learn-domain pass runs no checker; its results arrive with the second pass.
- Rerun command: the exact command the child used to run its checker, so the index can repeat
  it verbatim.
- Open questions: each with its evidence (a document citation, a query and its result, or a
  file and column), and who could answer it.
- Steps not run: any section skipped, and why.

`learn-domain` also returns the source map, glossary and, in the second pass, the primer and its
ranked SME questions. `map-data-source` also returns, per location, the grain and key proof,
scored joins, the dictionary with counts by meaning status (documented, sme-confirmed, inferred,
unknown) and the claims file.

## Checks on receipt

- Each listed path exists and sits under the onboarding folder.
- Each exit code that the pass should produce is stated. A missing one counts as not run.
- Each open question carries evidence. A question without evidence is kept but marked so.
- No returned text breaks a privacy limit. If one does, stop and tell the user before writing
  the index.
