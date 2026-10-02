# Use cases

## Worked example

The default bank has one specialist for each of three tasks. Oracle coverage is 1. The selector chooses candidate 0 for every task, so actual success is only task 0's weight 0.2. All tasks are deployable, leaving deployed success 0.2.

The changed selector chooses the correct specialist for every task, raising actual success to 1. Deployment denies task 2, whose weight is 0.5, so deployed success is 0.5. Oracle coverage remains 1. Better selection extracted available capability, but the authority boundary still limits what the system may realize. None of these numbers forecasts a future model's maximum.

## Changed assumption

An oracle ceiling can be mistaken for a deployable system when a report omits the selector. The gap may be large even if every task has a correct candidate somewhere. Evaluating only bank coverage rewards availability without measuring the controller's ability to identify the right answer.

Another failure transports the finite ceiling to unseen tasks or candidate classes. The stated maximum is conditional on the supplied bank and distribution. Adding a new candidate can raise it; changing task weights can change it; a new interface can change feasibility.

The independent curve also becomes misleading under shared errors. Candidates may agree because they share a failure mechanism, not because repeated sampling created independent evidence. Use the finite success matrix to study actual overlap, and treat the independent curve as a labeled construction rather than an empirical extrapolation.

## New inputs

The transfer bank has oracle coverage 1 because candidate 0 solves both tasks. Selection chooses candidate 1, which solves only task 0, so actual success is 0.5. Task 1 is denied, but it was already a selected failure, leaving deployed success 0.5.

For local use, define the candidate bank and task success predicate before inspecting selection. Keep permission filtering outside correctness labels so a denied correct answer is not counted as a model error. Report the supported conditional ceiling together with actual selector performance and the missing measurements needed for any proposed expansion. Do not rename a finite bank result an open-ended capability maximum.

## Acceptance invariants

- Deployment<=selection<=oracle for every fixture.
- Prefix coverage is nondecreasing.
- Invalid selected indices are rejected.
