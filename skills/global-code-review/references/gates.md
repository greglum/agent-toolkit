# Reviewing a change to a gate

Read this only when the diff touches checks, lint config, hooks, baselines,
suppressions, CI, or dependency manifests and lockfiles. A gate change can pass
review and still make the gate pass when it should fail. For each changed gate,
confirm these hold, and report each one that does not:

- **Ratchet.** A baseline is kept per rule and per file and only shrinks. A stale
  entry fails. A fix in one file never pays for a new violation in another.
- **Suppressions.** Every suppression or allowlist entry carries a reason that a
  tool checks. An unused suppression fails.
- **Advisory lane.** It may pass on findings, but fails when its tool cannot run.
  A missing tool, database, or report never reads as clean.
- **Change-scoped lane.** It says what it selected and why, marks every other lane
  not run, and never certifies the whole.
- **No vacuous pass.** A gate that matched nothing, found no engine, or checked
  zero files fails or says so. It does not pass.
- **Hooks.** A hook rewrites only bytes it can prove it wrote.
- **Dependency intake.** Apply the project's pinning and release-cooldown policy when
  one exists; do not invent a cooldown. With no policy, report the release age and
  any unresolved intake decision. Check install scripts and config-executing plugins,
  the license, and lockfile integrity hashes against the manifest.

To test a gate, find a change that should trip it and confirm it does. Reading
the config does not prove it.
