# Input contract

Pass one complete JSON object. Missing fields are not filled with example values.

- **candidate_success:** Marginal correctness probability in [0,1].
- **selector_accuracy:** Conditional probability of choosing a correct candidate when one exists.
- **sample_cost:** Nonnegative cost per generated candidate.
- **sample_latency:** Nonnegative serial time per candidate.
- **selector_cost:** Nonnegative selector expense for n>1.
- **selector_latency:** Nonnegative selector time for n>1.
- **deadline:** Nonnegative total time limit.
- **budget:** Nonnegative total expense limit.
- **shared_error:** Exact boolean choosing shared versus independent correctness construction.
- **sample_counts:** Nonempty list of positive integer candidate counts up to 1000.

## Valid transfer input

```json
{
  "candidate_success": 0.7,
  "selector_accuracy": 0.5,
  "sample_cost": 2,
  "sample_latency": 1,
  "selector_cost": 3,
  "selector_latency": 2,
  "deadline": 3,
  "budget": 6,
  "shared_error": false,
  "sample_counts": [
    1,
    2,
    4
  ]
}
```
