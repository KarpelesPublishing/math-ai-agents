# Use cases

## Worked example

Initially the default policy is [0.5,0.5], with verifier reward 1.5 and external success 0.55. The verifier prefers action 1 with reward 2, while the task prefers action 0 with success probability 0.9. Learning toward the verifier can therefore raise reward while lowering expected task success.

The changed reward vector [2,1] aligns both rankings. Reward-directed learning can now increase external success. Exact final policies differ by seed, so the hand check focuses on rankings, normalization, and expected metrics rather than a selected flattering run. Separate evaluation remains finite evidence even when the constructed expectation is known.

## Changed assumption

Verifier agreement is not an independent correctness guarantee. If reward and external success share the same mistaken criterion, evaluation can repeat the training error. This experiment keeps them separate precisely to make that mismatch inspectable.

Reward shaping is another boundary. Potential differences can preserve optimal behavior under their assumptions, but arbitrary terminal bonuses do not inherit that guarantee. The transfer case assigns potential 2 to the zero-reward action, giving it shaped reward 2 against the other action's reward 1. Training can then favor external failure.

This runtime trains only a one-step finite policy. It does not train a language model or claim convergence of a general agent. Multi-step return estimation, function approximation, safety constraints, and deployment shifts need additional models and evidence. Record all seeds and evaluation counts rather than presenting one policy snapshot as a universal result.

## New inputs

In the transfer case, action 0 has unshaped reward 0 and external success 0, but terminal potential 2 makes its shaped reward 2. Action 1 has reward 1 and success 1. The shaping condition is false, so the learner is trained on shaped rewards [2, 1] while the external task prefers action 1. Read the fields by name: verifier_optimal_action ranks the unshaped rewards and still says action 1, but shaped_optimal_action ranks the rewards the optimizer actually uses and says action 0, and training_objective_conflicts_with_task is true. expected_training_reward is the unshaped expectation, while expected_shaped_reward is the quantity the plotted curves track and the one that rises. Predict that conflict before inspecting the seeded curves.

For a compatible local experiment, use a finite declared action set and an independently defined success predicate. Keep evaluation evidence outside reward adaptation. If the real question concerns a trajectory policy, treat this laboratory as a mechanics check and specify the missing return, state, and evaluation contracts before claiming broader learning capability.

## Acceptance invariants

- Every learned policy sums to 1.
- Verifier and external optimal actions disagree by default.
- Nonzero terminal potentials flag broken invariant condition.
