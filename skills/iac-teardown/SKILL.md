---
name: iac-teardown
disable-model-invocation: true
description: >-
  Preflight and execute safe Terraform or OpenTofu stack decommissioning and cross-stack state
  migrations without breaking live sibling services. Catches unapplied import blocks, shared
  DNS or email records, deletion locks, versioned storage, and unexpected plan drift before
  destroy. Not for code-tree dead code (delete-first) or cloud billing triage (cloud-ops-audit).
compatibility: >-
  Needs Python 3.10+ for the bundled static preflight script. Live state checks, saved plans,
  and applies require Terraform or OpenTofu CLI and explicit user authorization; without them,
  runs static preflight only and reports live checks unavailable.
---

# IaC teardown

Decommission or migrate Infrastructure-as-Code stacks without disrupting surviving DNS, mail,
certificates, or sibling projects. Explicit invocation grants procedure only; every destructive
cloud write, state mutation, or data deletion requires explicit user authorization for that
target.

## 1. Bind target, authority, and credential scope

Read the repository's agent, infrastructure, and deployment instructions before running any IaC
command.

- Identify the retiring stack, surviving stacks, and any live external consumers (DNS, email,
  certificates, shared buckets, edge functions, or sibling applications). Accept handoffs
  from `cloud-ops-audit` or `delete-first` supplying source revision, target stack, surviving
  consumers, and flagged live-state hazards, and verify every item directly against current HCL
  and state.
- Keep privileged cloud profiles scoped strictly to IaC and cloud CLI commands; never export an
  admin cloud profile when running application builds, tests, or linters.
- Work in a clean task-owned branch or worktree and record the base commit.

Done when the target stacks, surviving dependencies, and explicit write scope are recorded.

## 2. Run static preflight before any plan or apply

Run the bundled preflight checker on every retiring and receiving IaC directory before touching
remote state:

```sh
python3 scripts/preflight_tf.py /path/to/tf-dir
```

`preflight_tf.py` emits JSON and exits `0` when clean, `2` when teardown hazards are found, or
`1` on invalid arguments or unreadable inputs. If `preflight_tf.py` exits `1`, stop and resolve
the input error before continuing. When live read-only inspection is authorized, capture `terraform state list` to a private temp
file outside the repo and pass `--state-list <file>`. If `terraform` or `tofu` or cloud
credentials are unavailable, run static preflight only, mark live state and plan checks
unavailable, and stop before any state mutation or apply step. Load
[the teardown checklist](references/teardown-checklist.md) to classify and stage every finding:

- **Unapplied or stale `import` blocks:** strip unapplied production `import` blocks from retiring
  stacks before running any `plan` or `apply`, or `apply` will import live production resources
  into the retiring state.
- **Shared DNS, email, and validation records:** identify `MX`, `CAA`, `_dmarc`, `SPF`, `DKIM`,
  certificate-validation CNAMEs, and sibling subdomains that must survive teardown.
- **Lifecycle and deletion locks:** spot `prevent_destroy`, `skip_destroy`, and cloud-level
  deletion protection.
- **Versioned or non-empty stores:** spot object buckets and container registries that block
  destroy until versions, delete markers, and tagged images are emptied.

Done when every static preflight finding has a staged owner and mitigation step.

## 3. Migrate shared live resources first

Move any shared live resource (DNS records, `_dmarc`, certificate-validation CNAMEs, or shared
policies) into the surviving stack **before** unlocking or destroying the retiring stack:

1. Add exact matching resource definitions and temporary `import` blocks in the surviving stack.
2. Run a saved plan (`plan -out=...`), inspect every line to confirm **import with zero changes
   and zero destroys** to existing production resources, apply it, and delete the plan file.
3. Remove the temporary `import` blocks from the surviving stack and re-run `plan` to confirm
   zero changes.
4. Run `terraform state rm` on those moved addresses in the retiring stack so destroying the
   retiring stack never deletes them in the cloud.
5. Verify live readback (DNS resolution and HTTP status) on surviving endpoints before continuing.

Done when surviving resources belong solely to the surviving state and pass live readback.

## 4. Verify zero-data preconditions and unlock in staged plans

Never disable deletion protection on a stateful store until its emptiness or backup state is
verified against the user's authorization.

- Check live item counts (database tables, clusters, buckets) before unlocking deletion
  protection. Stop and ask the user if unexpected live data exists.
- Always use `terraform plan -out=<file>`, inspect every planned change, apply `<file>`, and
  immediately `rm -f <file>` (even if aborted), because saved plans can hold plaintext secrets.
- Check `terraform show -json <file>` via `scripts/preflight_tf.py <tf-dir> --plan-json <json>`
  when a plan includes mixed actions. If unrelated unapplied drift (such as pending function code
  or sibling edits) appears in a shared stack, stop and use explicit `-target=` saved plans or
  confirm authorization before applying.
- For managed DB cluster modifications (for example disabling `manage_master_user_password`),
  verify `apply_immediately = true` when the change must take effect immediately rather than
  waiting for a weekly maintenance window.

Done when deletion locks are safely cleared and no unexpected drift will be applied.

## 5. Destroy, clean up dormant configs, and verify live readback

1. Empty remaining authorized versioned buckets (including delete markers) and container
   registries (including protected tags) using the authorized admin principal.
2. Generate a saved destroy plan (`plan -destroy -out=<file>`), verify zero surviving resources
   appear in the destroy list, apply it, and immediately delete the plan file.
3. If dormant HCL stays in Git for future redeployment, restore `prevent_destroy`, `skip_destroy`,
   and deletion-protection defaults in HCL after destroy completes; remove unused variables or
   stale provider lockfile entries (`.terraform.lock.hcl`) for removed resources so lint and
   `plan -detailed-exitcode` stay clean.
4. Update repository infrastructure docs, live check scripts, and CSP/origin allowlists, then
   verify surviving endpoints, mail DNS, and zero leftover billed resources.

Done when surviving services pass live readback, dormant configs and lockfiles are clean, zero
plan artifacts remain on disk, and repository checks pass.
