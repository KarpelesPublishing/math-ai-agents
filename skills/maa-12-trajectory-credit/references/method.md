# Method

For a complete trajectory, the return target is G_t=r_t+gamma G_(t+1), with terminal continuation zero. For a truncated trace, this implementation initializes the final continuation from the supplied value estimate instead. The backward recurrence makes that distinction visible in every earlier target.

Monte Carlo updates V(s_t) by alpha[G_t-V(s_t)]. TD(0) uses delta_t=r_t+gamma V(s_(t+1))-V(s_t), replacing the next value with zero only at true terminal transition. Accumulating TD(lambda) first adds one to the current state's eligibility, updates every value by alpha delta_t e_t(s), then decays eligibility by gamma lambda.

All three rules receive the same reward sequence and initial values, but their online updates differ. A state revisited within the trace can accumulate eligibility or receive multiple updates. This notebook implements one sequential pass, not an asymptotic convergence experiment. Lambda controls how far a later error reaches backward; it does not manufacture missing future rewards.

How this relates to Equation (12.4). The chapter writes the forward view: each visited state moves toward its lambda-return. This notebook implements the backward view, accumulating eligibility traces applied online during one pass. For a terminal episode the two give identical updates when the updates are offline, meaning the value estimates are held fixed during the episode and the summed increments are applied at the end. With online updates, as here, they still agree exactly when no state repeats within the episode, because every update touches only states already visited and no later TD error reads them. When a state repeats, online updates change estimates that later errors use, and the result can differ from the Equation (12.4) update. The default trajectory has no repeated state, so its values 0.4 and 0.5 equal the forward-view updates.

Give the ordered state list, rewards, initial values, discount, learning rate, lambda, and exact terminal flag. The state list must have one more element than the reward list. Values must exist for every named state. The code computes backward return targets, then applies each update rule to its own independent copy of the initial value map.

The return plot shows the target associated with each transition, while the trace-error plot shows the online TD errors used by eligibility updates. Consult the three final value maps to compare credit assignment. In the changed case the final state's estimate is 2 and terminal is false. Predict how that bootstrap changes the targets before running the calculation.

## Apply this to an agent

A release outcome may arrive after drafting and review. Follow how that late consequence changes earlier state values. Mark whether the trace truly ended or was merely cut off; otherwise an assumed continuation can be mistaken for evidence.

For worked interpretation and changed assumptions, read [use cases](use-cases.md).

## Limits

- This is a local calculation under declared inputs, not an empirical claim about a deployed agent.
- Read the returned assumptions and limitations before applying the numerical result.
