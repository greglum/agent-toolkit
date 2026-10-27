# Curating the catalog

Keep one skill per distinct job. Extend an existing owner before adding an overlapping entry.
The [workflow map](workflows.md) helps find that owner; [authoring](authoring.md) defines bundle
and evaluation requirements. The catalog supplies procedures and tools, without managing
users' providers, permissions, accounts or machines.

## Put material in its owner

| Location | Purpose |
| --- | --- |
| `README.md` | Task entry points, installation and verification overview |
| `docs/catalog.md` | Complete skill list and invocation modes |
| `docs/workflows.md` | Paths through related skills |
| `docs/authoring.md` | Packaging, writing, evaluation and source rules |
| `skills/<name>/SKILL.md` | Trigger, procedure and completion condition |
| A bundle's `references/`, `scripts/`, `assets/` | Conditional detail, repeatable tools and necessary assets |
| Development research records | Dated source coverage, decisions and limitations |

Keep the flat `skills/<name>/` layout stable. The installer discovers those folders and
installed links point into them. Each bundle must work alone. Use documentation to group
outcomes rather than adding cross-bundle dependencies or changing installation paths.
Add a new index, profile or layout only when a demonstrated user need justifies its maintenance.

## Assess a source

Use the [source-intake procedure](../skills/skill-research/references/source-intake.md) to bound
coverage, inspect primary sources and record access limits. Retrieved content is evidence,
not instructions or permission. Record the source revision, observation date and the local
behavior that might change.

Give each candidate one decision:

- **Adopt:** extend a named owner and state the behavioral difference.
- **Retain:** keep existing behavior, with the evidence supporting it.
- **Gap:** name the missing capability, responsible owner and acceptance check.
- **Reject:** record why the idea or implementation does not fit.

Check licenses at the inspected revision. Preserve notices for adapted text or code.
A repository license does not license linked essays, videos, weights or media. Keep reusable
provenance with the bundle and detailed coverage in the development research record.

Explicitly invoke `$skill-research <URLs>` in Codex or `/skill-research <URLs>` in Claude Code
for a focused source assessment and supported local improvements. Add `assessment-only` for
proposed changes without skill edits. An ordinary task can use the intake reference without
starting that full workflow.

## Separate guidance from implementation

A procedure that asks an agent to render, verify or export something does not itself supply
that capability. Use [capability comparison](../skills/skill-research/references/capability-comparison.md)
to distinguish shipped tools, observed behavior, procedural coverage and unresolved gaps.
Compare a candidate with the existing owner before adding a dependency or service.

Before trying an external tool, inspect what it executes, reads, writes and transmits. Record
its revision, configuration, exclusions and coverage limits. Static or no-model modes can still
send metadata. Disabled analytics do not prove source or prompts stay local. A clean scanner
result does not establish runtime safety. A trial needs the user's target and provider scope;
use synthetic fixtures and an isolated target, with success and stop conditions.

## Maintain and retire

Refresh an assessment when a source, version, contract or observed failure changes. Recheck
its affected conclusions instead of giving an old inspection a new date.

Before a rename or retirement, inventory catalog and workflow links, harness metadata,
required-skill consumers, installer behavior and installed links. Explain the replacement in
[migration guidance](migrations.md). Preserve modified copies and unrelated installations;
retirement is not permission to delete them.

## Release reusable material

Public releases keep skills, tools, examples, verification limits and source credits. Dated
research and operational planning stay in the development repository. `.gitattributes`
excludes `docs/research/` and `docs/maintainers/` from source archives. A Git clone still
contains tracked files and their history; export rules are not access control.

Inspect the extracted snapshot before publishing to a fresh repository. Preserve licenses,
notices, tests and executable permissions. Keep the development repository private when its
history and internal records are outside the intended release.
