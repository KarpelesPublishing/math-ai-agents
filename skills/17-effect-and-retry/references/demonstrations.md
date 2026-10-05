# Chapter demonstrations



These four calculations are shared with the notebook and illustrated reader. Read the source section and assumptions before choosing a state.

## C17-D01: Send it twice: what is different afterward?

For which kinds of request does a repeat leave the intended effect unchanged, and what happens when a key is lost?

**Source section:** The classification the specification actually uses

**Application:** Ask of every tool: if this is called twice with identical arguments, what is different afterward? Write the answer on the tool definition, because the agent cannot infer it from a name.

**Assumptions:** One tool at one state, with one record and constructed values (start 100, target 150, charge 50). The equation says nothing about sequences of tools, and a key only helps if the service really deduplicates under its contract: it must say what the key identifies, whether the arguments must match, who owns it and how long it is kept. Deduplication is not queryability. The service is also constructed to log every request and to reply as shown.

**Declared default controls:**

```json
{
  "kind": "put",
  "key": "none"
}
```

**Supported values:**

- `kind`: ['read', 'put', 'delete', 'charge']
- `key`: ['none', 'stored', 'lost']

**Evidence:** constructed teaching example

Constructed example: values defined for this reader; effects are counted with the laboratory's effect ledger, whose default trace sends two identical requests with no key and whose changed trace stores the key.

## C17-D02: From silence to a decision: retry, decline or read

After no reply, how likely is it that the effect landed, and what does that belief make of a retry, a decline and a perfect read?

**Source section:** Stage three: the retry decision, priced

**Application:** Do not turn a timeout into a probability by instinct, and do not leave the duplicate cost unpriced: a team that has never written it down has still decided, by leaving the choice to the retry library's default. Ask what the service does when the request lands and what it does when it does not, and what a status read would cost.

**Assumptions:** Two worlds only (applied, not applied), constructed likelihoods with silence 0.5 likely if the request did not apply, and the chapter's teaching construction: authorized attempts, preconditions hold, a retry certainly applies the effect, no other request costs, and the original attempt can no longer apply. The read is perfect and costs 1, as in workbench IV.3. A real transport symptom rarely supplies either likelihood, and an agent that writes its own status report is feeding its own belief. A request fee, expired authority or changed version would change the comparison. The laboratory's own retry price adds the request cost to belief times duplicate cost and compares that with a verification cost; this demonstration sets the request cost to 0 and follows Equation (17.3), so the notebook default (belief 0.8, retry cost 0.2, duplicate cost 10) is a different frame from the states shown.

**Declared default controls:**

```json
{
  "prior": 0.3,
  "silence_if_applied": 0.5,
  "c_dup": 40
}
```

**Supported values:**

- `prior`: [0.3, 0.99]
- `silence_if_applied`: [0.5, 0.9]
- `c_dup`: [0, 10, 40]

**Evidence:** constructed teaching example

Constructed example: the chapter's equal-likelihood baseline and its 0.99 prior; workbench problems IV.1 (belief 0.30, duplicate cost 40, missing cost 10) and IV.3 (a perfect read for 1, and the repeatable interface with duplicate cost 0); the other likelihoods and the duplicate cost 10 are defined for this reader. The duplicate term comes from the laboratory's retry pricing.

## C17-D03: Recovery before a repeat: how an undo can fail

When does a recovery tool count as Restored, and how can it fail to?

**Source section:** The four ways an undo fails

**Application:** Treat membership by the recovery route as a claim that needs evidence, like the observation route. Give the recovery path its own retry and escalation limits, so that an agent cannot spend its whole budget trying to clean up.

**Assumptions:** The four consequences and their statuses are constructed from the chapter's refund example; a real recovery has its own list. Absent and expired are shown together because both mean no undo can run; the chapter distinguishes them (none exists, or its window closed). Verification is taken to be a reliable read; in the lost-undo outcome no verifying read has been made yet, so nothing counts as verified, and once the read is made that outcome becomes one of the other three. Outstanding attempts must also be resolved or fenced against delayed effects, which this figure does not draw.

**Declared default controls:**

```json
{
  "stage": 1,
  "outcome": "works"
}
```

**Supported values:**

- `stage`: [1, 2, 3]
- `outcome`: ['works', 'unavailable', 'partial', 'lost']

**Evidence:** constructed teaching example

Constructed example: the chapter's refund, confirmation email, downstream webhook and partner ledger entry, and its four ways an undo fails; the notebook's transfer trace (a request with a lost reply, then a read) supplies the ledger entry in stage 1 through the laboratory's effect ledger.

## C17-D04: Which repeats are eligible: the six-step plan

For each step of the duplicate-record plan, does a lost reply leave a repeat eligible?

**Source section:** A trajectory, classified

**Application:** Before a retry leaves, run the gate on that request, not on the plan. If it fails, the next step may be a read, a recovery, a deliberate risk decision or a person. A posterior near zero is a risk estimate, not proof of absence.

**Assumptions:** The set is the chapter's conservative construction, not a rule from the HTTP standard. Steps 3 and 4 are idempotent only with stable identifiers and appropriate concurrency conditions; a record version may change between reading and writing. Steps 1 and 2 (search and read) have read-only semantics and are left out. If a read shows a request applied and complete, nothing here is repeated. Evidence goes stale: authority can expire and a version check can become out of date.

**Declared default controls:**

```json
{
  "step": "merge",
  "evidence": "none"
}
```

**Supported values:**

- `step`: ['merge', 'delete', 'notify', 'audit']
- `evidence`: ['none', 'absent', 'expired']

**Evidence:** constructed teaching example

Constructed example: the chapter's six-step plan and its classification of each step; the evidence cases are defined for this reader from the chapter's own routes.
