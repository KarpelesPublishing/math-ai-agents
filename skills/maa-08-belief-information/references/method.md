# Method

The predictive belief is b_minus(j)=sum_i b(i)P(j|i). For observation o, its probability is Z(o)=sum_j b_minus(j)O(o|j), and Bayes' rule gives b_plus(j)=b_minus(j)O(o|j)/Z(o). An observation with Z(o)=0 is impossible under the declared model and is rejected.

For reward vector r_a, acting now has value max_a sum_j b_minus(j)r_a(j). If the controller first observes, its gross expected decision value is sum_o Z(o) max_a sum_j b_plus_o(j)r_a(j). Gross value of information is the difference between that quantity and acting now. Net value subtracts the observation cost.

The maximum is taken after each possible observation because the action can adapt to the signal. Placing the maximum before averaging would price a fixed action and lose the decision benefit. An informative signal can still have zero value when it never changes the optimal action. Identical observation rows convey no state information at all. These are one-step values; the calculation does not solve a general partially observable planning problem.

Provide a prior belief, transition matrix, observation matrix, reward vector for each action, observed index, and observation cost. Kernel dimensions must align, all probability rows must normalize, and the observed index must exist. The function predicts belief, evaluates the observation likelihood, forms its posterior, and selects the best posterior action.

It then repeats the posterior calculation for every possible observation to obtain information value. The first plot compares prior, predictive, and posterior probability of state zero. The second varies observation cost while holding gross benefit fixed. In the changed case, replace the observation rows with identical distributions. Predict both the posterior and information value before execution.

## Apply this to an agent

The agent cannot directly observe every fact needed for release. Represent uncertainty as a belief, then compare acting now with acquiring an observation and choosing afterwards. A highly probable observation can still have no decision value.

For worked interpretation and changed assumptions, read [use cases](use-cases.md).

## Limits

- This is a local calculation under declared inputs, not an empirical claim about a deployed agent.
- Read the returned assumptions and limitations before applying the numerical result.
