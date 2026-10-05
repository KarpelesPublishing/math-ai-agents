# Input contract

Pass one complete JSON object. Missing fields are not filled with example values.

- **belief:** Normalized prior state probability list.
- **transition:** Square row-stochastic state transition matrix.
- **observation:** State by observation row-stochastic matrix.
- **observed:** Zero-based observation index.
- **action_rewards:** Action by state finite reward matrix.
- **observation_cost:** Nonnegative cost paid before the one later action.

## Valid transfer input

```json
{
  "belief": [
    0.8,
    0.2
  ],
  "transition": [
    [
      0.7,
      0.3
    ],
    [
      0.2,
      0.8
    ]
  ],
  "observation": [
    [
      0.8,
      0.2
    ],
    [
      0.3,
      0.7
    ]
  ],
  "observed": 1,
  "action_rewards": [
    [
      5,
      -4
    ],
    [
      0,
      2
    ]
  ],
  "observation_cost": 0.2
}
```
