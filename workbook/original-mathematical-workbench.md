# Mathematical Workbench

An equation becomes usable when a reader can decide what belongs in it, calculate its answer, and recognize when that answer has lost its warrant. This workbench gives each of the six parts a calculation, a diagnosis, and a problem in which an assumption changes. 

All cases and numerical values below are constructed exercises, not measurements of deployed systems. Treat stipulated probabilities as known within each exercise unless the question explicitly describes them as estimates. Utilities, costs, and rewards share units only where the problem says they do. Component population scores are `U_\mathcal V(S)`; a finite measured average is `\widehat U_\mathcal V(S)`. Outcome utilities remain `u(y)`, realized states remain `x_t`, and beliefs remain `\mathbf{b}_t`. Each problem uses only symbols defined in the chapters it cites, plus the local labels it introduces.

Work through the questions before turning to the solutions. 

## Technical Requirements

The original eighteen problems and five expansion problems require only the book and a way to calculate; a calculator is optional. To run the optional simulator probes, use Python 3.10 or later and a terminal on Windows, macOS, or Linux. The script uses the standard library and calls no external model or service. Obtain the companion files from the book's companion materials and keep the `scripts` folder beneath the working folder. Run the commands in "Simulator probes" and "Running the expansion probes" from that working folder.

The complete laboratory package adds 29 notebooks (one for each of the 27 chapters, an orientation, and a document-release capstone) and 28 assistant skills (one for each chapter plus a master skill). Open guide/index.html to read the executed calculations without installing Python. Open START-HERE.md for the launcher, editable inputs, and skill installation. Notebook execution requires Python 3.11 or later and the listed notebook dependencies; the standard-library chapter commands also support Python 3.10. The master skill routes the implemented methods and their input contracts. Its calculations use declared local models unless the reader supplies compatible data, and their assumptions remain part of the result. The standalone workbook preserves these original problems and adds chapter exercises with separate solutions.

## Part I: How New Behavior Appears

### I.1 Calculation: an interaction with a declared base

Use Chapters 2 and 5. A frozen model is evaluated on the same task distribution under a fixed evaluation contract. Retrieval and a typed tool are either enabled or disabled. The resource allowance, evaluator, sampling settings, and stopping rule are identical across conditions. The entries are stipulated mean scores on a scale from zero to one, not noisy sample estimates.

| Assembly | Score |
|---|---:|
| `U({\theta})` | 0.40 |
| `U({\theta,r})` | 0.52 |
| `U({\theta,t})` | 0.49 |
| `U({\theta,r,t})` | 0.73 |

Declare the base set and calculate `\Gamma(r;t)`. Decompose the joint improvement into the two isolated gains and their interaction. Check whether `\rho_\Gamma` is defined under the book's positivity conditions, then calculate it. Finally, distinguish the assertion that the combined assembly has the highest score from the assertion that retrieval and the tool cooperate positively. Which comparison establishes each assertion? Explain whether these scores establish how the cooperation occurs inside the system.

### I.2 Diagnostic: a forecast that saw its answer

Use Chapter 3. A team wants to forecast the interaction contrast of a model family member before assembling its agent. It collects predictor features `z_m`, chooses a family of forecasting rules with parameters `\psi`, and reports accurate predictions of `\Gamma_m` on a bank called held out. During development, however, the team repeatedly examines that bank's realized contrasts, uses them to choose the features, and stops revising when the prediction errors look small. It then fits the selected rule on the training members alone.

 Is that enough to make the reported test prospective? Identify the information path that matters and describe a repair that leaves the current work useful. Also say what would have to be recorded if the advertised forecast were made before the tool and retrieval components were available for evaluation.

### I.3 Changed assumption: the joint run gets extra resources

Return to I.1. The combined assembly actually received twice the resource allowance used by the other conditions. A subsequent matched rerun restores the original allowance for every assembly. The first three scores remain unchanged, while `U({\theta,r,t})` becomes 0.58. Treat these rerun means as stipulated values under the corrected contract.

Recalculate the joint gain, `\Gamma(r;t)`, and `\rho_\Gamma`. Can the combined assembly still be the best of the four while its interaction is negative? Explain how that outcome differs from saying that the tool is harmful in every context. Calculate the tool's improvement without retrieval and its improvement with retrieval. State which original claim must be withdrawn and which matched claim can replace it. Do not interpret the difference between the two joint scores as a separately identified causal effect of resources without explaining what the construction actually holds fixed.

## Part II: Choice

### II.1 Calculation: pay now to improve a later decision

Use Chapters 6 and 7. An authorized release produces reward 100 if correct and zero if incorrect. The current release is correct with probability 0.80. Alternatively, the agent can verify once, paying reward -6 immediately. Verification deterministically leads to a state where an authorized release is correct with probability 0.95. No further verification is allowed. Release ends the episode, and terminal value is zero. Both choices remain authorized throughout.

| Input | Value |
|---|---:|
| Correct-release reward | 100 |
| Incorrect-release reward | 0 |
| Current correctness | 0.80 |
| Verified correctness | 0.95 |
| Immediate verification reward | -6 |
| Discount factor `\gamma` | 0.90 |

Compute the verified state's optimal value, the current value of releasing immediately, and the current value of verification followed by release. Apply the convention that a reward on the transition out of the current state is undiscounted; discount only the next state's value. Which action should the agent take? Find the discount factor at which the two current actions tie. Explain why comparing the immediate verification cost with the immediate expected release reward is the wrong decision procedure.

### II.2 Diagnostic: a return that forgets remaining opportunities

An implementation of II.1 stores only the current document in `x_t`. It omits the remaining verification allowance. After verification, it leaves the same action menu available and offers another verification at the same cost. Its designer says the Bellman equation will eventually decide that verification is no longer worthwhile, so the missing allowance does not matter.

Identify the state distinction required by the stipulated problem. Explain why a plausible answer from the implementation would not establish that it solved that problem. Give a corrected description of the unverified state, the verified state, their available actions, and the terminal state. State where the budget belongs in Chapter 5's composite state, and explain what additional evidence would be needed before replacing the one-verification problem with a model of repeated verification. Finally, test whether the two states could share one exact `\kappa` class: compare their feasible action sets, terminal/permission labels, rewards, and transition mass into each proposed abstract class.

### II.3 Changed assumption: verification consumes the deadline

Keep every payoff, probability, and action restriction from II.1, but change `\gamma` to 0.75. Recompute the verification route and compare it with immediate release.

Explain what has changed about the optimal action and what has not changed about the evidence. Then consider a separate contractual change: the release permission expires before the verified state is reached. Under that change, may the verified release value from II.1 still be used? State which part of the model must change and what information is missing for a numerical answer. Distinguish discounting a still-authorized delayed action from removing that action from the feasible set. 

## Part III: Planning and Learning

### III.1 Calculation: which arm earns the next pull?

Use Chapter 11's UCB rule. There are two actions with stationary rewards bounded between zero and one. Each has already been sampled. Use `c=\sqrt{2}` and the natural logarithm.

| Action | Completed pulls `N_t(a)` | Empirical mean `\hat\mu_a` |
|---|---:|---:|
| A | 80 | 0.70 |
| B | 20 | 0.60 |

Calculate `t`, each exploration bonus, and each full index, rounding the final indices to four decimal places. Which action receives the next pull? Explain why the selected action need not have the larger empirical mean and why an index above one is not an assertion that the action's expected reward exceeds one. State the limitation of calling the bonus a value of information. 

### III.2 Diagnostic: information that cannot change the choice

Use Chapters 8 and 11. A hidden state is equally likely to be good or bad. Acting yields utility 12 in the good state and -2 in the bad state. Abstaining yields zero in either state. A free observation has two equally likely outcomes. After the first outcome, the posterior probability of the good state is 0.60; after the second, it is 0.40. These posteriors are consistent with the stated prior. The observation arrives before the decision and has no effect on the state or action set.

Calculate the expected utility of acting before observation and after each possible observation. Find the gross `\operatorname{VOI}(O)` by comparing the expected optimized utility after observation with the best utility beforehand. Does learning about the hidden state necessarily improve this decision? Identify the relevant action threshold. Explain why a system that reports the observation's information content has not yet reported its decision value, even when its report of information content is correct.

### III.3 Changed assumption: the same evidence meets higher stakes

Keep the prior, observation probabilities, posterior probabilities, and abstention payoff from III.2. Change only the utility of acting in the bad state to -10. The good-state utility remains 12. An observation now costs 0.50 utility units, paid regardless of its outcome, and has no other effect.

Compute the best action before observing and after each possible observation. Find the gross value of observation, subtract its cost, and decide whether to acquire it. Identify the largest observation cost consistent with a weak preference for acquisition. Explain why the answer can change even though the information channel is identical. 

## Part IV: Agent Architectures

### IV.1 Calculation: a lost response and an uncertain effect

Use Chapter 17's deliberately simplified retry decision. The response to an authorized non-idempotent tool call was lost. The original attempt is finished or cancelled with a guarantee against later application; the effect either landed or did not. The belief that it landed is `\beta=0.30`. A retry certainly applies the effect if it was absent and duplicates it if it was present. There are no other failures, delay costs, or request costs in this construction. Declining leaves the world as it stands. Use negative cost as utility.

| Input | Value |
|---|---:|
| Belief effect landed `\beta` | 0.30 |
| Duplicate cost `c_{\text{dup}}` | 40 |
| Missing-effect cost `c_{\text{miss}}` | 10 |

Compute the expected cost of retrying and of declining. Calculate the retry threshold and the expected-utility difference in Equation 17.3. Select the preferred action under these assumptions. 

### IV.2 Diagnostic: identical prompts, different worlds

Two executions have exactly the same visible prompt: the request was sent, the response timed out, and no further result is available. In one execution the service applied the effect before losing the response. In the other the request never reached the service. The operation adds a new ledger entry each time it is applied. Retrying does not replace an existing entry.

A developer hashes the prompt and treats matching hashes as proof that the two executions have the same state. Diagnose the error using `x_t=(c_t,m_t,w_t,b_t)`. Which coordinates could agree while the decision-relevant world differs? Explain the role of a belief over the possible effect states when the agent cannot inspect the service directly. Describe one observation that would distinguish these executions and one change to the tool interface that could make the distinction irrelevant to duplicate cost. Explain why known applied does not justify another non-idempotent append, while terminal non-application can permit a fresh authorized attempt. Explain why an empty ledger is insufficient if the original request is still in flight. Do not assume that a successful compensation erases the original entry or its consequences. If a repair is available, state what must be verified before it can support another attempt.

### IV.3 Changed assumption: purchase a decisive read

Keep IV.1's belief and costs. Before choosing whether to retry, the agent may purchase a read that perfectly reveals whether the effect landed. The read costs 1 utility unit, creates no effect, and is guaranteed to finish while the original authorization remains valid. After the read, the agent retries only if the effect is absent. Calculate the gross value of this observation and the net gain over the best action without it.

Now consider a separate interface revision: repetition has exactly the intended effect of one application, including after the original uncertain response. In the simplified cost model this makes `c_{\text{dup}}=0`; all other assumptions remain. Recompute the best action without the read. How much is the same perfect observation worth now, before paying for it? Explain what this comparison reveals about improving observability versus improving the effect semantics of the tool. 

## Part V: Societies of Agents

### V.1 Calculation: charge for the delay imposed on others

Use Chapter 21's directed Braess network. Total flow is one and travelers are nonatomic. Edges S-U and L-T have latency equal to their own flow. Edges U-T and S-L have constant latency one. A directed U-L edge has latency zero. The available routes are S-U-T, S-L-T, and S-U-L-T, carrying `q_{\mathrm{upper}}`, `q_{\mathrm{lower}}`, and `q_{\mathrm{middle}}` respectively.

At the split with half the flow on each outer route and none on the middle route, calculate every route's physical latency and the system's total physical latency. Is that split an equilibrium when each traveler minimizes physical latency? Then replace the experienced edge cost by Chapter 21's marginal-cost latency `\ell^{\mathrm{mc}}_e(q_e)`. Recalculate the three experienced route costs at the same split. Is the split now an equilibrium? Explain why the corrected experienced cost should not be substituted for physical latency when reporting the amount of travel delay.

### V.2 Diagnostic: the final confirmation disappears

Use Chapter 20's finite handshake construction. A sends a proposal to B. On receipt, B sends an acknowledgement. On receiving that acknowledgement, A sends a confirmation. A acts if it has received the acknowledgement; B acts only if it has received the confirmation. No message beyond these is sent, and the channel may lose any message. Silence reveals nothing about delivery. The no-message outcome is that neither party acts.

Compare an execution where all messages arrive with one where only the final confirmation is lost. Write each party's relevant local history and action in both executions. Which party cannot distinguish the executions? Does the rule guarantee that either both act or neither acts? Explain why adding one more acknowledgement does not, by itself, establish such a guarantee for a revised rule. Your answer should identify the observation available to a final receiver and missing from the final sender, rather than merely cite the name of an impossibility result.

### V.3 Changed assumption: remove the shortcut

Return to V.1, restore physical latency as every traveler's objective, and remove the U-L edge. Derive the equilibrium outer-route split and its total latency. Compare that result with the equilibrium when the zero-latency U-L edge is available under the same physical-cost objective. Show why all flow on the middle route is an equilibrium in the latter network; also explain why any positive outer-route flow would fail equilibrium there.

Calculate the ratio of the shortcut network's equilibrium latency to the best physical latency achievable in that network. Chapter 21's expression `1.5+0.5q_{\mathrm{middle}}^2` gives the minimum total latency at a fixed middle flow; explain what is being minimized. State what this example does and does not support about adding connections to a society of agents. 

## Part VI: Trust

### VI.1 Calculation: hard safety stays outside the score

Use Chapters 22 and 27. The following numbers are exact stipulated evaluations of two policies under a common horizon and distribution. Expected cost must not exceed 1. A proposed optimizer instead maximizes expected reward minus twice expected cost. Randomization means choosing one policy before the episode, so rewards and expected costs mix linearly.

| Policy | Expected reward | Expected cost |
|---|---:|---:|
| Careful | 7 | 0.50 |
| Aggressive | 11 | 2.00 |

Calculate each penalized score and identify the selected policy. Check feasibility under the actual expected-cost constraint. If mixing is permitted, determine the largest feasible probability of choosing Aggressive and the resulting expected reward. Then suppose Aggressive also contains an action excluded from `\mathcal A_{\mathrm{auth}}(x)` at the current state. Can the mixture's acceptable expected cost make that action available? Explain the distinction between an expected resource constraint and current authorization.

### VI.2 Diagnostic: a guard result becomes development evidence

Use Chapter 25's constructed guard rule. A fixed candidate procedure has `m=200` independently drawn paired guard cases, each difference bounded in `[-1,1]`. The declared uplift threshold is `\tau=0.25`, and the candidate was fixed before guard access. Compute the one-candidate false-accept bound `\exp(-200(0.25)^2/2)` and the union-bound upper limit for ten separately predeclared candidates meeting the same assumptions.

Now suppose the second guard result was shown to the procedure designer, who uses it to revise the third candidate. Does the ten-candidate accounting still support a release claim for that revised candidate? State what evidence role the consulted guard has acquired and what is needed before release.

Finally, the revised candidate clears the observed uplift threshold, has `\widehat C_G(\phi')\leq c-\varepsilon_{\rm safe}`, but lacks authority for its proposed canary action class. Identify the acceptance condition that blocks release. State one owner, rollback trigger, deadline, and fallback that the canary record must name.

### VI.3 Changed assumption: the destination may miss its deadline

Use Chapter 27. Acting now is correct with probability 0.80. A correct resolution has utility 10 and an incorrect resolution has utility -10. A designated destination is correct with probability `p_E(x)=0.95` when it returns by deadline `\Delta`. A timely delegation incurs a fee of 1, so under guaranteed timely return it can be compared directly with acting. Both routes are authorized.

Change the guarantee: the destination now returns on time with probability 0.60. The fee is paid whenever delegation is initiated, even if no reply arrives. A timely reply retains conditional correctness 0.95. A missed deadline triggers an authorized fallback with utility 2, and no further benefit or cost. Compute the immediate-action value, the guaranteed-return delegation value, and the changed delegation value. Which route wins before and after the change? Find the minimum timely-return probability at which delegation weakly matches acting. Explain why a destination's conditional accuracy alone cannot answer this question.

## Expansion problems

The five problems below extend the existing eighteen. They use the same document-release contract: an intended object, current version and recipient, current authority, a budget, and a confirmed effect. Their numerical inputs are constructed. Solve them before inspecting the separate solutions.

### E.1 Computer use: the saved coordinate

Use Chapter 18. The saved screen puts approved document v2 above unapproved v3. The current screen may preserve that layout or swap the rows. A coordinate policy uses the saved upper-row point. A semantic policy requests v2 by identifier. A transactional policy additionally supplies the saved state version.

1. Assign probability 0.6 to the unchanged layout and 0.4 to the swapped layout. Calculate intended completion and unauthorized release for the coordinate policy without mediation. Then add a monitor that denies every release of v3.
2. In the constant-rate freshness construction, use 0.02 material changes per second and delays of 5, 15, and 30 seconds. Calculate the no-invalidating-change probabilities. Identify what the rate would need to count.
3. A perfect fresh observation costs 1 utility unit. A wrong coordinate has probability 0.2. Compare a denied-attempt cost of 3 with an unguarded harmful-effect cost of 40, both in utility units. Assume observation is followed immediately by execution. Which information purchase pays?

Use the computer-use fixture to inspect which object each command reaches. A transactional denial after a state-version change is different from selecting the wrong document.

### E.2 Learning: feedback that changes the target

Use Chapter 13. The direct route has success probability 0.55. Retrieval raises it to 0.80 and costs 0.05 utility units. Success has utility 1 and failure has utility 0. Let p be the retrieve probability.

1. Calculate expected external utility at p equal to 0, 0.5, and 1.
2. Add 0.30 reward whenever retrieval is avoided. Calculate the same three expected training returns. Does the training objective still prefer the route with higher external success?
3. Use rewards 0 and 1, state potentials 0, 0.4, and 0, and discount one. Calculate shaped rewards and their sum. Repeat with terminal potential 0.2. Explain what changed.

Run the learning probe with separate training and evaluation seeds. Distinguish its exact population quantities from sampled successes. Explain why a successful update under the declared reward need not improve the external task.

### E.3 Orchestration: parallel work and shared error

Use Chapters 19 to 21. Two independent evidence checks each take three seconds. The supervisor's dispatch and combination consume two further seconds. Each check costs two work units; final verification costs one. Team dispatch and combination add three work units. The serial procedure has no supervisor overhead, so its time is the checks alone. The reported time covers evidence checks and supervisor overhead; final verification duration is excluded from both procedures.

1. Compare serial and parallel elapsed times and total costs when the service can run two checks at once.
2. Change capacity to one. What remains of the latency advantage?
3. A shared-source failure has probability 0.1. Otherwise, workers fail independently with probability 0.05 each. Calculate each marginal failure probability, joint failure, and the product of marginals.
4. The parent holds read and verify capabilities. The worker requests read and release. Determine its granted capability set under intersection.

A faster workflow must still satisfy the same authority contract. Do not count requested capabilities as granted ones.

### E.4 Resources: a useful ratio with a missing denominator

Use Chapter 16. Procedures A, B, and C have respective per-attempt costs of 1, 1.5, and 2 monetary units; authorized-success probabilities 0.60, 0.80, and 0.85; and latencies 1, 2, and 5 seconds.

1. Calculate population cost per authorized success, including failed-attempt costs.
2. Apply a minimum success requirement of 0.75 and a three-second deadline. Identify feasible procedures.
3. Extend the deadline to ten seconds and assign each failed task a loss of 20 monetary units. Compare expected combined costs for B and C.
4. Two attempts cost 2 and 3 monetary units; neither succeeds. Report total cost, successes, and empirical cost per success.

State which quantities are population inputs and which describe the two observed attempts. A permission violation would make an otherwise attractive procedure infeasible.

### E.5 Evaluation: repeat the task before averaging

Use Chapter 24. Two equally weighted tasks have success probabilities 0.2 and 0.8. Repeated runs are independent conditional on task, with identical procedure and reset rules.

1. Calculate mean single-run success, average all-success probability for two runs, and average at-least-one success probability.
2. Compare those results with squaring the mean and applying coverage to the mean. Explain which experiment each calculation describes.
3. A recorded bank has three successes and one failure. Calculate the fraction of two-run subsets with all successes and with at least one success.
4. Unfamiliar-task success is 0.4. A constructed evaluation contains 20 percent exposed tasks with success probability one. Calculate aggregate success. State what this number cannot establish about unfamiliar-task improvement.


## Closing task: one request, one record

### C.1 Cumulative: from drills to a decision record

Treat II.1, IV.1, and VI.3 as three stages of one constructed request, `R-7`, for document version `v2`. In stage one the agent chooses between verifying and releasing. In stage two the release times out. In stage three the agent chooses between acting again and delegating to the document owner. Stipulate that acting again means a second submission of `R-7`. Each case declares its own utility scale, so do not add or compare values across stages.

Complete one row per stage with these fields: belief about the effect and its source; action chosen; value, threshold, or flip condition. Then record what evidence does not establish, what remains unresolved with an owner, deadline, and fallback, which earlier problem's method does not apply to `R-7`, and where two stages conflict and which one binds.

## Worked Solutions

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

## One document request through the controller

A user asks the controller to release a specified document to a named recipient once its claims are supported. This constructed episode follows that request through the book's separate mechanisms. Its contract permits reading sources, preparing candidates, checking the release record, and one release submission after evidence and authorization checks. It also permits a read-only status check and a handoff to the document owner. It does not permit an unverified second submission. The budget reserves capacity for that status check and handoff before optional generation begins; no numerical utility scale from another example is imported.

The initial state contains the request, document version, recipient, current grant, source references, and remaining resources. A compact memory retains these decision facts and their provenance. It drops an irrelevant formatting discussion, but preserves that one factual claim lacks support. The prose draft is not itself evidence that the missing claim is true.

| Stage | Observation or retained state | Controller decision |
|---|---|---|
| Gather evidence | Source passage resolves the missing claim; version and locator retained | Continue with the same document request |
| Compare candidates | Draft alternatives differ in wording, with no new supporting evidence | Select the supported version; stop optional sampling |
| Check authority | Current grant covers the selected final document version, recipient, and release condition | Admit the specified release action |
| Submit release | Service times out after accepting the request for processing | Record effect as unresolved |
| Inspect status | Read-only status check still reports pending | Hold further submissions; prepare handoff |
| Transfer decision | Packet to document owner contains request identifier, evidence, and unresolved state | End autonomous action with a bounded follow-up route |

Each admitted step uses Chapter 5’s normalized transition over the composite state. A failed authority or precondition check takes its explicit rejection branch, consuming any declared checking cost without executing the rejected world effect. The trace follows the admitted release branch; it does not silently discard rejected proposals.

Candidate generation changes what the controller can choose among. It does not establish that a selected candidate is supported or grant permission to send it. Here the retrieved passage supplies evidence, the selector chooses wording, and the authority check binds the selected final version and recipient before admitting a particular world-changing action. Stopping optional sampling preserves the reserved recovery capacity. A new candidate would not answer whether a release submission later took effect.

The timeout creates a different uncertainty. The controller knows it submitted a request and lacks a completed response. It does not know whether the recipient received the document. Memory therefore retains the original request identifier and the distinction between attempted, pending, and confirmed effect. The status check consumes its reserved allowance without resolving that distinction. Pending is neither verified non-application nor permission to retry; the original request may still complete.

The controller now holds further submissions and transfers the packet to the document owner through the authorized channel. The handoff names the owner, the unresolved effect, and the next day’s noon review as its deadline. If no response arrives by that deadline, the fallback keeps further submissions blocked and returns control to the requester. No human acceptance or successful delivery is assumed. The episode ends with an auditable unresolved state and a named next decision, rather than manufacturing completion from a timeout or spending another sample on uncertainty that only execution evidence can resolve.

### Simulator probes

Use this small manifest to compare a matching approval with a stale approval under the same document version. If you did not extract `document-release-simulator.zip`, save the manifest as `release-probe.json` in the working folder. The `mathematical-agent-probes.zip` and `math-ai-agents-lab.zip` packages already contain the same manifest at `Companion/fixtures/release-probe.json`:

```json
{
  "seed": 0,
  "runs": [
    {"version": "v2", "approval_for": "v2", "seed": 0},
    {"version": "v2", "approval_for": "v1", "seed": 0}
  ]
}
```

The two rows differ only in approval scope. Each case records its seed explicitly; the top-level seed labels the manifest.

Run the simulator with this manifest from the folder that holds `scripts`. With `release-probe.json` saved there, or extracted from `document-release-simulator.zip`, use the first command. With either larger package, use the second:

```text
python3 scripts/document_release_simulator.py --manifest release-probe.json
python3 scripts/document_release_simulator.py --manifest Companion/fixtures/release-probe.json
```

On Windows, use `py -3` in place of `python3` if that is your Python launcher. The output is JSON: the matching row reports `authorized_release`, while the stale row reports `abstained`.

To investigate the other named faults, change one case at a time:

1. Keep `version` and `approval_for` equal to `v2`, and add `"fault": "dropped_acknowledgement"`. Expect a release proposal with `actual_effect` equal to `pending`, not confirmed delivery.
2. Replace that fault with `duplicate_request`. Expect `duplicate_effect`; the output records two applications rather than authorized completion.
3. Replace it with `late_cancellation`. Expect `recovered`; inspect the recorded released-and-rolled-back effect rather than assuming the original action never happened.
4. Compare the outcome, actual effect, cost, recovery time, and remaining budget across cases. You should be able to distinguish a policy proposal from an observed service effect.
5. For Chapter 10's simulator exercise, keep both fields equal to `v2` and add `"fault": "document_changed"`. Expect `abstained` with `actual_effect` equal to `restart_required`: the release option restarts instead of inheriting its predecessor's approval.
6. For Chapter 13's simulator exercise, add `"policy": "trained"` to the stale row (`approval_for` equal to `v1`), then repeat with `"policy": "fixed"`. Both report `abstained`; with `approval_for` equal to `v2`, both report `authorized_release`. The policy label does not change what the approval authorizes.

`scripts/document_release_simulator.py` makes this constructed trace reproducible. Try matching version and approval scope for authorized release. Then change only approval scope from `v2` to `v1`; outcome must be abstention. Change only fault to `dropped_acknowledgement`; proposal remains release, while actual effect becomes pending and another release is blocked. Finally inject `duplicate_request` or `late_cancellation`; those are distinct effects, not proof that a request stayed safely idempotent. The manifest records seed, fault, proposal, actual effect, cost, recovery time, and remaining budget. It is a deterministic teaching harness, not a model of a production document service.

## Expansion solutions

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


## Running the expansion probes

Extract the complete companion package and open a terminal in its root folder. Each command below reads one local fixture and prints JSON. On Windows, substitute py -3 for python3 when appropriate. The companion README identifies expected-output files and the chapter served by each probe.

1. Run the computer-use fixture. Inspect reached document, effect document, denial, and pending confirmation.
2. Run the learning fixture. Compare actual updated policies with the fixed baseline and separate sampled evaluation from exact expected values.
3. Run orchestration at capacity two, then capacity one. Compare elapsed time and work costs before interpreting team performance.
4. Run resources with a three-second deadline, then ten seconds. Retain zero-success procedures with an unavailable ratio.
5. Run evaluation with two repetitions. Compare task-first repetition with powers of the aggregate mean.

```text
python3 scripts/computer_use_probe.py --manifest Companion/fixtures/computer-use.json
python3 scripts/agent_learning_probe.py --manifest Companion/fixtures/learning.json
python3 scripts/orchestration_probe.py --manifest Companion/fixtures/orchestration.json
python3 scripts/resource_allocation_probe.py --manifest Companion/fixtures/resources.json
python3 scripts/evaluation_probe.py --manifest Companion/fixtures/evaluation.json
```

The commands execute finite constructed programs, not language-model benchmarks. Open the local release-console HTML file for the visual version of the stale-coordinate example. Its effects remain inside the page.
