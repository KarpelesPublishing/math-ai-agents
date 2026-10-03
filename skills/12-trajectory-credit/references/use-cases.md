# Use cases

## Worked example

Default returns are [1,1]. With alpha=0.5, Monte Carlo assigns draft and review values 0.5. TD(0) updates draft from a zero next value, leaving it at zero, then assigns review 0.5. TD(lambda) carries the later error back with eligibility 0.8, giving draft 0.4 and review 0.5.

In the changed truncated case, final bootstrap is 2. Returns become [3,3]. Treating that trace as terminal would incorrectly erase the supplied continuation estimate. Whether 2 is a good estimate is a separate question; the credit arithmetic simply makes its dependence explicit.

## Changed assumption

Bootstrapping can propagate a bad value estimate. Monte Carlo avoids that particular dependence in complete episodes, but it depends on the observed later return and can have high sampling variability. Neither target dominates in every setting.

The terminal flag is especially important in limited-budget logs. An observation window ending is not proof that the underlying task terminated. Setting terminal true after a timeout can systematically suppress continuation value. Setting it false at actual termination can add imaginary future reward.

Trace conventions also matter. Replacing traces and accumulating traces are different algorithms when states repeat. This implementation uses accumulating traces. Compare it with equations under that convention, and avoid claiming convergence from one pass over a short supplied trajectory. Learning-rate schedules, visitation, and process assumptions would need their own study.

## New inputs

The transfer case sets lambda to zero. Accumulating TD(lambda) then updates only the currently eligible state before immediate decay, so its final values should agree with TD(0) under the same sequential convention. This is an independent structural check rather than a visual similarity claim.

For local use, preserve reward timing and state identity, and mark whether the final boundary is real termination or missing observation. If the final value is a fitted estimate, record its provenance. A trajectory-credit report should show targets and bootstrap assumptions as well as updated values, so a surprising change can be traced to evidence rather than hidden continuation.

## Acceptance invariants

- Default MC draft 0.5 versus TD draft 0.
- Default trace draft 0.4.
- Lambda 0 transfer matches TD(0).
