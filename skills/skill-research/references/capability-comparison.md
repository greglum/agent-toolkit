# Compare delivered capability

Read before deciding whether a tool or skill's useful behavior is already covered locally.
The unit of comparison is the result a user can obtain, not matching words in skill files.

## Build the matrix

Trace each consequential source capability to its implementation, dependencies and delivered
artifact. Inspect the nearest local owner and the code or assets it actually ships. Separate
source observation from execution evidence on both sides. Use one row per distinct outcome:

| User outcome | Source mechanism and evidence | Local owner and runnable entrypoint | Local status | Consequence |
| --- | --- | --- | --- | --- |
| What the user can do or receive | Pinned code/docs; runtime exercised or not | Path and command, or no implementation | Implemented, partial, instructions only, absent, or unverified | Adopt, retain, gap, or reject with reason |

For a substantial tool, cover its primary creation path, meaningful interactions, exports,
validation and failure behavior. Include supporting machinery that makes the outcome repeatable,
such as schemas, bundled assets and deterministic transforms. A worked example or a promise
that the model could write code is not a reusable implementation. A checker pass proves only
the boundaries that checker exercises.

## Decide what to own

Judge functional coverage separately from procedural quality, visual quality, reliability and
comparative speed. An untested implementation can establish that a feature exists while leaving
its quality unverified. A lack of comparative benchmarks does not erase an observable feature
gap. Report a source's functional advantage plainly when local evidence supports it.

Retain a capability only at the scope the local implementation covers. A local skill that says
to verify a feature does not provide that feature. Record a partial overlap as separate covered
and missing outcomes. Keep the most consequential gaps prominent even when small prose edits
are adopted in the same round.

For each useful gap, name the existing owner, the missing machinery, the smallest complete
implementation, its dependencies and maintenance cost, and observable acceptance checks. Compare
extending our tooling, adapting licensed material, and using an external tool against the user's
stated goals. Prefer our owned implementation when that is the requested outcome; do not turn
an installation concern into a reason to ignore the capability.

Within authorized local harvest, implement bounded, justified skill/tooling improvements in the
owner and exercise the complete path. Larger work or work needing new authority stays a gap
with a concrete next action and the exact missing decision, access or dependency. Assessment-only
stays read-only. Installation, providers, billing and publication keep their existing boundaries.

**Ready:** every consequential outcome has a source/local evidence row, a disposition and an
applied improvement or actionable gap. The final report states functional advantages and the
remaining distance to parity without implying quality or runtime proof that was not measured.
