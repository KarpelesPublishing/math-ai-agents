# Input contract

Pass one complete JSON object. Missing fields are not filled with example values.

- **baseline_guard:** Nonempty binary baseline outcomes aligned with each candidate guard.
- **minimum_guard_gain:** Finite prespecified candidate-minus-baseline mean threshold.
- **guard_reused:** Exact boolean stating whether guard evidence influenced improvement or prior selection.
- **candidates:** Nonempty rows with name,development:binary list,guard:binary list matched to baseline_guard.

## Valid transfer input

```json
{
  "baseline_guard": [
    false,
    true
  ],
  "minimum_guard_gain": 0.1,
  "guard_reused": true,
  "candidates": [
    {
      "name": "proposal",
      "development": [
        true,
        true
      ],
      "guard": [
        true,
        true
      ]
    }
  ]
}
```
