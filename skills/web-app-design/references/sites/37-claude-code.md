# 37. Claude Code

**Observed:** 2026-10-05. **URL resolution:** the supplied post truncated `claude.com/product/claude…`; this research inferred and verified the canonical Claude Code product page at `claude.com/product/claude-code` from the post's command-line-agent description. **Research depth:** explicit official search, product page, current overview, project-instruction documentation, and commercial terms. No account, agent session, or installation was used.

## Purpose and audience

Claude Code is Anthropic's coding agent for developers working with repositories. Its documentation describes reading source, editing files, running commands, integrating tools, and use through terminal, IDE, desktop, and web surfaces. The product page lists macOS, Linux, and Windows support and subscription options. It is an optional implementation aid, not a curated visual-reference library. [Product page](https://claude.com/product/claude-code), [official overview](https://code.claude.com/docs/en/overview)

For existing web apps, its useful role is tracing the current design system, locating the owning component, implementing an agreed visual change, and running the repository's verification tools. For new marketing or product prototypes, it can translate a grounded brief into code. The provider's capability descriptions do not establish good taste, correct accessibility, or successful rendering in a particular application.

## Concrete design workflow

The overview documents repository instructions, reusable skills, hooks, and MCP integration. Project memory guidance distinguishes persistent instructions from learned context, and explicitly notes that written instructions are context rather than enforced configuration. This supports keeping the UX/UI process in a focused skill and authoritative app conventions in repository-owned guidance. [Customization overview](https://code.claude.com/docs/en/overview), [project instruction guidance](https://code.claude.com/docs/en/memory)

A future skill should provide the same brief regardless of coding harness: user task, constraints, selected reference principles, existing tokens/primitives, required states, and browser acceptance conditions. Have the executing agent inspect the current app before changing it, preserve working flows, and show the running result. A source edit or model claim that the page is finished is insufficient evidence for focus behavior, contrast, responsive layout, or interaction success.

## Access, rights, and data

Documentation describes subscription/Console account paths and supported third-party-provider options for some surfaces. That availability is not permission to switch the user's provider, add a paid subscription, connect a repository, or transfer production data. Use the user's existing approved setup. Plan eligibility, limits, and exact prices require recheck at use time. [Access requirements](https://code.claude.com/docs/en/overview)

Anthropic's commercial terms assign customer output rights between the parties and require evaluating outputs, while explicitly distinguishing consumer offerings governed by separate terms. Do not generalize commercial privacy or ownership language to every Claude account. Generated code also needs its own dependency and asset-rights checks. A model does not grant rights to a copied reference design or third-party photograph. [Commercial terms](https://www.anthropic.com/legal/commercial-terms)

## Use in the design skill

Keep Claude Code in the execution-aids lane. The skill must work with the current harness and available browser rig, and should not prescribe a migration to Anthropic.

**Analytical checks:** automation can produce visual regressions, inaccessible semantics, misleading demo states, or mismatched tokens. Review the diff and run required app/browser checks. Recheck current documentation paths, actual harness instruction loading, plan/terms, approved data scope, and available browser capabilities whenever using this optional tool.
