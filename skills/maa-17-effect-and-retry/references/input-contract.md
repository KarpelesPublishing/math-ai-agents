# Input contract

Pass one complete JSON object. Missing fields are not filled with example values.

- **idempotent:** Exact boolean. True declares server-side key/payload deduplication.
- **events:** Ordered event list: request has kind,key,payload,effect:boolean,ack:boolean; verify has observed_effect:boolean. All requests must concern one logical payload; distinct operations require separate traces.
- **verify_cost:** Nonnegative one-step cost of perfect verification.
- **retry_cost:** Nonnegative one-step request cost.
- **effect_probability:** Probability [0,1] that the unresolved original request already took effect.
- **duplicate_cost:** Nonnegative extra harm from a duplicate effect.

## Valid transfer input

```json
{
  "idempotent": false,
  "events": [
    {
      "kind": "request",
      "key": "send-2",
      "payload": "packet-B",
      "effect": true,
      "ack": false
    },
    {
      "kind": "verify",
      "observed_effect": true
    }
  ],
  "verify_cost": 0.5,
  "retry_cost": 0.1,
  "effect_probability": 0.6,
  "duplicate_cost": 4
}
```
