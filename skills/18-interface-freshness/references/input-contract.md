# Input contract

Pass one complete JSON object. Missing fields are not filled with example values.

- **observation_age:** Nonnegative elapsed time since observation.
- **max_age:** Nonnegative freshness limit in the same time unit.
- **observed_version:** Version seen in the observation.
- **current_version:** Version at action time.
- **current_permission:** Exact boolean current authorization.
- **effect_confirmed:** Exact boolean receipt of desired effect confirmation.
- **coordinate_target:** Current object located at previously observed coordinates.
- **semantic_target:** Current object resolved by semantic interface.
- **wanted_target:** Intended object identifier.
- **change_rate:** Optional nonnegative rate of invalidating interface changes per unit time. When given, Fresh(delay)=exp(-rate*delay) from Equation 18.3 is reported.
- **delays:** Optional list of nonnegative delays in the same time unit; requires change_rate.

## Valid transfer input

```json
{
  "observation_age": 0,
  "max_age": 1,
  "observed_version": "page-C",
  "current_version": "page-C",
  "current_permission": false,
  "effect_confirmed": false,
  "coordinate_target": "submit",
  "semantic_target": "submit",
  "wanted_target": "submit",
  "change_rate": 0.05,
  "delays": [
    2,
    10
  ]
}
```
