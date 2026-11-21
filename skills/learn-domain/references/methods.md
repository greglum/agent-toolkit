# Why the method looks like this

Observed 2026-11-20. Each entry restates the design rationale behind `SKILL.md`; authoritative
formats and status rules live in `SKILL.md` and `formats.md`.

## Three passes over a new subject

Koesten et al. (2021) describe making sense of unfamiliar data in three activities: inspect,
engage with the content, and place it in context. This skill follows that order: Intake and
the source map inspect what exists, the glossary and primer engage with the content, and the
questions place it in the context of the user's decisions and the experts who know the domain.

## Why authority and evidence stay visible

Separating what a source proves on its own authority from what it only claims keeps a
confident sentence in a weak source from turning into fact. Recording four evidence statuses
and surfacing conflicts as ranked questions prevents silent resolution of risk that belongs
to the decision owner.

## Structured expert interviews

Structured interviews give every expert the same basic prompts so core topics are not
skipped. The critical decision method (Klein, Calderwood & MacGregor, 1989; Hoffman,
Crandall & Shadbolt, 1998) walks an expert back through a real case they handled, surfacing
tacit rules experts rarely list in the abstract.

## Why domain knowledge is the hard part for agents

BEAVER (`arXiv:2409.02038`), BIRD (`arXiv:2305.03111`), and Spider 2.0 (`arXiv:2411.07763`)
identify external domain knowledge, join keys, and column mappings as recurring failure
points for agents on unfamiliar data.

## Why skipping experts is costly

Sambasivan et al. (CHI 2021) report that upstream data misunderstandings compound into
downstream cascades when domain experts are skipped. Ranking questions by decision impact
focuses limited expert time on what changes decisions.

## Why manual spot-checking remains

Automated structural validation in `check_domain_notes.py` cannot verify whether a cited
locator actually supports a claim or whether a source is reliable, so manual spot-checking
of high-weight `Checked` claims remains necessary.
