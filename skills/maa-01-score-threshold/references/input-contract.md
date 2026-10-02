# Input contract

Pass one complete JSON object. Missing fields are not filled with example values.

- **scales:** Finite strictly increasing numeric scale values.
- **scores:** Aligned continuous task scores in [0,1].
- **threshold:** Pass cutoff in [0,1].

## Valid transfer input

```json
{
  "scales": [
    10,
    20,
    40,
    80
  ],
  "scores": [
    0.1,
    0.3,
    0.6,
    0.8
  ],
  "threshold": 0.7
}
```
