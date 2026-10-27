# Studio round trip

Read when the task uses an existing visual animation editor, such as Motion Studio.
Use the project's supported integration. Preview access does not establish source-write
access, a subscription, or permission to connect another agent or provider.

1. **Bind the target.** Record the source revision and local edits, component, trigger,
   selected animation, and full or reduced motion mode. Check installed editor/runtime
   compatibility. An animation missing from the editor may be unsupported or not yet triggered;
   do not rewrite correct application architecture just to make it discoverable.
2. **Tune a candidate.** Use the visual timeline for the uncertain timing or easing decision.
   Keep application state, layout, tokens and accessibility ownership in the application.
   A scrubbed timeline cannot establish that pending, retry, reversal or dismissal works.
3. **Apply without losing work.** Read the current source before applying. Coordinate visual
   edits and agent edits to the same target through one writer. If source changed since the
   preview, reconcile against the current version before applying the candidate. Inspect the
   saved diff, including shared tokens and any generated code; a copied prompt or pending
   preview is not a saved implementation.
4. **Reopen from source.** Reload from the saved files with pending drafts and editor overrides
   cleared. Exercise the real trigger, interruption and keyboard paths through
   [rendered review](rendered-review.md). Verify full and reduced motion outside the editor's
   preference simulation. Automatic adaptation may retain delays or staggers that conflict
   with the product's reduced-motion policy.
5. **Verify delivery.** When development instrumentation changed, run the production build
   and check that the delivered application works without the editor, companion service,
   session history or development credentials. Keep that evidence separate from preview.

Finish with the target, saved diff, fresh-session behavior and required build evidence.
Report a source-apply limitation without claiming the preview was delivered. A task that
requests only visual exploration can finish with the candidate and its unsaved status.

## Sources

Original procedure informed by Motion's [Studio announcement](https://motion.dev/magazine/introducing-motion-studio)
(Matt Perry, September 22, 2026), [editing](https://motion.dev/docs/studio-editing),
and [reduced-motion guidance](https://motion.dev/docs/studio-reduced-motion), observed
October 23, 2026. Documentation has no pinned revision or established redistribution license;
no text, code or presets copied. Source persistence, independent preference checks and a
production check are our verification requirements, not claims that the editor performs them.
Recheck when the installed integration, source writer, supported animation type or access
terms change. This reference neither installs Studio nor selects a model.
