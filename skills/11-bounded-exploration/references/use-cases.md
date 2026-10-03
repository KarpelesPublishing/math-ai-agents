# Use cases

## Worked example

In the default world, the optimal mean is 0.7 and the other arm's mean is 0.4. Every pull of the worse arm contributes 0.3 pseudo-regret; a pull of the best contributes zero. Therefore each policy's final regret must equal 0.3 times its worse-arm pull count, independent of realized successes.

The common cost 0.05 changes net observed reward but not pseudo-regret between arms, because it applies equally to every pull. The changed world reverses which arm is optimal. Counts and trajectories can change substantially even though the mean gap stays 0.3. That is a finite exploration diagnostic, not an empirical result about real tools.

## Changed assumption

Stationarity is a central assumption. If an arm's success probability changes with time, task type, or another agent's behavior, the single mean no longer describes the process. A policy can then look stubborn because its accumulated evidence belongs to a different world.

The seeded comparison also does not provide a confidence interval for policy performance. Policies consume random numbers differently, especially Thompson sampling, so the same seed is a reproducibility device rather than perfectly matched outcome exposure. Use repeated independently declared seeds and a suitable comparison design for statistical claims.

A simulator oracle is not a deployed capability. Real logs usually do not reveal the true means needed for pseudo-regret. When those means are unavailable, report observed reward and an evaluation design instead of treating empirical averages as known truths.

## New inputs

The transfer problem has three arms, with gaps 0.6,0.3,0 relative to the best mean 0.8. Its pseudo-regret must equal 0.6 n_0+0.3 n_1. Check that identity against each returned count vector.

For a local exploration plan, specify budget, outcome predicate, arm availability, and the evidence supporting stationarity. Different tool costs require an extended objective rather than the equal-cost comparison here. Keep exploration expense separate from any proposed value-of-information calculation. If the real task asks whether one extra observation is worthwhile, use the belief and information method rather than relabeling regret.

## Acceptance invariants

- Pull counts sum to round budget.
- Regret equals the independent mean-gap calculation.
- Repeated same input gives identical seeded results.
