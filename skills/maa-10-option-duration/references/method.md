# Method

For an option of duration d with primitive rewards r_0,...,r_(d-1), its completed value is sum_(t=0)^(d-1) gamma^t r_t + gamma^d V_cont. The continuation discount depends on duration, not on the fact that the option has one convenient label.

The option is executable only when its initiation predicate holds. Its executed prefix is limited by remaining deadline and the declared interruption cap. Continuation value is added only if every primitive step executes and the termination flag is true. An executed prefix may have nonzero reward while completion remains false.

This is a deterministic trace calculation. It does not model a distribution of option durations or an internal stochastic policy. Those would require expected discounted rewards and state-dependent termination probabilities. The finite representation is still useful for catching a common modeling error: assigning the full continuation value to a macro-action that never reaches its promised boundary.

Each option row supplies a name, exact boolean initiation status, primitive rewards, exact boolean termination status, and optional continuation value. Global inputs specify discount, deadline, elapsed start time, and optional interruption cap. Validation rejects invalid counts, nonfinite rewards, and ambiguous truth values.

The function determines the available prefix, sums its discounted rewards, and conditionally adds completion continuation. It reports full duration, executed duration, completion, and continuation discount. The figures compare executed value and primitive-step count; they should not be combined because their units differ. Run the changed interruption case and inspect which reward terms disappeared. A high full-option value is irrelevant if the actual prefix cannot reach it.

## Apply this to an agent

A reusable agent skill has initiation conditions, primitive actions and a termination rule. Distinguish useful partial progress from a completed handoff when a deadline or interruption cuts the skill short.

For worked interpretation and changed assumptions, read [use cases](use-cases.md).

## Limits

- This is a local calculation under declared inputs, not an empirical claim about a deployed agent.
- Read the returned assumptions and limitations before applying the numerical result.
