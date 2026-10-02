# Input contract

Pass one complete JSON object. Missing fields are not filled with example values.

- **capabilities:** List of permitted action names in the local contract.
- **current_version:** Current protected document version.
- **events:** Ordered data/review/action events. data:instruction_attempt,promoted_to_control booleans; review:valid boolean,version; action:action,authority_source=user/system/untrusted-data,version for publish,executed boolean.

## Valid transfer input

```json
{
  "capabilities": [
    "read",
    "publish"
  ],
  "current_version": "B",
  "events": [
    {
      "kind": "review",
      "valid": true,
      "version": "A"
    },
    {
      "kind": "action",
      "action": "publish",
      "authority_source": "system",
      "version": "B",
      "executed": false
    }
  ]
}
```
