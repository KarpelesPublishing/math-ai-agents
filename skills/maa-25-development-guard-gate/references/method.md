# Method

For candidate c, development rate is the mean of its binary development outcomes. The selected candidate maximizes that rate, with input order resolving ties. Guard outcomes are aligned by position with the baseline guard. The selected gain is mean_i[Y_c,i-Y_baseline,i].

Acceptance requires gain at least the prespecified threshold and guard_reused=false. The threshold is a procedural rule, not a confidence bound. Finite sample noise can produce a pass even when the target-population gain is smaller. A statistical release rule would require additional assumptions, error control, and an appropriately reserved evaluation design.

The function reports every candidate's descriptive guard rate for teaching inspection, but the acceptance decision uses only the development-selected row. Those displayed guard results must not feed later candidate selection if the same evidence is to remain a clean guard. Repeated adaptive reuse changes its role. A boolean flag records that declared contamination boundary; it does not independently audit the history of a real experiment.

Supply binary baseline guard outcomes, candidate development and guard vectors, minimum gain, and reuse status. Guard lengths must match the baseline; every observed outcome must be zero or one. Development samples need not share guard length because they serve a different purpose.

The function calculates development rates, freezes the winner, computes paired guard gains, and applies the acceptance contract. Separate figures show development selection and guard gains. In the default case, identify the winner before looking at the second plot. The changed case improves that winner's guard evidence without changing selection. The transfer case gives a favorable gain but declares prior reuse, so you can test whether contamination blocks a clean release claim.

## Apply this to an agent

Changing memory, prompts or tools creates a new candidate procedure. Select it using development evidence, then apply a separate reserved release guard. Reusing the guard to choose another candidate changes the evidence contract.

For worked interpretation and changed assumptions, read [use cases](use-cases.md).

## Limits

- This is a local calculation under declared inputs, not an empirical claim about a deployed agent.
- Read the returned assumptions and limitations before applying the numerical result.
