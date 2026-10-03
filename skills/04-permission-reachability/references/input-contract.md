# Input contract

Pass one complete JSON object. Missing fields are not filled with example values.

- **nodes:** Unique nonempty state identifiers.
- **start:** Registered initial node.
- **goal:** Registered desired node.
- **edges:** Directed edge list with from,to:registered identifiers and allowed:exact boolean.

## Valid transfer input

```json
{
  "nodes": [
    "queued",
    "approved",
    "sent"
  ],
  "start": "queued",
  "goal": "sent",
  "edges": [
    {
      "from": "queued",
      "to": "approved",
      "allowed": false
    },
    {
      "from": "approved",
      "to": "sent",
      "allowed": true
    }
  ]
}
```
