# Method

Let C(i,a) be the chooser probability of action a in state i, and T(a,j) the tool probability of next state j after that action. The composed kernel is K(i,j)=sum_a C(i,a)T(a,j). Its rows sum to one when both factors are normalized. A row-vector state distribution evolves as mu_(t+1)=mu_t K.

This finite factorization deliberately omits state-dependent tool effects beyond the declared action encoding. To model them, enlarge the state/action representation rather than silently crediting the chooser with tool behavior. The changed tool kernel leaves C fixed, so any distributional difference is attributable to that controlled factor change inside this construction.

For reliability, independent equal-probability steps give P(all n succeed)=p^n. A shared condition that makes every step succeed together with probability p gives P(all n succeed)=p. Both have marginal step success p. The general chain rule is the product of conditional probabilities P(S_t|S_1,...,S_(t-1)); supplied marginals are not those conditionals.

The conditional_success vector is therefore a separate input. Its product describes its own declared trajectory law and need not have the same length or dependence structure as the plotted equal-step cases. None of these constructed distributions predicts a real agent without corresponding evidence.

The assembly comparison makes the remaining system factors explicit. O maps state to observed context; M maps observed context through the declared memory transform; R applies the retrieval transform; C is the same frozen chooser; T supplies the tool effect. The assembly kernel is O M R C T. Every row-stochastic product remains row stochastic. These finite maps are a construction, not a representation learned from documents. The state and context encoding must contain whatever history matters for the intended Markov boundary.

Supply normalized chooser rows, normalized tool rows, and an initial state distribution. The chooser's action dimension must match the tool's row count, and the tool's next-state dimension must match the chooser's state count. The function multiplies the factors, then propagates the initial distribution for the declared number of steps.

The state-zero occupancy chart shows recurrence under the composite kernel. The two reliability charts use transition count on the horizontal axis and all-step success probability on the vertical axis. They are separate constructions, not estimates from the occupancy curve. Change the tool matrix while keeping the chooser fixed, then compare terminal state distributions. Use the explicit conditional vector to check the chain rule independently by hand.

Compare five assemblies: complete context, blurred memory, blurred retrieval, blurred observation, and a single-transition controller. Their declared resource allowances match in the default case. A blurred map sends either context to the same equal mixture, erasing its distinction before the fixed chooser acts. The recurrence comparison changes transition count while reserving the same allowance; it does not claim equal consumed work. Read assembly_budgets_matched and assembly_depths_matched before attributing an observed difference to one factor. The transfer case deliberately breaks budget equality.

## Apply this to an agent

Use the composed kernel to describe the agent built around the same frozen model. Compare memory, retrieval and tool assemblies, then distinguish a step success rate from the probability that the complete workflow succeeds.

For worked interpretation and changed assumptions, read [use cases](use-cases.md).

## Limits

- This is a local calculation under declared inputs, not an empirical claim about a deployed agent.
- Read the returned assumptions and limitations before applying the numerical result.
