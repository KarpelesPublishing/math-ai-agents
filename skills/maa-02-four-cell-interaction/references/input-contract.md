# Input contract

Pass one complete JSON object. Missing fields are not filled with example values.

- **scores:** Four finite scores ordered neither,first only,second only,both.
- **budgets:** Four nonnegative matched resource budgets in the same order.

## Valid transfer input

```json
{
  "scores": [
    0.2,
    0.5,
    0.55,
    0.7
  ],
  "budgets": [
    8,
    8,
    8,
    8
  ]
}
```
