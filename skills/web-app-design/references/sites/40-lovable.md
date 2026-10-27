# 40. Lovable

**Observed:** 2026-10-05. **Research depth:** explicit official searches for visual edits, design systems, export, and ownership; homepage, current preview-toolbar docs, GitHub integration, and terms. Public text was accessible. No account, generation, repository connection, deployment, or transaction occurred.

## Purpose and current workflow

Lovable is a browser app-building platform for users who describe software in natural language and iterate in a preview. Its current preview toolbar replaces the former Visual edits experience. It supports selecting elements, editing text inline, drawing annotations, and pinned comments. A selected element or sketch supplies spatial context to a change request. [Official product](https://lovable.dev/), [current preview toolbar](https://docs.lovable.dev/features/preview-toolbar)

The toolbar documentation says element-selection and drawing requests consume build credits. Inline text changes have account/workspace free allowances before becoming credit-consuming usage; comments themselves are free, while sending a thread to the agent consumes credits. Old claims that all visual edits are free should not be carried into the skill. Check current allowances rather than hard-coding them. [Toolbar usage rules](https://docs.lovable.dev/features/preview-toolbar)

## Fit for product and marketing work

The platform can be useful for a bounded new prototype, marketing concept, or application whose code already lives in an approved Lovable workflow. It is an execution environment, not independent evidence that a proposed UI is well designed. The future skill still needs a user-task model, deliberate visual hierarchy, real interaction states, and browser verification.

For established repositories, the current GitHub integration has a material limitation: it exports a Lovable project into a newly created repository and starts two-way sync, but does not import an existing GitHub repository. Disconnecting and reconnecting creates another repository. This makes Lovable a poor default route for in-place design improvement to an arbitrary existing app. [GitHub integration and limitations](https://docs.lovable.dev/integrations/github)

## Ownership, data, and integration constraints

The terms say users own their customer data/projects and generated output between the parties, subject to third-party rights. They also require independent review and testing and disclaim unique or infringement-free output. Keep separate records for any sourced assets, components, or reference designs. [Current terms](https://lovable.dev/terms)

The same terms grant broad uses of customer data, describe a prospective opt-out, restrict sensitive-data submission unless an agreement permits it, and set limits on automated service access. Review the applicable account agreement and supported integration before using private source or data. Researching the resource does not authorize connecting it to a production system. Exact subscription costs, quotas, hosting limits, and installed project dependencies were not verified. [Data and service-use conditions](https://lovable.dev/terms)

## Use in the design skill

Keep this optional and within an approved environment. For an existing local app, apply the learned design principles in that app instead of migrating it to a builder. If Lovable is already the approved target, point at one concrete layout or interaction problem, preserve the current tokens, and review generated code through the established handoff.

**Analytical checks:** accessible controls, focus, preserved form input, loading/empty/error states, authorization, responsive layout, and actual network/data behavior. Attractive demo data cannot prove a live workflow. Keep generation, export, local verification, publication, and production acceptance as separate evidence. Recheck preview-toolbar behavior, credits, GitHub limitations, terms/privacy configuration, and runtime behavior before use.
