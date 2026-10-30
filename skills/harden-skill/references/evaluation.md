# Skill evaluation protocol

Use this protocol to compare an existing skill snapshot with a staged candidate. Keep the
workspace outside the repository unless the user asks to retain artifacts.

## Contents

- [Workspace](#workspace)
- [Behavioral cases](#behavioral-cases)
- [Isolation](#isolation)
- [Grading](#grading)
- [Adaptive trigger evaluation](#adaptive-trigger-evaluation)
- [Human review and retention](#human-review-and-retention)

## Workspace

Create a unique directory below the operating system's temporary directory:

```text
harden-skill/<target>-<timestamp>/
├── manifest.json
├── baseline-manifest.json
├── candidate-manifest.json
├── baseline/                        # repo-shaped selected-path bundle
│   └── <canonical-repo-relative-skill-path>/
├── candidate/                       # repo-shaped copy edited in isolation
│   └── <canonical-repo-relative-skill-path>/
├── cases/
│   ├── case-01/
│   │   ├── prompt.md
│   │   ├── inputs/
│   │   ├── baseline/{outputs,transcript,grading.json,timing.json}
│   │   └── candidate/{outputs,transcript,grading.json,timing.json}
│   └── ...
├── triggers/queries.json
└── benchmark.json
```

Record canonical and wrapper paths, baseline file states, harness/model settings, permissions,
validator commands, artifact-retention policy, and timestamps in `manifest.json`. Treat
transcripts as potentially sensitive and never commit them by default. Both bundle roots mirror
the selected repository-relative paths exactly; the final directory of the canonical skill path
must remain identical to the frontmatter `name`, because generic snapshot directory names make
valid skills fail directory-parity checks.

## Behavioral cases

Start with three realistic cases:

1. the common path that exercises the skill's main promise;
2. a boundary or malformed input that tests refusal, recovery, or safe failure;
3. an ambiguity or adjacent-domain case that tests a consequential decision.

Use two only when each run is materially expensive, such as a deployment, long external
job, or paid high-volume call. State the cost reason. A `full benchmark` may add cases, but
case variety matters more than count.

When extending an existing suite, keep proven regression cases separate from capability
cases that probe remaining weaknesses. Report both groups separately. A high regression
pass rate is useful preservation evidence; add harder capability cases without discarding
those checks or imposing a universal target pass rate. Freeze each comparison's cases;
changes to cases or graders require rerunning both arms and the no-skill control.

For every case, write the user-like prompt, fixed inputs, expected outcome, and checkable
assertions before comparing outputs. Fix the noise bar (the smallest difference that counts)
and the apply gate under Grading before the first run. Remove trivial assertions that add
no evidence. Keep required safety and regression assertions even when both versions pass,
but exclude those shared passes from claims of added value.

Match the bar to the skill's nature. For a judgment skill (planning, review, slicing), state
the outcome a competent practitioner would reach and the smells that make an output bad, not
a parts list of the expected answer; a parts list only checks that the output matches, not
whether the skill chose well.
Use exact assertions only when the skill exists to hit an exact target.

For code-review skills, include a verified incident's pre-fix revision and its fix or revert
when available, plus independently checked correct code. Keep the answer key out of the run's
inputs. Grade missed defects and false alarms separately, including whether a proposed fix
would break correct behavior. If evaluating repeated review, also record duplicate findings
and rounds to a stable verdict; a higher finding count alone is not an improvement. Preserve
independent adjudication of unexpected findings as described under Grading.

Case inputs never reuse the products, names, or data of the skill's own examples; a model that
copies an example's wording looks like a pass. When a worker writes cases, give it the skill's
job and domain, not its body.

Watch for a **lucky pass**: the right outcome arrived because the prompt or input happened to
include a fact the skill was supposed to ask for. Remove the volunteered fact in at least one
case, or record that the skill's eliciting step went untested.

## Isolation

Run every baseline and candidate case in a fresh context. Give both versions the same:

- prompt and input snapshot;
- model, client, tool availability, permissions, and working-directory shape;
- output contract and time budget;
- repository rules that a real invocation would load.

Expose only the selected skill version. Do not reveal the intended fix, prior findings, other
version, expected winner, or previous output. Run each case from a neutral, project-shaped copy,
so names like candidate or baseline do not reveal the test. Place that copy outside any
repository or folder whose instruction files state the skill's lesson: Claude Code `-p` loads
every `CLAUDE.md` above its working directory, which leaks guidance into both arms. User-level
instructions such as `~/.claude/CLAUDE.md` still load; run with `--bare` (it skips `CLAUDE.md`
discovery but needs API-key auth) or record which user instructions both arms carried. Deny
tools that reach other sessions or live services (in Claude Code, `SendMessage` and
`ListAgents`), and route tools that click, write, or run commands to mocks that record the
calls. Have one judge grade both versions of each case under shuffled labels, assertion by
assertion. Use subagents when supported; otherwise use separate non-interactive or interactive
sessions. If neither is available, static checks may continue, but behavioral comparison remains
unverified.

Run the same cases with no skill as a control. A skill whose margin over the control falls
inside the noise bar has no measurable effect: report it that way, not as a win, because it
costs context without changing behavior. Plugin-eval style
runners may load no user skills, settings, or repository instructions, so supply the rules a
real invocation would load as fixtures.

## Grading

Use programs for mechanical assertions such as parseability, file existence, counts, exit
codes, and diffs. Use a blinded evaluator or human review for judgment such as clarity,
appropriateness, and usability. A pass requires concrete output or transcript evidence;
section titles and self-reported success are insufficient.

Before trusting a judge, grade a known-good answer and an empty answer with it; it must pass
the first and fail the second. Pair one outcome check with one process check per case.
Bind the process check to required behavior, such as authorization or source preservation,
and accept other valid tool sequences. When outcome and process grades disagree, inspect
the trace and grader before blaming the skill; preserve mandatory safety assertions.

Prefer a code check over a judge when the criterion is objective, and give each judge one
failure mode with a pass or fail verdict. When a judge grades many cases, measure it against
human labels: keep the examples used to tune it apart from those used to measure it, and
report its true positive and true negative rates, not accuracy, which hides a judge that
passes everything.

Audit material claims the output makes beyond the fixed assertions: commands run, checks
passed, sources consulted, files changed, and delivery completed. Verify those against the
trace and artifact. A correct artifact does not validate an invented browser or deployment
claim. For planted-defect cases on real source, an additional finding is pending independent
adjudication until checked, not automatically a false positive or a new ground-truth success.
Keep that adjudication outside the fixed score until the expected set is resolved.

Store each assertion as:

```json
{
  "text": "The audit-only run leaves the target hash unchanged",
  "passed": true,
  "evidence": "before and after SHA-256 are both ..."
}
```

Count a run that errored, timed out, was truncated, hit a usage or rate limit, or used the wrong
model separately from graded results, and rerun it; these are harness errors, not regressions.
An empty output is an error, not a clean pass. For Codex runs, capture `codex exec --json`,
because plain output keeps only the last message.

Record duration and token usage when the harness exposes them. Compare cost alongside
quality, but do not reject a meaningful quality gain solely because it uses more tokens.

Apply the candidate only when:

- every structural error and target validator is cleared;
- every safety and completion assertion passes;
- no case has a material regression;
- the candidate improves the reported problem or removes a demonstrated risk; and
- subjective outputs have human review or are labeled pending review.

Before revising, classify each failure as a **skill defect** or a **bad case**. A bad case
demanded behavior outside the skill's job, or penalized a reasonable judgment call; report
the case as flawed and leave the skill unchanged.

If a material failure occurs, revise once using the failure category rather than its exact
wording, then rerun all affected cases. Preserve the live target if the revision still
fails.

When a skill will run on a smaller or cheaper model than the one editing it (an executor, a
worker, an Ollama route), run at least one case on that model. A skill that only works on
the model that wrote it is fragile.

## Adaptive trigger evaluation

Run this section when implicit triggering is in scope and invocation is observable.

Create ten realistic queries:

- five positives spanning formal/casual phrasing, implicit/explicit domain language,
  terse/detailed context, and single/multi-step requests;
- five near-miss negatives that share vocabulary or artifacts but belong to an adjacent
  skill or ordinary agent behavior.

Install the user's other skills, or present their names and descriptions, alongside the target;
a lone skill saturates because nothing competes for the query. Run every query once. A positive
passes when the trace proves this skill's `SKILL.md` was loaded; a negative passes when it was
not loaded. Rerun only first-pass failures twice. After three total runs, treat a positive as
passing with at least two observed loads and a negative as passing with at most one observed
load. Report raw counts, client, model, and the trace mechanism. This adaptive default spends
repeated runs where variance is visible.

Claude Code traces are Skill tool calls in `claude -p --output-format json`. Codex 0.161.0
and later emit `codex.skill_invocation` events marked explicit or implicit; they carry account
identifiers, so export them only to a local collector. A load proves selection, not task
success.

For `full benchmark`, use 8–10 positives and 8–10 negatives, a fixed roughly 60/40
train/validation split containing both labels, and three runs per query. Revise from train
failures only and select by validation performance. Keep fresh queries for a final sanity
check.

For an explicit-only skill, do not test natural-language triggering. Validate the client's
suppression metadata and run one explicit invocation that proves the skill loads. When a
client has no documented suppression or invocation trace, label that client unverified.

## Human review and retention

Present paired outputs without identifying the candidate when practical. Ask the reviewer
to record specific, actionable observations; an empty comment means no issue observed.
Do not hide failed assertions behind an aggregate score.

Delete the workspace after the final report by default. With `keep eval artifacts`, move or
create it at a user-approved persistent path, exclude secrets and unnecessary input copies,
and report the exact location. Never silently add eval artifacts to the target repository.

## Source scope

The regression/capability distinction and flexible process checks draw on Anthropic's
[Demystifying evals for AI agents](https://www.anthropic.com/research/demystifying-evals-for-ai-agents),
published January 9, 2026; sections "Capability vs. regression evals" and "Step 5: Design
graders thoughtfully", observed October 29, 2026, Pacific/Honolulu. Reuse rights are
unestablished; original paraphrase only. Recheck on changed guidance or contrary trials.
This does not prescribe a model, pass-rate target, new runner or additional authority.
