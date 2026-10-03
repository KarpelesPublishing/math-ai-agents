# Method

After n_a pulls and s_a successes, the empirical mean is s_a/n_a. Greedy choice selects the largest empirical mean. UCB adds an exploration bonus sqrt(2 ln t / n_a), where t is the number of completed pulls (Equation 11.2 with c equal to the square root of two), favoring arms whose uncertainty remains large relative to their evidence.

Thompson sampling uses a Beta(1,1) prior for each Bernoulli arm. Its posterior is Beta(s_a+1,n_a-s_a+1). Each round draws one candidate mean from each posterior and chooses the largest draw. A posterior sample is a decision device, not a certificate that an arm's true mean equals that sampled value.

Cumulative pseudo-regret is sum_t [max_a mu_a-mu_(A_t)]. It uses the simulator's known means and measures expected reward forgone by choices. Realized net reward sums observed zero/one outcomes minus pull costs. These differ because sampling noise can favor a worse arm in a finite run. Information value is another quantity: it prices how evidence improves a future decision, not the historical cumulative shortfall.

A separate one-pull information calculation uses the final Beta posterior. For each possible sampled arm, it averages the best posterior mean after a hypothetical success or failure, then subtracts the best current posterior mean. The net value also subtracts one pull cost. This is the Bayesian value of information for one later arm choice, not cumulative regret or a recommendation to continue the original budget.

Supply arm means, a finite round budget, seed, and common pull cost. Each policy initializes untried arms once while budget remains, then uses its own decision rule. The simulator samples outcomes with a local seeded random generator, preserving offline reproducibility without modifying global random state.

The report gives pull counts, successes, pseudo-regret, and realized net reward for all policies. Curves show cumulative pseudo-regret by round. They are nondecreasing because each known-mean shortfall is nonnegative. Compare how frequently each policy visits the better arm, but do not rank policies statistically from a single seed. The changed case swaps means, testing whether early sampling and tie order affect the finite outcome.

The returned policy table also contains posterior means and gross/net one-pull information values. Inspect those separately from the regret chart: a policy can have accumulated regret even when an additional observation no longer changes its preferred action.

For worked interpretation and changed assumptions, read [use cases](use-cases.md).

## Limits

- This is a local calculation under declared inputs, not an empirical claim about a deployed agent.
- Read the returned assumptions and limitations before applying the numerical result.
