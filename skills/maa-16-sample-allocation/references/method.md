# Method

Under independent equal candidate correctness p, the probability that at least one of n candidates is correct is C_n=1-(1-p)^n. Under one shared good/bad condition, C_n=p for every positive n. Equal marginals do not distinguish those joint laws.

For n>1 with independent errors, this implementation defines selected success as q C_n, where q is the probability that the selector chooses a correct candidate conditional on one existing. Under the shared condition a bank that holds a correct candidate holds only correct candidates, so any choice from it is correct and selected success equals C_n=p whatever q is. When n=1 the selector is bypassed, so success is p. This convention matters: with independent errors, paying an unreliable selector can make two samples worse than one.

Expense is n c_sample+c_selector and serial latency is n t_sample+t_selector for multiple candidates. Single-candidate allocation omits selector overhead. Feasibility requires both quantities to lie within declared limits. The selected allocation maximizes success, breaking ties toward lower expense. A candidate count with high oracle coverage is not necessarily feasible or operationally best.

Provide candidate counts and all probability, cost, latency, deadline, and dependence inputs. Numeric validation rejects negative resource values, invalid probabilities, and unsupported counts. For each allocation the function calculates coverage, selected success, expense, latency, and feasibility, preserving every row for inspection.

The two figures compare oracle coverage and selector completion by sample count. Their gap is the selector boundary, not an error bar. The selected allocation may skip the visually highest point if it violates a resource constraint. In the changed case keep every scalar fixed and enable shared_error. Predict which row now wins and explain why sampling no longer improves coverage. Export dependence and selector assumptions with the result.

## Apply this to an agent

Generating more candidate actions helps only if the controller can select a correct one within its budget and deadline. Compare coverage with actual selection, then replace independent errors with a shared failure. More attempts cannot remove a failure common to every attempt.

For worked interpretation and changed assumptions, read [use cases](use-cases.md).

## Limits

- This is a local calculation under declared inputs, not an empirical claim about a deployed agent.
- Read the returned assumptions and limitations before applying the numerical result.
