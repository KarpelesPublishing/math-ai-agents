# Input contract

Pass one complete JSON object. Missing fields are not filled with example values.

- **actions:** Nonempty list of uniquely named alternatives. Each has name:string, probabilities:normalized numeric list, utilities:aligned finite numeric list, cost:nonnegative number. Include abstention explicitly.

## Valid transfer input

```json
{
  "actions": [
    {
      "name": "retry",
      "probabilities": [
        0.7,
        0.3
      ],
      "utilities": [
        8,
        -12
      ],
      "cost": 1
    },
    {
      "name": "escalate",
      "probabilities": [
        1
      ],
      "utilities": [
        1
      ],
      "cost": 0
    }
  ]
}
```
