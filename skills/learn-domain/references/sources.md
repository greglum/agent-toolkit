# Adopted ideas and departures

Observed 2026-11-20. This file restates ideas only. No upstream code, prompt, template or
text was copied, and no upstream code was run. Commit SHAs and repository licenses below were
verified against GitHub on 2026-11-20.

## Skills and plugins

- GoogleCloudPlatform/data-agent-kit-plugin, curate-context,
  <https://github.com/GoogleCloudPlatform/data-agent-kit-plugin>, revision
  `716f429da2671acbb1faaa3944948ff9e86c5cd4`, Apache-2.0. Idea: items the sources do not
  support go to a list of open questions instead of into the context. Departure: here they
  stay in the primer as `Open` claims tied to a ranked question, and a checker enforces the
  tie.
- anthropics/knowledge-work-plugins, data-context-extractor,
  <https://github.com/anthropics/knowledge-work-plugins>, revision
  `0e0fcacddcc892eb92a1b7873ff9d68159c47571`, Apache-2.0. Idea: a short fixed set of analyst
  interview questions. Departure: the standard prompts here are adapted to the domain and
  ranked with evidence-driven questions by decision impact.
- mattpocock/skills, domain-modeling, <https://github.com/mattpocock/skills>, revision
  `abeeaf95660ba9e8b7c753eb38f441ca707a8823`, MIT. Idea: choose one term per concept and
  list the synonyms to avoid. Departure: applied to an outside subject rather than a
  codebase, and the checker flags an avoided synonym wherever it appears; codebase terms and
  ADRs stay with each project's own codebase documentation.
- openai/plugins, gather-business-context and create-data-context,
  <https://github.com/openai/plugins>, revision `981b02c0c44058b595f3b4180002c3ae3c806d40`,
  no SPDX license (marked proprietary in research). Idea only, no text: rank sources, keep
  conflicts visible with a named person to resolve them, keep an evidence register, and label
  coverage. Departure: evidence lives in per-claim status tags, and conflicts become ranked
  questions that name the decision they unblock.

Research found no skill that builds a cited primer or turns data anomalies into an expert
question list, and found formats but no checker. That is a search result as of the
observation date, not a proof.

## Papers and methods

- Koesten et al. (2021), "Talking datasets: Understanding data sensemaking behaviours",
  *International Journal of Human-Computer Studies*, DOI
  `10.1016/j.ijhcs.2020.102562` (<https://doi.org/10.1016/j.ijhcs.2020.102562>): inspect,
  engage, place in context.
- Klein, Calderwood & MacGregor (1989), "Critical decision method for eliciting knowledge",
  *IEEE Transactions on Systems, Man, and Cybernetics*, 19(3), 462-472, DOI
  `10.1109/21.31053` (<https://doi.org/10.1109/21.31053>); and Hoffman, Crandall & Shadbolt
  (1998), *Human Factors*, 40(2), 254-276, DOI `10.1518/001872098779480442`
  (<https://doi.org/10.1518/001872098779480442>): critical decision method for expert
  interviews.
- BEAVER (`https://arxiv.org/abs/2409.02038`, 2024); BIRD (`https://arxiv.org/abs/2305.03111`,
  2023); Spider 2.0 (`https://arxiv.org/abs/2411.07763`, 2024): external knowledge, join keys
  and column mappings are hard for agents on unfamiliar data.
- Sambasivan et al. (2021), *"Everyone wants to do the model work, not the data work": Data
  Cascades in High-Stakes AI*, *CHI 2021*, DOI `10.1145/3411764.3445518`
  (<https://doi.org/10.1145/3411764.3445518>): data cascades, including skipped domain
  experts.

Recheck trigger: a new revision of these sources, or a real project where the checker passes
notes that still misled the user.
