# Separate workbook solutions

## Original worked solutions


### Solution I.1

The base is `{\theta}`. Retrieval and the tool are the disjoint additions. Subtracting the base score gives isolated improvements of 0.12 and 0.09. The joint improvement is 0.33. Chapter 2's contrast is therefore `0.73-0.52-0.49+0.40=0.12`. The decomposition checks: `0.12+0.09+0.12=0.33`.

Both isolated gains and the total joint gain are positive, so the interaction share is defined. It is `0.12/0.33=4/11`, approximately 0.3636. Here that means roughly 36.36 percent of the joint improvement over the base is the amount left after subtracting the isolated improvements. 

The highest-score claim requires only comparison of 0.73 with the other scores. Positive cooperation requires the four-condition subtraction: the additive prediction from the isolated gains is 0.61, below the observed joint score. Those are different tests. Here positive cooperation names a positive interaction contrast, not an established internal mechanism. The scores do not identify how the components produce it; that requires further evidence.

### Solution I.2

No. The held-out targets influenced the choice of predictors, the forecasting family, and the stopping decision. Restricting the final fitting routine does not remove that information from the procedure that selected the routine. The test bank has become development evidence even if the final coefficient calculation did not read it.

Keep the current results as development results. Freeze the forecast target, available predictor definitions, model-selection procedure, evaluation metric, and prediction rule before opening a fresh test bank. Fix test membership by a declared rule without using its realized contrasts to make the forecast look favorable. Record the issued predictions before obtaining the target measurements. Evaluate those predictions once according to the frozen scoring rule; any revision informed by the results starts another development cycle and needs another genuinely unexamined test.

If the claim is that forecasting precedes assembly, preserve a dated record of which features were actually available then. A feature computed from the later agent's observed performance would violate that information boundary even if it were given an innocent name. The record should also identify the component definitions and evaluation contract that will generate `\Gamma_m`. Otherwise a forecast can appear successful because its target was quietly changed after issuance.

### Solution I.3

Under the corrected allowance, the joint gain is `0.58-0.40=0.18`. The isolated gains remain 0.12 and 0.09, so `\Gamma(r;t)=0.58-0.52-0.49+0.40=-0.03`. The decomposition is `0.12+0.09-0.03=0.18`. All gains required for the share's domain remain positive. Thus `\rho_\Gamma=-0.03/0.18=-1/6`, approximately -0.1667. The signed share records a shortfall from additivity; it should not be described as a positive fraction of cooperative gain.

The combined assembly remains best because 0.58 exceeds the other scores. Adding the tool without retrieval improves the score by `0.49-0.40=0.09`. Adding it with retrieval improves the score by `0.58-0.52=0.06`. The tool helps in both comparisons, but helps less when retrieval is already present. Negative interaction does not mean universal harm. Overlap or saturation can also produce a shortfall from additivity; these four means do not identify its mechanism.

Withdraw the original matched-cooperation claim. Its joint condition changed both components and resources relative to the intended factorial design. The matched rerun supports a narrower and different result: the combined assembly performs best among these conditions, with a negative interaction contrast at the original allowance.

The two joint scores differ by 0.15. Within the stipulated construction, the allowance is the only declared change to that assembly. An empirical resource-effect claim would additionally require confidence that the rerun preserved the other conditions and that sampling variation was handled. Subtracting unmatched experimental records does not supply those controls automatically.

### Solution II.1

Start at the final decision. The verified state has value `0.95(100)+0.05(0)=95`, because release terminates the episode. At the current state, immediate release has value `0.80(100)+0.20(0)=80`. Verification has current value `-6+0.90(95)=79.5`. Immediate release wins by 0.5 utility units.

The verified probability is better, but the route to it consumes immediate utility and delays the release reward. The tie occurs when `-6+95\gamma=80`, so `\gamma=86/95`, approximately 0.9053. Above that value verification wins; below it immediate release wins, holding the other assumptions fixed. 

Comparing the immediate cost -6 with reward 80 would omit verification's continuation value. The computation also needs the terminal convention. The reward 100 belongs to the release transition, not to an additional future state whose value should be discounted again. Counting both the reward and a terminal value of 100 would credit the same successful release twice. Here terminal value is zero, and each consequence enters exactly once.

### Solution II.2

A plausible output cannot validate an implementation that solves a different policy problem. The state must distinguish whether the verification opportunity remains. Chapter 5's `b_t` is the remaining resource coordinate in `x_t`; it can encode the remaining allowance alongside whatever other budget information the problem needs. A current document alone need not determine the permitted next actions or the future reward law.

The unverified state permits immediate release or the single verification. Verification consumes the allowance and leads to the verified state, whose available action in this problem is release. Release from either state leads to termination. The terminal state has value zero and no further reward-producing action. 

The two states cannot share one exact `\kappa` class. Their feasible action sets differ: the unverified state offers release and verify, while the verified state offers only release. Their terminal and permission labels agree, since both are nonterminal and both permit release. For the common action release, both enter the terminal class with probability one, so Equation (5.3) is not what fails. The reward law fails: release is correct with probability 0.80 in one state and 0.95 in the other. Their values also differ, 80 against 95. Merging them would give one class a single value and would lose the verification option.

A repeated-verification model would need evidence about what another verification observes, how errors correlate across attempts, how it changes subsequent correctness, what resources it consumes, and when it must stop. 

### Solution II.3

The verification route becomes `-6+0.75(95)=65.25`. Immediate release remains 80, so immediate release wins by 14.75. It also won in II.1; the change strengthens that preference rather than reversing it. The evidence has not become worse: the stipulated correctness after verification remains 0.95. What changed is the current value assigned to its delayed reward.

Permission expiry is different. If release is unauthorized on arrival at the verified state, its action value cannot remain an available option in the maximization. The state must record the relevant time or authority condition, and the available action set must reflect it. The numerical value of verification then depends on the actions that remain, such as an authorized fallback or return of control, and their rewards. Those have not been specified, so the earlier value 95 cannot be reused and no replacement numerical optimum follows.

Discounting expresses a preference among allowed consequences. Authorization determines which routes may be considered. A large penalty attached to an unauthorized release leaves it inside an optimization that might still select it if another reward becomes large enough. Removing it from the feasible set expresses the stated restriction directly.

### Solution III.1

The completed-pull clock is `t=80+20=100`. Each bonus is `\sqrt{2\ln(100)/N_t(a)}`. For A it is approximately 0.3393; for B it is approximately 0.6786. Adding the empirical means gives indices 1.0393 and 1.2786. B receives the next pull.

| Action | Exploration bonus | Full index |
|---|---:|---:|
| A | 0.3393 | 1.0393 |
| B | 0.6786 | 1.2786 |

B's smaller sample count gives it the larger uncertainty allowance. Its lower observed mean is outweighed by that allowance. An index above one is an optimistic selection score, not a reward probability. 

The bonus is not a computed `\operatorname{VOI}(O)`. It does not enumerate possible observations, update the current decision on each branch, and price the resulting improvement in optimized utility. It supports an exploration policy under Chapter 11's bandit assumptions. Calling it information value would obscure both that role and the separate decision calculation used in the following problems.

### Solution III.2

Before observation, acting has expected utility `0.50(12)+0.50(-2)=5`, above abstention's zero. After the first observation its utility is `0.60(12)+0.40(-2)=6.4`. After the second it is `0.40(12)+0.60(-2)=3.6`. Acting remains best on both branches.

The expected optimized utility after observation is `0.50(6.4)+0.50(3.6)=5`. Gross `\operatorname{VOI}(O)` is consequently zero. The observation changes the belief but never changes which action maximizes expected utility. With no other effect or cost, observing and not observing are tied for this decision. A positive acquisition cost would make observation strictly worse.

Acting breaks even when the good-state probability is `2/(12+2)=1/7`. The prior and both posteriors exceed that threshold. Their relative positions explain the result more clearly than the numerical subtraction alone. The belief moves entirely inside a region where the same action is preferred.

Reporting that the observation carries information, such as a posterior moving from 0.50 to 0.60, describes the change in belief. Decision value is the change in optimized utility, and here that change is zero.

### Solution III.3

Before observation, acting now has utility `0.50(12)+0.50(-10)=1`, so it is still preferable to abstaining. The two posterior action utilities become `0.60(12)+0.40(-10)=3.2` and `0.40(12)+0.60(-10)=-1.2`. Act after the first outcome and abstain after the second.

Expected optimized utility before paying for the observation is `0.50(3.2)+0.50(0)=1.6`. Gross information value is `1.6-1=0.6`. Subtracting the acquisition cost gives a net improvement of `0.6-0.50=0.10`. Equivalently, the purchased-observation route has value 1.10 against immediate action's 1. Acquire the observation under the stipulated contract. At a cost of 0.60, the routes tie; higher costs favor acting without it.

The new action threshold is `10/(12+10)=5/11`, approximately 0.4545. The posterior probabilities now lie on opposite sides of the threshold. The less favorable observation supports abstention, avoiding the negative expected utility of acting on that branch. This change in the decision boundary, produced by the larger bad-outcome cost, gives the unchanged observation channel value.

### Solution IV.1

Retrying duplicates the effect with probability 0.30, so its expected cost is `0.30(40)=12`. Declining misses the effect with probability 0.70, so its expected cost is `0.70(10)=7`. Declining is preferable. The corresponding utilities are -12 and -7.

Equation 17.3 gives the difference as `0.70(10)-0.30(40)=-5`, agreeing with the direct calculation. The retry threshold is `10/(10+40)=0.20`. The current belief 0.30 is above that threshold. At the threshold the alternatives tie; below it the omission risk outweighs the duplication risk under this cost model.

A lost response does not reveal whether the effect landed. The exercise starts by granting authority and specifying what the retry does. A real decision needs those premises established rather than supplied by arithmetic. If another attempt can also fail, if fees matter, or if authority has expired, this two-action calculation no longer describes the full decision. Its useful result is conditional and precise: with these effect semantics, belief, costs, and allowed choices, declining has five more expected utility units than retrying.

### Solution IV.2

The hash identifies a visible text representation. It does not establish equality of the composite states. The prompt coordinate `c_t` can match; stored memory `m_t` and remaining budget `b_t` can also match. The world coordinate `w_t` differs because the ledger contains an added entry in one execution and lacks it in the other. That distinction changes what another application does.

A belief over the effect states represents the agent's unresolved uncertainty. A read that locates the operation's authoritative ledger entry, reliably distinguishing this operation from others, could resolve the uncertainty if the service also guarantees the original attempt cannot apply later. Merely reading the last response stored in the client would not, since both client histories contain the same timeout. 

An interface that makes repeated application of this particular operation have the intended effect of one application can instead remove duplicate-effect cost in the simplified model. This is equality after Chapter 17’s intended-effect projection; request logs and budget need not match. Such semantics must actually cover the retry, including its identifying key and retention behavior; naming a request repeatable does not establish them.

A compensation is a different operation. It may create another ledger entry and new consequences, so successful compensation alone does not prove that the world equals the world in which the first entry never existed.

Known applied and complete means no repeat of the append. Terminal non-application permits a fresh attempt only if authority and preconditions still hold; a still-pending original could otherwise apply after the fresh attempt. Recovery must actually finish and verify restoration of relevant consequences and preconditions; its mere availability proves none of this, and outstanding attempts must be resolved or fenced against delayed effects.

### Solution IV.3

With a perfect read, decline if the effect is present and retry if it is absent. Both branches avoid duplication and omission under the construction. Expected loss before paying for the read is zero, compared with the best no-read loss of 7 from IV.1. Gross information value is 7. After the read cost of 1, expected utility is -1 instead of -7, a net gain of 6.

In the separate repeatable-interface design, duplication costs zero. A retry then has zero expected cost even without observation: it supplies the missing effect when needed and adds no duplicate-effect loss when the effect already exists. Declining still has expected cost 7. The no-read optimum is therefore retry, with utility zero.

Perfect observation cannot improve on that zero-loss outcome. Its gross value is zero, and purchasing it would reduce utility by 1. The observation still reveals something about the world. Its value to this particular choice disappears because the improved effect semantics already make an unobserved retry as good as acting with the additional information. This zero value depends on the exercise's absence of request costs and other failures. RFC intended-effect idempotence alone does not imply those premises.

### Solution V.1

At the stated split, S-U and L-T each carry 0.5, so each has physical latency 0.5. The outer routes each cost `0.5+1=1.5`. The unused middle route costs `0.5+0+0.5=1`. Total physical latency is `0.5(1.5)+0.5(1.5)=1.5`. This is not an equilibrium for physical-cost minimizers: a traveler on an outer route can improve by taking the middle route. Nonatomic travelers treat their individual effect on flow as negligible.

Marginal-cost latency doubles the flow-dependent edge latency and leaves a constant edge unchanged. Each variable edge therefore has experienced cost 1 at this split. Each outer route has experienced cost 2; the middle route also has experienced cost 2. No unilateral route change gives a strict improvement. The split is now an equilibrium under the corrected costs, including the unused route in the comparison.

| Route | Physical latency at split | Marginal-cost route cost |
|---|---:|---:|
| S-U-T | 1.5 | 2 |
| S-L-T | 1.5 | 2 |
| S-U-L-T | 1 | 2 |

Physical delay remains 1.5 in total. The correction prices delay imposed on others so that individual incentives reflect the system objective. A report that replaces physical latency with the corrected experienced cost would mix the institution's incentive with the outcome that institution was designed to improve.

### Solution V.2

When all messages arrive, A's history is: sent proposal, received acknowledgement, sent confirmation. A acts. B's history is: received proposal, sent acknowledgement, received confirmation. B acts. When the final confirmation disappears, A has exactly the same history and still acts. B's history lacks receipt of confirmation, so B does not act.

A cannot distinguish those executions from its local observations. The rule therefore permits a run in which only A acts, violating the stated coordination requirement. The failure is established by an explicit pair of permitted histories; it does not depend on estimating how often confirmation loss occurs.

An additional acknowledgement can tell A that B received confirmation if that acknowledgement arrives. It leaves B without an observation establishing receipt of the new acknowledgement. Whether that matters depends on the revised action rules. Merely extending the message list is not a proof that those rules satisfy safety in every permitted run. The analysis must again compare executions that differ by loss of the final message and inspect which local action can change.

### Solution V.3

Without U-L, outer flows sum to one and route costs are `1+q_{\mathrm{upper}}` and `1+q_{\mathrm{lower}}`. Both routes must be used at equilibrium: placing all flow on either creates cost 2 while the unused alternative costs 1. Equal used-route costs force equal flows of 0.5, giving total latency 1.5.

With U-L restored, all flow on the middle route produces physical cost 2 on every route. Used travelers cannot improve by switching, so it is an equilibrium. To see why positive outer flow fails, subtract the middle-route cost `1+q_{\mathrm{middle}}` from the upper-route cost `1+q_{\mathrm{upper}}+q_{\mathrm{middle}}`. The difference is `q_{\mathrm{upper}}`. A positive upper flow therefore uses a strictly more expensive route. The same argument applies to positive lower flow. Only the all-middle flow satisfies equilibrium.

For a fixed middle flow, distributing the remaining outer flow equally minimizes the two congestion-sensitive edge contributions. Chapter 21's resulting minimum is `1.5+0.5q_{\mathrm{middle}}^2`. Its minimum over feasible middle flows is 1.5 at zero. The shortcut network's equilibrium-to-optimum ratio is `2/1.5=4/3`.

This example shows that an added option can change individually rational routing in a way that worsens the declared collective objective. It does not prove that connections are generally harmful. The conclusion depends on the directed topology, latency functions, flow model, and individual objective. Those are the assumptions to inspect before carrying the argument into an agent network.

### Solution VI.1

The penalized scores are `7-2(0.50)=6` and `11-2(2)=7`. The proposed optimizer selects Aggressive, whose expected cost 2 exceeds the permitted 1. A finite penalty has traded against the violation rather than enforced the constraint.

For a mixture, expected cost is 0.50 plus 1.50 times the probability of choosing Aggressive. Setting that expression at most 1 gives a maximum Aggressive probability of `1/3`. Expected reward at that boundary is `7+(11-7)/3=25/3`, approximately 8.3333. Because Aggressive has the higher reward, this is the best feasible mixture of these two policies under the expected-cost condition. It exceeds Careful's reward while remaining exactly at the expected-cost limit.

Authorization is another distinction again. If Aggressive requires an action outside `\mathcal A_{\mathrm{auth}}(x)`, an acceptable average resource use does not permit executing it with positive probability. The allowable route set must exclude that policy at the relevant state. Among the two listed policies, Careful then remains the available choice, assuming its actions are authorized. 


### Solution VI.2

The stipulated one-candidate bound is `\exp(-200(0.25)^2/2)=\exp(-6.25)`, approximately `0.00193045`. For ten candidates that were each fixed before separate guard access and each met the same boundedness and independent-draw conditions, the union bound is at most `10(0.00193045)=0.0193045`.

The revised third candidate fails the fixed-before-guard condition. The result shown to its designer has become development evidence; the simple ten-decision accounting no longer supports a guard-based release claim for that revision. A newly frozen guard, or a newly declared evaluation plan with evidence not used to redesign the candidate, is needed.

Release is blocked unless `\operatorname{Authorized}_{\mathcal G}(\phi')=1`, the Boolean authority condition, holds. A complete canary record could name the service owner, rollback on a verifier failure, a one-business-day review deadline, and a fallback that restores the parent version and holds the affected action class. Other records can use different details, but they must be declared before the monitored release begins.

An audit should retain more than the two reported probabilities. It should identify the parent and candidate procedures, the rule that generated the candidate set, the development cases consulted, the guard membership rule, the evaluator version, and the time at which access closed. It should also record who authorized guard access, its query limit, and whether both procedures saw the same task version, tool responses, seeds, and resource limits. A bounded score difference can still mislead if one procedure received a newer tool, a larger retry budget, or a different task population.

Indirect access counts. A designer who never reads a guard score but receives a ranking, a failure example, or a pass-or-fail summary has still learned from the guard. The record should state which reports candidate designers could see. A report that changes a later candidate makes that guard development evidence for the candidate.

A fresh guard is not a reshuffle of the old rows. It needs cases whose outcomes and proxies have not informed the next design decision, under a declared task and evaluation contract. If that is impractical, the organization can make a narrower claim: it released a patch under monitoring, with authority and rollback controls, without applying the earlier bound to the adaptive sequence. That is less dramatic, but it is accurate.

### Solution VI.3

Immediate action has value `0.80(10)+0.20(-10)=6`. With guaranteed timely response, delegation has value `0.95(10)+0.05(-10)-1=8`, so delegation wins. Its expected resolution utility before the fee is 9.

Under the changed timing assumption, the deadline branches matter. Delegation has value `0.60(9)+0.40(2)-1=5.2`. The fee is subtracted once because it is paid on both branches. Immediate action's value remains 6 and now wins by 0.8.

| Route condition | Expected value |
|---|---:|
| Act immediately | 6 |
| Delegate with guaranteed timely return | 8 |
| Delegate with timely-return probability 0.60 | 5.2 |

For delegation to match acting, timely-return probability must weight resolution value 9 and fallback value 2 so that their average, minus the fee, reaches 6. Rearranging gives a minimum probability of `5/7`, approximately 0.7143. Above that boundary delegation wins; at it the routes tie. 

The destination's 0.95 correctness is conditional on timely return. Treating it as the success probability of the whole route would discard the deadline branch. `\operatorname{Del}(E,\Delta)` names a destination and a delay commitment precisely because a correct answer that fails to arrive in time does not implement the same action. Here the fallback is authorized and its utility is specified. Without those facts, a high conditional accuracy would leave the delegation decision incomplete.

### Worked record for C.1

Every row concerns `R-7` and `v2`, and authority is stipulated in all three problems. It would end if the permission expired (II.3) or the version changed.

| Stage | Belief (stipulated) | Action | Value or flip condition |
|---|---|---|---|
| II.1 | Release correct with probability 0.80 | Release | 80 against 79.5; verification wins only above `\gamma=86/95\approx0.9053` |
| IV.1 | Effect landed with probability 0.30 | Decline retry | Cost 7 against 12; retry wins only below belief 0.20 |
| VI.3 | Timely return with probability 0.60 | Hold, then delegate | Acting 6, delegating 5.2; delegation wins above probability 5/7, about 0.7143 |

Every belief is a stipulated probability. None establishes that `R-7` took effect, that the owner will answer, or that the utility scales are comparable.

The stages conflict at VI.3. Taken alone, acting again (6) beats delegating (5.2). But a second submission retries an unverified effect, which stage two declined, and a higher expected value does not enlarge the feasible set. Authority and the unresolved effect bind. The record therefore holds further submissions, and the handoff follows from that constraint, not from the comparison of 5.2 with 6, which does not price holding.

Unresolved: whether `R-7` took effect. Owner: the document owner. Deadline: the next day's noon review, as in the trace below. Fallback: keep submissions blocked and return control to the requester. The owner decides next whether to confirm completion or authorize one fresh attempt. Problem III.1 does not apply, because `R-7` is a single decision with no repeated pulls.


## Original expansion solutions


### E.1 Computer use

Without mediation, the coordinate policy completes the intended release with probability 0.6 and releases the unapproved record with probability 0.4. With complete current permission mediation, intended completion remains 0.6; the other branch is denied, and unauthorized release is zero within the construction. The monitor has changed the effect boundary without improving visual grounding.

Freshness is exp(-0.02 times delay). The three probabilities are approximately 0.9048, 0.7408, and 0.5488. The rate must count material changes that invalidate the selected binding, not every visual update. Periodic sorting, attacker-triggered changes, or a document update under an unchanged row can require a different model.

The expected denied-attempt cost is 0.2 times 3, or 0.6. A perfect observation costing 1 does not pay under those assumptions. The unguarded expected harmful-effect cost is 0.2 times 40, or 8. Removing that modeled loss for a cost of 1 gives a net advantage of 7. This diagnostic comparison does not grant permission to run an unguarded protected effect.

The semantic request still names v2 after the rows exchange places. The version-bound request is denied when the supplied state version is stale. Neither result proves that every real semantic interface binds objects correctly.

### E.2 Learning

External utility is 0.55 plus 0.20p. At p equal to 0, 0.5, and 1, the values are 0.55, 0.65, and 0.75. External success is separately 0.55 plus 0.25p; retrieval cost accounts for their difference.

The avoidance bonus adds 0.30 times (1-p). Training return becomes 0.85 minus 0.10p. Its three values are 0.85, 0.80, and 0.75. The modified objective prefers avoiding retrieval even though retrieval improves external success. The learner can optimize the supplied objective correctly while doing worse on the original criterion.

With zero terminal potential, shaped rewards are 0.4 and 0.6. Their sum remains 1. With terminal potential 0.2, they become 0.4 and 0.8, summing to 1.2. The surviving terminal term explains the difference. Policy ranking is preserved by the common-offset argument only under the stated boundary conditions.

The sampled probe changes policy parameters using selected-action gradients. Its exact expectations remain calculations in a known finite model. An observed success count estimates those quantities under its sampling procedure.

### E.3 Orchestration

Serial time is six seconds and total work cost is five. With capacity two, team time is three plus two, or five seconds; total work cost is eight. Parallel execution saves one second while spending three additional units.

With capacity one, checks consume six seconds before the two-second overhead, giving team time eight seconds. The same topology now loses on both reported dimensions relative to the declared serial procedure.

Each marginal failure probability is 0.1 plus 0.9 times 0.05, or 0.145. Joint failure is 0.1 plus 0.9 times 0.0025, or 0.10225. The product of marginals is 0.021025. A common source makes the product unsuitable even though residual failures are independent after conditioning on the source being sound.

The capability intersection contains read only. The worker's request for release supplies no grant, and the parent's verify capability is not automatically given when it was not requested.

### E.4 Resources

Cost per authorized success is approximately 1.6667 for A, 1.875 for B, and 2.3529 for C. These are ratios of population mean costs to declared completion probabilities, not estimates from the two later observed attempts.

Only B satisfies both the 0.75 minimum and three-second deadline. A fails the completion requirement; C fails the deadline. The lowest ratio does not identify a feasible choice by itself.

At a ten-second deadline, B and C are feasible. Their expected combined costs are 1.5 plus 0.2 times 20, or 5.5, and 2 plus 0.15 times 20, or 5. C is preferable under this declared failure valuation despite its higher cost-per-success ratio.

The observed unsuccessful attempts cost five units in total and produce zero successes. Their empirical cost-per-success ratio is undefined. The companion represents that unavailable number as null and retains the underlying counts.

### E.5 Evaluation

Mean single-run success is 0.5. Average two-run consistency is (0.04+0.64)/2, or 0.34. Average at-least-one coverage is (0.36+0.96)/2, or 0.66. Squaring the mean gives 0.25, while coverage applied to the mean gives 0.75.

Task-first repetition retains the same task across the two runs. Averaging probabilities before applying the nonlinear operation removes that shared task distinction. The two procedures need not yield the same result.

There are six two-run subsets of the observed bank. Three contain two successes, so observed all-success fraction is 0.5. All six contain at least one success, so its fraction is one. Their interpretation as population estimators requires the stated sampling assumptions.

The exposure mixture gives 0.2 times one plus 0.8 times 0.4, or 0.52. The increase over 0.4 is generated by the constructed composition. It does not establish an improvement on unfamiliar tasks or a measured contamination effect in any real benchmark.




## Chapter 1: separate solutions

## Question 1

List default pass flags.

Each score is compared with the default cutoff 0.5: 0.42, 0.46 and 0.49 fall below it and 0.52 and 0.56 do not, so the pass flags are 0,0,0,1,1.

## Question 2

Does changing only the cutoff prove model change?

No. Outputs remain fixed; the measurement transformation changes.

## Question 3

What is the first transfer slope?

(0.3-0.1)/(20-10)=0.02 score per scale unit.


## Chapter 2: separate solutions

## Question 1

Verify the decomposition.

The joint gain is 0.80-0.20=0.60 and the isolated gains are 0.30-0.20=0.10 and 0.25-0.20=0.05. The interaction is 0.80-0.30-0.25+0.20=0.45, and 0.60=0.10+0.05+0.45.

## Question 2

What changes when only the intact budget doubles?

The changed budgets are 10, 10, 10 and 20, so the matched-budget flag becomes false. The scores are unchanged, so the numeric contrast remains 0.45.

## Question 3

Is -0.30 a cooperation fraction in the transfer case?

No. In the transfer case the interaction is 0.70-0.50-0.55+0.20=-0.15 and the joint gain is 0.70-0.20=0.50, so the signed ratio is -0.15/0.50=-0.30. That value lies outside the chapter's fraction domain [0,1].


## Chapter 3: separate solutions

## Question 1

What are default fit coefficients?

The three development points (1,0.2), (2,0.3) and (3,0.4) lie on one line with slope (0.4-0.2)/(3-1)=0.1 and intercept 0.2-0.1(1)=0.1.

## Question 2

Does the changed test update the fit?

No. The fit uses only the development points, so the slope stays 0.1 and the intercept 0.1, and the predictions stay 0.5 and 0.6. The changed test values 0.8 and 0.95 only change the residuals (-0.3 and -0.35) and the error summaries.

## Question 3

Why must log-family scales be positive?

The real natural logarithm is undefined at zero and negative scales.


## Chapter 4: separate solutions

## Question 1

What is the default shortest authorized path?

draft -> review -> release, two edges.

## Question 2

Does the changed raw graph still reach release?

Yes; permission filtering removes the authorized bridge only.

## Question 3

Why is the transfer send action unusable?

Its initiation state approved is unreachable from queued.


## Chapter 5: separate solutions

## Question 1

Compute the default first kernel row.

[0.8*0.9+0.2*0.2,0.8*0.1+0.2*0.8]=[0.76,0.24].

## Question 2

Why can an independent-step model and a shared good-or-bad-condition model both have step marginals p?

They describe independent step failures and one shared good/bad condition, respectively.

## Question 3

Compute the transfer conditional product.

0.9*0.8*0.7=0.504.


## Chapter 6: separate solutions

## Question 1

Calculate release utility in the default case.

0.9*10+0.1*(-50)=4 utility units.

## Question 2

What first-outcome probability ties review under the default utilities?

60p-50=2, so p=52/60, approximately 0.8667.

## Question 3

Why does the transfer case not have a unique utility winner?

Retry and escalation both have expected utility 1; input order resolves the computational tie, not the valuation.


## Chapter 7: separate solutions

## Question 1

Compute draft value with two decisions.

max(2,-1+6)=5.

## Question 2

Why does horizon 3 not exceed horizon 2 here?

Both routes reach done, whose subsequent rewards are zero.

## Question 3

What is transfer later value?

0+0.5*4=2.


## Chapter 8: separate solutions

## Question 1

Compute default posterior.

[0.5*0.9,0.5*0.1]/0.5=[0.9,0.1].

## Question 2

What observation cost makes default information break even?

Acting now has expected reward 0.5(10)+0.5(-10)=0. After either observation the posterior is [0.9,0.1] or its mirror image, so the best action has expected reward 0.9(10)+0.1(-10)=8. The gross value of information is 8, so information breaks even at an observation cost of 8 utility units.

## Question 3

Compute transfer posterior after observation 1.

[0.12,0.28]/0.4=[0.3,0.7].


## Chapter 9: separate solutions

## Question 1

What is the default optimal path cost?

The route S,B,G costs 2+1=3 and the route S,A,G costs 1+4=5, so the optimal path cost is 3 via S,B,G.

## Question 2

Which changed heuristic condition fails?

Admissibility: h(B)=10 exceeds true remaining cost 1; consistency also fails on B->G.

## Question 3

What does h=0 produce?

Uniform-cost search on nonnegative edges.


## Chapter 10: separate solutions

## Question 1

What is default continuation discount?

0.9^3=0.729.

## Question 2

What is interrupted review-release value?

-1-0.9=-1.9, without continuation.

## Question 3

Why is transfer continuation contribution 2 rather than 4?

The transfer option takes 2 steps, so its continuation value 8 is discounted by 0.5^2=0.25, not 0.5, and contributes 8(0.25)=2 rather than 8(0.5)=4.


## Chapter 11: separate solutions

## Question 1

Express default regret through counts.

0.3 times the number of pulls of arm 0.

## Question 2

Does common pull cost change arm pseudo-regret?

No; identical cost cancels in the expected-reward comparison.

## Question 3

Express transfer regret.

The best transfer mean is 0.8, so each pull of arm 0 costs 0.8-0.2=0.6 and each pull of arm 1 costs 0.8-0.5=0.3. Regret is 0.6*n0+0.3*n1, where n0 and n1 count pulls of arms 0 and 1; pulls of the best arm add none.


## Chapter 12: separate solutions

## Question 1

Compute default trace update to draft.

Updating draft uses learning rate 0.5, a temporal-difference error of 1 at review (reward 1, no bootstrap) and trace weight discount times lambda, 1(0.8)=0.8: 0.5*1*0.8=0.4.

## Question 2

What are changed return targets?

[3,3], because final bootstrap 2 adds to final reward 1.

## Question 3

What should lambda = 0 match?

TD(0) under the same sequential update convention.


## Chapter 13: separate solutions

## Question 1

Compute initial default external success.

The default policy starts uniform and the success probabilities are 0.9 and 0.2, so initial external success is 0.5*0.9+0.5*0.2=0.55.

## Question 2

Which action has the highest default verifier reward?

Action 1, whose verifier reward 2 exceeds action 0's reward 1, despite its lower external success 0.2 against 0.9.

## Question 3

What are transfer shaped rewards?

[0+2,1+0]=[2,1], reversing the external objective.


## Chapter 14: separate solutions

## Question 1

Compute default epsilon.

Each row has half L1 distance 0.02; maximum is 0.02.

## Question 2

Compute horizon 20 finite bound.

With the common reward bound 1 and epsilon 0.02, the finite-horizon bound is 1*0.02*20*19/2=3.8.

## Question 3

What if the reward model also differs?

This transition-only bound is insufficient; add a declared reward-error term.


## Chapter 15: separate solutions

## Question 1

Why exclude old-review?

Its authority version v1 differs from current v2, despite being fresh.

## Question 2

What is default retrieval value?

The budget is 6 tokens. review-v2 (4 tokens, value 8) and summary (2 tokens, value 3) fit exactly, giving 8+3=11 within 6 tokens; old-review is excluded.

## Question 3

Does action preservation prove all future information survives?

No; it checks only the supplied decision vectors.


## Chapter 16: separate solutions

## Question 1

Compute default n=5 coverage and selection.

Coverage is 1-0.6^5=0.92224. Selected success is 0.92224*0.9=0.830016, because the selector finds a correct candidate with probability 0.9 when one exists.

## Question 2

Why prefer n1 under shared error?

With a shared error, coverage stays 0.4 whatever the count. For two or more candidates selected success is 0.4*0.9=0.36 and the selector adds cost, so one candidate (success 0.4) is preferred.

## Question 3

What if no allocation is feasible?

selected_allocation is unavailable; revise the allowed contract or abstain.


## Chapter 17: separate solutions

## Question 1

How many effects occur in the default trace?

Two effects. The first lost acknowledgement does not remove its effect.

## Question 2

What duplicate-harm value makes verification and retry tie?

Verification costs 1. Retry costs 0.2 plus the probability 0.8 that the effect already happened times the duplicate cost d. They tie when 1=0.2+0.8d, so d=1.

## Question 3

What happens when a stored idempotency key is reused with a different payload?

Validation rejects the conflicting key/payload contract.


## Chapter 18: separate solutions

## Question 1

Why does default coordinate completion fail?

The stored coordinate now targets delete instead of release.

## Question 2

Can matching versions replace current permission?

No. Permission is independently required.

## Question 3

What does observation age 3 do under max_age = 2?

All three methods refuse issuance until renewed observation.

## Question 4

With change_rate 0.02 per second, compute the no-invalidating-change probability for delays of 5, 15 and 30 seconds.

exp(-0.02*5)=0.9048, exp(-0.02*15)=0.7408, exp(-0.02*30)=0.5488, matching the freshness_by_delay field.


## Chapter 19: separate solutions

## Question 1

Compute default policy 1 mixture value.

0.5*0.4+0.5*0.9=0.65.

## Question 2

Why does the changed mixture favor policy 0?

Under the changed partner weights [0.9,0.1], policy 0 is worth 0.9(0.95)+0.1(0.2)=0.875 and policy 1 is worth 0.9(0.4)+0.1(0.9)=0.45. Its strong column 0 value 0.95 receives weight 0.9.

## Question 3

Which transfer policy wins?

Policy 1 is a generalist: it succeeds with probability 0.6 against every partner, so under weights [0.2,0.6,0.2] it is worth 0.6, while policies 0 and 2 are each worth 0.2.


## Chapter 20: separate solutions

## Question 1

Compute default disagreement.

0.51^2-0.3^2=0.1701.

## Question 2

Why can Bob know acknowledgement receipt at zero drops?

The declared model removes every world where the acknowledgement was lost.

## Question 3

Compute transfer agreement.

1-(0.75^3-0.5^3)=0.703125.


## Chapter 21: separate solutions

## Question 1

Compute default price of anarchy.

2/1.5=4/3.

## Question 2

Why exclude toll revenue from social travel time?

It is modeled as a transfer, not physical delay.

## Question 3

Compute transfer social optimum.

The optimal shortcut flow is z=capacity(constant_time-overhead)-demand=1(1-0)-0.5=0.5, which already lies within [0,0.5], so z=0.5. The total social time is (0.5+0.5)^2/(2(1))+1(0.5-0.5)+0(0.5)=0.5.


## Chapter 22: separate solutions

## Question 1

Which default action wins the hard constraint?

Only reviewed-release (risk 0.05) and abstain (risk 0) are authorized and within the limit 0.1; fast-release is unauthorized and risky-authorized has risk 0.2. Of the two, reviewed-release has the higher reward, 5 against 0.

## Question 2

Can risk_limit = 0.25 authorize fast-release?

No. Its current permission remains false, and its risk 0.3 also exceeds the limit 0.25.

## Question 3

Why does transfer choose wait despite negative reward?

It is the only authorized action satisfying risk<=0.


## Chapter 23: separate solutions

## Question 1

How many changed security violations occur?

Two: instruction promotion and forbidden publish execution.

## Question 2

Why does the changed plot rise only once?

It counts forbidden action executions, not instruction-promotion events.

## Question 3

Does a valid review of version A authorize publishing version B?

No. Review is bound to the document version.


## Chapter 24: separate solutions

## Question 1

Compute the default paired difference.

Differences 0,1,0,0 average to 0.25 over four matched pairs.

## Question 2

Compute candidate success under the changed hard-task weight.

0.1*1+0.9*0.5=0.55.

## Question 3

Why is the transfer matched difference unavailable?

Neither procedure shares a task/run key with the other; there are zero common pairs.


## Chapter 25: separate solutions

## Question 1

Why not release steady by default?

It was not the development-selected candidate; choosing it after guard inspection contaminates the guard role.

## Question 2

What changed gain allows flashy to pass?

One repaired outcome over 4 pairs gives 0.25>=0.2.

## Question 3

Does contamination erase observed gain?

No; it invalidates the clean acceptance claim, while descriptive gain remains.


## Chapter 26: separate solutions

## Question 1

What are default oracle,actual,deployed values?

Each task is solved by some candidate, so the oracle coverage is 1. Selecting candidate 0 for every task solves only task 0, so actual selection success is 0.2 (its weight), and with deployment allowed everywhere the deployed value is also 0.2. The three values are 1, 0.2 and 0.2.

## Question 2

Why is changed deployment 0.5 despite perfect selection?

The denied task has weight 0.5.

## Question 3

Can adding a candidate reduce oracle prefix coverage?

No; any previously covered task remains covered.


## Chapter 27: separate solutions

## Question 1

Compute default review mean.

Effective arrival 2; mean 1/(3-2)=1.

## Question 2

Why is changed stationary mean unavailable?

Arrival 3.6 exceeds service 3, so the M/M/1 queue is unstable.

## Question 3

Does mean 1 prove the transfer receipt arrived after 0.5?

No. It is a planning diagnostic; individual timing needs observed timestamps.


## Capstone solutions

1. Perfect preparation does not remove stale targeting, injected instructions, absent approval, unavailable review, acknowledgement loss, budget limits or deadlines. Success requires one intended, authorized and confirmed effect.
2. Probabilities for preparation, shared failure, layout, injection, acknowledgement and availability declare the environment. Refreshing, blocking, reviewing, retrying and verifying are policy branches. A reviewer capability and a perfect guard are assumptions of the construction.
3. A deployment claim requires an explicit task/population contract, actual effect and authority observations, representative runs, justified dependence assumptions, measured guard/reviewer behavior, resource accounting and an appropriate comparison. The simulation's exact rules cannot be silently attributed to a real system.
