# Use cases

## Worked example

The first default request produces one effect and no acknowledgement. The second produces another effect and receives an acknowledgement. The terminal ledger therefore has two effects, one duplicate relative to the intended single operation, and confirmation of at least one effect. Confirmation does not prove uniqueness.

Blind retry costs 0.2+0.8(10)=8.2 in the declared next-step comparison. Verification costs 1, so at the unresolved decision point verification would be preferred. In this finished trace the second acknowledgement has already confirmed an effect, so the reported preferred_next_step is stop; the prices apply to the moment before that confirmation. Enabling idempotence suppresses the repeated same-key effect: the count stays at one and duplicate count falls to zero. The retry comparison then costs 0.2, below verification. This reversal follows from a receiving-service contract, not from the controller deciding that a retry is probably safe. Keep the key, payload, and service behavior in the evidence record.

## Changed assumption

The most dangerous shortcut is to equate an absent acknowledgement with an absent effect. That rule encourages the controller to replay actions whose consequences may already be durable. The converse shortcut also fails: receiving an acknowledgement does not establish that only one effect occurred. The default trace ends with confirmation and a duplicate.

A second failure concerns idempotency scope. A key that is checked only in client memory cannot protect against service restarts, multiple clients, or an independently repeated operation. This implementation assumes the receiver's key ledger is the effect boundary. If a real service has a retention window, payload normalization rule, or transaction boundary, those conditions must be added before adopting the simplified cost comparison.

Verification has its own limitations. The comparison assumes a perfect query, while real observations can be stale or ambiguous. A false negative could provoke another retry; a false positive could terminate a workflow that never completed. Do not treat the returned recommendation as a complete recovery controller. It prices one next step under a declared conditional belief and a specific duplicate-harm contract.

## New inputs

The transfer trace uses a request with a lost acknowledgement followed by an explicit verification. Its effect count stays at one, and confirmation becomes true at the second event. The verification cost is 0.5; blind retry would cost 0.1+0.6(4)=2.5, so at an unresolved decision point the declared comparison again favors verification. Because this trace is already confirmed, the reported preferred_next_step is stop.

For reader data, preserve event order and give each effect-bearing request its durable operation identifier. If you have only client logs, mark actual effect as unknown in your measurement design instead of inventing a boolean and passing it to this deterministic replay. Obtain server evidence or construct separate possible traces. Compare those traces to identify which next observation would distinguish them. The method is useful precisely because it refuses to turn transport uncertainty into a fabricated state fact.

## Acceptance invariants

- Nonidempotent default counts two effects.
- Idempotent changed trace counts one effect.
- Transfer verification confirms without adding an effect.
