# Input contract

Pass one complete JSON object. Missing fields are not filled with example values.

- **rounds:** Integer request/acknowledgement rounds 1..6; enumeration has 2^(2 rounds) worlds.
- **drop_probability:** Independent per-message drop probability in [0,1].

## Valid transfer input

```json
{
  "rounds": 3,
  "drop_probability": 0.5
}
```
