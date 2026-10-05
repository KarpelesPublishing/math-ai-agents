# Input contract

Pass one complete JSON object. Missing fields are not filled with example values.

- **risk_limit:** Maximum allowed adverse-event probability in [0,1].
- **risk_penalty:** Nonnegative utility deduction per unit probability.
- **actions:** Each row has name,reward:finite number,risk:probability,authorized:exact boolean. Abstention must be an explicit row.

## Valid transfer input

```json
{
  "risk_limit": 0,
  "risk_penalty": 100,
  "actions": [
    {
      "name": "act",
      "reward": 20,
      "risk": 0.01,
      "authorized": true
    },
    {
      "name": "wait",
      "reward": -1,
      "risk": 0,
      "authorized": true
    }
  ]
}
```
