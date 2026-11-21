# IaC teardown checklist

Observed 2026-11-21. Provider resource names, validation record formats, and Terraform/OpenTofu
CLI flags change over time; verify against active provider versions before applying.

Use these patterns when `scripts/preflight_tf.py` flags hazards in a Terraform or OpenTofu stack.

## 1. Unapplied `import` blocks in a retiring stack

An `import { to = ... id = ... }` block left in a retiring stack is dangerous even if the live
resource is not in `terraform.tfstate` yet. Running `terraform apply` (for example to clear a
deletion-protection flag) executes the `import` block and pulls the live production resource into
the retiring state, so the subsequent `destroy` deletes production DNS or storage.

**Fix:** Remove unapplied `import` blocks and their orphaned resource definitions from the
retiring stack **and verify with `terraform state list`** before running any `plan` or `apply` in
that directory.

## 2. Shared DNS, email, and validation records

Check every DNS resource in the retiring stack against live consumers before removal:

- **Email auth and routing (`MX`, `TXT` SPF/DKIM, `_dmarc`):** inbound mail or another provider
  often shares `_dmarc` with a retiring outbound transactional mail stack. Move shared DNS records
  verbatim into the surviving mail or prod DNS stack via `import` + `state rm` before destroying
  the outbound mail stack.
- **Sibling subdomain and certificate validation records (`A`, `AAAA`, `CNAME`, `_*.acm-validations.aws.`):**
  migrate sibling subdomain aliases and their ACM renewal validation CNAMEs into the surviving
  DNS stack first. Verify `0 to change, 0 to destroy` on the import plan before `state rm`.

## 3. Staged unlock and restoring dormant HCL guards

When retiring live infrastructure while keeping HCL in Git for future rebuilds:

1. Verify empty data stores first.
2. Remove `prevent_destroy` / `skip_destroy` and set cloud deletion protection (`deletion_protection`,
   `deletion_protection_enabled`) to inactive/false in a targeted unlock apply.
3. Empty versioned S3 buckets (both object versions and delete markers) and ECR repositories
   (including retention-protected tags).
4. Apply the saved `-destroy` plan, then delete the `.tfplan` file immediately.
5. Restore `prevent_destroy = true`, `skip_destroy = true`, and active deletion protection in HCL
   so future applies retain their safety guards.

## 4. Unrelated stack drift and deferred DB edits

- If `terraform plan` on a shared stack includes unapplied function or resource changes from
  earlier commits, inspect `terraform show -json <tfplan>` with `preflight_tf.py --plan-json`.
  Use explicit `-target=` saved plans when authorized to modify only the targeted resources, and
  refresh outputs separately if needed.
- On managed databases (for example AWS Aurora / RDS), changing `manage_master_user_password` or
  password versions defers until the next maintenance window unless `apply_immediately = true` is
  set explicitly.

## 5. Provider lockfile and lint hygiene

When removing the last resource of a provider (such as `archive` or `random`) from a root module,
run `terraform init -upgrade` (or `providers lock`) inside that root so `.terraform.lock.hcl` does
not retain orphaned provider hashes or cause `tflint` / `plan -detailed-exitcode` mismatches.
Remove unused variables once no resources reference them.
