# Use cases

## Worked example

Flashy wins development at 1.0, above steady at 0.75. Flashy's default guard equals the baseline, so gain is 0 and release is rejected against threshold 0.2. Steady's guard gain is 0.25, but selecting it after seeing that result would turn guard into another development set.

In the changed case, flashy repairs one baseline failure, giving guard gain 0.25. It now meets the declared threshold and is accepted because the guard is not reused. That pass means the finite procedural gate passed. It does not establish a confidence guarantee or remove the need for reversible deployment and monitoring.

## Changed assumption

The most direct contamination failure is choosing the candidate with the best guard score instead of the development winner. Another is repeatedly tuning a procedure after every failed guard result while continuing to call the same data untouched. Both make the guard participate in improvement.

The transfer case has a large favorable gain but guard_reused=true. The method rejects a clean release claim because the evidence no longer has its reserved role. The gain remains a descriptive quantity; contamination does not make arithmetic disappear.

A gate can also fail through undefined pairing or a post hoc threshold. Here positions define matched guard tasks, so the caller must preserve that meaning. Choose the threshold before inspecting outcomes and keep candidate, data, and procedure identifiers in the record. Passing this small deterministic rule is not certification of a generally improved agent.

## New inputs

The transfer proposal has guard success 1 compared with baseline 0.5, for gain 0.5. It exceeds threshold 0.1, but release remains rejected because the guard was reused. This separates favorable observed evidence from a valid acceptance protocol.

For local improvement work, freeze the candidate and its runtime before opening guard outcomes. Record the source of every prior evaluation and preserve a genuinely new guard after contamination. If uncertainty control is required, design that statistical rule explicitly rather than assigning a scientific meaning to a convenient numeric threshold. Keep rollback and monitoring outside the claim that the finite gate itself makes deployment safe.

## Acceptance invariants

- Selection depends only on development.
- Default rejects zero guard gain.
- Reused guard blocks acceptance despite favorable gain.
