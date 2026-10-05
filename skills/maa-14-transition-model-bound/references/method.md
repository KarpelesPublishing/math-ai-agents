# Method

For each state, total variation between the true and modeled transition rows is half the sum of absolute probability differences. Uniform error epsilon is the maximum of those row distances. An average row error cannot replace that maximum in a uniform bound.

With common expected immediate rewards in [0,R], one fixed policy, and discount gamma<1, the chapter's discounted value bound is gamma epsilon R/(1-gamma)^2. This quantity applies under those prerequisites; it is not an estimate fitted to the finite error curve. Reward-model mismatch would need another term.

For H rewards and zero terminal continuation, the undiscounted finite-horizon bound is R epsilon H(H-1)/2. It also bounds the discounted finite calculation because discounting can only reduce these nonnegative error contributions. The implementation computes V_h=r+gamma P V_(h-1) and modeled W_h=r+gamma Q W_(h-1), starting both at zero, then records max_s |V_h(s)-W_h(s)|.

The kernels already absorb a fixed policy. A state-value bound alone does not provide the uniform action-value error and action gap needed to certify a choice ranking. Keep that missing prerequisite explicit.

Provide two aligned square probability matrices and one nonnegative reward vector. Every row must sum to one. Declare discount and horizon. The function computes the uniform total-variation error, maximum reward, both finite value recurrences, the actual maximum error at each horizon, and the two conditional bounds.

Figures use reward horizon on the horizontal axis and reward units on the vertical axis. Plotting bound and actual error separately avoids disguising a small error beneath a large envelope. In the changed case increase horizon from five to twenty and predict how the quadratic envelope changes. Inspect the actual curve independently; it need not grow at the same rate. Export common-reward and fixed-policy assumptions with the numerical result.

## Apply this to an agent

An agent planning with an approximate environment model may assign the wrong value to a workflow state. Compare the model with a declared reference kernel and inspect both actual value error and the conditional bound. This fixed-policy calculation does not certify the best action.

For worked interpretation and changed assumptions, read [use cases](use-cases.md).

## Limits

- This is a local calculation under declared inputs, not an empirical claim about a deployed agent.
- Read the returned assumptions and limitations before applying the numerical result.
