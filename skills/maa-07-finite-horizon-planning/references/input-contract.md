# Input contract

Pass one complete JSON object. Missing fields are not filled with example values.

- **horizon:** Integer decision count 1..200.
- **discount:** Gamma in [0,1].
- **start:** State key.
- **states:** Object mapping states to optional terminal:number and actions:list. Action has name,reward:number,probabilities:normalized list,next_states:aligned registered state keys.

## Valid transfer input

```json
{
  "horizon": 2,
  "discount": 0.5,
  "start": "wait",
  "states": {
    "wait": {
      "actions": [
        {
          "name": "now",
          "reward": 1,
          "probabilities": [
            1
          ],
          "next_states": [
            "end"
          ]
        },
        {
          "name": "later",
          "reward": 0,
          "probabilities": [
            1
          ],
          "next_states": [
            "paid"
          ]
        }
      ]
    },
    "paid": {
      "actions": [
        {
          "name": "collect",
          "reward": 4,
          "probabilities": [
            1
          ],
          "next_states": [
            "end"
          ]
        }
      ]
    },
    "end": {
      "actions": [
        {
          "name": "stop",
          "reward": 0,
          "probabilities": [
            1
          ],
          "next_states": [
            "end"
          ]
        }
      ]
    }
  }
}
```
