# Use cases

## Worked example

Fast-release has penalized value 10-5(0.3)=8.5 and wins unconstrained penalty choice, but it is unauthorized. Among authorized actions, risky-authorized has value 8-5(0.2)=7 and wins the penalty comparison. It exceeds the default risk limit 0.1.

The hard constrained choice is reviewed-release, with reward 5 and risk 0.05. Abstention is also feasible but has reward 0. When the limit changes to 0.25, risky-authorized becomes feasible and wins at reward 8. Fast-release stays forbidden because a risk-threshold change cannot create permission. The three selected labels therefore answer different questions.

## Changed assumption

A large penalty can look like a safety rule while leaving prohibited behavior available. If reward grows or the penalty is miscalibrated, the controller may choose the forbidden row. The hard authorization predicate avoids that particular tradeoff by removing the action before optimization.

Risk estimates also carry uncertainty. A supplied value 0.05 is not evidence of a bound unless an evaluation or formal process supports it. This notebook does not add confidence limits to supplied probabilities. When a limit must be conservative, provide a justified upper estimate or use a separate measurement design.

Pathwise properties need another representation. A mean-risk constraint cannot ensure that every trajectory respects a temporal invariant or that a tool never receives an unauthorized command. Use an explicit monitor and effect trace for those questions. Keep refusal and escalation alternatives visible when no permitted action meets the risk contract.

## New inputs

The transfer limit is zero. Act has risk 0.01 and is therefore infeasible, even though its penalized value is 19 under penalty 100. Wait has risk 0 and reward-1, so it is the only constrained choice. Negative reward does not invalidate a feasible refusal.

For local use, identify who owns the permission predicate and who owns the risk threshold. State the adverse event precisely and keep its probability denominator consistent across alternatives. A practical report should explain which rows fail authority, which fail expected risk, and which remain available. It should not convert a low average into a guarantee about every run.

## Acceptance invariants

- Forbidden rows never enter constrained choice.
- Changed threshold admits risky-authorized only.
- Empty feasible set returns unavailable choice.
