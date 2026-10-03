# Method

For record i, let t_i be token cost, v_i declared decision value, and x_i in{0,1} retrieval status. The finite allocation maximizes sum_i v_i x_i subject to sum_i t_i x_i<=B. Freshness requires now-timestamp_i<=ttl_i. An authority-bearing record also requires its version to equal the current version.

The code uses exact zero-one knapsack dynamic programming over integer budgets. Descending budget updates prevent the same record from being selected repeatedly. Its frontier gives the greatest eligible additive value at every budget from zero to B. These values are supplied judgments, not embedding similarity or empirically learned information gain.

For compression, the implementation compares argmax_a Q_original(a) with argmax_a Q_compressed(a). Equal choices mean this particular decision is preserved. They do not imply the compressed memory retains every fact or supports every future task. Ties follow list order, so a genuine decision-preservation claim should also inspect whether a meaningful action gap remains.

Supply records with token counts, value, timestamps, time-to-live, authority flags, and version identifiers. The function checks numeric domains and rejects a timestamp later than now. It constructs freshness and authority validity before allocating budget. Invalid records remain visible in the returned table rather than disappearing without explanation.

The plot shows the eligible retrieval frontier against token budget. The metrics identify selected and excluded records, used tokens, and compression choices. In the changed case reduce the budget and alter the compressed action values. Predict which record remains affordable and whether the action still matches. The two interventions address separate questions, so report both rather than attributing the entire change to memory quality.

For worked interpretation and changed assumptions, read [use cases](use-cases.md).

## Limits

- This is a local calculation under declared inputs, not an empirical claim about a deployed agent.
- Read the returned assumptions and limitations before applying the numerical result.
