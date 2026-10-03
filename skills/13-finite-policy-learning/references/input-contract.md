# Input contract

Pass one complete JSON object. Missing fields are not filled with example values.

- **rewards:** Finite verifier reward per one-step action.
- **success_probabilities:** External success chance per action in [0,1].
- **terminal_potentials:** Potential value of each terminal action outcome; zero is the episodic invariant condition.
- **episodes:** Bounded training sample count 1..10000.
- **seeds:** Nonempty integer seed list.
- **learning_rate:** Logit step size in [0,1].
- **discount:** Gamma in [0,1].
- **evaluation_runs:** Positive separate evaluation count.

## Valid transfer input

```json
{
  "rewards": [
    0,
    1
  ],
  "success_probabilities": [
    0,
    1
  ],
  "terminal_potentials": [
    2,
    0
  ],
  "episodes": 100,
  "seeds": [
    7,
    17
  ],
  "learning_rate": 0.1,
  "discount": 1,
  "evaluation_runs": 100
}
```
