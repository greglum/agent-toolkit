# Select measures before changes

Choose obligations for the actual product, using its current measurement owners. All
eight dimensions stay visible even when an item is inapplicable. A static site still
has untrusted content, storage, links, exports, and dependency boundaries; lack of a
server is not a blanket security exemption. A CLI can justify web accessibility checks
as inapplicable while assessing its own interaction contracts.

| Dimension ID | Select measures and evidence | Preserve the limit |
| --- | --- | --- |
| `functional` | Critical journey/contract inventory, boundary and error outcomes; existing tests and observed running outcomes | Selected passing tests do not prove every feature or provider |
| `reliability` | Applicable timeout, cancellation, retry, stale response, persistence failure, recovery; controlled faults and final states | Local recovery is separate from operational uptime and SLOs |
| `security` | Enumerate inputs/outputs, authorization, parsers, storage, imports/exports, secrets, requests, dependencies; select version-qualified ASVS controls and adversarial checks | Schema validation and dependency scans do not prove all trust boundaries |
| `maintainability` | Existing language analyzers for complexity/duplication, ownership/dependency seams, hotspot distributions, changed and whole scope | Record tool/version/configuration and raw counts; file length is not complexity |
| `tests` | Risk/contract coverage, assertion strength, flakiness; bounded mutation analysis when already available and proportionate | Coverage is execution, not correctness; retain uncovered behavior and exclusions |
| `accessibility` | Applicable WCAG 2.2 A/AA criterion/state matrix, axe violations/incomplete, manual keyboard/focus, contrast, reflow, names/status | Automated scan and screenshots alone cannot establish AA conformance |
| `performance` | Representative journeys, cold/warm repeated runs, browser/device/network/build profile, resource/cost budget where relevant | Lab values, field percentiles, provider latency and cost are distinct |
| `reproducibility` | Locked inputs, setup, commands/statuses, revision plus diff, versions, observation time, artifacts | A local build does not prove deployment, bit-for-bit reproduction, or SLSA compliance |

Freeze meaningful failure cases and representative UI states: normal, empty, error,
menu/modal, long content, keyboard, and narrow screen where applicable. Count verified
checks against the applicable criterion/state matrix, not axe rules executed. Keep
assistive technology checks unrun if they were not performed.

Use product budgets or current project gates. Sonar's vendor defaults for **new code**
are not universal limits. Retain small-change exemptions and analyzer coverage gaps.
Do not substitute a keyword counter for cognitive complexity or substring matches for
an analyzer's duplication algorithm. Report unavailable tools honestly.

Record analyzer completion, test/coverage runner status, and reported findings separately.
A zero exit may mean a report was written, not that it contains no violations. Preserve
the raw output, but treat missing or failed coverage as unavailable evidence even when
the analyzer substitutes zero. For combined complexity/coverage scores, retain the raw
complexity, coverage kind and measured scope. Review hotspots and duplicate candidates
for responsibility and behavior before splitting or extracting; a lower score alone
does not establish a better design. Preserve required project thresholds.

For mutation tools, record killed, timeout, survived, no-coverage, invalid, and ignored
counts plus selected source and exclusions. Stryker's full score is detected/valid,
where detected includes killed and timeout; covered-only scores have a different
denominator. Record how the selected tool classifies compile failures and timeouts; tools
can count them differently. Compare scores only with matching classifications and denominators.
Label a manual fault probe as a probe, not a tool-produced mutation score.

For performance, preserve each run and median/range. Google's good field Core Web
Vitals thresholds are LCP <=2.5 s, INP <=200 ms, CLS <=0.1 at the 75th percentile,
segmented mobile/desktop. Lighthouse without interaction does not measure INP; TBT
is a proxy. Missing field data stays unknown if field performance is in frozen scope.

## Primary sources and provenance

These links support measurement choices, not the local scoring formula. Observed
2026-10-20. No upstream prose or code was copied. Recheck when the selected standard,
tool/version/configuration, product requirements, or trust boundaries change.

- [ISO/IEC 25010:2023 official abstract](https://www.iso.org/standard/78176.html): product quality reference model with nine characteristics. This skill's eight dimensions are a local profile; the paid full standard was not reviewed.
- [SonarQube Server 2026.1 metric definitions](https://docs.sonarsource.com/sonarqube-server/2026.1/user-guide/code-metrics/metrics-definition) and [quality gates](https://docs.sonarsource.com/sonarqube-server/quality-standards-administration/managing-quality-gates/introduction-to-quality-gates): analyzer definitions, scope, defaults/exemptions.
- [OWASP ASVS](https://owasp.org/projects/asvs) and [Input Validation Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html): select versioned controls and evaluate trust boundaries. ASVS 5.0.0 overview was reviewed; its detailed release directory was unavailable. Fetch actual selected requirements before claiming verification.
- [Stryker metrics](https://stryker-mutator.io/docs/mutation-testing-elements/mutant-states-and-metrics/) and [equivalent mutants](https://stryker-mutator.io/docs/mutation-testing-elements/equivalent-mutants/): denominators and interpretation.
- [WCAG 2.2](https://www.w3.org/TR/WCAG22/) and [axe-core](https://github.com/dequelabs/axe-core): complete processes, human evaluation, incomplete checks.
- [Google Web Vitals](https://web.dev/articles/vitals): field thresholds and lab/field distinction.
- [Google SRE: Implementing SLOs](https://sre.google/workbook/implementing-slos/): product-specific reliability targets.
- [SLSA v1.2 tracks](https://slsa.dev/spec/v1.2/tracks) and [provenance](https://slsa.dev/spec/v1.2/provenance): builder/process/inputs and separate reproducibility concerns.

The observations above are dated research, not a current application assessment.
Mutable documentation links have no verified immutable revision here. Refresh the
narrow source needed when applying version-specific controls. No source endorsement,
conformance, security certification, or production acceptance follows from this skill.

Analyzer completion and metric interpretation were rechecked October 26, 2026, against
[crapper CLI](https://github.com/unclebob/crapper/blob/6fd92c4c9bcc56efb64a2f8743d5a2993bcfd42d/src/crapper/cli.py),
[dryer CLI](https://github.com/unclebob/dryer/blob/66ff6d21a42c04afcad89c78a80066176d1294b0/src/dryer/cli.py),
and the Stryker references above. These examples establish reporting differences, not
a recommendation to install those tools or import their thresholds.
