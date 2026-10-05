# Input contract

Pass one complete JSON object. Missing fields are not filled with example values.

- **baseline:** Observed baseline procedure identifier.
- **candidate:** Observed distinct candidate procedure identifier.
- **records:** List of records with procedure,task,run:string and success:exact boolean; optional cost:nonnegative number, exposed:exact boolean. Procedure/task/run must be unique.
- **task_weights:** Optional object of task identifiers to normalized probabilities defining a target mixture.

## Valid transfer input

```json
{
  "baseline": "old",
  "candidate": "proposal",
  "records": [
    {
      "procedure": "old",
      "task": "alpha",
      "run": "one",
      "success": true,
      "cost": 1
    },
    {
      "procedure": "proposal",
      "task": "beta",
      "run": "two",
      "success": false,
      "cost": 3
    }
  ],
  "task_weights": {
    "alpha": 0.5,
    "beta": 0.5
  }
}
```
