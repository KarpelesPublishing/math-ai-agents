# Use cases

## Worked example

The default development line has slope 0.1 and intercept 0.1. It predicts 0.5 and 0.6 at unseen scales 4 and 5, matching the supplied test outcomes. RMSE and bias are zero up to numerical rounding.

The changed test outcomes are 0.8 and 0.95. The forecast remains 0.5 and 0.6 because the development data did not change. Residuals become -0.3 and -0.35, with negative bias and a positive RMSE. That failure is informative. Refitting after seeing it might improve the retrospective graph, but it would not repair the original prospective forecast.

## Changed assumption

The simplest leakage pattern is to move a disappointing test observation into the development set and continue calling the remaining assessment unseen. Another is to inspect several families against the same test outcomes and report only the best one. Both use the test to shape the prediction, so the reported errors cease to measure the original prospective protocol.

The implementation checks explicit scale overlap, but it cannot detect hidden reuse, shared tasks, or a family chosen after reading test results. Those are evidence-management problems. Record the family, data boundary, fit command, and forecast before opening the withheld outcome file.

A successful linear or log extrapolation also does not reveal an emergence mechanism. It is conditional performance of one declared family over one supplied range. New environments or measurement rules can break that relationship even if the development residuals were tiny.

## New inputs

The transfer data follows a logarithmic family. Doubling scale adds approximately log(2) to its outcome. Fit in log coordinates, then predict at scales 8 and 16. The slope is approximately 1 and the intercept approximately zero, so the predictions are approximately 2.0794 and 2.7726.

When applying the method locally, define the forecast target before choosing the family. It might be a continuous score, a completion probability, or another declared quantity. The runtime allows finite targets without pretending all are probabilities. Explain the target units and score transformation in the accompanying report. If a bounded probability is required, this unconstrained regression may be the wrong family.

## Acceptance invariants

- Default unseen RMSE is approximately zero.
- Changed test leaves coefficients fixed but raises RMSE.
- Overlapping development and test scales are rejected.
