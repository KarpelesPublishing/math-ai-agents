# Input contract

Pass one complete JSON object. Missing fields are not filled with example values.

- **success_matrix:** Candidate by task matrix of exact boolean task success.
- **task_weights:** Normalized task-distribution weights.
- **selected_candidates:** Zero-based candidate index chosen for each task.
- **deployment_allowed:** Exact boolean deployment permission for each task.
- **independent_candidate_success:** Probability for a separate constructed independent-candidate saturation curve.

## Valid transfer input

```json
{
  "success_matrix": [
    [
      true,
      true
    ],
    [
      true,
      false
    ]
  ],
  "task_weights": [
    0.5,
    0.5
  ],
  "selected_candidates": [
    1,
    1
  ],
  "deployment_allowed": [
    true,
    false
  ],
  "independent_candidate_success": 0.6
}
```
