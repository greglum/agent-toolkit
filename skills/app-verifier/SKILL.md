---
name: app-verifier
description: >-
  Set up a way for agents to run and check this app: create or update a project-owned skill
  or doc that records how to launch it, reach each feature without real credentials, and see
  the end state proving it works. Use to record how to verify features, or refresh that record
  after code changes. Not for auditing or fixing UI.
compatibility: Needs a shell to run the repository's own setup and dev commands, and browser automation or a headless browser to drive the running app. Without a browser, launch and HTTP checks can still be recorded, and rendered end states are marked unverified. Installs nothing beyond the repository's documented setup.
---

# App verifier

Leave the repository a skill or doc that lets any agent launch the app, reach each feature
without real credentials or live data, and see the end state that proves it works. Every step
in it ran successfully in this session or is marked unverified.

Writing that record is the deliverable. Run no deploys, read or enter no real credentials,
and touch no live data. Install dependencies only when the repository's documented setup does
and the request covers setup. A missing fixture harness is product code: propose the smallest
one the stack supports, and build it only when the user asks for one.

## Procedure

1. **Choose the mode and the home.** Search the repository's agent instructions, README,
   contributor docs, and skills for a record that already launches the app or lists features
   to check. If one exists, this is a maintenance run: go to step 6. Otherwise place the
   record where the project keeps its skills, else in its developer docs, else beside the
   README, and follow its naming, frontmatter, and index conventions. Never name it plain
   `verify` unless the user asks: some harnesses run a project skill with that name before
   every commit. Done when the mode and the destination path are chosen, and each cites the
   convention it follows or is listed as a choice.

2. **Launch the app.** Find the documented dev command in package scripts, task runners, the
   README, and CI, with its prerequisites: config sync, environment files, generated assets,
   and work a pre-script does that a direct invocation skips. Run it, and read the address
   from the server's log; a configured port is only a request. Never drive or stop a server
   you did not start. Done when the app answers at the address it reported, from commands
   run in this session, or the failing command and its error are recorded.

3. **Find credential-free entry points.** An app with no sign-in needs only its routes.
   Otherwise look for fixture harness entries, mock service layers, story or specimen pages,
   seeded local databases, demo modes, and no-login routes; end-to-end tests show which work
   and which stable handles they use. Note the data states (empty, dense, error) each entry
   reaches through its scenarios or seeds. A sign-in or "configuration required" page is a
   setup state: record the step that produces it, enter nothing, and never read or print
   secret values. Done when each entry point has loaded and shown real content, or is
   recorded as blocked with the missing prerequisite.

4. **Drive each feature.** List user-facing features from routes, navigation, harness
   entries, and docs, including views a route sweep misses: in-page tabs, dialogs, drawers,
   and expanded rows. Cover the features the request names, else the primary journeys, and
   list the rest as unmapped. For each, load its entry point, act as a user does through
   stable handles (role and accessible name, label, route path), and observe the end state
   that proves it works. Skip actions that send messages or reach external services. Done
   when every listed feature has an entry point, actions, and an observed end state, or an
   unverified or blocked mark with the reason.

5. **Write and prove the record.** Follow [record shape](references/record-shape.md). Record
   commands and actions exactly as they worked, plus every trap you met: the actual port,
   setup and sign-in pages, in-page tabs, slow first loads. Give each entry its source paths
   and the commit it was verified at. Then, from a fresh shell, follow the written launch and
   one feature entry exactly as written, and stop every process you started. Done when that
   cold run passes, nothing you started is still running, and every recorded step either ran
   this session or is marked unverified.

6. **Maintain.** Check each entry's source paths for changes since its recorded commit, and
   look for routes, harness entries, and tabs added since then. Re-run the launch and every
   changed or new entry, then update its actions, end state, and commit. When an entry
   fails, relaunch and retry it once. A second failure through real user actions is either
   drift in the record, which you fix, or a product regression, which you report and never
   write into the record as expected behavior. Done when every entry is unchanged,
   re-verified at the current commit, or reported with its failure, and nothing you started
   is still running.

7. **Hand off.** Report the record's path, the mode, and the features verified, unverified,
   blocked (with prerequisites), and unmapped. List regressions found and the choices you
   made where the repository was silent, least confident first. Tell the user that
   `fit-surface`, `web-app-design`, and `deslop-ui` look for exactly this harness, port, and
   view list before judging a rendered UI. Done when the report accounts for every listed
   feature and every regression.

The record at its destination, proven by step 5 or re-run in step 6, marks the run
finished.
