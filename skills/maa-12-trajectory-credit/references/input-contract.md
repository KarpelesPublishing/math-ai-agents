# Input contract

Pass one complete JSON object. Missing fields are not filled with example values.

- **states:** Trajectory state identifiers, one more than reward count.
- **rewards:** Finite observed immediate rewards.
- **discount:** Gamma in [0,1].
- **learning_rate:** Step size in [0,1].
- **lambda:** Trace decay parameter in [0,1].
- **terminal:** Exact boolean distinguishing true termination from truncation.
- **values:** Initial finite value for every trajectory state.

## Valid transfer input

```json
{
  "states": [
    "a",
    "b",
    "c",
    "d"
  ],
  "rewards": [
    1,
    0,
    2
  ],
  "discount": 0.9,
  "learning_rate": 0.2,
  "lambda": 0,
  "terminal": true,
  "values": {
    "a": 0,
    "b": 1,
    "c": 0,
    "d": 0
  }
}
```
