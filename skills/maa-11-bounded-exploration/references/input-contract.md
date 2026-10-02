# Input contract

Pass one complete JSON object. Missing fields are not filled with example values.

- **means:** Arm success probabilities in [0,1], known only to this constructed simulator.
- **rounds:** Integer pull budget 1..10000.
- **seed:** Nonnegative integer random seed.
- **pull_cost:** Nonnegative common cost per pull.

## Valid transfer input

```json
{
  "means": [
    0.2,
    0.5,
    0.8
  ],
  "rounds": 90,
  "seed": 19,
  "pull_cost": 0.1
}
```
