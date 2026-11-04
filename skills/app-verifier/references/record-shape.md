# Record shape

Write for an agent that has never run this app and reads the record cold, in the middle of
another task. Keep commands and handles literal. Leave implementation detail to the code;
name only user paths, stable handles, required state, commands, and observable results.

## Header

- **As a skill:** frontmatter with the `name` chosen in step 1 and a `description` that
  names the app, its surface, and the triggers: run the app, check a UI change, reach a
  feature without signing in. A skill without frontmatter is never selected.
- **As a doc:** a heading that the repository's docs index or agent instructions link to.
  Add that link when the index exists.

## Sections, in this order

1. **Launch.** Prerequisites, including setup steps the dev command runs for you and which
   direct invocations skip them. The command. The readiness signal, such as the log line that
   prints the address. How to read the actual port. How to stop the server. Whether two
   instances can run side by side.
2. **Credential-free access.** Each fixture harness, seeded entry, or no-login route, with
   its URL pattern, its scenario or seed parameters, and the data states it reaches. Say what
   still needs credentials, without naming any secret value.
3. **Traps.** Each trap you met, with its symptom and how to tell it from a defect: the port
   moved, a setup or configuration page, a sign-in page, in-page tabs a route sweep misses,
   a slow first compile, a browser that needs a flag in containers.
4. **Features.** One entry per feature, in the format below. Past about ten features, use an
   index plus one file per feature in a sibling folder.
5. **Cleanup.** Stop what the run started. Reset any fixture data an action changed. Keep
   screenshots and other evidence at a path the record names.

## Feature entry

```markdown
### <Feature name>

- Entry: <URL or harness entry, with scenario or seed>
- Views: <in-page tabs, dialogs, drawers, expanded rows this feature owns>
- Ready: <observable fixture content or enabled control that makes these actions safe to start>
- Actions:
  1. <user-level action with its stable handle, such as: choose the "Save" button>
  2. <next action>
- End state: <what a user can see or check that proves the feature works>
- Sources: <paths whose change should trigger a re-run>
- Status: verified <YYYY-MM-DD> at <short commit> | unverified: <reason> | blocked: <prerequisite and route attempted>
```

Add "with uncommitted changes" to a verified status when the feature's source paths were
dirty, so maintenance does not trust the commit alone.

If the entry records accessibility evidence, attach each claim to its surface/state, method,
observation, and remaining checks. A fixture launch or tool calibration does not verify the
product. Keep accessibility assessment with the UI audit; this record supplies reproducible
entry points and observations.

An end state is something a user could check: "the row reads Saved and still does after a
reload", not "the page loaded" or "no console errors". A status message alone is weak proof
when a second view of the changed value exists.

Readiness is distinct from the server listening and from the final feature result. Record
the actual visible content or actionable control and how the browser waits for it. Prefer
the test runner's retrying assertions over fixed delays or global network silence; polling
and streaming can continue after a view is usable. Capture application console errors and
failed requests during the journey, with their origin and effect; an empty console alone
does not prove success.

This refinement was checked against Anthropic's
[webapp-testing](https://github.com/anthropics/skills/blob/dbd4588f9e1033efb41dad4bef2f7947c8993d44/skills/webapp-testing/SKILL.md)
(Apache-2.0) and Playwright's
[v1.63.0 readiness guidance](https://github.com/microsoft/playwright/blob/v1.63.0/docs/src/api/params.md),
observed October 25, 2026. We retain observable readiness rather than the upstream skill's
mandatory `networkidle` wait. Recheck against the destination's installed runner version.

## Reuse a native recipe

When the project already records a host-native run or verification recipe, keep that as the
launch owner. Review its commands, side effects and installed-host requirements before reuse.
For a new record, exercise documented setup and one feature under this task's authority.
For a refresh, rerun only unverified or invalidated steps. Fill missing safe fixture entries,
visible readiness, feature outcomes, source identities and cleanup ownership
in the existing record; create no parallel schema merely to wrap it. Keep commands and stable
handles readable by both Claude Code and Codex, and label host-only steps with a fallback or
an explicit unavailable check. A generated recipe is a lead until its actual steps run.

Do not invoke a generator that commits, installs dependencies or reaches external targets
without the authority those actions require. Reusing a native command does not grant those
actions or authorize renaming a project skill to `verify`.

This refinement uses Anthropic's [native run and verification documentation](https://code.claude.com/docs/en/skills#run-and-verify-your-app),
observed November 4, 2026, sections Run and verify your app and Run your checks before each
commit. Living-page reuse rights were not established; original guidance only. Native feature
availability is host/version-specific and was not trialed here. Recheck the installed host and
project recipe before reuse; this branch adds no launcher or automatic recipe conversion.
