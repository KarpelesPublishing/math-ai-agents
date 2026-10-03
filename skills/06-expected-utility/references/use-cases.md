# Use cases

## Worked example

The release row has expected utility 0.9(10)+0.1(-50)=4. Review has utility 2 and abstention has utility 0, so release wins under these inputs. Its expected loss is -4 because loss is defined here as negative utility. A negative reported loss is therefore a favorable valuation, not a negative count of adverse events.

The first-outcome utility needed to tie review is (2+5)/0.9, approximately 7.78. The supplied value 10 exceeds that threshold. When the failure utility changes to -100, release falls to -1 while review stays at 2. The recommendation reverses without changing the model's probability of success. Read this as a statement about the action contract, not as evidence that the controller became less capable.

## Changed assumption

An expected-utility winner can be the wrong action for an incompletely specified decision. A prohibited release must first be removed from the feasible action set. Assigning it a large negative utility is not equivalent to enforcing a hard permission boundary. Likewise, an outcome labeled success can hide costs imposed on someone outside the table. If those costs matter to the decision, they need a declared valuation or a separate constraint.

The failure experiment in this notebook is a changed loss, not an adversarially chosen probability. It demonstrates that a high success probability does not settle the choice. A second useful test is to set the first-outcome probability to zero. The break-even first utility becomes unavailable because no value assigned to an impossible outcome can change expected utility. Returning zero as a threshold would manufacture information.

Probability estimates also deserve their own evidence. A row containing 0.9 is a statement of belief until a calibration or measurement protocol supports it. The arithmetic can be exact while the decision remains sensitive to a poorly supported input. Keep the probability source and utility owner in the exported report.

## New inputs

The transfer case compares retry with escalation. Retry's expected utility is 0.7(8)+0.3(-12)-1=1, which ties escalation at 1. Because retry appears first, the implementation selects it. That tie is useful: the calculation identifies an operational choice that the valuation does not uniquely resolve.

Replace the table with a local action contract whose outcomes are mutually exclusive and collectively exhaustive. Include the cost of waiting, asking for help, or preserving the current state when those are real alternatives. After execution, report the winning value and the runner-up, then identify the input whose plausible change would reverse them. Do not export the selected label alone. A decision record should preserve why it won and which assumptions made the comparison possible.

## Acceptance invariants

- Default expected utilities are 4,2,0.
- Changed loss reverses release to review.
- Probability normalization and aligned vector lengths are enforced.
