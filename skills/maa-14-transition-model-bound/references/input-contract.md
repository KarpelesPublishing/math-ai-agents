# Input contract

Pass one complete JSON object. Missing fields are not filled with example values.

- **true_transition:** Square row-stochastic true kernel after fixing a policy.
- **model_transition:** Same-size approximate row-stochastic kernel for that policy.
- **rewards:** Common immediate state reward vector, finite and nonnegative.
- **discount:** Gamma in [0,0.9999].
- **horizon:** Integer reward horizon 1..1000 with zero terminal continuation.

## Valid transfer input

```json
{
  "true_transition": [
    [
      1,
      0
    ],
    [
      0,
      1
    ]
  ],
  "model_transition": [
    [
      1,
      0
    ],
    [
      0,
      1
    ]
  ],
  "rewards": [
    1,
    2
  ],
  "discount": 0.5,
  "horizon": 4
}
```
