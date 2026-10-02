# Input contract

Pass one complete JSON object. Missing fields are not filled with example values.

- **nodes:** Unique graph identifiers.
- **start:** Registered search start.
- **goal:** Registered goal.
- **edges:** Directed from/to identifiers with finite nonnegative cost.
- **heuristic:** Object mapping each node to a nonnegative estimated remaining cost.
- **heuristic_cost:** Nonnegative declared cost of one heuristic evaluation, separate from path cost.

## Valid transfer input

```json
{
  "nodes": [
    "source",
    "middle",
    "target"
  ],
  "start": "source",
  "goal": "target",
  "edges": [
    {
      "from": "source",
      "to": "middle",
      "cost": 2
    },
    {
      "from": "middle",
      "to": "target",
      "cost": 2
    },
    {
      "from": "source",
      "to": "target",
      "cost": 7
    }
  ],
  "heuristic": {
    "source": 0,
    "middle": 0,
    "target": 0
  },
  "heuristic_cost": 0
}
```
