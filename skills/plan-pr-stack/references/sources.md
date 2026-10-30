# Sources and departures

Observed October 30, 2026 UTC. Original implementation and prose. No upstream code,
prompt, template, media or benchmark dataset copied.

- GitHub Lever, [landing-plan and planner](https://github.com/github/lever/tree/f859d0aa2be96981157ee0480655c84877e3cd98/skills/landing-plan),
  MIT. Inspected dependency/overlap/wave construction and output. Informed the distinct
  planning outcome. This implementation requires explicit overlap ordering and keeps unknowns,
  full repository identities and unresolved external dependencies visible. It omits automatic
  PR mutation, readiness verdicts and illustrative timing estimates.
- Edward Z. Yang and ghstack contributors,
  [README, structure and design constraints](https://github.com/ezyang/ghstack/blob/68d401f6f6e7afef25df79666e787f442a0b41b0/README.md),
  MIT verified at the same pin. Its synthetic base/head/orig branches show why generic branch
  matching cannot recover every stacking system. Supply explicit dependencies for those cases.
  No ghstack code was executed or copied.
- Git Town contributors, [stacked changes](https://www.git-town.com/stacked-changes),
  living page observed October 30, 2026, sections on unnecessary stacking and keeping stacks
  current. Independently supports keeping unrelated changes independent and refreshing after
  parent changes. Repository [license](https://github.com/git-town/git-town/blob/d0cc7951b01e74ba36ba057c0f31fd5eee6e83b8/LICENSE)
  is MIT; exact documentation blob retrieval was unavailable. Living-page reuse rights were
  not separately established. Original synthesis only, with no copied text.
- GitHub, [REST pull request files](https://docs.github.com/en/rest/pulls/pulls#list-pull-requests-files),
  living documentation observed October 30, 2026, pull-request files endpoint limit.
  Its 3,000-file cap means pagination alone cannot establish complete coverage. Compare file
  response records with `changed_files` before adding both paths of a rename. Documentation
  reuse rights not assessed; original collection instructions only.

Recheck on identity/API/schema changes, a new stacking system, or a trial that finds an
incorrect edge or omitted dependency. Source existence establishes capability, not faster
delivery, automatic skill selection or a general improvement in agent behavior.
