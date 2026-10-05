# Use cases

## Worked example

The default prior is equally split and the transition preserves it. Observation zero produces posterior [0.9,0.1]. Acting now has value zero because either action has equally weighted gains and losses. After observing, the controller can choose the appropriate action, giving expected value 8 before cost and 7 after cost.

The gross information value is therefore 8. With identical observation rows in the changed case, the posterior remains [0.5,0.5] regardless of the signal. Gross information value falls to zero and net information value becomes -1. The signal still arrives, but it does not earn its cost.

## Changed assumption

A belief update can be mathematically correct under an incorrect observation model. If a tool's signal changes distribution, or if hidden states were defined too coarsely, the posterior can look confident without being calibrated. Inspect the likelihood source rather than treating normalization as validation of the world model.

Information also has opportunity cost. The implemented cost is a single utility deduction; a deadline or state transition during observation would require a larger model. Likewise, this function assumes the same action set remains available after the observation.

An impossible signal should not be assigned an arbitrary uniform posterior. It is evidence that the declared boundary is incomplete or the input is inconsistent. The rejection asks you to repair that model rather than fabricate a belief. Preserve unmodeled outcomes in the next measurement design.

## New inputs

The transfer case predicts a new belief before receiving observation one. Its transition mixes the initial states, so the prior is not the correct distribution to insert directly into Bayes' rule. First calculate the predictive belief [0.6,0.4], then weight it by observation-one likelihoods [0.2,0.7] and normalize.

Use local data only when the state, observation, and action definitions share one boundary. If likelihoods are fitted estimates, retain their sample sizes and calibration limits outside this exact calculation. Report gross information value separately from cost so a negative net result can be traced to unhelpful evidence, high price, or both.

## Acceptance invariants

- Default posterior is [0.9,0.1].
- Identical likelihood rows give zero gross information value.
- Impossible observed signals are rejected.
