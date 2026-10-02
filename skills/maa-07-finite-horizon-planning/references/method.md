# Method

Let V_h(s) be the best expected return from state s with h decisions remaining. Terminal continuation defines V_0(s). For h>=1, Q_h(s,a)=r(s,a)+gamma sum_s' P(s'|s,a)V_(h-1)(s'), and V_h(s)=max_a Q_h(s,a). Recording the maximizing action gives a policy indexed by state and remaining horizon.

Backward induction starts with V_0 and builds V_1,V_2,...,V_H. Each stage uses only the previous stage's values. This separation prevents a within-stage update from accidentally pretending that extra decisions remain. Rewards are expected immediate state-action rewards; their outcome dependence is already integrated into the declared number.

Stopping must be represented as an explicit transition or action. The example's done state has a zero-reward self-loop, so extra horizon after termination adds nothing. Discount gamma scales later reward relative to present reward. Gamma=1 is valid for this finite computation, even though some infinite-horizon formulas require a strict discount. A terminal value can encode a declared continuation estimate, but it is not learned here.

Encode states as a JSON object, with an action list for every state. Each action supplies its immediate reward and a normalized transition vector aligned with next-state identifiers. Validation rejects unknown destination states, absent actions, invalid probabilities, and unsupported horizons.

The code initializes terminal values and repeatedly evaluates all actions from each state. Its returned tables preserve every value stage and policy stage. The figure shows the start state's value against remaining decisions, making horizon effects visible. Compare the first stage with the full-horizon stage before reading the selected action. In the changed case only horizon changes from three decisions to one. All transition and reward assumptions remain fixed.

For worked interpretation and changed assumptions, read [use cases](use-cases.md).

## Limits

- This is a local calculation under declared inputs, not an empirical claim about a deployed agent.
- Read the returned assumptions and limitations before applying the numerical result.
