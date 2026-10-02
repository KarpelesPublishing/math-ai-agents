# Method

For matrix M_ij, mean self-play is the average diagonal value. Mean cross-play averages off-diagonal values when at least two policies exist. These descriptive summaries weight their cells uniformly; they are not automatically the deployment estimand.

With target partner weights w_j summing to one, policy i has value V_i=sum_j w_j M_ij. A second weight vector computes another environment mixture over the same columns. Selecting argmax_i V_i conditions the recommendation on that distribution. Changing weights can reverse the winner even when every matrix entry is fixed.

The supplied entries are probabilities or compatible normalized performance values under a shared success definition. The runtime does not estimate them from counts. Matching task distributions, budgets, and measurement rules is an assumption of the comparison. If partners adapt to the selected policy, a frozen matrix may cease to describe their behavior; the report should then become a dynamic-game measurement design rather than a static guarantee.

Provide a square matrix and two normalized column-weight vectors. The function validates probabilities and dimensions, computes diagonal and off-diagonal summaries, then evaluates every row under both mixtures. It returns selected policy indices and their expected mixture values.

The figures show self-play diagonal values, partner-transfer values, and changed-supervisor values separately. Policy index identifies each row; retain a name mapping in reader notes when policies have operational names. In the changed case the primary partner mixture becomes concentrated on column 0. Predict whether that favors the first policy's strong diagonal or the second policy's more even transfer. No matrix observations change.

For worked interpretation and changed assumptions, read [use cases](use-cases.md).

## Limits

- This is a local calculation under declared inputs, not an empirical claim about a deployed agent.
- Read the returned assumptions and limitations before applying the numerical result.
