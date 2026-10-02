# Use cases

## Worked example

Default coverage at n=5 is 1-0.6^5=0.92224. Selected success is 0.9 times that value, or 0.830016. Cost and serial latency are both 6, so this allocation exactly fits the limits and wins among the listed options.

Under shared error, every multiple-candidate row has coverage 0.4 and selected success 0.36. The single candidate bypasses selection and remains at 0.4 with lower expense. It therefore wins. More samples now add cost without improving justified completion, even though each candidate has the same marginal correctness as before.

## Changed assumption

The formula q C_n is a declared selector model. Real selector accuracy can depend on candidate count, task difficulty, disagreement, or the distribution of wrong answers. A constant q should not be adopted merely because it makes the curve easy to draw. Measure it on held-out candidate sets or state its uncertainty.

Independence is another strong assumption. Repeated samples from one shared flawed context can agree for the wrong reason. The changed construction is deliberately extreme, showing why marginal correctness alone cannot justify the usual saturation curve.

Resource models also need care. Parallel generation changes latency, and a deadline can alter selector behavior. This notebook uses serial time and fixed overhead. If no row is feasible, the selected allocation is unavailable; it does not invent a smaller budget or recommend exceeding a hard limit.

## New inputs

The transfer case gives single-candidate success 0.7. Multiple candidates face selector accuracy 0.5 and overhead that makes them miss the three-unit deadline or six-unit budget. The feasible recommendation is one candidate, even though an oracle would see broader coverage in a larger bank.

For local allocation data, distinguish candidate success evidence from selector evidence. Record whether failures are independent, shared, or simply unknown. Unknown dependence calls for a measurement design or sensitivity constructions, not an automatic independence assumption. Use run-level evaluation after executing the chosen allocation to test actual authorized confirmed completion.

## Acceptance invariants

- Selected allocation meets both resource limits.
- Default coverage increases under independence.
- Shared errors make one candidate optimal here.
