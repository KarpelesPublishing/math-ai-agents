# Use cases

## Worked example

Default mean self-play is (0.95+0.9)/2=0.925. Mean cross-play is (0.2+0.4)/2=0.3, so the proportional loss of Equation 19.2 is (0.925-0.3)/0.925, about 0.676, which the report returns as joint_policy_correlation_loss. Under equal partner weights, policy 0 scores 0.575 and policy 1 scores 0.65, so policy 1 wins despite policy 0's stronger diagonal.

With weights [0.9,0.1], policy 0 scores 0.875 and policy 1 scores 0.45. The preferred policy reverses. The second supervisor mixture already demonstrates that reversal in the default report. Interpret it as conditional transfer across partner distributions, not proof that one policy is intrinsically more cooperative.

## Changed assumption

A cross-play matrix can conceal unmatched conditions. If one row receives easier tasks, more time, or a different supervisor, weighted averages compare more than policy behavior. Preserve those conditions before treating a cell difference as transfer evidence.

Uniform off-diagonal averaging is also easy to misuse. The deployed system may almost never encounter some partners, while frequently meeting an omitted partner. A high average across the supplied bank says little about an unsupported population.

Another failure is strategic adaptation. A partner that reacts to the deployed policy creates a changing environment. Static matrix values may describe the initial interaction but not later equilibria. This laboratory calculates a declared finite comparison and does not infer common knowledge, incentives, or an equilibrium from success entries.

## New inputs

The transfer matrix includes a specialist for column 0, a generalist with success 0.6 everywhere, and a specialist for column 2. Under weights [0.2,0.6,0.2], the generalist wins at 0.6 while each specialist scores 0.2. Concentrating the supervisor on the two extreme columns gives the specialists 0.5 each, still below 0.6.

For local data, collect off-diagonal cells deliberately rather than testing only familiar pairings. Record counts and uncertainty separately if entries are estimates. Define the partner mixture relevant to deployment and inspect plausible shifts before choosing a policy. Self-play remains a useful diagnostic, but it answers a narrower question.

## Acceptance invariants

- Mixture values equal independent weighted row sums.
- Changed partner weights reverse winner.
- One-policy cross-play mean is unavailable.
- joint_policy_correlation_loss equals (mean diagonal minus mean off-diagonal) over mean diagonal; it is null when there is no off-diagonal or the diagonal mean is zero.
