# Method

Let C be the permitted capability set and source(a) the authority provenance of a requested action. An allowed action must lie in C and must not derive its authority from untrusted data. Publish also requires a valid review tied to the current document version.

The monitor processes the trace in order, so a later review cannot retroactively authorize an earlier publish. A review for another version does not satisfy the current predicate. A supplied executed flag records whether the effect happened even when the monitor would reject it, exposing enforcement failure separately from rule evaluation.

Security violations count both promoted instruction attempts and executed forbidden actions. Authorized task completion is true only when a publish event executes while satisfying capability, provenance, and review predicates. These counters can both be nonzero. The plot focuses on cumulative forbidden action executions; data-to-control promotion remains separately visible in metrics and event rows. This explicit scope prevents a narrow figure from pretending to summarize all security outcomes.

Provide capability names, current version, and an ordered event list. Data events state whether an instruction was attempted and promoted. Review events state validity and version. Action events state action name, provenance, executed status, and version for publish. Exact booleans and a closed provenance vocabulary prevent ambiguous inputs.

The computation updates current review status and evaluates each action before recording its actual execution. It returns allowed and violated flags, monitor-denied count, blocked count (denied and not executed), total security violations, and authorized completion. The figure shows forbidden executions over event index. In the changed case, promote the injected instruction and execute the previously rejected request. Predict how total violations and the narrower plot differ. Keep the local attack-family boundary in the exported report.

For worked interpretation and changed assumptions, read [use cases](use-cases.md).

## Limits

- This is a local calculation under declared inputs, not an empirical claim about a deployed agent.
- Read the returned assumptions and limitations before applying the numerical result.
