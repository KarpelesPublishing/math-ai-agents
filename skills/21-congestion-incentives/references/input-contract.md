# Input contract

Pass one complete JSON object. Missing fields are not filled with example values.

- **demand:** Positive continuous traveler or job flow in normalized units.
- **capacity:** Positive flow scale of each linear congestible edge.
- **constant_time:** Nonnegative fixed delay of each outer constant edge.
- **shortcut_overhead:** Nonnegative real delay on the shortcut.
- **shortcut_toll:** Nonnegative private incentive charge, excluded from travel-time social cost.

## Valid transfer input

```json
{
  "demand": 0.5,
  "capacity": 1,
  "constant_time": 1,
  "shortcut_overhead": 0,
  "shortcut_toll": 0
}
```
