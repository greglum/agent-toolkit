# Cloud cost and alarm traps

Observed 2026-11-21. Provider pricing, free-tier quotas, and evaluation defaults change over time;
recheck live service limits and current pricing before relying on thresholds for a new rollout.

## Untagged and threshold-cliff costs

| Trap | Why tagged budgets hide it | What to check live |
| --- | --- | --- |
| Public IPv4 / Elastic IPs | Often lack project cost-allocation tags | `ec2 describe-addresses` and unattached allocations |
| Extra action-enabled budgets | First 2 action-enabled budgets may be free, with a daily fee starting at the 3rd untagged at account level | `budgets describe-budget-actions-for-account` |
| Disabled Lambda + log metric filter | A log metric filter with `default_value = "0"` emits custom metric data points on every `"disabled"` invocation | Enabled EventBridge schedules and active custom CloudWatch metrics |
| Stopped compute instances | Stopping an instance halts compute billing only; attached EBS volumes and reserved IPv4 EIPs continue billing | Stopped instances, attached EBS sizes, and associated EIPs |
| Expiring free-trial compute | Free-tier compute hides current monthly run rate until the trial end date | Current instance family trial expiration vs non-trial hourly price |
| Orphaned snapshots and secrets | Manual DB snapshots and unused secrets survive stack or workspace deletion | Manual RDS/EBS snapshots and secret `LastAccessedDate` |

## False-alarm mechanics

- **Sliding-window boundary spill on auto-pausing serverless DBs:** An alarm using `period = 3600`,
  `evaluation_periods = 2`, `statistic = "Average"`, `threshold = 0` evaluates sliding 1-hour
  windows every minute. Any wake longer than ~1 minute (even a 5-minute visit or a 23-minute
  maintenance wake) straddles the window boundary 61 minutes after start and pages on every wake.
  Prefer shorter periods with `Maximum > 0` and `datapoints_to_alarm` / `evaluation_periods`
  above routine wake durations.
- **Managed master secret auto-rotation:** Enabling automatic RDS master-user secret rotation
  (for example every 7 days) wakes an auto-paused serverless DB weekly even with zero user traffic.
  When application roles use non-rotating app credentials, prefer write-only non-rotating master
  passwords unless weekly rotation is required.
- **Cross-region global endpoint timeouts on low-vCPU Lambdas:** Creating a fresh `boto3.client("iam")`
  per invocation inside a 128 MB regional Lambda with a 1 s timeout and 1 attempt forces a new
  cross-region TLS handshake every run. Cache clients lazily at module scope for warm reuse and
  keep per-service timeouts within the function timeout budget so one service hang cannot starve
  independent fallback actions.
- **Masked `ExceptionGroup` sub-exceptions:** Raising `ExceptionGroup` without logging the inner
  exception classes/messages hides the failing downstream call in JSON Lambda error logs. Log
  explicit `{type}: {msg}` entries before raising.

## Cross-cloud cost-bound parity checks

Before recommending or executing a migration across cloud providers (for example AWS to GCP):

- Check whether existing flat-rate or hard-capped layers (such as CloudFront flat-rate Free plans
  with zero overage charges or scale-to-zero Aurora Serverless v2) have true no-overage parity
  in the destination cloud, and record any shared-account free-tier quota limits.
- Do not treat asynchronous billing alerts or billing-disable webhook functions (which can lag by
  hours) as equivalent to a hard edge or rate cap; design edge rate-limiting or hard caps before
  enabling destination billing.
