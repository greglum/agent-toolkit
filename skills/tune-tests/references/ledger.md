# Test value rubric and ledger

## Score

When the repository defines a test value score, use its dimensions, scale, and threshold
exactly, and cite where it lives. Otherwise rate each dimension none, low, medium, or high:

| Dimension | Question |
|---|---|
| Regression likelihood | Is the failure specified, observed before, or likely in ordinary change? |
| Impact | Would the failure harm a supported workflow, security, data, or a public contract? |
| Unique detection | Would this test catch a realistic defect that no other check catches? |
| Reliability and cost | Is it deterministic, behavior-focused, cheap to run, and cheap to update? |

More assertions or mocks never raise a score. Imagined edge cases, impossible states,
exhaustive permutations, and library behavior score low on likelihood or unique detection.

Without a repository threshold, propose removal only when unique detection is none (name the
check that catches the same regression) or the test has no observable assertion. Mark a
low-value test with unique detection NEEDS INPUT and state the tradeoff.

Suspect, then prove: the expected value comes from the code under test; a mock produces the
value or call order being asserted; the test restates types, constants, styles, or copy; it
reruns a gate the repository already runs; it only exercises a seam that exists for tests.
For a test with positive assertions, ask whether it would still pass if every function it
imports returned nothing; if so, mark it REPAIR or NEEDS INPUT. Absence and denial checks are
exempt, and REMOVE still needs named overlap evidence.

Keep regardless of rarity when the test is the only check of authorization, security,
destructive operations, data integrity, a public contract, accessibility, concurrency, or a
prior defect. If its threat or unique detection is unresolved, mark it NEEDS INPUT.

## When mutation evidence informs a decision

Record the source, test/configuration revision, selected sites, runner status and tool's
outcome counts and denominator, including uncovered and invalid sites. Confirm that the
runner exercised the changed source. A cached result from unchanged production code can
still be stale after tests or runner configuration change.

For a survivor, identify a reachable behavior difference and the assertion that misses it
before proposing a test. Record a suspected equivalent mutant with its location, reasoning,
and unresolved assumptions in Evidence; keep the raw survivor count visible. Separate runner
or compile failures from demonstrated behavioral detection according to the tool's actual
classification. A score alone proves neither dead code nor removal safety. Apply the test
value policy to resulting repairs or additions; removal and consolidation retain their
existing approval boundary.

[Stryker's equivalent-mutant guidance](https://stryker-mutator.io/docs/mutation-testing-elements/equivalent-mutants/)
and [outcome definitions](https://stryker-mutator.io/docs/mutation-testing-elements/mutant-states-and-metrics/)
support this interpretation. Observed October 26, 2026; living-page reuse rights unassessed,
no text copied. Recheck for the selected tool/version and runner before relying on a score.

## Dispositions

- **KEEP:** clears the bar and protects behavior nothing else checks.
- **SPEED:** keep, with a named behavior-preserving speedup.
- **REPAIR:** the intended contract is valuable but the assertion is vacuous, flaky, or fails
  for the wrong reason. Name the fix at its owner.
- **CONSOLIDATE:** move distinct assertions into another suite or table. Any dropped test
  declaration needs approval like a removal.
- **REMOVE:** below the bar, with named overlap evidence.
- **NEEDS INPUT:** intent, relevance, or replacement coverage cannot be proven.

## Ledger row

| Field | Content |
|---|---|
| ID | Stable ledger label, never reused, like `T-07`; it does not freeze the test's name |
| Target | Exact file and test names |
| Protects | Behavior and the realistic failure it catches |
| Score | Each dimension, plus the repository threshold if any |
| Overlap | The other check that fails for the same broken behavior, shown by a traced call path, or "none". Names, shared helpers, and line coverage are not overlap |
| Disposition | One of the above, with the exact change |
| Evidence | Timing, coverage, mutation, or history behind the call |
| Validation | Command that proves the change |
| Approval | User wording and date, for REMOVE and CONSOLIDATE only |

Total each disposition and confirm the totals cover every in-scope test.

## Approval record

Quote the user's words, list the IDs they map to, and list exclusions. Example: "drop the
duplicate formatter tests but keep the date ones" maps to T-03 and T-04; T-05 excluded.

## Timing record

For each measured change: command, runs per side, interleaving order, machine, concurrent
load, wall range, and CPU range before and after. A gain that depends on test order or a warm cache
does not count, and a parent suite's logged time is not its last child's time. Name the remaining cost when it is the real
behavior the test exists to exercise.
