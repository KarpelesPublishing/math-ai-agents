# Use cases

## Worked example

The baseline succeeds on two of four runs, giving 0.5. The candidate succeeds on three of four, giving 0.75. All four task/run identifiers match, so the paired differences are 0,1,0,0 and their mean is 0.25. Their sample standard error is 0.25 under independent-pair sampling. The small table supports a descriptive matched improvement; it is not precise evidence of a deployment guarantee.

Easy-task rates are 1 for both procedures. Hard-task rates are 0 for the baseline and 0.5 for the candidate. Equal target weights reproduce 0.5 and 0.75. When the target mixture assigns 0.9 to hard tasks, the reweighted rates become 0.1 and 0.55. The observations did not change. The estimand did. Preserve that distinction when presenting the changed-case figure.

## Changed assumption

Repeated attempts can make a procedure's average look more certain than the task evidence warrants. Four runs on one task are not automatically equivalent to four independent tasks from a population. If failures share a document, environment state, or procedure configuration, the binomial and independent-pair uncertainty formulas can be too optimistic. Their names in the output keep those assumptions visible.

Another failure occurs when an observed subset is treated as the target population. Exposure may select difficult cases, favorable cases, or runs where a monitor was available. An exposure-conditional rate is useful only for its declared subset unless a sampling design justifies transport. The denominator should be reported beside the rate, including zero exposed observations as an unavailable conditional rate.

The transfer fixture contains different task/run keys for the two procedures. The raw rates still exist, but no matched difference can be calculated. Missing cells also prevent the proposed equal-task mixture from being estimated. Returning zero would falsely imply no difference; borrowing another procedure's outcome would fabricate evidence. The useful next step is to run both procedures on the missing matched tasks under the same evaluation contract.

## New inputs

Apply this method to compatible local records by keeping the sampling unit explicit. If a run identifier denotes a random seed, environment instance, or attempt number, document that meaning before comparing procedures. Choose the success predicate before examining outcomes, and preserve costs even when they complicate an appealing success-rate story.

The transfer table demonstrates the missing-data boundary. Its old procedure has one success on alpha, while the proposal has one failure on beta. That is insufficient for a matched comparison or a two-task target estimate. Export a measurement request that names the missing alpha/proposal and beta/old cells. When the data are supplied, recompute the matched and mixture quantities. Avoid converting a procedure average into a per-step reliability law; trajectory completion needs run-level evidence or a declared conditional process.

## Acceptance invariants

- Default matched mean is 0.25 over four pairs.
- Changed candidate mixture rate is 0.55.
- Unmatched transfer returns null difference and missing mixture estimates.
