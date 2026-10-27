---
name: create-pr
description: Create a pull request from committed branch changes after verifying the head repository, push destination, and intended base. Use for PR creation; preserve uncommitted work and report an existing matching PR instead of creating a duplicate.
compatibility: Requires Git, push access to the head repository, and the GitHub CLI (gh) or an equivalent GitHub API client with access to the base repository. Without a client, report the PR as unrun with the blocker; nothing is installed or configured automatically.
disable-model-invocation: true
allowed-tools: Bash(git *), Bash(gh *)
arguments:
  - name: base
    description: "Target branch to merge into (overrides repository convention)"
  - name: draft
    description: Create as draft PR
  - name: no-push
    description: Skip pushing; verify the remote head matches the selected commit
---

# Create a pull request

Deliver a PR for the requested committed change. Reuse the user's authority to create it
and push the identified head branch. Preserve dirty and staged work; creating a PR does
not authorize committing that work, rewriting history, merging, or adding reviewers.

## 1. Resolve the repositories and immutable scope

Read repository instructions, PR templates, and required gates. Record branch, full HEAD
SHA, status, remotes, and upstream. Report uncommitted paths as excluded. A detached HEAD
needs an identified publication branch. Verify GitHub access and an available client or
connector. The CLI examples use `gh`; an equivalent API must preserve the same identities
and checks. Missing access remains a blocker, with no automatic install or credential setup.

Use explicit `--base`, then documented repository convention, then the verified remote
base repository's default branch. Resolve the base repository, head repository/owner,
remote URL, and head branch separately; a fork's push remote can differ from the base repo.
Ask only when evidence cannot settle these targets or required authority. A branch cannot
PR into the same repository/ref, but identical branch names in different repositories
can be valid. Do not reject a fork merely because its branch has the base's name.

Verify the base exists remotely and record its full SHA. Obtain that exact commit object
through authorized remote reading if needed. Do not substitute a stale local base. Compute
its merge base with the recorded head SHA. Inspect all commits in `<base-sha>..<head-sha>`
and the full diff from the merge base to the selected head. Two-endpoint base-to-head diffs
can incorrectly include reversals of newer base-only work. If objects or the merge base
cannot be resolved, report the blocker instead of inventing PR content.

Track every changed path, including deletes, renames, modes, generated files, lockfiles,
and binaries. Inspect their material effects in bounded batches. If the PR diff is empty,
report that and finish without creating a PR; commits alone do not prove a useful change.

## 2. Verify gates and prepare content

Run required repository gates within the authorized scope or record why they are unavailable.
Honor gates that must pass before publication. Build the title and body from the entire final
change, its concrete purpose, and observed validation. Follow the repository's template;
otherwise lead with the concrete user problem and resulting behavior, followed by relevant
validation. Keep titles grounded in the change; quantify benefits only when measured. Explain
the final implementation, with details that help readers understand the resulting behavior. Separate
passed, failed, unrun, and planned checks. Do not mark a planned test as passed or infer CI
success from local output. A check that selected zero tests, was skipped or cached, or masked
its exit code did not run; a forced failure counts only after confirming the forcing edit
applied. Include material risks and excluded work when relevant, and state in a line whether the
change is easily reversible or a one-way door, and its blast radius. Judge reversibility by what a
revert cannot undo: data written in a new shape, anything sent or deployed, and deletions.

Present the title, body, base/head repository and branch, recorded SHAs, and complete change
scope. Routine content generation proceeds under existing authority; it does not add a
confirmation stop. Write the body to a temporary file with actual newlines and literal text.

## 3. Publish the exact selected head

Recheck local HEAD, branch, selected targets, and gate results. Reassess any change that would
publish an unreviewed commit. Push only to the identified head repository and branch, using
an explicit refspec. Verify the remote branch's full SHA equals the selected head afterward.
With `--no-push`, perform that same equality check before creating the PR. If verification
fails or the remote branch moved, report it and stop dependent creation.

A push rejection needs diagnosis against the selected remote. Do not automatically force
push, pull/rebase, reset, or change destinations as recovery. Preserve existing state.

## 4. Create once and verify

Query open PRs in the resolved base repository by the exact head repository/owner and
branch. Check the base and head identities of each match. If a matching PR already exists,
return its verified URL and state instead of duplicating it. Do not change its metadata
unless updating that PR is authorized. An inaccessible query is not evidence of absence.

Create with explicit repository, supported head selector, base, title, and `--body-file`.
Attach UI visuals only when the user named them or this run captured them within the request's
scope, and never when they show private data; use the GitHub CLI's `--attach` option where the
installed version offers it. A local path in the body is not an attachment.
Use `--draft` when requested. If the host rejects a draft (some plans disallow drafts on
private repositories), report it and ask before opening a ready-for-review PR, which notifies
reviewers. For example, adapting the head selector to the client's
supported fork syntax:

```bash
gh pr create \
  --repo <base-owner/repository> \
  --head <verified-head-selector> \
  --base <base-branch> \
  --title <reviewed-title> \
  --body-file <prepared-body-file>
```

If creation times out or returns an uncertain outcome, query the exact tuple before retrying.
Verify the returned PR URL/number, base and head repositories/branches, selected head SHA,
draft/state, and any attachments by reading the created body back. Reconcile changed evidence before claiming success. A created PR whose
verification failed must be reported as created with verification unavailable, not retried
blindly. Attach the created or selected PR to the current task when the harness provides
PR artifacts. Remove only the temporary body file owned by this run.

## 5. Finish

Return the PR URL, created/existing outcome, base and head identities, verified head SHA,
change scope, local/push/PR evidence, excluded dirty work, and any failed or unrun checks.
If the user's requested finish includes monitoring, continue through the repository's PR
monitoring workflow; `monitor-pr` can supply event handling when available. PR creation alone
does not imply review approval, CI success, or merge readiness. No PR is
complete without a supported creation or existing-PR outcome for the requested tuple.

Source context for these refinements: [PR writing sources](references/sources.md).
