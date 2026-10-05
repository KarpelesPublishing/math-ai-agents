# Method

Let S_ct be the binary success of candidate c on task t and w_t the normalized task weight. Oracle task coverage is O_t=max_c S_ct, giving weighted bank coverage sum_t w_t O_t. A supplied selector chooses c(t), so actual success is A_t=S_(c(t),t). With deployment permission D_t, deployed success is A_t D_t.

Pointwise, deployed success<=actual success<=oracle coverage. Weighted values inherit that ordering. The inequalities condition on this bank, task distribution, interface, and permission contract. They are not a universal maximum over possible models or future procedures.

The prefix coverage curve adds candidates in their supplied order and is nondecreasing. Candidate order changes that curve but not final full-bank coverage. The independent construction gives 1-(1-p)^n for equal independent candidate correctness p. Its diminishing increments are a property of that joint law, not evidence that actual candidate diversity is independent or that the bank predicts future progress.

Provide a rectangular candidate-by-task boolean matrix, normalized task weights, one selected candidate index per task, and one deployment permission flag per task. The code validates exact booleans and index ranges. It forms oracle, selected, and deployed task flags, then aggregates them under the target weights.

The first figure shows prefix coverage of the supplied bank. The second shows a separate independent constructed saturation law. Their labels distinguish observed finite structure from a hypothetical sampling model. In the changed case improve selection while denying deployment on the heaviest task. Predict all three aggregate values before execution. Export the bank identity and task boundary whenever reporting a ceiling.

## Apply this to an agent

A finite bank may contain a successful action that the agent cannot recognize or is not permitted to deploy. Separate oracle coverage, actual selection and authorized completion. The bank ceiling says nothing about unexamined tasks or future candidate classes.

For worked interpretation and changed assumptions, read [use cases](use-cases.md).

## Limits

- This is a local calculation under declared inputs, not an empirical claim about a deployed agent.
- Read the returned assumptions and limitations before applying the numerical result.
