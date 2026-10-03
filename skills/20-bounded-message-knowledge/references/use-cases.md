# Use cases

## Worked example

At d=0.3 and R=2, no successful request/ack pair has probability 0.51^2=0.2601. No request arrives with probability 0.3^2=0.09. Bob-only commitment therefore has probability 0.1701, and agreement has probability 0.8299.

With zero drops, only one positive-probability world remains. Requests and acknowledgements arrive, so both parties commit and agreement is 1. Bob can know acknowledgement receipt in this restricted model because delivery failure has been declared impossible. That conclusion depends on the model assumption, not on receiving an additional receipt.

## Changed assumption

Increasing retries does not monotonically create stronger epistemic guarantees. It can alter agreement probability while leaving Bob unable to distinguish a lost acknowledgement from a delivered one. Probability of agreement and knowledge of agreement are different quantities.

The bounded model also supplies synchronized round ticks and independent message losses. Real asynchronous systems may lack those assumptions or face crashes rather than simple drops. This notebook makes no impossibility or consensus theorem claim for those broader settings.

A zero-drop result is especially easy to overread. Declaring failure probability zero removes alternate worlds by assumption. It does not prove the channel cannot fail. When the channel contract is uncertain, retain the plausible loss worlds and identify what extra receipt, timeout rule, or failure detector would be needed for the intended decision.

## New inputs

At d=0.5 and R=3, Bob-only commitment is 0.75^3-0.5^3=0.296875. Agreement is 0.703125. Compute that before opening the generated result, then compare it with enumeration.

For a local handoff protocol, map which messages each participant can observe and what decision each view permits. Include dropped replies and partial histories. If a release requires evidence that the other party received an acknowledgement, an unobserved send is insufficient. Export a procedure with receipt requirements and stop conditions rather than calling the protocol successful because some world reaches completion.

## Acceptance invariants

- Enumerated world weights sum to 1.
- Analytic agreement equals enumerated metric.
- Impossible worlds excluded from knowledge at boundary probabilities.
