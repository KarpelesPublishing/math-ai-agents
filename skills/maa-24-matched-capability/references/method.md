# Method

For procedure p, the observed success rate is s_p/n_p, where n_p counts all supplied rows for that procedure and s_p counts true success flags. This denominator is explicit. Exposure-conditional rates use only exposed rows and have a different denominator. They describe that observed subset; they do not automatically estimate success in the target task population.

For a matched task/run pair i, define d_i=Y_candidate,i-Y_baseline,i. Each difference is -1, 0, or 1. The matched mean is sum_i d_i/m over the m common pairs. When m is at least two, the reported standard error is the sample standard deviation of those differences divided by sqrt(m). This formula requires independent representative pairs for its usual sampling interpretation. Matching identifiers alone does not establish randomization or causal attribution.

The Wilson interval is reported for each procedure's binary rate. With z approximately 1.96, its center is (p_hat+z^2/(2n))/(1+z^2/n), and its half-width accounts for both p_hat(1-p_hat)/n and z^2/(4n^2). The interval is conditional on a binomial sampling model, not a universal confidence statement about correlated repeated tasks.

A target mixture uses weights w_t that sum to one and task-specific observed rates p_hat_p,t. Its estimate is sum_t w_t p_hat_p,t only when every positively represented task has observations for that procedure. Missing cells remain unavailable. None of these averages identifies the probability that an entire long trajectory succeeds.

Validate the records before computing rates. Procedure, task, and run identifiers must be nonempty strings, successes and exposure flags must be exact booleans, costs must be finite and nonnegative, and duplicate procedure/task/run rows are rejected. These requirements prevent accidental double counting and ambiguous pairing.

The computation groups rows by procedure, calculates denominators and rates, and then forms a separate intersection of task/run keys for the declared baseline and candidate. The matched difference uses that intersection alone. If it is empty, the difference and standard error are unavailable. With one matched pair, the point difference exists but sample standard error does not.

Task weights are an optional second input boundary. They must form a normalized probability distribution over named tasks. The code computes task-specific rates from the supplied rows and reweights them without altering the records. The rate chart shows observed procedure averages; the paired-difference chart shows the individual common-pair differences. Consult the table and metrics together so an impressive average does not erase a thin denominator, missing task cell, or different observation cost.

## Apply this to an agent

Evaluate the complete agent procedure, including retries, tools, budget and stopping rule. Pair comparable task/run outcomes and report missing pairs. A success average does not identify a stepwise error law or a causal improvement.

For worked interpretation and changed assumptions, read [use cases](use-cases.md).

## Limits

- This is a local calculation under declared inputs, not an empirical claim about a deployed agent.
- Read the returned assumptions and limitations before applying the numerical result.
