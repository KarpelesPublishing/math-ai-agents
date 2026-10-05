# Method

Let E_t count durable effects after event t, and let C_t indicate whether at least one effect has been confirmed. A request whose effect flag is true increments E_t unless a valid idempotency contract recognizes the same key and payload. Its acknowledgement changes C_t; losing that acknowledgement does not undo the effect. A verification event can confirm an effect already present in the ledger.

An idempotency key is useful only if the receiving service records and checks it. Here the key maps to a payload identifier. Repeating the same pair suppresses an additional effect when idempotence is enabled. Reusing a stored key for a different payload raises an error because the requested contract is ambiguous. Counting repeated attempts without this mapping would not establish idempotence.

For one unresolved request, let p denote the conditional probability that it already took effect. Let c_r be the retry cost, d the harm of a duplicate, and c_v the cost of perfect verification. A nonidempotent retry has expected next-step cost c_r+pd. With the declared idempotency contract, duplicate harm vanishes and this comparison becomes c_r against c_v. This small calculation omits the benefit and cost of any later recovery steps.

The distinction between conditional belief and recorded truth matters. The trace says what happened in this constructed run; p represents what the controller believes before resolving an uncertain request. Neither quantity can replace the other in a deployed report.

Read the trace in order. A request includes a key, payload identifier, actual effect flag, and received acknowledgement flag. A verification includes whether the existing effect was observed. The computation maintains the effect count, key ledger, confirmation status, and unresolved-effect status, then emits a row after each event. Exact boolean checks prevent strings such as "false" from being treated as truthy evidence.

Two charts show cumulative effects and confirmation over event index. The first can rise while the second remains zero. That separation is the reason this notebook exists. A confirmation of an absent effect is rejected rather than silently accepted. The local trace is deliberately stronger than ordinary client logs because it has the ground truth needed to teach and test the inference boundary.

The cost comparison uses separate declared inputs. It does not estimate the unresolved-effect probability from the trace, nor does it assume retries are independent. The changed case enables the key/payload contract while preserving the same event sequence. The transfer case replaces the retry with verification, so you can inspect how uncertainty is resolved without increasing the effect count.

Once the logical effect is confirmed and no uncertainty remains, the recommended next step is stop. The verification and retry prices remain visible for inspecting the unresolved decision point; they do not justify another request after completion. Different payloads are rejected because this ledger counts duplicates of one intended logical operation.

## Apply this to an agent

A tool may perform an effect even when its acknowledgement is lost. Keep the effect ledger separate from what the agent knows, then compare verification with another request. An idempotency key works only when the tool stores and enforces its contract.

For worked interpretation and changed assumptions, read [use cases](use-cases.md).

## Limits

- This is a local calculation under declared inputs, not an empirical claim about a deployed agent.
- Read the returned assumptions and limitations before applying the numerical result.
