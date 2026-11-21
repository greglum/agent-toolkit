# Temporal contract

Write the contract before any split or metric. It fixes what the model may know and when.
The audit reads it as JSON. See the [example contract](../assets/contract.json).

## Fields

| Field | Meaning |
| --- | --- |
| `schema_version` | Integer `1` |
| `unit` | One row: what is observed, for example one lap for one car |
| `hierarchy` | Levels from row upward, for example `lap`, `stint`, `race`, `season` |
| `prediction_time` | The moment the model must answer, in words; rows carry the value |
| `label_horizon` | How long after prediction time the label is decided, in words |
| `label_horizon_time` | The same horizon as a nonnegative number in the time unit; every row's label window must be at least this long |
| `group_key` | Rows that share conditions and must stay on one side of a split |
| `forward_only` | `true` when train must precede test; `false` allows later train rows outside the embargo |
| `embargo_time` | Buffer around each test period, in seconds for ISO times or the numeric time unit |
| `features` | Each feature name mapped to its availability rule in words |
| `regime_breaks` | List of `{"time", "note"}` for rule, tyre, car or sensor changes |
| `notes` | Optional free text |

Unknown fields are input errors, so a typo cannot switch a check off.

Times are plain numbers or ISO 8601 that Python's `datetime.fromisoformat` accepts, with
`Z` allowed for UTC. Use one form in a run: all numbers, all with an offset, or all without.
Checked against the Python 3.10 `datetime.fromisoformat` documentation on 2026-11-20:
Python 3.10 accepts 3 or 6 fractional-second digits (`YYYY-MM-DD[*HH[:MM[:SS[.fff[fff]]]][+HH:MM[:SS[.ffffff]]]]`),
while newer Python versions accept broader ISO 8601 forms. `temporal.py` normalizes a trailing `Z`
to `+00:00` and rejects non-ISO suffixes such as ` UTC`.

## Three times for one value

Race telemetry shows why event time is not enough. Take a gap-to-car-ahead value.

- **Sensor time**: when the car crossed the timing line. The value describes this moment.
- **Ingest time**: when the value reached the platform, after radio, network and queue delay.
- **Availability time**: when the model's feature pipeline can read it. This adds windowing,
  late-arrival handling and any manual correction.

Join features on availability time. A corrected lap time published after the session has the
original sensor time but a much later availability time. Joined on sensor time, it leaks the
correction into training and into backtests.

Some values are revised. Keep the value as it was known at prediction time, an as-of join,
not the final corrected value.

## Choosing the group key

Pick the smallest level whose rows still share hidden conditions with each other:

- Laps in one race share weather, track rubber, safety cars and strategy. Group by race.
- Stints in one race are contiguous in time. Grouping by stint needs purge, because a label
  near the end of a stint is decided inside the next one.
- Several cars in the same race overlap in time. Grouping by car mixes concurrent rows across
  the split. Prefer race, or treat cars as one forward-only time order.

## Label horizon and purge

A label such as "pits within the next three laps" is decided up to 180 seconds after
prediction time. Its window is `(prediction_time, label_end_time]`. A train row whose window
reaches past the test start uses outcomes from the test period. The planner purges those rows.
The auditor treats a window ending exactly at the test start as clean.

## Regime breaks

List known breaks, such as a new tyre compound, a rule change on pit windows or a sensor
firmware update. The auditor reports folds whose span crosses a break. Compare those folds
with the rest before pooling them, and say so in the report.
