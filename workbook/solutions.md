# Separate workbook solutions

The Mathematics of Artificial Intelligence Agents

A Readable Guide to Decisions, Planning, Memory, Tools, Learning, and Cooperation

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

Perfect observation cannot improve on that zero-loss outcome. Its gross value is zero, and purchasing it would reduce utility by 1. The observation still reveals something about the world. Its value to this particular choice disappears because the improved effect semantics already make an unobserved retry as good as acting with the additional information. This zero value depends on the exercise's absence of request costs and other failures. RFC 9110 idempotence alone does not imply those premises.

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

Authorization is a separate matter. If Aggressive requires an action outside `\mathcal A_{\mathrm{auth}}(x)`, an acceptable average resource use does not permit executing it with positive probability. The allowable route set must exclude that policy at the relevant state. Among the two listed policies, Careful then remains the available choice, assuming its actions are authorized. 


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

Unresolved: whether `R-7` took effect. Owner: the document owner. Deadline: the next day's noon review, as in the trace below. Fallback: keep submissions blocked and return control to the requester. The owner decides next whether to confirm completion or authorize one fresh attempt. Problem III.1 does not apply, because `R-7` is a single decision with no repeated pulls. IV.1's comparison needs the original unable to apply later.


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

# Chapter demonstration answers

<a id="demonstration-1"></a>

## Demonstration 1

With the larger-rise scores (0.1, 0.3, 0.6, 0.8 at scales 10, 20, 40, 80) and a cutoff of 0.70, which checkpoints pass, and what is the first graded step?

Only the last one: 0.8 >= 0.7, while 0.6 < 0.7. The first step is (0.3 - 0.1) / (20 - 10) = 0.02 score per scale unit.

**Prediction answer:** Scale 5.

The scores did not move. Only the 0.52 at scale 4 now falls short of 0.55, so the first pass is the 0.56 at scale 5.

**If you chose another answer:** Change the cutoff control from 0.50 to 0.55 on the gradual set: 0.52 < 0.55 fails at scale 4, and 0.56 >= 0.55 passes at scale 5.

<a id="demonstration-2"></a>

## Demonstration 2

Suppose the model law were 0.30, 0.30 and 0.40 for A, B and evidence, and the evaluator rewards evidence. What do greedy decoding and one sampled draw score?

Greedy returns evidence, the largest at 0.40, so it scores 1. One draw scores 0.30 x 0 + 0.30 x 0 + 0.40 x 1 = 0.40.

**Prediction answer:** It falls to 0.00.

Greedy still returns A (0.45), and an evaluator that rewards only evidence judges A a failure, so the score is 0.00.

**If you chose another answer:** Greedy returns A whatever the evaluator is. Change the evaluator control to rewards asking for evidence: A is judged a failure, so the score is 0.00.

<a id="demonstration-3"></a>

## Demonstration 3

A coding assistant gets each line right with probability 0.90. What is the chance a 20-line function is entirely right, and how does it change at 0.99 per line?

0.90^20 = 0.1216, about one in eight. 0.99^20 = 0.8179, about four in five, a factor of 0.8179 / 0.1216 = 6.7 from a nine-point gain per line.

**Prediction answer:** About 9 times.

0.95^40 / 0.90^40 = 0.1285 / 0.0148 = 8.7, about 9 times, from a gain of five points per token.

**If you chose another answer:** Compute 0.95^40 = 0.1285 and 0.90^40 = 0.0148 (or set length 40 and the 0.90 to 0.95 step): the ratio is 8.7, about 9 times.

<a id="demonstration-4"></a>

## Demonstration 4

In the larger-model comparison, which audit row decides that no verdict is possible, and why?

The counterfactual row: there is no matched smaller system differing in exactly one thing, because the two models differ in parameters, data and training recipe. 3 rows answered of 6, and the deciding row is the counterfactual, whose answer is that none is available.

**Prediction answer:** No, all five must be fixed.

The chapter says a claim is checkable only once all five are fixed, and an open row leaves a dispute that no chart can settle.

**If you chose another answer:** Set the declaration control to Scale axis: the figure marks it open, and the chapter says a claim is checkable only once all five are fixed.


## Chapter 2: separate solutions

## Question 1

Verify the decomposition.

The joint gain is 0.80-0.20=0.60 and the isolated gains are 0.30-0.20=0.10 and 0.25-0.20=0.05. The interaction is 0.80-0.30-0.25+0.20=0.45, and 0.60=0.10+0.05+0.45.

## Question 2

What changes when only the intact budget doubles?

The changed budgets are 10, 10, 10 and 20, so the matched-budget flag becomes false. The scores are unchanged, so the numeric contrast remains 0.45.

## Question 3

Is -0.30 a cooperation fraction in the transfer case?

No. In the transfer case the interaction is 0.70-0.55-0.50+0.20=-0.15 and the joint gain is 0.70-0.20=0.50, so the signed ratio is -0.15/0.50=-0.30. That value lies outside the chapter's fraction domain [0,1].

# Chapter demonstration answers

<a id="demonstration-1"></a>

## Demonstration 1

In the second example the singles are 0.55 and 0.50 and both operations score 0.70. What is Gamma, and may the ratio be called a fraction?

0.70 - 0.55 - 0.50 + 0.20 = (-0.15). The joint gain is 0.70 - 0.20 = 0.50, so the ratio is (-0.15) / 0.50 = (-0.30), a signed diagnostic and not a fraction because Gamma is negative. The pair has the highest score of the four cells yet scores 0.70 rather than the additive 0.85.

**Prediction answer:** Zero.

0.35 - 0.30 - 0.25 + 0.20 = 0: the joint gain 0.15 is exactly the two isolated gains 0.10 + 0.05.

**If you chose another answer:** Choose the case 'Additive: 0.20, 0.30, 0.25, 0.35': the joint gain 0.15 equals 0.10 + 0.05, so Gamma is exactly zero.

<a id="demonstration-2"></a>

## Demonstration 2

System B has baseline 0.50, so its singles are 0.52 and 0.51 and the pair scores 0.80. What are its four-cell and three-cell numbers?

Four cells: 0.80 - 0.52 - 0.51 + 0.50 = 0.27. Three cells: 0.80 - 0.52 - 0.51 = (-0.23), which is 0.27 - 0.50. The three-cell number is negative only because the baseline was removed twice.

**Prediction answer:** Smaller than 0.45.

0.80 - 0.72 - 0.71 + 0.70 = 0.07, far below 0.45: B's baseline already supplies most of its intact score. With three cells, 0.80 - 0.72 - 0.71 = (-0.63), negative.

**If you chose another answer:** Keep baseline 0.70 and four cells: Gamma is 0.80 - 0.72 - 0.71 + 0.70 = 0.07, smaller than A's 0.45. With three cells, 0.80 - 0.72 - 0.71 = (-0.63), negative.

<a id="demonstration-3"></a>

## Demonstration 3

With half of p's influence surviving, what do the neither and i-only cells read, and what is Gamma?

Neither: 0.20 + 0.5 x (0.30 - 0.20) = 0.25. I only: 0.25 + 0.5 x (0.80 - 0.25) = 0.525. Gamma = 0.80 - 0.30 - 0.525 + 0.25 = 0.225, which is 0.45 x (1 - 0.5).

**Prediction answer:** 0.00.

With the whole influence leaking, the p-off cells score like the p-on cells: i only 0.80 and neither 0.30, so Gamma = 0.80 - 0.30 - 0.80 + 0.30 = 0.

**If you chose another answer:** Set the surviving share to 1.00: the i-only cell reads 0.80 and the neither cell 0.30, so Gamma = 0.80 - 0.30 - 0.80 + 0.30 = 0.

<a id="demonstration-4"></a>

## Demonstration 4

With 1600 trials per cell, what is the smallest contrast whose interval excludes zero?

One cell: 0.4 / sqrt(1600) = 0.010. Gamma: 2 x 0.010 = 0.020. Smallest contrast = 1.96 x 0.020 = 0.039, so 0.05 clears zero and 0.03 does not.

**Prediction answer:** 0.15 clears zero, 0.05 does not.

At 400 trials the standard error of Gamma is 2 x 0.4 / 20 = 0.04, so the half-width is 0.078: 0.15 clears it and 0.05 does not.

**If you chose another answer:** Set trials to 400 and compare: Gamma's half-width is 1.96 x 0.04 = 0.078, so 0.15 clears zero and 0.05 does not.


## Chapter 3: separate solutions

## Question 1

What are default fit coefficients?

The three development points (1,0.2), (2,0.3) and (3,0.4) lie on one line with slope (0.4-0.2)/(3-1)=0.1 and intercept 0.2-0.1(1)=0.1.

## Question 2

Does the changed test update the fit?

No. The fit uses only the development points, so the slope stays 0.1 and the intercept 0.1, and the predictions stay 0.5 and 0.6. The changed test values 0.8 and 0.95 change only the residuals: 0.8-0.5=0.3 and 0.95-0.6=0.35. The mean residual is 0.325. Positive residuals mean that observations exceeded the forecast. This observed-minus-forecast convention matches the book and reader.

## Question 3

Why must log-family scales be positive?

The real natural logarithm is undefined at zero and negative scales.

# Chapter demonstration answers

<a id="demonstration-1"></a>

## Demonstration 1

With exact measurements and a = 1.5, c = 1.0, what loss does the fit forecast at C = 1, and what is the residual at 3 powers of ten?

Forecast = a x 1 + c = 1.5 + 1.0 = 2.5 because 1 to any power is 1. The observed value is also 2.5, so the residual is 2.5 - 2.5 = 0, at any distance.

**Prediction answer:** Bigger at 4 powers of ten.

For this constructed wiggle the bars on the right grow with distance: the fitted a and c trade off against b, and the forecast a + c drifts.

**If you chose another answer:** Choose the wiggle and compare the residual at 1 and at 4 powers of ten (the bars on the right): the miss grows with distance.

<a id="demonstration-2"></a>

## Demonstration 2

Keep the forecast as registered. The observed contrast is 0.46. What is the residual, and is it inside the interval?

Residual = 0.46 - 0.39 = 0.07. The interval ends at 0.456667, so 0.46 is just outside it: an assumption needs investigating, not hiding.

**Prediction answer:** Inside.

The interval runs from 0.323333 to 0.456667, so 0.36 is inside: one successful check, not a proof of the line.

**If you chose another answer:** Set the observed value to 0.36 with the forecast kept: the interval is 0.39 plus or minus 0.066667, from 0.323333 to 0.456667, so it is inside.

<a id="demonstration-3"></a>

## Demonstration 3

Take the metric-created jump with q = 0.1 + 0.1 x (m - 1) and a threshold of 0.65. Which member is the first to pass?

q(7) = 0.1 + 0.1 x 6 = 0.70 >= 0.65 and q(6) = 0.1 + 0.1 x 5 = 0.60 < 0.65, so member 7 is the first to pass.

**Prediction answer:** By 0.1, a small step like every other.

q rises by 0.1 at every member (0.4 to 0.5 at the jump), so the sudden event belongs to the cutoff, not to the model.

**If you chose another answer:** Choose the metric-created jump at threshold 0.50: q goes from 0.40 to 0.50, a step of 0.1 like every other, while the verdict jumps by 1.

<a id="demonstration-4"></a>

## Demonstration 4

Declare the log family on the first data set and let the outcomes flatten off. What is the frozen forecast at x = 4?

The log fit has slope 0.1780 and intercept 0.1937, so the forecast is 0.1780 x ln(4) + 0.1937 = 0.1780 x 1.3863 + 0.1937 = 0.440, close to the observed 0.45.

**Prediction answer:** The log family fits better, and the registered forecast is unchanged.

The log family has the smaller RMSE after the fact, but switching now would be a retrospective fit; the registered forecast keeps its own RMSE.

**If you chose another answer:** Declare the straight line and choose flattening off: the metrics show the log family with the smaller RMSE, yet the registered forecast stays as made.


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

# Chapter demonstration answers

<a id="demonstration-1"></a>

## Demonstration 1

Suppose a new state, audit, can only be entered from release. With the move from review to release denied, is audit reachable, and how many states does the controller reach in all?

No. Audit sits behind release, and release has no permitted path, so audit is unreachable too. The reached states are draft, review and archive, so 1 + 2 = 3 of the 5 states.

**Prediction answer:** No: release is lost, but draft, review and archive are still reached.

Release has no permitted path, and draft, review and archive remain: 1 + 2 = 3 of 4 states.

**If you chose another answer:** Choose 'Review to release' in the selector: archive is a dead end, so release has no permitted path, and draft, review and archive remain (3 of 4 states).

<a id="demonstration-2"></a>

## Demonstration 2

In a binary tree with p = 0.5, what is the expected number of open vertices at depth 4, and is the infinite tree's survival positive?

(2 x 0.5)^4 = 1^4 = 1.000 open vertex on average, and survival is 0 because d x p = 1 is not above 1.

**Prediction answer:** Yes: a finite sample can show one, although the infinite tree dies out.

Draw 3 at p = 0.30 shows an open path. A finite tree can; only the infinite tree's survival is zero below 1/2.

**If you chose another answer:** Set p to 0.30 and look at draw 3: it shows an open path to the bottom. The threshold concerns the infinite tree, not a finite drawing.

<a id="demonstration-3"></a>

## Demonstration 3

In the binary tree with p = 0.5, what is the committed-run probability, the expected number of open depth-two descendants, and the chance that a path exists?

Committed: 0.5^2 = 0.25. Expected count: 4 x 0.25 = 1.00. Existence: each branch gives 0.5 x (1 - 0.5^2) = 0.375, so 1 - (1 - 0.375)^2 = 1 - 0.390625 = 0.609375.

**Prediction answer:** Below 1 (0.64), yet a path exists with probability about 0.45.

4 x 0.4^2 = 0.64 is below 1, and a path still exists with probability 0.446464.

**If you chose another answer:** Choose p = 0.4 with 2 children: the expected count is 0.64, below 1, but the chance of a path is 0.446464. An average does not rule a path out, and above 1 would not make it certain either.

<a id="demonstration-4"></a>

## Demonstration 4

With the grant rate at 0.60 and the other rates as shown, is d x p above or below 1?

p = 0.95 x 0.98 x 0.60 x 0.80 = 0.44688 and d x p = 2 x 0.44688 = 0.89376, which is below 1. This matches 0.60 being under the break-even grant rate of 0.6713.

**Prediction answer:** p falls by about 2.25 times, and d x p falls below 1.

p goes from 0.67032 to 0.29792, a factor of 0.90 / 0.40 = 2.25, and d x p goes from 1.34064 to 0.59584, below 1.

**If you chose another answer:** Compare the grant rates 0.90 and 0.40 in the selector: p scales with the grant rate, 0.90 / 0.40 = 2.25, so p goes from 0.67032 to 0.29792 and d x p from 1.34064 to 0.59584, below 1.


## Chapter 5: separate solutions

## Question 1

Compute the default first kernel row.

[0.8*0.9+0.2*0.2,0.8*0.1+0.2*0.8]=[0.76,0.24].

## Question 2

Why can an independent-step model and a shared good-or-bad-condition model both have step marginals p?

A marginal fixes only each step's own success rate, not how steps depend on each other. In the independent model each step succeeds with probability p on its own. In the shared model one condition is good with probability p and every step succeeds exactly when it is good, so each single step still succeeds with probability p. Same marginals, different joint laws: p^n versus p for all n steps.

## Question 3

Compute the transfer conditional product.

0.9*0.8*0.7=0.504.

# Chapter demonstration answers

<a id="demonstration-1"></a>

## Demonstration 1

If a blind call requested 0.60 of the time, what would the fully connected assembly (row 5) score?

Blind rate = (1 - 0.60) / 2 = 0.20. Row 5 = 0.20 + 0.60 x 0.775 = 0.20 + 0.465 = 0.665.

**Prediction answer:** Row 6 rises from 0.300 to 0.420, the value of row 4.

Row 6 becomes 0.30 + 0.40 x 0.30 = 0.42, the same as row 4: a denied tool adds no information, only a second blind try.

**If you chose another answer:** Choose 'Makes a second blind call' with two calls allowed: only row 6 moves, from 0.300 to 0.420, because a second blind call rescues some requests but the denied tool adds no information.

<a id="demonstration-2"></a>

## Demonstration 2

With the default tool, what is the chance of state 0 after two transitions when the system starts in state 0?

K(0,0) = 0.76 and K(1,0) = 0.3 x 0.9 + 0.7 x 0.2 = 0.41. After two steps: 0.76 x 0.76 + 0.24 x 0.41 = 0.5776 + 0.0984 = 0.676.

**Prediction answer:** Down, from about 0.68 to about 0.38.

The default tool gives 0.76 x 0.76 + 0.24 x 0.41 = 0.676 and the changed tool gives 0.50 x 0.50 + 0.50 x 0.25 = 0.375.

**If you chose another answer:** Compare the default tool and the changed tool at two transitions: 0.676 against 0.375. The chooser's rows are the same, but the recurrent system is not, because K also contains the tool.

<a id="demonstration-3"></a>

## Demonstration 3

A tool is right with probability 0.75. How many bits does it deliver, and what is H(Y | O)?

H(Y | O) = 0.25 x 2.000 + 0.75 x 0.415 = 0.500 + 0.311 = 0.811 bits, so I = 1 - 0.811 = 0.189 bits.

**Prediction answer:** The information stays 0.531 bits and success stays at the model-only 0.300.

The report still delivers 0.531 bits, but no later call reads it, so success stays at 0.30: the bits arrived where no decision uses them.

**If you chose another answer:** Set the report to 'The run stops (tool, no recurrence)' at accuracy 0.90: the information is still 0.531 bits because it depends only on the tool, and success is still 0.300 because nothing reads the report.

<a id="demonstration-4"></a>

## Demonstration 4

With per-step success 0.90 and one retry per step, what is the chance of finishing 2 steps?

q = 1 - 0.10 x 0.10 = 0.99. Two steps: 0.99 x 0.99 = 0.9801.

**Prediction answer:** Closer to 0.1.

0.95^40 = 0.129: forty required steps at 0.95 leave about one run in eight intact, and the half-success horizon is about 14 steps.

**If you chose another answer:** Choose per-step 0.95 with independent steps: after 40 steps the chance is 0.129, closer to 0.1. The product falls fast even when each factor is near 1.


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

# Chapter demonstration answers

<a id="demonstration-1"></a>

## Demonstration 1

In the book's table with an unsupported release worth -400 and a day costing 40, what does releasing now score?

0.85 x 100 + 0.15 x (-400) = 85 - 60 = 25. Requesting evidence scores 92 - 12 = 80, so it still wins, and escalation (57.5) now beats releasing now.

**Prediction answer:** Release now loses most (85 to 25); evidence still wins, and escalation overtakes release.

Release now falls from 85.0 to 25.0, evidence from 92.0 to 80.0 and escalation from 59.5 to 57.5, so evidence still wins and escalation passes release.

**If you chose another answer:** Choose the book table and 'Made worse': release now falls by 60 (85.0 to 25.0), evidence by 12 and escalation by 2, so evidence still wins and escalation passes release even though no probability moved.

<a id="demonstration-2"></a>

## Demonstration 2

If releasing now had support probability 0.90, what hour price would make the two actions tie?

97 - 90 = 7 points. Below 7 requesting evidence wins; above 7 releasing now wins.

**Prediction answer:** Neither: they tie exactly at 85.0.

Request evidence scores 97 - 12 = 85 and releasing now scores 0.85 x 100 = 85: an exact tie, which Equation (6.3) does not break.

**If you chose another answer:** Set the hour price to 12 with release support 0.85: request evidence scores 97 - 12 = 85 and releasing now 85, an exact tie that the rule does not break.

<a id="demonstration-3"></a>

## Demonstration 3

With a square-root utility and a gamble paying 100 with probability 0.8, what is the certainty equivalent?

E[u] = 0.8 x 10 = 8, so CE = 8 x 8 = 64, which is 16 below the mean payoff of 80.

**Prediction answer:** Below the mean: 25.

With a square-root utility E[u] = 0.5 x 10 = 5, so CE = 25: the agent gives up 25 of mean payoff to remove the variance.

**If you chose another answer:** Choose the square-root curve with the gamble that pays 100 half the time: E[u] = 5, so CE = 25, below the mean of 50. The straight line gives 50 and the square gives about 70.7.

<a id="demonstration-4"></a>

## Demonstration 4

With a wrong answer worth -4 and declining worth 0, what is the answer threshold t?

t = (0 - (-4)) / (1 - (-4)) = 4 / 5 = 0.80, so only the 40 cases with p above 0.80 are answered.

**Prediction answer:** Coverage falls to 0.20 and the error rate falls to 0.050.

The threshold rises from 0.80 to 0.90, so 20 cases are answered instead of 40 and the error rate among them falls from 0.100 to 0.050.

**If you chose another answer:** Compare wrong answer -4 with -9 at declining 0: the threshold goes from 0.80 to 0.90, so coverage falls from 0.40 to 0.20 and the error rate from 0.100 to 0.050.


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

# Chapter demonstration answers

<a id="demonstration-1"></a>

## Demonstration 1

With gamma = 0.95, about how many steps does it take for a reward to fall to roughly a third of its value, and what is a reward of 100 worth at 20 steps?

The scale is 1 / (1 - 0.95) = 1 / 0.05 = 20 steps, and 100 x 0.95^20 = 35.8, roughly a third.

**Prediction answer:** Less than 1, but still above 0.

100 x 0.9^50 = 0.52: small, but every finite delay keeps a positive weight.

**If you chose another answer:** Set gamma to 0.90 and steps to 50: the worth is 0.52, below 1 but above 0, because a finite delay never reaches zero.

<a id="demonstration-2"></a>

## Demonstration 2

If a verified release were worth 90 (support probability 0.90), release at once were worth 85 and verifying cost 8, what would verifying be worth at the start with gamma = 1, and does the controller verify?

Verifying is worth (-8) + 90 = 82 and releasing at once is worth 85, so the controller releases. The break-even cost is 90 - 85 = 5.

**Prediction answer:** Verify, then release.

Verify then release scores (-5) + 97 = 92, which beats 85 by 7.

**If you chose another answer:** Choose the chapter's controller and step to the start state: verify then release scores (-5) + 97 = 92, above 85.

<a id="demonstration-3"></a>

## Demonstration 3

In the now or later model with two decisions left and gamma = 0.2, which action is worth more, and by how much?

Later = 0 + 0.2 x 4 = 0.8 and now = 1 + 0.2 x 0 = 1.0, so now wins by 0.2. The break-even discount is (1 - 0) / 4 = 0.25.

**Prediction answer:** Prepare with two left, cash with one left.

With two left, prepare is (-1) + 1 x 6 = 5 against cash 2. With one left, preparing is worth -1 because no decision remains to release.

**If you chose another answer:** Choose the cash or prepare model at discount 1.00 and step the decisions remaining: two left gives prepare 5 against cash 2; one left gives prepare (-1) against 2.

<a id="demonstration-4"></a>

## Demonstration 4

For the all-zeros guess at gamma = 0.9, the residual is 97. What does Equation (7.5) allow the error to be, at most?

97 / (1 - 0.9) = 97 / 0.1 = 970. The true error is 97, well inside that ceiling.

**Prediction answer:** Far above the actual error.

The residual is 97 and 97 / (1 - 0.99) = 9700, a hundred times the true error of 97.

**If you chose another answer:** Set gamma to 0.99 at the all-zeros stage: the bound is 97 / 0.01 = 9700 against a true error of 97. Dividing by 1 - gamma inflates it.


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

# Chapter demonstration answers

<a id="demonstration-1"></a>

## Demonstration 1

Start from (1/3, 1/3, 0, 1/3) with a move that goes west with chance 0.2 instead of 0.1. What is the west-end weight after the first non-goal report?

Predicted west end = 0.2 x (1/3) + 0.2 x (1/3) = 0.133. The goal is predicted to hold 0.8 x (1/3) + 0.2 x (1/3) = 1/3, so the report keeps 1 - 1/3 = 2/3. West end = 0.133 / 0.667 = 0.200.

**Prediction answer:** No, it becomes (0.6, 0.4).

Predicted first state = 0.8 x 0.7 + 0.2 x 0.2 = 0.60, so the belief is (0.6, 0.4). The report must be weighted against this predicted belief.

**If you chose another answer:** Choose the notebook transfer case and step to the second stage: the first state gets 0.8 x 0.7 + 0.2 x 0.2 = 0.60, so the belief is (0.6, 0.4).

<a id="demonstration-2"></a>

## Demonstration 2

With prior 0.50 and a runner that always reports pass when the tests pass, what false-positive probability puts the posterior exactly at 0.80?

0.5 / (0.5 + 0.5 x f) = 0.8 gives 0.5 + 0.5 x f = 0.625, so f = 0.25. Below 0.25 the pass report clears 0.80; above it does not.

**Prediction answer:** It falls from above 0.80 to below it.

0.5 / (0.5 + 0.5 x 0.03) = 0.9709 is above 0.80, and 0.5 / (0.5 + 0.5 x 0.30) = 0.7692 is below it.

**If you chose another answer:** Compare the first two instruments at prior 0.50: 0.9709 for false-positive 0.03 and 0.7692 for 0.30, so the posterior falls below 0.80.

<a id="demonstration-3"></a>

## Demonstration 3

For plans (4, 1) and (0, 3), at what belief on the first state do they tie?

4b + 1 x (1 - b) = 3 x (1 - b) gives 3b + 1 = 3 - 3b, so b = 1/3. Above 1/3 plan 1 is larger; below it plan 2 is.

**Prediction answer:** Plan 2, with 2.25.

Plan 1 is 4 x 0.25 + 1 x 0.75 = 1.75 and plan 2 is 0 x 0.25 + 3 x 0.75 = 2.25, so plan 2 is selected.

**If you chose another answer:** Choose the two contingent plans at belief 0.25: plan 1 is 4 x 0.25 + 1 x 0.75 = 1.75, plan 2 is 0 x 0.25 + 3 x 0.75 = 2.25.

<a id="demonstration-4"></a>

## Demonstration 4

With the chapter's tool, prior 0.5 and no price, what is the value of the look?

After a pass: 0.9 x 0.5 x 10 - 0.15 x 0.5 x 40 = 4.5 - 3.0 = 1.5, so release. After a fail: 0.1 x 0.5 x 10 - 0.85 x 0.5 x 40 = 0.5 - 17.0 = (-16.5), so decline at 0. Acting now: 10 x 0.5 - 40 x 0.5 = (-15), so decline at 0. Value = 1.5 + 0 - 0 = 1.5.

**Prediction answer:** No, exactly 0.

Identical rows leave the belief at (0.5, 0.5) after any report, so the same action stays best and the value is exactly 0; at price 1 the net is (-1).

**If you chose another answer:** Choose the notebook changed case: identical rows leave the belief unchanged, the best action never changes, and the value is exactly 0.


## Chapter 9: separate solutions

## Question 1

What is the default optimal path cost?

The route S,B,G costs 2+1=3 and the route S,A,G costs 1+4=5, so the optimal path cost is 3 via S,B,G.

## Question 2

Which changed heuristic condition fails?

Admissibility: h(B)=10 exceeds true remaining cost 1; consistency also fails on B->G.

## Question 3

What does h=0 produce?

Uniform-cost search on nonnegative edges: the queue orders by cost so far alone. On the transfer graph it still returns the optimal route source, middle, target at cost 4, not the direct cost 7, because a zero estimate is admissible.

# Chapter demonstration answers

<a id="demonstration-1"></a>

## Demonstration 1

If the edge from A to B cost 2 and the direct edge from s to B cost 7, what would B's record become after A is expanded?

3 + 2 = 5, which is strictly below 7, so the record falls to 5 and A becomes B's parent.

**Prediction answer:** No, it falls to 6.

A offers B the route 3 + 3 = 6, strictly below the record of 7, so B's record falls to 6 and no estimate was involved.

**If you chose another answer:** Choose the bookkeeping graph and step to step 2: expanding A offers B the route 3 + 3 = 6, strictly below 7, so the record falls to 6.

<a id="demonstration-2"></a>

## Demonstration 2

In the notebook graph the rival route through A reaches G at cost 5 and B has recorded cost 2. What is the largest estimate at B that still lets B be expanded before that goal is selected?

B scores 2 + h-hat(B) and the goal scores 5, so h-hat(B) <= 3. At 3 the scores tie at 5 and B wins on smaller recorded cost (2 against 5). Above 3, the cost-5 route is returned although 3 was available.

**Prediction answer:** Yes, the cost-25 route.

The score of a is 1 + 25 = 26, above goal_b's 25, so goal_b is selected first and a stays on the queue: cost 25 against the best 10.

**If you chose another answer:** Choose the two-route graph at the fourth level: a scores 1 + 25 = 26, goal_b scores 25 and is selected first, so the search returns cost 25.

<a id="demonstration-3"></a>

## Demonstration 3

If the start's estimate is 8 and the upper edge costs 4 instead of 6, what is the smallest estimate at the upper vertex that satisfies consistency?

8 <= 4 + h-hat(upper) requires h-hat(upper) >= 8 - 4 = 4.

**Prediction answer:** Upper vertex first, score 7, below 8.

The upper vertex scores 6 + 1 = 7 against 3 + 5 = 8, so it is selected first, and 7 is below the start's 8: the estimate fell by 7 across an edge costing 6.

**If you chose another answer:** Set the start to 8 and the upper estimate to 1: the upper vertex scores 6 + 1 = 7, the lower 3 + 5 = 8, so the upper is first and its score is below 8.

<a id="demonstration-4"></a>

## Demonstration 4

In the notebook graph the estimate saves one expansion and needs 4 estimates. What is the most one estimate may cost for the estimate to break even?

1 x 200 / 4 = 50 ms per estimate. Above 50 ms the zero-estimate search is faster; below it the estimate pays.

**Prediction answer:** None.

Both searches select four vertices and expand three; duplicate merging has already removed the wasted alternatives, so the estimate saves nothing and any price is pure overhead.

**If you chose another answer:** Choose the research workflow: both searches expand the same three vertices (s, found, fetched), so the structural estimate saves none.


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

# Chapter demonstration answers

<a id="demonstration-1"></a>

## Demonstration 1

With no early stop and a start rule of at least 4, how many start states are allowed, and how long does the option run from x = 8?

The allowed states are 4, 5, 6, 7 and 8, so 8 - 4 + 1 = 5 states. From x = 8 it checks one record per step, so it runs 8 x 1 = 8 steps.

**Prediction answer:** It runs 4 steps from x = 6, and it cannot start from x = 3..

From x = 6 the option checks 6 - 2 = 4 records. Row x = 3 is below the start rule, so it is blocked.

**If you chose another answer:** Set the start rule to 4 and the early stop to 2 records remaining: from x = 6 the option checks 6 - 2 = 4 records, and row x = 3 is blocked because 3 is below 4.

<a id="demonstration-2"></a>

## Demonstration 2

With discount 0.9, rewards 2 and 3, and continuation 10, what is the value if the option takes 3 steps and the third step pays 0?

2 + 0.9 x 3 + 0.81 x 0 + 0.729 x 10 = 2 + 2.7 + 0 + 7.29 = 11.99.

**Prediction answer:** It grows, from 0.9 to 2.439..

The overstatement is 10 x (0.9 - 0.9^4) = 10 x (0.9 - 0.6561) = 2.439, up from 10 x (0.9 - 0.81) = 0.9.

**If you chose another answer:** Set the duration to 4 with the chapter example and discount 0.9: the overstatement is 10 x (0.9 - 0.9^4) = 2.439, up from 0.9 at duration 2.

<a id="demonstration-3"></a>

## Demonstration 3

In the parallel schedule with an unchanged source, how long must the audit take before it, rather than the chain Draft, Verify, Publish, sets the release time?

The chain takes 2 + 3 + 1 = 6 minutes, so the audit must take more than 6 minutes. At exactly 6 the two chains tie. The cost stays 4 + 7 + 2 + 3 = 16 credits.

**Prediction answer:** The audit sets 8 minutes, and the cost stays 16 credits..

T = max{2 + 3 + 1, 8} = max{6, 8} = 8 minutes, so the audit is the longest chain. The cost is still 4 + 7 + 2 + 3 = 16 credits.

**If you chose another answer:** Set the audit to 8 minutes in parallel with an unchanged source: T = max{6, 8} = 8 minutes, so the audit is the longest chain, and the cost stays 4 + 7 + 2 + 3 = 16 credits.

<a id="demonstration-4"></a>

## Demonstration 4

At discount 0.9, what is the value of review-release if it is stopped after 1 step?

Only the first reward is earned and nothing is discounted yet: 1 x (-1) = -1. This demonstration adds no continuation, so archive (1) is higher.

**Prediction answer:** Review-release is worth -1.9, so archive (1) is higher..

Only two rewards are earned: 1 x (-1) + 0.9 x (-1) = -1.9, with no continuation, so archive (1) is higher.

**If you chose another answer:** Choose 'interrupted after 2 steps' at discount 0.9: only two rewards are earned, 1 x (-1) + 0.9 x (-1) = -1.9, with no continuation, so archive (1) is higher.


## Chapter 11: separate solutions

## Question 1

Express default regret through counts.

Arm 1 (mean 0.7) is best, so each pull of arm 0 (mean 0.4) costs 0.7 - 0.4 = 0.3 and pulls of arm 1 cost nothing. Regret = 0.3 x n0. Check against the returned counts: greedy 0.3 x 2 = 0.6, UCB 0.3 x 31 = 9.3, Thompson 0.3 x 46 = 13.8, matching the reported pseudo-regrets.

## Question 2

Does common pull cost change arm pseudo-regret?

No. Pseudo-regret compares mean payoffs of arms, and a cost charged equally to every pull cancels from each gap. It only lowers net observed reward, by 0.05 x 120 = 6 for every policy (for example greedy: 90 successes - 6 = 84).

## Question 3

Express transfer regret.

The best transfer mean is 0.8, so each pull of arm 0 costs 0.8-0.2=0.6 and each pull of arm 1 costs 0.8-0.5=0.3. Regret is 0.6 x n0 + 0.3 x n1, where n0 and n1 count pulls of arms 0 and 1; pulls of the best arm add none. With the returned counts: greedy 0.6 x 1 + 0.3 x 1 = 0.9, UCB 0.6 x 9 + 0.3 x 25 = 12.9, Thompson 0.6 x 2 + 0.3 x 2 = 1.8, matching the reported values.

# Chapter demonstration answers

<a id="demonstration-1"></a>

## Demonstration 1

If tool A succeeds 0.78 and tool B 0.90, how much regret does an agent that rotates evenly build up over 500 tasks?

Half the tasks go to A and cost 0.12 each: 250 x 0.12 = 30. Equivalently 500 x 0.90 - (250 x 0.78 + 250 x 0.90) = 450 - 420 = 30.

**Prediction answer:** Stuck regret grows ten times; the optimistic run grows by less than ten times..

Stuck regret is 0.12 x 1,000 = 120 and 0.12 x 10,000 = 1,200, ten times. The optimistic run goes from 29.64 to 105.24, about 3.6 times.

**If you chose another answer:** Choose the ten-times-longer run in the book's world: stuck regret goes from 0.12 x 1,000 = 120 to 0.12 x 10,000 = 1,200 (ten times), while the optimistic run goes from 29.64 to 105.24, about 3.6 times.

<a id="demonstration-2"></a>

## Demonstration 2

At pull 5 of the table the counts are 3 and 1 after 4 completed pulls. With c = 1.414, what is B's bonus?

ln 4 = 1.386, so the bonus is 1.414 x sqrt(1.386 / 1) = 1.414 x 1.177 = 1.665 (rounded).

**Prediction answer:** Tool B, because its bonus is larger than the gap in means..

B's index is 0.000 + 1.665 = 1.665 and A's is 0.667 + 0.961 = 1.628, so B is called although its mean is lower.

**If you chose another answer:** Pick pull 5 with c = 1.414: B's bonus is 1.414 x sqrt(1.386 / 1) = 1.665, so its index 1.665 beats A's 0.667 + 0.961 = 1.628 and B is called.

<a id="demonstration-3"></a>

## Demonstration 3

With prior 0.85 and a check that is right 0.70 of the time, a report of unsupported leaves the release score at 70.8. Does that report change the action?

P(supported and report unsupported) = 0.85 x 0.30 = 0.255 and P(report unsupported) = 0.36, so the release score is 100 x 0.255 / 0.36 = 70.8. That is below 92, which is also the action chosen before the check, so this report changes nothing; only the supported report (score 92.97) does.

**Prediction answer:** It removes uncertainty but does not change the action..

The gain is positive, but a supported report moves the release score only to 100 x 0.8947 = 89.5, still below 92, so the same action wins and VOI is 0.

**If you chose another answer:** Set accuracy 0.60 and prior 0.85: the gain is positive (the reports correlate with the claim), but neither report lifts the release score above 92, so the action never changes and VOI is 0.

<a id="demonstration-4"></a>

## Demonstration 4

With a shift of 5, what is the gross value, and is the call worth buying at cost 2?

Release scores 80 after flag and 95 after clear, and 90 before. With the call: 1/3 x 92 + 2/3 x 95 = 94.0, so gross value = 94 - 92 = 2.0. Net = 2 - 2 = 0, a tie.

**Prediction answer:** Yes: gross value is 7/3 = 2.333, above 2, so the net value is 0.333..

With 10 added, flag leaves release at 85 (evidence wins, 92) and clear gives 100: 1/3 x 92 + 2/3 x 100 = 97.333 against 95 before, so gross 7/3 and net 7/3 - 2 = 0.333.

**If you chose another answer:** Set the shift to 10 and the cost to 2: with the call the best scores are 92 after flag and 100 after clear, 1/3 x 92 + 2/3 x 100 = 97.333, against 95 without it, so gross value is 7/3 = 2.333 and net 0.333.


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

# Chapter demonstration answers

<a id="demonstration-1"></a>

## Demonstration 1

In the draft, review, done run (step size 0.5, lambda 0.8, terminal) after one pass, what does the outcome rule give draft, and what does the one-step rule give draft?

The return from draft is 0 + 1 = 1, so the outcome rule gives 0 + 0.5 x (1 - 0) = 0.5. The one-step error at draft is 0 + 0 - 0 = 0 (review is still 0 when draft is updated), so draft stays at 0.

**Prediction answer:** All four under the outcome rule, only state 4 under the one-step rule..

The outcome rule moves every state to 0.5 + 0.1 x (1 - 0.5) = 0.55; the one-step errors for states 1 to 3 are 0 + 0.5 - 0.5 = 0, and only state 4 moves, 1 + 0 - 0.5 = 0.5.

**If you chose another answer:** Choose the four-action run at pass 1: the outcome rule moves every state to 0.5 + 0.1 x (1 - 0.5) = 0.55, while the one-step errors for states 1 to 3 are 0 + 0.5 - 0.5 = 0, so only state 4 moves.

<a id="demonstration-2"></a>

## Demonstration 2

Suppose three of the seven B-only episodes pay 1 and the A episode ends at 0. What is B, and how far is the outcome rule's value for A from the one-step rule's?

B = (3 + 0) / 8 = 0.375. The outcome rule gives A = 0, the one-step rule gives A = 0.375, so they differ by 0.375.

**Prediction answer:** Outcome rule 0, one-step rule 0.75..

B = (6 + 0) / 8 = 0.75. The outcome rule copies A's one return, 0; the one-step rule gives A = 0 + B = 0.75.

**If you chose another answer:** Use six ones and an A episode ending at 0: B = (6 + 0) / 8 = 0.75, the outcome rule gives A the one return it saw (0), and the one-step rule gives A = 0 + B = 0.75.

<a id="demonstration-3"></a>

## Demonstration 3

With 8 transitions remaining and lambda = 0.3, what weight does the first target get, and what does the complete return get?

First target: 1 - 0.3 = 0.7. Complete return: 0.3^7 = 0.0002187, which the figure labels as less than 0.001. The weights still add to 1.

**Prediction answer:** The complete return, 0.9^7 = 0.478, against 0.1 for the one-step target..

The complete return gets 0.9^7 = 0.4783 and the one-step target gets 1 - 0.9 = 0.1, as in Figure 12.4.

**If you chose another answer:** Set lambda to 0.9: the one-step target gets 1 - 0.9 = 0.1, while the complete return gets the remaining weight 0.9^7 = 0.4783, as in Figure 12.4.

<a id="demonstration-4"></a>

## Demonstration 4

At step size 0.5, what is the estimate of y after training, and which action does the controller now choose?

delta = 1 + 0 - 0.5 = 0.5, so the estimate becomes 0.5 + 0.5 x 0.5 = 0.75. Inspect scores -0.1 + 0.75 = 0.65, above finish's 0.6, so the controller now inspects.

**Prediction answer:** 0.50 and 0.80: any successor above 0.22..

delta = -0.02 + successor - 0.20: 0.10 gives -0.12, 0.50 gives 0.28 and 0.80 gives 0.58. The error is positive above 0.22.

**If you chose another answer:** Use delta = -0.02 + successor - 0.20: successor 0.10 gives -0.12, 0.50 gives 0.28 and 0.80 gives 0.58, so only the two higher successors give a positive error.


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

# Chapter demonstration answers

<a id="demonstration-1"></a>

## Demonstration 1

For rewards 1 then 2 with gamma = 0.9, what return is credited to the first action?

G_0 = 1 + 0.9 x 2 = 2.8. The second step's return stays G_1 = 2.

**Prediction answer:** 2.0.

G_0 = 1 + 0.5 x 2 = 2.0, which is the chapter's Exercise 1. The first reward counts in full and the second is halved.

**If you chose another answer:** The first reward counts in full and each later reward is multiplied by gamma for every step of delay, so G_0 = 1 + 0.5 x 2 = 2.0. Choose the exercise stream and gamma 0.5 to see it.

<a id="demonstration-2"></a>

## Demonstration 2

With retrieve success 0.70 (cost still 0.05) and p = 0.5, what is the true gradient?

Net value of retrieving = 0.70 - 0.05 = 0.65, gain = 0.65 - 0.55 = 0.10, so the slope is 0.10 x 0.5 x 0.5 = 0.025.

**Prediction answer:** The mean stays 0.05 and the spread shrinks.

The baseline depends only on the context, so the expected gradient stays 0.05. Only the variance changes, as Figure 13.2 says.

**If you chose another answer:** A baseline that does not depend on the sampled action changes variance, not the expected gradient. Set phi to 0 and compare the baselines.

<a id="demonstration-3"></a>

## Demonstration 3

In the transfer case, if training ended at probability 0.90 for action 0, what is the true success?

0.90 x 0 + 0.10 x 1 = 0.10, far below the start of 0.5 x 0 + 0.5 x 1 = 0.50, even though the trained-on reward is 0.90 x 2 + 0.10 x 1 = 1.90.

**Prediction answer:** Below 0.55.

Below. The update raises the action with the higher reward, which has task success 0.2, so true success falls while reward rises.

**If you chose another answer:** The update raises the action with the higher reward, and that action has the lower task success, so true success ends below 0.55. Select the default case and step the training length to 400.

<a id="demonstration-4"></a>

## Demonstration 4

If the direct route's end state had potential 0.1 and the retrieve route's end 0, which route would rank first, and by how much?

Direct = 0.55 + 0.1 = 0.65, retrieve = 0.80 - 0.05 = 0.75. Retrieving still ranks first, by 0.10.

**Prediction answer:** Answer directly.

Direct = 0.55 + 0.3 = 0.85 against retrieve = 0.75. The end potential belongs to one route only, so it survives and flips the ranking.

**If you chose another answer:** The direct route's end potential is added to its return and not cancelled: 0.55 + 0.3 = 0.85 against 0.75, so the direct route ranks first. Set the direct end to 0.3 and the retrieve end to 0.


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

# Chapter demonstration answers

<a id="demonstration-1"></a>

## Demonstration 1

At T = 1.30, what is the model score minus the actual score, and which column is higher?

732 - 753 = -21, so the actual score is higher by 21. The columns can also run the other way.

**Prediction answer:** T = 0.10 wins and scores below the random policy in the actual environment.

At T = 0.10 the model reports 2086 and the actual score is 193, which is 17 below the random policy's 210.

**If you chose another answer:** The model column is largest at T = 0.10 (2086), and that setting scores only 193 in the actual environment, below the random policy's 210. Pick the model column in the judge control.

<a id="demonstration-2"></a>

## Demonstration 2

With gamma = 0.8, epsilon = 0.05 and R = 1, what is the discounted bound, and what is the largest possible value?

Bound = 0.8 x 0.05 / (1 - 0.8)^2 = 0.04 / 0.04 = 1.0. The largest possible value is 1 / 0.2 = 5, so the bound is a fifth of the range.

**Prediction answer:** About 200.

0.99 x 0.02 x 1 / (1 - 0.99)^2 = 0.0198 / 0.0001 = 198, about 200, against a largest possible value of 100.

**If you chose another answer:** The denominator (1 - 0.99)^2 is 0.0001, so 0.99 x 0.02 / 0.0001 = 198, about 200. Select gamma 0.99 in the default case.

<a id="demonstration-3"></a>

## Demonstration 3

True values 0.90 and 0.60, adversarial error 0.12. Which action does the model pick, and does the guarantee hold?

Model values: 0.90 - 0.12 = 0.78 and 0.60 + 0.12 = 0.72, so the model still picks tool 6. Twice the error is 0.24, below the gap 0.30, so the guarantee holds.

**Prediction answer:** It scores tools 5 and 6 equally, a tie.

Tool 6 falls to 0.90 - 0.15 = 0.75 and tool 5 rises to 0.60 + 0.15 = 0.75: an exact tie, so the strict test 2 x error < gap cannot certify the ranking.

**If you chose another answer:** Marking the best down and the runner-up up by 0.15 gives 0.75 for both, an exact tie. Set the adversarial pattern and the error 0.15.

<a id="demonstration-4"></a>

## Demonstration 4

With R = 1, epsilon = 0.04 and a gap of 0.5, what is the certified horizon?

R x epsilon x H(H-1) = 0.04 x H(H-1). At H = 4 it is 0.04 x 12 = 0.48, below 0.5. At H = 5 it is 0.04 x 20 = 0.80, which is not. H-star = 4.

**Prediction answer:** It grows from 2 to 4.

At 0.08, 10 x 0.08 x 2 x 1 = 1.6 passes and H = 3 gives 4.8; at 0.01, H = 4 gives 10 x 0.01 x 12 = 1.2 and H = 5 fails by equality at 2.0.

**If you chose another answer:** H(H-1) grows like H squared, so the horizon scales roughly with the square root of gap over R x epsilon: 0.08 certifies 2 rewards and 0.01 certifies 4. Choose scenario R = 10 and step the error down.


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

# Chapter demonstration answers

<a id="demonstration-1"></a>

## Demonstration 1

In the transfer case (budget 3, now 20, current version doc-C), which record is retrieved, and what is the total value at λ = 0?

expired (value 10, written at 10, lifetime 2) is excluded because its age 20 - 10 = 10 exceeds 2. current (3 tokens, value 4) is fresh and bound to doc-C, so it is retrieved for a total of 4.

**Prediction answer:** review-v2 and summary, for a total of 11.

old-review is excluded: its authority belongs to v1, and a fresh timestamp does not repair that. review-v2 (4 tokens, 8) and summary (2 tokens, 3) fill the budget of 6 for a value of 11.

**If you chose another answer:** old-review carries authority for v1 but the current version is v2, so it is excluded before its value of 100 is counted. review-v2 and summary fit exactly and total 8 + 3 = 11. Choose the default case and λ = 0.

<a id="demonstration-2"></a>

## Demonstration 2

If epsilon is 2.5 and the worst-case errors are applied to scores 10 and 6, what are the summary's two scores and the largest possible regret?

The scores are 10 - 2.5 = 7.5 and 6 + 2.5 = 8.5, so the summary follows the second action, with regret 10 - 6 = 4, within the limit 2 x 2.5 = 5.

**Prediction answer:** It switches to Action 0, with regret 2 inside the limit 4.

The summary prefers Action 0 (6 > 5), so the regret is 6 - 4 = 2, and the largest error is 2, so the premise holds and 2 is within 2 x 2 = 4.

**If you chose another answer:** Summary values 6 and 5 prefer Action 0, whose full value is 4, so the regret is 6 - 4 = 2. The largest error is 2, so the premise holds with ε = 2 and 2 is within the limit 2 x 2 = 4. Select the changed case and ε = 2.

<a id="demonstration-3"></a>

## Demonstration 3

A new record has value 5 and 2 tokens, with λ = 3. What is its net value, and is it retrieved?

5 - 3 x 2 = (-1). The net value is negative, so Equation (15.1) leaves it out.

**Prediction answer:** Similarity only, because the copy still has similarity 0.98.

The copy keeps the same wording and so the same similarity, 0.98, which is the highest. Absence from one view says nothing about the others.

**If you chose another answer:** Deleting from the visible store leaves the summary index's copy, whose wording and similarity (0.98) are unchanged, so Similarity only still retrieves it. Choose deletion from the store only.

<a id="demonstration-4"></a>

## Demonstration 4

A record is worth 10 if current and 0 if invalid, costs 2 tokens, with λ = 1 and p = 0.3. What is its net value?

Expected value 0.3 x 10 + 0.7 x 0 = 3.0; net 3.0 - 1 x 2 = 1.0. It is positive, so retrieve it (break-even p = 2 / 10 = 0.2).

**Prediction answer:** p = 0.5.

The net value is p x 8 - 4 x 1, which is zero at p = 4 / 8 = 0.5.

**If you chose another answer:** Net value = 8p - 4, which is zero at p = 4 / 8 = 0.5. Set λ to 4 and read the break-even line.


## Chapter 16: separate solutions

## Question 1

Compute default n=5 coverage and selection.

Coverage is 1-0.6^5=0.92224. Selected success is 0.92224*0.9=0.830016, because the selector finds a correct candidate with probability 0.9 when one exists.

## Question 2

Why prefer n1 under shared error?

With a shared error, coverage stays 0.4 whatever the count. A bank with a correct candidate then holds only correct candidates, so for two or more candidates selected success is 0.4*1+0.6*0=0.4 whatever the selector accuracy. Success ties at 0.4, but the extra samples and the selector add cost, so one candidate (cost 1) is preferred.

## Question 3

What if no allocation is feasible?

selected_allocation is unavailable; revise the allowed contract or abstain.

# Chapter demonstration answers

<a id="demonstration-1"></a>

## Demonstration 1

At p = 0.2 with every problem sharing p, what is the coverage of five samples, and what does a blind pick from them deliver?

Cov(5) = 1 - 0.8^5 = 1 - 0.32768 = 0.6723. A blind pick delivers p = 0.2, so 0.4723 of coverage is not delivered.

**Prediction answer:** About 0.40.

Cov(10) = 1 - 0.95^10 = 1 - 0.5987 = 0.4013, the chapter's 0.40. A blind pick from those ten still delivers only p = 0.05.

**If you chose another answer:** Cov(10) = 1 - 0.95^10 = 1 - 0.5987 = 0.4013, about 0.40: far above one sample (0.05) but far below 0.90. Choose the shared setting, p = 0.05 and k = 10 to see it.

<a id="demonstration-2"></a>

## Demonstration 2

With independent samples, p = 0.4 and selector success 0.75, what is Sel(3)?

Cov(3) = 1 - 0.6^3 = 0.784, so Sel(3) = 0.784 x 0.75 = 0.588, which beats the blind 0.40 by 0.188.

**Prediction answer:** Five samples beat 0.40.

Sel(5) = 0.92224 x 0.5 = 0.4611, above 0.40 by 0.0611. Two samples would give 0.64 x 0.5 = 0.32, below the blind line: a weak selector can cost more than it earns for small banks.

**If you chose another answer:** Sel(5) = 0.92224 x 0.5 = 0.4611, which is above 0.40. Choose the notebook default setting and selector 0.5 to see it; at two samples the same selector gives 0.64 x 0.5 = 0.32, below the blind line.

<a id="demonstration-3"></a>

## Demonstration 3

Short samples cost 1 unit and long ones 4. With 20 short samples verified at 0.25 each, how many units are used, and what is Sel if pi = 0.6 and p = 0.2?

Units: 20 x 1 + 20 x 0.25 = 25. Cov(20) = 1 - 0.8^20 = 1 - 0.0115 = 0.9885, so Sel = 0.9885 x 0.6 = 0.593.

**Prediction answer:** 4. Length with a selector.

Length with a selector: Cov(12) = 0.9943 and Sel = 0.9943 x 0.785 = 0.781, just above volume with a selector (0.99998 x 0.73 = 0.730). Both beat the two blind allocations (0.35 and 0.20).

**If you chose another answer:** Length with a selector is highest: 0.9943 x 0.785 = 0.781, against 0.730 for volume with a selector and 0.35 and 0.20 for the two blind allocations. Choose the book values to see the four bars.

<a id="demonstration-4"></a>

## Demonstration 4

A procedure costs 3 per attempt and completes 0.5 of 100 attempts. What is its cost per success?

Total cost 100 x 3 = 300 and successes 100 x 0.5 = 50, so 300 / 50 = 6 per success.

**Prediction answer:** B.

B: its completion 0.80 meets the floor 0.75 and its 2 seconds meet the 3 second deadline. A completes only 0.60 and C takes 5 seconds. A has the lowest cost per success (1.6667) yet is not feasible.

**If you chose another answer:** Only B is feasible: 0.80 is at least 0.75 and 2 s is at most 3 s. A completes 0.60, below the floor, and C takes 5 s, past the deadline. Choose a 3 second deadline and a floor of 0.75 to see it.


## Chapter 17: separate solutions

## Question 1

How many effects occur in the default trace?

Two effects. The first lost acknowledgement does not remove its effect.

## Question 2

What duplicate-harm value makes verification and retry tie?

Verification costs 1. Retry costs 0.2 plus the probability 0.8 that the effect already happened times the duplicate cost d. They tie when 1=0.2+0.8d, so d=1.

## Question 3

What happens when a stored idempotency key is reused with a different payload?

The service raises an error and applies nothing. The stored key is bound to its first payload, so a different payload under the same key is ambiguous: it is neither deduplicated as a repeat nor counted as a new effect.

# Chapter demonstration answers

<a id="demonstration-1"></a>

## Demonstration 1

A charge of 50 with a stored key is sent 4 times from a record of 100. Where does the record end?

The key makes the service count it once: 100 + 1 x 50 = 150. Without the key it would be 100 + 4 x 50 = 300, and with the key lost the same 300.

**Prediction answer:** 250.

Each request adds a charge: 100 + 3 x 50 = 250. The equation fails, which is why a retry after a lost reply is not safe on this evidence alone.

**If you chose another answer:** With no key every request is applied: 100 + 3 x 50 = 250. Choose the charge with no key to see the bars.

<a id="demonstration-2"></a>

## Demonstration 2

Prior belief 0.2 with silence 0.9 likely if applied and 0.5 if not, a missing cost of 10 and a duplicate cost of 10. What is the belief after silence, and does a retry beat a decline?

Belief = (0.9 x 0.2) / (0.9 x 0.2 + 0.5 x 0.8) = 0.18 / 0.58 = 0.310. Retry costs 0.310 x 10 = 3.10 and decline costs 0.690 x 10 = 6.90, so retry wins; the threshold is 10 / (10 + 10) = 0.50.

**Prediction answer:** Read first.

Retry costs 0.30 x 40 = 12, decline costs 0.70 x 10 = 7, and a read costs 1: its gross value is 7 and its net value 7 - 1 = 6 (workbench IV.3). The default state shows it.

**If you chose another answer:** Reading first costs 1, against 12 for a retry and 7 for a decline, so it has the lowest expected cost; its net value is 7 - 1 = 6. The default state (belief 0.30, duplicate cost 40) shows it.

<a id="demonstration-3"></a>

## Demonstration 3

A refund returns the money and retracts the email, but the downstream webhook and the partner's ledger entry stay. How many of the four consequences are verified restored, and is Restored true?

1 + 1 + 0 + 0 = 2 of 4, and Restored needs 4 of 4, so it is false.

**Prediction answer:** No: only 1 of 4 consequences is verified restored.

Verified restored = 1 + 0 + 0 + 0 = 1 of 4, and Restored needs every relevant consequence: the refund does not retract the email, the webhook or the partner's ledger entry.

**If you chose another answer:** Restored needs every relevant consequence verified, and here 1 + 0 + 0 + 0 = 1 of 4: the refund returns the money but does not retract the email, the webhook or the partner's ledger entry. Choose the partial undo and stage 3.

<a id="demonstration-4"></a>

## Demonstration 4

A read proves a non-idempotent charge was applied and complete. Is the charge in Rep(x)?

No. Applied is not Absent, the charge is not idempotent and nothing was restored, so 0 + 0 + 0 = 0 routes hold. The request is already done, so stop.

**Prediction answer:** No, it is not eligible.

A second notification may send a second email, so no idempotent route holds, and nothing else is in hand: 0 + 0 + 0 = 0 routes, Ready x 0 = 0.

**If you chose another answer:** Not eligible: a second notification may send a second email, so route 1 is false, and with no proof of non-application 0 + 0 + 0 = 0 routes hold. Choose step 5 with no extra evidence.


## Chapter 18: separate solutions

## Question 1

Why does default coordinate completion fail?

The layout changed from layout-1 to layout-2, so the stored coordinate now reaches delete instead of release. The request is still issued (age 1 is within the limit of 2 and permission is true), but the target is wrong, so confirmed completion is false.

## Question 2

Can matching versions replace current permission?

No. In the transfer case the observation is fresh and the versions match (page-C and page-C), yet current permission is false, so all three interfaces refuse issuance. A version match says the layout is unchanged; it does not grant authority.

## Question 3

What does observation age 3 do under max_age = 2?

Age 3 exceeds the limit of 2, so the observation is stale and all three methods refuse issuance, including the semantic one whose target would be correct. A renewed observation is needed before any interface may act.

## Question 4

With change_rate 0.02 per second, compute the no-invalidating-change probability for delays of 5, 15 and 30 seconds.

exp(-0.02*5)=0.9048, exp(-0.02*15)=0.7408, exp(-0.02*30)=0.5488, matching the freshness_by_delay field.

# Chapter demonstration answers

<a id="demonstration-1"></a>

## Demonstration 1

With belief 0.7 in layout 1, what is the chance of a prohibited release for the coordinate command with no check, and with the check on?

No check: 0.7 x 0 + 0.3 x 1 = 0.30. Check on: 0.7 x 0 + 0.3 x 0 = 0. Authorized completion stays 0.7 x 1 + 0.3 x 0 = 0.70 in both.

**Prediction answer:** 0.40.

P(release v3) = 0.6 x 0 + 0.4 x 1 = 0.40, which is the chapter's exercise 1. With the check on it falls to 0 while intended completion stays 0.60.

**If you chose another answer:** The saved point reaches v3 in layout 2, which has belief 0.4: P(release v3) = 0.6 x 0 + 0.4 x 1 = 0.40. Choose the coordinate command, belief 0.6 and the check off to see it.

<a id="demonstration-2"></a>

## Demonstration 2

If layout 2 has belief 0.001 and nothing further is observed, does the saved-point click survive? What if the belief is exactly 0?

At 0.001 the weight is positive, so layout 2 counts and removes the click (5 - 4 = 1 removed, 4 of 5 remain). At 0 layout 2 is not counted, the click survives and 5 of 5 remain, but only if layout 1 is truly current.

**Prediction answer:** No, any positive weight removes it.

Any positive weight on layout 2 puts it in the support, and layout 2 does not authorize the click, so 5 - 4 = 1 command is removed. The size of the weight never enters.

**If you chose another answer:** The intersection counts every state with positive belief, however small: layout 2 counts at 0.01, does not authorize the click, and removes it (4 of 5 remain). Choose belief 0.01 with no further observation.

<a id="demonstration-3"></a>

## Demonstration 3

At 0.05 invalidating changes per second and a 20 second delay, what is Fresh?

Rate x delay = 0.05 x 20 = 1.0, so Fresh = exp(-1) = 0.3679. The chance of an invalidating change is 1 - 0.3679 = 0.6321.

**Prediction answer:** Above one half.

Fresh = exp(-0.02 x 30) = exp(-0.60) = 0.5488, just above one half (the half point is 0.6931 / 0.02 = 34.7 seconds).

**If you chose another answer:** Fresh = exp(-0.02 x 30) = exp(-0.60) = 0.5488, which is above one half: the half point is 0.6931 / 0.02 = 34.7 seconds. Choose the default case and a delay of 30 to see it.

<a id="demonstration-4"></a>

## Demonstration 4

If one more look cost 3 units, the wrong-target loss were 40 and the chance of a wrong target 0.1, would looking first pay?

Clicking now costs 0.1 x 40 = 4.0. Looking costs 3, so the net advantage is 4.0 - 3 = 1.0 and it pays. The break-even chance is 3 / 40 = 0.075, below 0.1.

**Prediction answer:** No, clicking now is cheaper.

Clicking now costs 0.1 x 3 = 0.3, below the 2 units a look costs, so the net advantage is 0.3 - 2 = -1.7: the permission check bounded the effect.

**If you chose another answer:** Clicking now costs 0.1 x 3 = 0.3, well below the cost 2 of looking, so the look does not pay (net advantage 0.3 - 2 = -1.7). Choose loss 3, chance 0.1 and a look costing 2.


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

# Chapter demonstration answers

<a id="demonstration-1"></a>

## Demonstration 1

A matrix has a diagonal mean of 10 and an off-diagonal mean of 8. What is the loss, and what changes if the diagonal mean is 0?

(10 - 8) / 10 = 0.20. With a diagonal mean of 0 the denominator is 0, so the statistic is undefined and the chapter says to report the difference instead.

**Prediction answer:** Nearer 0.7.

(20.15 - 5.71) / 20.15 = 14.44 / 20.15 = 0.717. Select Laser Tag small4 to see it.

**If you chose another answer:** The gap is 20.15 - 5.71 = 14.44, and 14.44 / 20.15 = 0.717, nearer 0.7. Select Laser Tag small4 to see it.

<a id="demonstration-2"></a>

## Demonstration 2

If party two starts at B instead, which option does party one answer with first, and how many updates until party two is back at B?

Party one's payoffs against B are A: (-1), B: 0, C: 1, so it plays C. Party two answers A, party one B, party two C, party one A, party two B, so party two is back at B after 6 updates.

**Prediction answer:** It returns to where it began.

Party two is back at A after 6 updates, so the cycle repeats. Set Updates shown to 6 to see the dotted line.

**If you chose another answer:** It does not stop: party two is back at A after 6 updates, so the cycle repeats. Set Updates shown to 6 to see the dotted line.

<a id="demonstration-3"></a>

## Demonstration 3

A different procedure loses 60 points at baseline, 25 at depth 4 and 20 at depth 8. How many extra points does the step from depth 4 to depth 8 buy?

Points removed at depth 4: 60 - 25 = 35. At depth 8: 60 - 20 = 40. The step adds 40 - 35 = 5 points, much less than the first 35.

**Prediction answer:** Almost the same.

Level ten removes 56.7 points, only 0.6 more than level five. Choose Level ten and read the Extra points from the last step.

**If you chose another answer:** Doubling the depth from level five to level ten does not double the gain: level five already removes 56.1 points and level ten removes 56.7, only 0.6 more. Choose Level ten and read the Extra points from the last step.

<a id="demonstration-4"></a>

## Demonstration 4

For the two-policy matrix with weight 0.7 on partner 0, which policy ranks first, and what are the two values?

Policy 0: 0.7 x 0.95 + 0.3 x 0.2 = 0.725. Policy 1: 0.7 x 0.4 + 0.3 x 0.9 = 0.55. Policy 0 ranks first, since 0.7 is above the crossing at 0.56.

**Prediction answer:** Policy 1.

Policy 1 scores 0.5 x 0.4 + 0.5 x 0.9 = 0.65 against 0.575 for policy 0, despite the weaker diagonal. The default state shows it.

**If you chose another answer:** The diagonal alone does not give the ranking: policy 0 scores 0.5 x 0.95 + 0.5 x 0.2 = 0.575 against the mix, while policy 1 scores 0.5 x 0.4 + 0.5 x 0.9 = 0.65, despite the weaker diagonal. The default state shows it.


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

# Chapter demonstration answers

<a id="demonstration-1"></a>

## Demonstration 1

If 4 messages are delivered out of 4 planned, what is the highest level of mutual knowledge of message 1, and how many link steps lead back to the silent run?

Highest level = 4 - 1 = 3. Level 4 fails because B sent message 4 and cannot tell run 3 from run 4. The walk back crosses 4 - 0 = 4 links to run 0, where message 1 was not delivered, so common knowledge fails.

**Prediction answer:** Level 2, blocked by A.

Highest level = 3 - 1 = 2. A sent message 3 and cannot tell run 2 from run 3, so A does not know level 2 and level 3 fails.

**If you chose another answer:** Highest level = 3 - 1 = 2, and message 3 was sent by A, who cannot tell run 2 from run 3, so A blocks level 3. Set Messages delivered to 3 to see it.

<a id="demonstration-2"></a>

## Demonstration 2

If A needed 1 and B needed 1, in which run does only B attack?

In run 1 only the proposal arrived: B has received (1 + 1) / 2 = 1, enough, and A has received 1 / 2 = 0.5, rounded down to 0. So B attacks alone.

**Prediction answer:** Run 2.

In run 2 A has received 1 message and attacks, while B has received (2 + 1) / 2 = 1.5, rounded down to 1, and holds. Dashed boxes show A cannot tell run 2 from run 3.

**If you chose another answer:** Run 2 is the unsafe run: A has received 1 message and attacks, while B has received 1 and needs 2. In run 3 both attack, and A cannot tell run 2 from run 3.

<a id="demonstration-3"></a>

## Demonstration 3

With two private decisions and 3 messages delivered, who holds the token, and how many of the four runs end with exactly one owner?

A has received 3 / 2 = 1.5, rounded down to 1, and releases; B has received (3 + 1) / 2 = 2 and takes it. B holds it. Only run 2 strands the token, so 4 - 1 = 3 of 4 runs end with exactly one owner.

**Prediction answer:** Run 2.

In run 2 A has received 1 message and releases the token, while B has received 1 and needs 2, so nobody holds it. Select 2 messages delivered.

**If you chose another answer:** Run 2 strands the token: A has received 1 message and releases it, while B has received 1 and needs 2. Select 2 messages delivered to see it.

<a id="demonstration-4"></a>

## Demonstration 4

With a drop probability of 0.2 and 2 rounds, what is the chance that Bob commits and Alice does not?

A round in which the reply does not get back to Alice has probability 1 - 0.8 x 0.8 = 0.36. So Bob commits alone with probability 0.36^2 - 0.2^2 = 0.1296 - 0.04 = 0.0896, and agreement is 0.9104.

**Prediction answer:** Lower than 0.75.

With R = 2, Bob commits alone with probability 0.75^2 - 0.5^2 = 0.3125, so agreement is 0.6875, below 0.75. Select 2 rounds at 0.5.

**If you chose another answer:** With R = 2, Bob commits alone with probability 0.75^2 - 0.5^2 = 0.3125, so agreement is 0.6875, below 0.75. Select 2 rounds at 0.5.


## Chapter 21: separate solutions

## Question 1

Compute default price of anarchy.

At the default (demand 1, zero-cost shortcut) equilibrium sends all traffic through the shortcut, so each congestible edge carries 1 and the social time is 2(1)(1)=2. The social optimum uses no shortcut, 0.5 on each outer route, with social time 1(0.5+1)=1.5. The price of anarchy is 2/1.5=4/3, about 1.333.

## Question 2

Why exclude toll revenue from social travel time?

A toll moves money from the traveller to whoever collects it; nobody spends extra time because of it. The objective is total travel time, so adding toll payments would count the same transfer as if it were delay and change the quantity being minimized. The toll belongs in private cost, where it changes route choices, and stays out of social cost.

## Question 3

Compute transfer social optimum.

The optimal shortcut flow is z=capacity(constant_time-overhead)-demand=1(1-0)-0.5=0.5, which already lies within [0,0.5], so z=0.5. The total social time is (0.5+0.5)^2/(2(1))+1(0.5-0.5)+0(0.5)=0.5.

# Chapter demonstration answers

<a id="demonstration-1"></a>

## Demonstration 1

At demand 1.5, what does each trip cost with the link, and how does that compare with the cost of an outer route?

Equilibrium puts 0.5 on each outer route and 0.5 on the middle, so each congestible edge carries 1.0. An outer route costs 1.0 + 1 = 2.0 and the middle costs 1.0 + 1.0 = 2.0, a tie. Total latency is 2 x 1.0 x 1.0 + 2 x 0.5 x 1 = 3.0, which is 2.0 per trip.

**Prediction answer:** Higher.

At demand 1 everyone takes the link, each trip costs 2, and total latency rises from 1.5 to 2. Select demand 1 with the link to see it.

**If you chose another answer:** At demand 1 everyone takes the link, each trip costs 2, and total latency rises from 1.5 to 2 although no road got slower. Select demand 1 with the link to see it.

<a id="demonstration-2"></a>

## Demonstration 2

With a delay of 0.25 on the middle link, what is the highest ratio?

The peak is at demand m = 1 - 0.25 = 0.75. Equilibrium: 0.75 x (2 x 0.75 + 0.25) = 0.75 x 1.75 = 1.3125. Optimum: 0.75 x (0.75 / 2 + 1) = 0.75 x 1.375 = 1.03125. The ratio is 1.3125 / 1.03125 = 1.273, below 4/3.

**Prediction answer:** Fall below 4/3.

With delay 0.5 the peak is at demand 0.5: 0.5 x (2 x 0.5 + 0.5) / (0.5 x (0.5 / 2 + 1)) = 0.75 / 0.625 = 1.2, below 4/3. Select 0.5 to see it.

**If you chose another answer:** With delay 0.5 the peak falls to 0.75 / 0.625 = 1.2, below 4/3, and it can never rise above 4/3 when every delay is linear. Select 0.5 to see it.

<a id="demonstration-3"></a>

## Demonstration 3

At demand 0.75 with the marginal-cost charge, what flow goes on the middle link?

Both route types are used, so their charged costs match: 2v + 1 = 4v gives v = 0.5. The middle flow is 1 - 0.75 = 0.25, each outer route carries 0.25, and the physical total is 2 x 0.5 x 0.5 + 2 x 0.25 = 1.0.

**Prediction answer:** None (0.00).

Charged costs are 2v + 1 for an outer route and 4v for the middle; at v = 0.5 they tie at 2, so the flow stays on the outer routes, and the physical total is 1.5. Marginal-cost charge at demand 1 shows it.

**If you chose another answer:** Charged costs are 2v + 1 for an outer route and 4v for the middle; at v = 0.5 they tie at 2, so no traffic uses the middle link and the physical total is 1.5. Marginal-cost charge at demand 1 shows it.

<a id="demonstration-4"></a>

## Demonstration 4

With r = 1 and extra = 0.5, what must the benchmark carry, and what is its cost?

It carries (1 + 0.5) x 1 = 1.5. At 1.5 the optimum uses only the outer routes, 0.75 each: 1.5 x (1.5 / 2 + 1) = 1.5 x 1.75 = 2.625. The equilibrium cost 2.0 is below it, and 1 / 0.5 = 2 times 2.625 is a much looser ceiling.

**Prediction answer:** Below it.

Equilibrium at r = 1 costs 2 x 1 x 1 = 2, while the optimum at rate 2 costs 2 x (2 / 2 + 1) = 4. Select rate 1 and extra 1.

**If you chose another answer:** Equilibrium at r = 1 costs 2 x 1 x 1 = 2, while the optimum at rate 2 costs 2 x (2 / 2 + 1) = 4, so it is below. Select rate 1 and extra 1.


## Chapter 22: separate solutions

## Question 1

Which default action wins the hard constraint?

Only reviewed-release (risk 0.05) and abstain (risk 0) are authorized and within the limit 0.1; fast-release is unauthorized and risky-authorized has risk 0.2. Of the two, reviewed-release has the higher reward, 5 against 0.

## Question 2

Can risk_limit = 0.25 authorize fast-release?

No. Its current permission remains false, and its risk 0.3 also exceeds the limit 0.25.

## Question 3

Why does transfer choose wait despite negative reward?

Both actions are authorized, but act has risk 0.01, above the limit 0, so the risk filter removes it. Wait has risk 0 and is the only feasible row. The constrained rule maximizes reward only among feasible rows, so its reward of -1 does not matter: a feasible refusal beats an infeasible action however large that action's reward or penalized value (19 under penalty 100).

# Chapter demonstration answers

<a id="demonstration-1"></a>

## Demonstration 1

Work this one by hand (3 is not an offered multiplier). In workbench VI.1 with the limit at 1 and the multiplier at 3, which policy does the penalty rule pick, and which does the constraint rule pick?

Careful: 7 - 3 x 0.5 = 5.5. Aggressive: 11 - 3 x 2 = 5. The penalty rule picks Careful (the flip point is 4 / 1.5 = 2.67, and 3 is above it). Aggressive costs 2, above the limit 1, so the constraint rule picks Careful too: here the two rules agree.

**Prediction answer:** The penalty rule picks Aggressive at 2, ties at 4 and picks Careful at 6; the constraint rule always picks Careful.

The two scores cross where the reward gap 4 equals the cost gap 1 times the multiplier, at 4. The constraint rule never reads the multiplier. Switch the penalty control to see it.

**If you chose another answer:** The scores 8 - 0.5 x m and 12 - 1.5 x m cross at m = 4, so the penalty rule changes its pick at the flip point while the constraint rule, which reads only the limit, stays on Careful. Switch the penalty control to see it.

<a id="demonstration-2"></a>

## Demonstration 2

Work this one by hand, using the control for the margin. With step size 0.005, discount 0.9 and advantage 0.1, what is the allowance, and does a margin of 0.5 cover it? What about a margin of 1.0?

sqrt(2 x 0.005) = 0.1, so 0.1 x 0.9 x 0.1 / (1 - 0.9)^2 = 0.009 / 0.01 = 0.9. That is above 0.5, so a margin of 0.5 does not cover it, and below 1.0, so a margin of 1.0 does.

**Prediction answer:** 0.005 fits (allowance 0.378) and 0.02 does not (0.756).

Quadrupling the step only doubles the allowance, because it grows with sqrt(2 delta): 0.378 then 0.756, against a margin of 0.5. Switch the step control to see it.

**If you chose another answer:** Compute sqrt(2 x 0.005) x 0.85 x 0.1 / 0.0225 = 0.378, which is under 0.5, and twice that, 0.756, for a step of 0.02, which is over 0.5. Switch the step control to see it.

<a id="demonstration-3"></a>

## Demonstration 3

Work this one by hand (a budget of 0.08 is not offered). With budget 0.08 and the charges 0.04, 0.05, 0.03, 0.05 proposed in order, which are charged and what is left? And a bad episode costs 100 with probability 0.02: what is CVaR at alpha 0.97?

Budget: 0.04 <= 0.08 is charged, leaving 0.04; 0.05 > 0.04 is refused; 0.03 <= 0.04 is charged, leaving 0.01; 0.05 > 0.01 is refused. Left 0.01. CVaR: tail share 0.03; at z = 0 the bracket is 2 / 0.03 = 66.67, at z = 100 it is 100, so CVaR is 66.67 while the mean cost is 2.

**Prediction answer:** Larger at alpha 0.99 (100 against 10).

At 0.99 the tail is exactly the bad episodes, so it averages 100. At 0.9 the tail is ten times wider than the bad episodes, so zeros dilute it: 1.0 / 0.1 = 10. Switch the alpha control to see it.

**If you chose another answer:** At alpha 0.9 the worst 10 percent of episodes holds the 1 percent bad ones and nine parts zeros, so the average is 1.0 / 0.1 = 10; at 0.99 it is 100. Switch the alpha control to see it.

<a id="demonstration-4"></a>

## Demonstration 4

Work this one by hand (0.2 is not an offered limit). With the risk limit at 0.2 and the penalty at 5, which action does the gate pick, and is fast-release eligible?

Eligible rows are authorized with risk at most 0.2: reviewed-release (0.05), risky-authorized (0.2, which meets the limit exactly) and abstain (0). Rewards 5, 8 and 0, so risky-authorized wins. Fast-release is not authorized, so it stays out.

**Prediction answer:** Risky-authorized becomes the gate pick; fast-release stays out.

Risky-authorized has risk 0.2, within 0.25, and reward 8, so it wins the eligible rows. Fast-release is not authorized, so no limit admits it. Switch the risk limit control to see it.

**If you chose another answer:** Risk 0.2 is within the new limit 0.25, so risky-authorized (reward 8) joins the eligible rows and beats reviewed-release (5). Fast-release is not authorized, so a looser limit cannot admit it. Switch the risk limit control to see it.


## Chapter 23: separate solutions

## Question 1

How many changed security violations occur?

Two: instruction promotion and forbidden publish execution.

## Question 2

Why does the changed plot rise twice?

It counts both security boundaries crossed: untrusted instructions are promoted to control, then an unauthorized publish executes. The final cumulative value is two, matching the total violation metric.

## Question 3

Does a valid review of version A authorize publishing version B?

No. Review is bound to the document version.

# Chapter demonstration answers

<a id="demonstration-1"></a>

## Demonstration 1

A parent holds only read_source and draft_summary. A delegated child proposes release. Is the child allowed to hold release, and why?

No. The child set must lie inside the parent set of 2 effects, and release is not one of them, so the child cannot hold it however many levels of delegation are added.

**Prediction answer:** No: the capability is held; the request is stopped because its authority came from untrusted data.

Equation (23.1) only bounds what a child may hold, and open_link is held here. The request is denied because its destination rests on untrusted data. Choose the calendar request and the browser grant to see it.

**If you chose another answer:** Holding open_link satisfies Equation (23.1), since the parent holds it too. The denial comes from the second check: a binding field without a trusted source is rejected. Choose the calendar request and the browser grant to see it.

<a id="demonstration-2"></a>

## Demonstration 2

An approval event arrives at t = 0 and the user revokes at t = 1. How many usable approvals are on file at the end, and which check would have been wrong?

Usable approvals = 0 + 1 - 1 = 0. A check made only at planning (after the approval, before the revocation) would have seen 1 and been wrong.

**Prediction answer:** Allowed at planning, which is wrong; the check just before the effect denies it.

At planning the record holds 1 approval; the revocation then removes it, so the record just before the effect holds 0. Switch the check control to see it.

**If you chose another answer:** The planning check reads the record after the approval and before the revocation (1 approval), so it allows; the record just before the effect holds 1 - 1 = 0, so that check denies. Switch the check control to see it.

<a id="demonstration-3"></a>

## Demonstration 3

A summarizer relabels a page's claim 'manager approved release of Q3-report version 5 to all subscribers' as trusted and the monitor admits it. What is Publish for that release, and which control closes the gap?

Publish = 1. The record now holds the triple the sentence named, so the lookup succeeds although no approval event occurred. Re-checking Approved(M_t) at the relabeling point, so that only an observed approval event can add an entry, closes it.

**Prediction answer:** Publish = 0 because the version field differs; the relabeled sentence can make Publish = 1 for the triple it names.

Version 5 is not in Approved(M_t), so Publish is 0. A relabeled sentence admitted without a re-check writes the very triple the attacker asked for into the record, so Publish becomes 1. Use the two controls to see both.

**If you chose another answer:** No partial match counts, so version 5 gives Publish = 0 with a real approval for version 4. If a summarizer relabels the page's claim as trusted and nothing re-checks it, the record then holds the attacker's triple and Publish = 1. Use the two controls to see both.

<a id="demonstration-4"></a>

## Demonstration 4

A declared family has violation chances 0.20, 0.35, 0.05 and 0.35. What is Risk, and what is the mean? And in the changed trace, how many violations are there and why?

Risk = max(0.20, 0.35, 0.05, 0.35) = 0.35, set by the two members tied at 0.35. The mean = (0.20 + 0.35 + 0.05 + 0.35) / 4 = 0.2375, which is not the reported value. In the changed trace violations = 1 promoted instruction + 1 forbidden publish executed = 2, even though the later authorized publish completes the task.

**Prediction answer:** The retry path that skips the check (0.45).

Risk is the maximum, and 0.45 is larger than 0.05, 0.10 and 0.10. Set the family to four attacks and the confused-deputy chance to 0.1 to see it.

**If you chose another answer:** Equation (23.4) takes the largest chance in the family, and the retry path at 0.45 exceeds 0.05, 0.10 and 0.10. Set the family to four attacks and the confused-deputy chance to 0.1 to see it.


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

# Chapter demonstration answers

<a id="demonstration-1"></a>

## Demonstration 1

Work this one by hand (800 tasks per bank is not shown). Benchmark 0.80 and matched 0.73 on 800 tasks each: what is the standard error of the gap, and does the interval exclude zero? And what is the aged benchmark's aggregate if 50 percent of its tasks were exposed?

SE = sqrt(0.80 x 0.20 / 800 + 0.73 x 0.27 / 800) = sqrt(0.0002 + 0.000246) = sqrt(0.000446) = 0.0211, between the 400-task value 0.0299 and the 1600-task value 0.0149, so the interval 0.07 plus or minus 1.96 x 0.0211 = [0.029, 0.111] excludes zero. At a 50 percent exposed share the aggregate is 0.5 x 1 + 0.5 x 0.4 = 0.70, which is 0.30 above the unfamiliar-task rate of 0.40.

**Prediction answer:** Yes: at 100 tasks the interval is about 0.07 plus or minus 0.117, so it includes zero.

The standard error at 100 tasks is sqrt(0.80 x 0.20 / 100 + 0.73 x 0.27 / 100) = 0.0598, so the interval is 0.07 plus or minus 1.96 x 0.0598 = 0.117, which includes zero. Choose the two-bank case and the difference reading to see all three sizes.

**If you chose another answer:** Whether a gap excludes zero depends on the sample size, not only on the gap: at 100 tasks the standard error is 0.0598 and 1.96 x 0.0598 = 0.117 exceeds 0.07, so the interval includes zero. Choose the two-bank case and the difference reading to see all three sizes.

<a id="demonstration-2"></a>

## Demonstration 2

With all eight members tested, what is the onset at threshold 0.60? And with only the even members tested?

g(6) = 0.58 is below 0.60 and g(7) = 0.66 is at or above it, with margin 0.66 - 0.60 = 0.06, so the onset is m = 7. With only members 2, 4, 6 and 8 tested the first score at or above 0.60 is g(8) = 0.71, so the onset moves to m = 8.

**Prediction answer:** No: no tested member reaches 0.70, so the onset is undefined.

g(7) = 0.66 is below 0.70 and member 8, which reaches 0.71, was not tested, so the set is empty: untested, not never. Choose threshold 0.7 and the odd members to see it.

**If you chose another answer:** Among members 1, 3, 5 and 7 the largest score is g(7) = 0.66, below 0.70, and member 8 (0.71) was not tested, so no tested member passes and the onset is undefined. Choose threshold 0.7 and the odd members to see it.

<a id="demonstration-3"></a>

## Demonstration 3

With 1600 tasks and four configurations tested at alpha 0.05, what is the margin t, and what is the frontier for a best estimate of 0.74?

t = sqrt(ln(4/0.05) / (2 x 1600)) = sqrt(4.382 / 3200) = 0.037, so LCF = 0.74 - 0.037 = 0.703.

**Prediction answer:** It shrinks, because fewer configurations share the failure budget.

With two configurations the failure budget is split two ways, t = sqrt(ln(2 / 0.05) / 800) = 0.068, against 0.074 for four. Switch the configurations control to see it.

**If you chose another answer:** The budget alpha is split across the tested configurations, so fewer configurations means a smaller margin: sqrt(ln(2 / 0.05) / 800) = 0.068 against 0.074 for four. Switch the configurations control to see it.

<a id="demonstration-4"></a>

## Demonstration 4

Tasks at 0.10 and 0.90, three runs: what is the true chance that all three succeed, and the mean-rate value? And for a recorded bank of 3 successes in 4 runs, what fraction of two-run subsets contains only successes?

(0.1^3 + 0.9^3)/2 = (0.001 + 0.729)/2 = 0.365, against 0.5^3 = 0.125. Recorded bank: C(3,2) / C(4,2) = 3 / 6 = 0.5 of the two-run subsets contain only successes, and all 6 contain at least one success.

**Prediction answer:** Above: 0.34.

(0.2^2 + 0.8^2) / 2 = (0.04 + 0.64) / 2 = 0.34, above 0.5^2 = 0.25, because the task is drawn once and repeated, so the easy task is weighted by its square. Choose the 0.20 and 0.80 bank with 2 runs to see it.

**If you chose another answer:** Average the task-level chances: (0.04 + 0.64) / 2 = 0.34, which is above the square of the mean, 0.25. Choose the 0.20 and 0.80 bank with 2 runs to see it.


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

# Chapter demonstration answers

<a id="demonstration-1"></a>

## Demonstration 1

A canary declares its boundary as c - margin with c = 1.20 and margin 0.15. Costs by period are 1.00, 1.05, 1.08 and 1.12. In which period does the alert fire, and what happens if the boundary had been moved to c after looking?

The boundary is 1.20 - 0.15 = 1.05. A cost of 1.05 is not above 1.05, so the first cost above it is 1.08 in period 3. With the boundary moved to 1.20 none of the four costs is above it, so no alert fires.

**Prediction answer:** Period 5.

Costs 0.80, 0.83, 0.86, 0.89 stay at or below 0.90 and 0.92 in period 5 is the first above it.

**If you chose another answer:** The boundary is 1.00 - 0.10 = 0.90 and the first cost above it is 0.92 in period 5. Set the rule control to 'chosen after looking' to see it move to period 8.

<a id="demonstration-2"></a>

## Demonstration 2

A frozen candidate beats its parent on 2 of 8 guard cases, loses on 1 and ties on 5. Its threshold is 0.20. Does it pass a clean guard?

Gain = (2 x 1 + 1 x (-1) + 5 x 0) / 8 = 1/8 = 0.125, which is below 0.20, so it does not pass.

**Prediction answer:** Flashy is frozen and fails the guard (gain 0.00).

Flashy has the best development rate (4/4) but its guard outcomes equal the parent's, so every Z is 0 and the gain is 0.00.

**If you chose another answer:** Development picks flashy (4/4 against 3/4), and its four guard cases match the parent, so every Z is 0 and the gain is 0.00, below 0.20. Steady's 0.25 does not count: choosing it after seeing the guard would put the guard inside selection.

<a id="demonstration-3"></a>

## Demonstration 3

With m = 300 guard cases and threshold 0.25, what is the bound for one decision?

exp(-300 x 0.0625 / 2) = exp(-9.375) = 0.0000848, about 8.5 in 100,000.

**Prediction answer:** The total falls to 2 x 0.00193 but decisions 3 to 10 get no bound.

Only decisions 1 and 2 were fixed before guard access, so the total is 2 x 0.00193 = 0.00386, and the eight later decisions need a new frozen guard.

**If you chose another answer:** Only decisions 1 and 2 still satisfy the fixed-before-guard condition, so the covered total is 2 x 0.00193 = 0.00386. That smaller number counts fewer decisions; decisions 3 to 10 have no bound until a new frozen guard exists.

<a id="demonstration-4"></a>

## Demonstration 4

A candidate has uplift 0.40, cost 0.92, authority granted and rollback tested, with c = 1.00 and margin 0.10. Is it accepted?

The limit is 1.00 - 0.10 = 0.90 and 0.92 > 0.90, so the cost condition is 0 and accept = 1 x 0 x 1 x 1 = 0.

**Prediction answer:** No, 0.95 is above c - margin = 0.90.

The cost condition compares with c minus the margin, 1.00 - 0.10 = 0.90, and 0.95 is above it, so accept = 1 x 0 x 1 x 1 = 0.

**If you chose another answer:** Cost is held to c minus the margin, 1.00 - 0.10 = 0.90, not to c. 0.95 is above 0.90, so the cost condition is 0 and accept = 1 x 0 x 1 x 1 = 0.


## Chapter 26: separate solutions

## Question 1

What are the default oracle, actual and deployed values?

Each task is solved by some candidate, so the oracle coverage is 1. Selecting candidate 0 for every task solves only task 0, so actual selection success is 0.2 (its weight), and with deployment allowed everywhere the deployed value is also 0.2. The three values are 1, 0.2 and 0.2.

## Question 2

Why is changed deployment 0.5 despite perfect selection?

The changed selector picks the passing specialist for every task, so actual success is 0.2 + 0.3 + 0.5 = 1.0. Deployment then denies task 2 (counting from 0), whose weight is 0.5, so deployed success is 0.2 + 0.3 = 0.5. The lost 0.5 is an authority limit, not a selection or model error.

## Question 3

Can adding a candidate reduce oracle prefix coverage?

No; any previously covered task remains covered.

# Chapter demonstration answers

<a id="demonstration-1"></a>

## Demonstration 1

If only 1 of the 10 programs passes and k = 4, what is the exact coverage?

1 - C(9,4) / C(10,4) = 1 - 126 / 210 = 0.40, which equals k / n = 4 / 10.

**Prediction answer:** Above 0.488.

Exact coverage is 1 - 56 / 120 = 0.533, above the independent-draw 0.488; they agree only at k = 1.

**If you chose another answer:** Exact coverage is 1 - C(8,3) / C(10,3) = 1 - 56 / 120 = 0.533, while 1 - (1 - 0.20)^3 = 0.488. The two differ; step the subset size down to 1 to see them meet.

<a id="demonstration-2"></a>

## Demonstration 2

If only the heavy task (weight 0.5) were solved by anything in the bank, what is the largest Sel any selector could reach?

Cov = 0.2 x 0 + 0.3 x 0 + 0.5 x 1 = 0.5, so Sel is at most 0.5 for every selector.

**Prediction answer:** 1.00, 0.20, 0.20.

Every task has a passing specialist (Cov = 1.00) but candidate 1 solves only the weight-0.2 task, so Sel = 0.20 and deployed = 0.20.

**If you chose another answer:** Each task has a passing specialist, so Cov = 0.2 + 0.3 + 0.5 = 1.00. Always taking candidate 1 solves only the task of weight 0.2, so Sel = 0.20, and all tasks may deploy, so deployed = 0.20.

<a id="demonstration-3"></a>

## Demonstration 3

A practical selector reaches 50.0 percent against 77.5 for unit tests. A new verifier is hoped to collect 40 percent of the gap. What is the new success?

Gap = 77.5 - 50.0 = 27.5. New success = 50.0 + 0.4 x 27.5 = 61.0, a hypothesis until measured.

**Prediction answer:** 61.0.

The gap is 77.5 - 44.5 = 33.0, half is 16.5, and 44.5 + 16.5 = 61.0, still below the ceiling and only a hypothesis.

**If you chose another answer:** The gap is 77.5 - 44.5 = 33.0 points. Half of it is 16.5, so success would be 44.5 + 16.5 = 61.0. Set the share control to 0.5 to see it.

<a id="demonstration-4"></a>

## Demonstration 4

Two fits agree on all three points but project limits of 0.65 and 0.86. By how much do they differ?

0.86 - 0.65 = 0.21, a spread of 21 points that the three observed points cannot resolve.

**Prediction answer:** Power law.

The power-law family projects about 0.86, against about 0.74 for the hyperbolic and 0.65 for the exponential.

**If you chose another answer:** The limits are about 0.65 (exponential), 0.74 (hyperbolic) and 0.86 (power law). Switch the highlighted family to compare.


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

# Chapter demonstration answers

<a id="demonstration-1"></a>

## Demonstration 1

A model is 0.97 sure and an expert is right with probability 0.95. Which route does Equation (27.2) choose, and by how much?

0.95 < 0.97, so the route is the most probable class. The classifier leads by 0.97 - 0.95 = 0.02.

**Prediction answer:** Acting wins.

Delegation is worth 0.60 x 9 + 0.40 x 2 - 1 = 5.2, below acting at 6, even though the expert is still right 0.95 of the time.

**If you chose another answer:** With on-time probability 0.60 delegation is worth 0.60 x 9 + 0.40 x 2 - 1 = 5.2, below acting at 6. The expert's 0.95 holds only when the reply arrives in time.

<a id="demonstration-2"></a>

## Demonstration 2

If the hold cost 4 instead of 2, what is its net value and does it still beat waiting?

0.95 x 8.04 + 0.05 x (-4) - 4 - 1 = 7.638 - 0.2 - 5 = 2.438, which is above waiting at 2, so it still wins narrowly.

**Prediction answer:** Waiting for confirmation.

At cost 5 the hold is worth 7.638 - 0.2 - 5 - 1 = 1.438, below waiting at 2, so waiting wins.

**If you chose another answer:** At cost 5 the hold is worth 0.95 x 8.04 + 0.05 x (-4) - 5 - 1 = 1.438, below waiting at 2, so waiting has the highest value.

<a id="demonstration-3"></a>

## Demonstration 3

With mu = 4 per hour and f = 0.75, what is the mean time in review in minutes?

Review arrivals = 0.75 x 4 = 3 per hour. Mean = 1 / (4 - 3) = 1 hour, which is 60 minutes.

**Prediction answer:** 1 hour, then 5 hours, then no stationary mean.

1 / (3 - 2) = 1 hour, 1 / (3 - 2.8) = 5 hours, and at 0.9 the arrivals 3.6 exceed capacity 3, so no stationary mean exists.

**If you chose another answer:** The time is 1 / (3 - f x 4): 1 hour at 0.5, 1 / 0.2 = 5 hours at 0.7, and at 0.9 the arrivals 3.6 exceed the capacity 3, so there is no stationary mean.

<a id="demonstration-4"></a>

## Demonstration 4

If the delay cost rose to 3 and the confirmation still arrived with probability 0.5, does the test allow waiting (fallback authorized everywhere)?

VOI = 0.5 x 9 + 0.5 x (-1) - (-1) = 5, and 5 > 3, so waiting passes. It would fail at or below q = 3 / 10 = 0.30, because equality fails the strict test.

**Prediction answer:** No, the test needs VOI strictly above the delay cost.

VOI = 10 x 0.20 = 2, equal to the delay cost 2, and the inequality is strict, so waiting is not allowed.

**If you chose another answer:** VOI = 0.20 x 9 + 0.80 x (-1) - (-1) = 2, which equals the delay cost 2. Equation (27.4) needs strictly more, so waiting fails at the boundary.


## Capstone solutions

1. Perfect preparation does not remove stale targeting, injected instructions, absent approval, unavailable review, acknowledgement loss, budget limits or deadlines. Success requires one intended, authorized and confirmed effect.
2. Probabilities for preparation, shared failure, layout, injection, acknowledgement and availability declare the environment. Refreshing, blocking, reviewing, retrying and verifying are policy branches. A reviewer capability and a perfect guard are assumptions of the construction.
3. A deployment claim requires an explicit task/population contract, actual effect and authority observations, representative runs, justified dependence assumptions, measured guard/reviewer behavior, resource accounting and an appropriate comparison. The simulation's exact rules cannot be silently attributed to a real system.
