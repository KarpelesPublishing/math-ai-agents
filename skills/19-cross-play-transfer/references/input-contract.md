# Input contract

Pass one complete JSON object. Missing fields are not filled with example values.

- **matrix:** Square policy by partner success-probability matrix, entries in [0,1].
- **partner_weights:** Normalized target partner distribution.
- **supervisor_weights:** Normalized changed partner or supervisor distribution over the same columns.

## Valid transfer input

```json
{
  "matrix": [
    [
      1,
      0,
      0
    ],
    [
      0.6,
      0.6,
      0.6
    ],
    [
      0,
      0,
      1
    ]
  ],
  "partner_weights": [
    0.2,
    0.6,
    0.2
  ],
  "supervisor_weights": [
    0.5,
    0,
    0.5
  ]
}
```
