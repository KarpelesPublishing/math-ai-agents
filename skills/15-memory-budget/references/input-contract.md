# Input contract

Pass one complete JSON object. Missing fields are not filled with example values.

- **budget:** Nonnegative integer token budget up to 10000.
- **now:** Nonnegative current time.
- **current_version:** Current document or state version identifier.
- **records:** At most 20 records. Each has id,tokens:positive integer,decision_value:nonnegative number,timestamp,ttl:nonnegative numbers,authority:boolean,version:string.
- **original_action_values:** Finite values for each original decision alternative.
- **compressed_action_values:** Aligned values after compression.

## Valid transfer input

```json
{
  "budget": 3,
  "now": 20,
  "current_version": "doc-C",
  "records": [
    {
      "id": "expired",
      "tokens": 1,
      "decision_value": 10,
      "timestamp": 10,
      "ttl": 2,
      "authority": false,
      "version": "doc-C"
    },
    {
      "id": "current",
      "tokens": 3,
      "decision_value": 4,
      "timestamp": 19,
      "ttl": 3,
      "authority": true,
      "version": "doc-C"
    }
  ],
  "original_action_values": [
    1,
    0
  ],
  "compressed_action_values": [
    2,
    1
  ]
}
```
