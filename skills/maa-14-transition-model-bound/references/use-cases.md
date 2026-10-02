# Use cases

## Worked example

Both default row distances are 0.02, so epsilon=0.02. With R=1 and gamma=0.9, the discounted infinite bound is 1.8. At horizon 5 the finite bound is 0.02(5)(4)/2=0.2. The actual finite error is calculated from the two recurrences and must remain below the finite envelope.

At horizon 20 the finite bound grows to 3.8, even though each transition row changed by the same amount. That growth is a sensitivity statement under a worst-case construction. It does not say that the actual error became 3.8, and it does not establish that any particular action ranking reversed.

Two bounds are reported and both are valid. At horizon 20 the finite-horizon bound (3.8) is the looser one and the discounted infinite-horizon bound (1.8) the tighter, so the tightest valid statement is their minimum. The finite bound is not a stronger warning.

## Changed assumption

A common misuse inserts average model error into a uniform bound. A model may be accurate on frequently observed states and badly wrong at the one state that changes the plan. The maximum row distance protects the stated domain, while an average describes a different estimand.

Another misuse compares reward functions that differ and then attributes all value error to transition mismatch. This input contract intentionally supplies only one common reward vector. If the model invents immediate reward, the implementation's bound assumptions no longer apply.

Finally, an error bound is not a decision certificate. Even a small value bound can overwhelm a smaller action gap, and this fixed-policy state calculation does not inspect alternative actions. Use it to audit model sensitivity, then state the extra action-value and gap information required for ranking guarantees.

## New inputs

The transfer kernels are identical. Epsilon is zero, finite values agree at every stage, and both bounds are zero. This identity is a useful check of matrix alignment and recurrence behavior. If an implementation returned nonzero error here, investigate the computation before interpreting a more realistic model.

For reader data, explain how the true kernel was measured or constructed. Usually a deployed world does not provide exact transition probabilities. In that case the calculated epsilon is conditional on estimates and their support, not a known universal error. Preserve uncertainty or specify the measurements needed to bound it on the relevant policy domain.

## Acceptance invariants

- Actual finite error stays below stated envelope.
- Identical kernels give zero epsilon and error.
- Rows must be normalized and rewards shared.
