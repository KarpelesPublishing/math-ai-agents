# Method

For logits theta_i, softmax gives pi_i=exp(theta_i)/sum_j exp(theta_j). REINFORCE uses the score gradient d log pi_A/d theta_i=1{i=A}-pi_i. The update here is theta_i <- theta_i+alpha(R_A-b)(1{i=A}-pi_i), where b is the current expected shaped reward. A baseline independent of the sampled action's randomness reduces variability without changing the expected score-gradient direction.

This one-step experiment uses deterministic verifier reward after action selection. Shaped reward adds gamma Phi(terminal) with initial potential zero. In a properly terminated episodic construction, zero terminal potential preserves the original objective. A nonzero action-dependent terminal potential can change rankings, so the report exposes that condition.

Expected verifier reward is sum_i pi_i r_i; expected external success is sum_i pi_i p_i. They are different functions of the same policy. Independent evaluation draws actions and Bernoulli success from a fresh seeded stream. Its empirical rate has finite-sample noise and is not identical to the known constructed expectation.

Supply aligned verifier rewards, external success probabilities, and terminal potentials. Declare episodes, learning rate, discount, seeds, and evaluation count. Each seed begins with equal logits. Stable softmax subtracts the maximum logit before exponentiation, avoiding avoidable overflow.

At every training episode, the code samples one action, computes its centered shaped reward, updates all logits, and records expected unshaped verifier reward. After training, it reports the policy, expected external success, and a separate empirical evaluation rate. Curves are labeled by seed. Compare their direction with the external metrics rather than calling any upward reward curve task improvement. The changed reward vector is the only altered mechanism.

For worked interpretation and changed assumptions, read [use cases](use-cases.md).

## Limits

- This is a local calculation under declared inputs, not an empirical claim about a deployed agent.
- Read the returned assumptions and limitations before applying the numerical result.
