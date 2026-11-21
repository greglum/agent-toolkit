# Contract fields

A contract is one JSON object. The checker rejects unknown keys, so a typo such as
`max_lag` fails as invalid input (exit 2) instead of being ignored.

## Top level

| Field | Required | Meaning |
| --- | --- | --- |
| `status` | yes | `draft` or `confirmed`. A draft always yields a `contract_not_confirmed` finding. |
| `source` | no | Who or what confirmed the contract, such as a spec name and revision. |
| `notes` | no | Free-form object. `infer_contract.py` lists skipped non-numeric columns here. |
| `missing_tokens` | no | Cell values that mean missing, compared without case. Default: empty, `NA`, `NaN`, `null`, `None`, `-`. |
| `time` | yes | Time block below. |
| `channels` | yes | Nonempty list of channel objects below. |

## Time block

| Field | Default | Meaning |
| --- | --- | --- |
| `sensor` | required | Column with the time the sensor took the reading (event time). |
| `ingest` | none | Column with the time the platform received or stored the row (availability time). |
| `unit` | `s` | `s`, `ms`, `us`, `ns` (epoch or session numbers) or `iso8601`. Both columns share it. |
| `min_lag_s` | `0` | Ingest minus sensor below this is `lag_negative`: clock skew or a time zone error. |
| `max_lag_s` | none | Ingest minus sensor above this is `lag_late`: late-arriving or backfilled rows. |
| `gap_factor` | `3` | A gap is a step between sorted unique sensor times larger than this many expected periods. The period comes from the fastest `expected_rate_hz`. |
| `rate_tolerance` | `0.05` | Allowed relative difference between observed and expected rate, for the whole file and each half. |

Sensor time and ingest time answer different questions. Sensor time orders physical events.
Ingest time says when a reading could have been known. A model or live decision may use a
reading only after its ingest time. Never substitute one for the other.

## Channel object

| Field | Meaning |
| --- | --- |
| `name` | Channel name. Matches a column of that name, or one with a unit suffix: `name[bar]`, `name (bar)` or `name_bar`. |
| `column` | Exact column name when it differs from `name`. |
| `unit` | Declared unit, such as `kPa`, `degC`, `km/h`. `null` yields `unit_undeclared`. |
| `expected_rate_hz` | Expected sample rate. Must be positive. Channel names must be unique. |
| `min`, `max` | Physical limits. Values outside are `out_of_range`. |
| `typical_min`, `typical_max` | Plausible operating range for nonzero readings. Used only for the unit-scale check. Falls back to `min` and `max`. |
| `saturation` | Sentinel values the sensor or logger writes at its limits, such as `65535` or a clamp value. |
| `max_missing_fraction` | Allowed fraction of rows with a missing cell. |
| `note`, `unit_note`, `observed` | Free text and the observed block written by `infer_contract.py`. Ignored by the check. |

Each numeric cell lands in exactly one class, checked in this order: `missing`,
`unparseable`, `saturated`, `zero`, `out_of_range`, `valid_nonzero`. Zero has its own class
because many loggers write zero for a dropout. A zero outside `min`..`max` also yields
`zero_outside_range`.

Units the checker can convert between, for candidate suggestions: pressure (Pa, kPa, MPa,
bar, mbar, psi), temperature (K, degC, degF), speed (m/s, km/h, mph), length (m, mm, km) and
acceleration (m/s2, g). For other units it tries generic factors: 1000, 100, 3.6, 14.5038 and
their inverses, and a 273.15 offset.

## Worked example: race telemetry

The channels and values below are synthetic. They match the bundled
[contract](../assets/contract.json).

```json
{
  "status": "confirmed",
  "source": "Synthetic example contract for the bundled fixtures",
  "time": {"sensor": "t_sensor", "ingest": "t_ingest", "unit": "s",
           "min_lag_s": 0, "max_lag_s": 2.0, "gap_factor": 3, "rate_tolerance": 0.05},
  "channels": [
    {"name": "brake_pressure_front", "unit": "kPa", "expected_rate_hz": 10,
     "min": 0, "max": 20000, "typical_min": 500, "typical_max": 15000,
     "saturation": [20000], "max_missing_fraction": 0.01},
    {"name": "coolant_temp", "unit": "degC", "expected_rate_hz": 10,
     "min": -20, "max": 140, "typical_min": 60, "typical_max": 120,
     "saturation": [-40, 150], "max_missing_fraction": 0.05},
    {"name": "wheel_speed_fl", "unit": "km/h", "expected_rate_hz": 10,
     "min": 0, "max": 400, "saturation": [], "max_missing_fraction": 0.01}
  ]
}
```

Why each choice matters:

- `brake_pressure_front` is zero whenever the driver is off the brake, so zeros are normal
  and excluded from the scale check. `typical_min` of 500 kPa is set for braking samples only.
  The [faulty sample](../assets/faulty.csv) records it in bar, so braking values near 60 sit
  below 500. The check reports `unit_scale_suspicion` with the candidate bar to kPa (x100).
- `coolant_temp` lists `-40` and `150` as saturation sentinels, so a pinned sensor is counted
  as `saturated`, not as a real temperature or an `out_of_range` reading. Missing cells
  (`""`, `NA`) are counted separately.
- `wheel_speed_fl` has no typical range, because speed can legitimately be near zero in the
  pit lane. Its scale error is caught only through the header: the faulty sample's column is
  `wheel_speed_fl[m/s]`, which yields `unit_mismatch`.

Running the check on the faulty sample also finds one timestamp regression, one duplicate
time, one 1.1 s gap, two rows with negative ingest lag and one late row.
