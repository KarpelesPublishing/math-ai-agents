# Input contract

Pass one complete JSON object. Missing fields are not filled with example values.

- **arrival_rate:** Nonnegative incoming task rate per declared time unit.
- **service_rate:** Positive reviewer service rate in the same unit.
- **delegation_fraction:** Fraction in [0,1] entering review.
- **agent_risk_limit:** Probability threshold in [0,1] for autonomous task handling.
- **tasks:** Rows with name,agent_authorized:boolean,risk:probability,deadline:nonnegative time,human_authorized:boolean,review_received:boolean.

## Valid transfer input

```json
{
  "arrival_rate": 1,
  "service_rate": 2,
  "delegation_fraction": 1,
  "agent_risk_limit": 0.05,
  "tasks": [
    {
      "name": "approval",
      "agent_authorized": false,
      "risk": 0.01,
      "deadline": 0.5,
      "human_authorized": true,
      "review_received": true
    }
  ]
}
```
