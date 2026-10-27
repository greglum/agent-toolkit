# 38. Cursor

**Observed:** 2026-10-05. **Research depth:** explicit official search for UI design, rules, and privacy; homepage, Design Mode, rule documentation, security page, pricing, and terms. Public pages were reachable. No editor installation, account, agent run, or data transfer was performed.

## Purpose and audience

Cursor is an AI coding environment for developers. For UX/UI work, its most relevant current feature is Design Mode in the Agents Window browser. The documentation describes selecting elements, selecting related elements together, drawing annotations, and giving voice instructions while an agent edits the underlying code. The selected context includes element identity, computed styles, component/prop information where available, and a screenshot. [Official product](https://cursor.com/), [Design Mode](https://cursor.com/docs/agent/design-mode)

This tightens the connection between a visible problem and its source. A team can point to a crowded toolbar, compare two card styles, or annotate a misaligned region. These are concrete implementation workflows. They do not prove that the agent understands the user's task, chooses a coherent art direction, or preserves all hidden states.

## Working apps versus marketing

Cursor is useful for existing applications because the design iteration can stay near current source and a running preview. Marketing work can use the same loop for typography, composition, and interactive effects. It contributes no independent curated catalog of good patterns; pair it with a small set of relevant references and a task-specific brief.

The skill should turn visual feedback into a precise change: explain which relationship is wrong, which component owns it, and what happens on other viewports and states. A screenshot can expose spacing but cannot verify keyboard operation, screen-reader meaning, reduced motion, form preservation, or authorization-sensitive behavior. Those need separate runtime checks.

## Instructions, access, and reuse

Cursor documents project rules in `.cursor/rules` with `.mdc` metadata, user/team rules, and plain `AGENTS.md` in the root or nested directories. It notes that some rules apply to Agent and do not affect every editor feature. Verify that the chosen execution path actually loads the relevant guidance; do not create redundant always-loaded instructions just to document one design workflow. [Rules documentation](https://cursor.com/docs/rules)

The security page says Privacy Mode is available to free and Pro users and disables training on their data when enabled, with provider protections. This is a vendor commitment, not proof of a particular user's active settings or an assertion that code never leaves the computer. Inspect the applicable configuration and agreement before sending private app content. [Security and Privacy Mode](https://cursor.com/security)

Free/paid plan descriptions and service terms are public, but exact quotas, pricing, feature availability, and generated-output obligations should be checked when needed. The software service is not a blanket license for assets or code found through it. Do not change provider, buy a plan, connect private repositories, or migrate the project as an implied step of improving UI. [Pricing](https://cursor.com/pricing), [terms](https://cursor.com/terms-of-service)

## Use in the design skill

Treat Cursor as an optional visual execution aid in the user's approved environment. Supply current tokens, allowed components, meaningful states, and acceptance conditions before iteration.

**Analytical checks:** concurrent visual edits can conflict; selected element context can omit neighboring behavior; generated CSS can accumulate exceptions. Review ownership and the resulting diff, then verify the running app. Recheck current Design Mode behavior, rules loading, privacy settings, plan eligibility, and browser acceptance whenever using it.
