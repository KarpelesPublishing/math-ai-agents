# Input contract

Pass one complete JSON object. Missing fields are not filled with example values.

- **discount:** Gamma in [0,1].
- **deadline:** Nonnegative integer primitive-step deadline.
- **start_time:** Nonnegative elapsed time, same unit as deadline.
- **interrupt_after:** Optional nonnegative integer executed-step cap for each option.
- **options:** Each option has name,initiation:boolean,rewards:nonempty primitive reward list,terminated:boolean,continuation_value:number.

## Valid transfer input

```json
{
  "discount": 0.5,
  "deadline": 2,
  "start_time": 0,
  "options": [
    {
      "name": "inspect",
      "initiation": true,
      "rewards": [
        0,
        4
      ],
      "terminated": true,
      "continuation_value": 8
    },
    {
      "name": "disabled",
      "initiation": false,
      "rewards": [
        9
      ],
      "terminated": true,
      "continuation_value": 0
    }
  ]
}
```
