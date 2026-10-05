# Method

Let reward R(a), expected adverse-event probability rho(a), penalty lambda>=0, and current permission A(a) describe an action. Penalty choice maximizes R(a)-lambda rho(a). A finite lambda trades reward against risk; it does not enforce rho(a)<=b or A(a)=true.

Authority filtering forms the set of actions whose permission predicate is true. The constrained choice further requires rho(a)<=b and maximizes reward within that intersection. An empty intersection returns no feasible choice. Abstention appears only if it is explicitly supplied with its own reward, risk, and permission.

An expected-risk limit is a statement about a probability or average, not a pathwise guarantee. A permitted action with rho=0.05 can still realize an adverse event. Similarly, a penalty-optimal action can violate the declared limit when reward is large enough. The method accepts supplied risks; it does not estimate them or prove that a real system's risk is below the given number.

Provide action rows and declare the risk threshold and penalty separately. Validation checks finite rewards, probability domains, and exact permission booleans. The function returns unconstrained penalty choice, authorized penalty choice, constrained choice, and the number of feasible actions. Every alternative remains in the table with its flags and penalized value.

Reward and risk plots use separate vertical units. Compare selected labels with those figures instead of reading a reward bar as safety evidence. Run the default case and identify the first filter that removes each rejected action. In the changed case raise the expected-risk limit to 0.25 while preserving rewards, risks, and permissions. Predict whether a forbidden action can become available through that change.

## Apply this to an agent

Apply current authorization before choosing among an agent's actions. Compare a reward penalty with an explicit expected-risk constraint. A finite penalty can still favor an unauthorized choice, and expected risk does not establish safety on every trajectory.

For worked interpretation and changed assumptions, read [use cases](use-cases.md).

## Limits

- This is a local calculation under declared inputs, not an empirical claim about a deployed agent.
- Read the returned assumptions and limitations before applying the numerical result.
