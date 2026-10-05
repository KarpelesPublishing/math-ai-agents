# Input contract

Pass one complete JSON object. Missing fields are not filled with example values.

- **development_x:** At least two development scales with variation.
- **development_y:** Aligned finite development observations.
- **test_x:** Separate unseen scales, with no development overlap.
- **test_y:** Aligned withheld observations used only for scoring.
- **family:** linear or log, declared before inspecting test outcomes.

## Valid transfer input

```json
{
  "development_x": [
    1,
    2,
    4
  ],
  "development_y": [
    0,
    0.69314718056,
    1.38629436112
  ],
  "test_x": [
    8,
    16
  ],
  "test_y": [
    2.07944154168,
    2.77258872224
  ],
  "family": "log"
}
```
