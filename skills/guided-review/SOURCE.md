# Sources and local ownership

Observed October 6, 2026, America/Los_Angeles. This is an original workflow written
for this catalog. No upstream prompt, implementation, UI asset, or skill text was
copied. Public feature ideas informed the design. A future code adaptation must
inspect the exact source revision and preserve its license and notices.

| Reference | Source and license at observation | Adopted idea | Local departure |
|---|---|---|---|
| Capy 0.4.4 | [Release](https://capy.ai/changelog/0.4.4), [review docs](https://docs.capy.ai/review); commercial platform, no reusable guide-engine license established | Brief orientation, ordered steps, before/after behavior | Local guide only; no vendor connection, GitHub submission, or inferred approval |
| CodeRabbit Change Stack | [Documentation](https://docs.coderabbit.ai/change-stack/index), [snapshot model](https://docs.coderabbit.ai/change-stack/snapshots); managed product, no core-source license established | Coherent dependency groups and revision-bound review state | Account for the complete selected diff, including excluded or unavailable artifacts |
| Graphite Code Tours | [First-party launch](https://www.graphite.com/blog/code-tours); managed product, no tour-source license established | Continuous explanation beside code | Commit links and existing diff viewer rather than a second review application |
| Plannotator | [Core prompt](https://github.com/backnotprop/plannotator/blob/1d9fe3f10fb34af0ef3ce9eed8db1c103a0b05cc/packages/core/guide-prompt.ts), app revision `1d9fe3f10fb34af0ef3ce9eed8db1c103a0b05cc`; core Apache-2.0. [Standalone skill](https://github.com/plannotator/guides/blob/da10932bcb861cc3830bcd50c2249249b2bbb538/skills/plannotator-guide/SKILL.md), revision `da10932bcb861cc3830bcd50c2249249b2bbb538`; no license found in its pinned tree | Conceptual chapters; tests beside their subject | Preserve checkout/index, trace surrounding behavior, expose coverage gaps; require no remote viewer assets |
| Vinta PR Review Canvas | [Generation format](https://github.com/vintasoftware/pr-review-canvas/blob/56fa66f4fa6da3ba9ea8e51233cdf83631d599d1/prompts/generation-format.md), revision `56fa66f4fa6da3ba9ea8e51233cdf83631d599d1`; Apache-2.0 | Hunk coverage, exact source coordinates, concrete human checkpoints | No default posting, model changes, forced folding, or persistent review-state service |
| Warp common-skills | [Guide reference](https://github.com/warpdotdev/common-skills/blob/69b4753651ab7fab518c82be087b9f1d5b966631/.agents/skills/write-pr-description/references/review-guide.md), revision `69b4753651ab7fab518c82be087b9f1d5b966631`; MIT | Specific decisions and reviewer questions; contracts before callers | Separate guide artifact from PR-authoring ownership |
| GitLab mr-guided-review | [Skill](https://gitlab.com/gitlab-org/ai/skills/-/raw/27cf0dc8a0874e77c67063611f4d359f0e28dd9f/skills/mr-guided-review/SKILL.md), revision `27cf0dc8a0874e77c67063611f4d359f0e28dd9f`; MIT | Concrete before/after orientation before critique | Complete batch guide without an artificial confirmation gate; existing reviewers own defect assessment |
| Community PR-Agent | [Prompts](https://github.com/The-PR-Agent/pr-agent/blob/99b72f62abb4c6dc7ebde98818dc535cf54d8023/pr_agent/settings/pr_reviewer_prompts.toml), revision `99b72f62abb4c6dc7ebde98818dc535cf54d8023`; MIT at this revision | Structured concerns and explicit partial coverage | No second bot, model router, numeric effort score, or provider upload |

Local `review-pr`, `global-code-review`, and repository-owned review workflows keep
their findings, verdicts, and gates. This skill owns human navigation and comprehension.
A repository's own review commands stay in that repository.

Recheck current product contracts before a vendor trial. Recheck pinned code, licenses,
notices, renderer data paths, and installed versions before importing or executing
upstream tooling. A static source assessment is not a product trial or a benchmark.
