# Method

For an action a with mutually exclusive outcomes o, the expected utility is EU(a)=sum_o P(o|a)u(o,a)-c(a). The outcome probabilities in each row must sum to one. Utilities need not be positive, and they need not use money, but all alternatives must share the same utility scale. A unit of benefit cannot be added to an hour of delay until you state how those quantities enter one valuation.

The selected action is an argmax of this expected utility over the supplied action set. This is a decision rule under declared values, not a claim that those values are correct. Expected loss is the negative of expected utility in this implementation. It is not a second independent objective or an estimate of physical harm.

A break-even calculation exposes sensitivity. Let p be the probability of the first outcome of the first action, v its unknown utility, B the weighted utility of its other outcomes, c its cost, and A the best alternative's expected utility. The equality pv+B-c=A gives v=(A+c-B)/p when p is positive. At p=0 that utility cannot affect the choice, so the threshold is unavailable.

For a two-outcome first action, the probability curve holds both outcome utilities fixed and varies p. Its slope is the difference between those utilities. A steep line indicates strong sensitivity to probability calibration. The curve does not estimate p; it shows what would follow if p took each plotted value.

The input is an action table, encoded as JSON. Each row supplies a unique action name, its probability vector, a utility vector of the same length, and an optional nonnegative cost. Validation rejects nonfinite numbers, negative probabilities, totals that differ from one, and vectors that do not align. These checks prevent a plausible-looking average from concealing an invalid outcome space.

The computation creates one row per alternative with expected utility, expected loss, and cost. It selects the greatest expected utility and reports the first-outcome break-even utility against the best remaining alternative. Ties follow the input order; if a tie needs a different operational policy, define that policy before acting. The action plot marks each action by name on the horizontal axis, in input order, and shows utility units on the vertical axis; the markers are joined by a line only to show order, not a trend. Consult the returned table for action names.

A second figure appears when the first action has exactly two outcomes. It varies the first-outcome probability while assigning the remaining probability to the second outcome. Compare this sensitivity line with the constant value of the preferred alternative. For the changed case, alter the severe loss while preserving the probabilities. That isolates a stakes change from a belief change.

## Apply this to an agent

A document-release agent must choose among release, review and abstention using the stated consequences. Change the loss of an incorrect release before changing the probability estimate. The preferred action depends on both; the calculation supplies no new authority.

For worked interpretation and changed assumptions, read [use cases](use-cases.md).

## Limits

- This is a local calculation under declared inputs, not an empirical claim about a deployed agent.
- Read the returned assumptions and limitations before applying the numerical result.
