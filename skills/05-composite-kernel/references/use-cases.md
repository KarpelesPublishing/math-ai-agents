# Use cases

## Worked example

With p=0.99 and n=100, independent all-step success is about 0.366. Under the shared condition, all-step success is 0.99. The per-step marginals are identical. That contrast rules out treating a marginal success rate as enough information to determine long-run completion.

The default composed first row is [0.76,0.24]: action-zero contribution is 0.8 times [0.9,0.1], and action-one contribution is 0.2 times [0.2,0.8]. In the changed case this row becomes [0.50,0.50] because only the tool factor changes. The frozen chooser now participates in a different recurrent system, even though its own probabilities are unchanged.

## Changed assumption

A product of marginal rates can be exact in an independent construction and seriously wrong under shared failures. It can also be pessimistic when the workflow detects, retries, or recovers from errors. This notebook does not include recovery, so its all-step event should not be renamed authorized confirmed terminal completion.

A composite kernel can also fail through a state boundary that omits information needed for the next transition. If memory version or tool state affects outcomes, but neither appears in the current state, the supplied kernel may not describe a Markov process. Adding more recurrence iterations will not repair that omission.

The changed case is a controlled mechanism experiment, not a fitted explanation of empirical behavior. Real ablations need matched budgets, observations, and task populations. Preserve those conditions before claiming that one surrounding component accounts for measured agent improvement.

The optional assembly table supplies observation, memory and retrieval ablations alongside recurrence. A changed terminal distribution identifies the consequence of the stipulated map within this construction. It does not show that a real memory or retrieval mechanism has the same effect. Different budgets or transition depths change the comparison contract and must be reported; the transfer table exposes a mismatched budget.

## New inputs

The transfer case uses three conditional probabilities 0.9,0.8,0.7. Their chain-rule product is 0.504. The equal marginal independent construction gives 0.9^3=0.729, while the shared construction gives 0.9. They answer different distributional questions.

For a local controller, specify the complete state sufficient for one transition, then identify the chooser and effect boundary. If data provide only run-level completions, route them to the evaluation method instead of manufacturing a step kernel. If they provide uncertain tool acknowledgements, use an effect trace. The right reliability calculation follows the available evidence, not the presence of a convenient average.

## Acceptance invariants

- Kernel rows remain normalized.
- Independent 100-step case is approximately 0.366.
- Changed tool alters occupancy with fixed chooser.
- All composed kernels have normalized rows.
- The transfer assembly comparison reports unequal resource allowances.
- Different transition depths are reported instead of treated as identical recurrences.
