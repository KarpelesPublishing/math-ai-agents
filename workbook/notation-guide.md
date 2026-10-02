# Notation Guide

Chapter links in this companion copy open the corresponding laboratory reading page. The symbols and explanations are retained from the book; its original notation source is preserved in reference-sources/notation-guide.md.

Core symbols carry their meanings across chapters. Explicitly declared local aliases and diagram
labels are scoped where they appear; a local count or vertex label does not redefine a global quantity.

That rule costs something. It means a few symbols are less conventional than the ones a specialist
in one subfield would expect, because a letter that is standard in information theory may already be
doing a job in decision theory. Where this book departs from a field's usual notation, it is to
avoid a collision, and the departure is noted at the point of use.

This guide is for returning to, not for memorizing. Every symbol is also defined where it first
appears.

## Conventions

- Scalars are italic; vectors are bold lowercase; matrices are uppercase.
- Sets, spaces, and operators use calligraphic or roman forms.
- Random variables are uppercase and their realized values are the matching lowercase letter, so the
  composite state random variable is written one way and a particular value of it another.
- Named operations such as `dec`, `Mem`, and `Reach` are roman, never italic single letters.
- Probability is `\Pr` and expectation is `\mathbb E`. Chapters 1 and 22 typeset the expectation operator as `\mathbb E`; Chapters 6, 7, 10, 11, 13, 15, 16, and 19 typeset the same operator as roman `E` (`\operatorname{E}` or `\mathrm{E}`). Both forms denote one operator. A plain `E` used as a subscript label, such as a delegated destination in Chapter 27, names a thing and is not an operator.
- Every logarithm states its base or its units at first use.
- Subscript `t` is time, except where a chapter declares otherwise (Chapter 19's matrix `M_{st}` uses `s` and `t` as run indices). Subscript `m` indexes a member of a declared model family.
- A few letters change meaning between chapters, for example `\Gamma`, `\alpha`, `\delta`, `\tau`, `C`, `z`, `u`, `\Phi`, and `\lambda`. Each meaning is scoped to the chapter listed beside it and restated where it applies.

## The two quantities the book is built on

Two objects recur from Part I onward and are worth reading before Chapter 1.

**The score of an assembly.** `U_\mathcal V(S)=\mathbb E[Y_S\mid\mathcal V]` is the population score of
the system built from enabled component set `S`, under declared evaluation contract `\mathcal V`;
`Y_S` is the score of one run of that system.
`\widehat U_\mathcal V(S)` is its finite-sample estimate. The contract fixes task distribution,
scoring rule and units, sampling settings, resource budget, and stopping rule. When the set holds
only the frozen model, `U` describes the model-alone system. As components are
added to the set, the same notation carries through unchanged, which is the point of writing it this
way.

**The interaction contrast.** `\Gamma(A;B)` is the signed difference between the joint gain and the
sum of isolated gains under one matched evaluation contract. Four scores identify this nonadditivity,
not a mechanism or the necessity of either component. Chapter 2 defines it. `\rho_\Gamma` divides the
contrast by the positive total joint gain. Nonnegative isolated gains and a nonnegative contrast
additionally make the ratio a fraction between zero and one. Negative contrasts remain meaningful signed quantities.


## Part I symbols

| Symbol | Meaning | Introduced |
|---|---|---:|
| `K_\theta(z\mid c)` | Model conditional law over outputs given context | [1](../guide/chapters/01-score-threshold.html) |
| `U_\mathcal V(S)` | Population task score of assembly `S` | [1](../guide/chapters/01-score-threshold.html) |
| `\widehat U_\mathcal V(S)` | Finite-sample estimate of that task score | [1](../guide/chapters/01-score-threshold.html) |
| `\operatorname{dec}` | Decoding map from a distribution to a candidate output | [1](../guide/chapters/01-score-threshold.html) |
| `\operatorname{eval}_\tau` | Evaluator with threshold, parser, or tolerance `\tau` | [1](../guide/chapters/01-score-threshold.html) |
| `\theta` | Model parameters, frozen unless a chapter says otherwise | [1](../guide/chapters/01-score-threshold.html) |
| `\mathbb E` | Expectation, as in Chapters 1 and 22 (Chapters 6, 7, 10, 11, 13, 15, 16, and 19 write the same operator as roman `E`; a plain subscript label such as Chapter 27's `p_E` is not this operator) | [1](../guide/chapters/01-score-threshold.html) |
| `\mathcal V` | Declared evaluation contract: task distribution, scoring rule and units, sampling settings, budget, and stopping rule | [1](../guide/chapters/01-score-threshold.html) |
| `q`, `n` | Per-token success probability and target length in the exact-match example, so the score is `q^n` | [1](../guide/chapters/01-score-threshold.html) |
| `\Gamma(A;B)` | Interaction contrast between component sets | [2](../guide/chapters/02-four-cell-interaction.html) |
| `\rho_\Gamma` | Interaction share of total joint gain | [2](../guide/chapters/02-four-cell-interaction.html) |
| `q_m` | Per-attempt success probability for family member `m` | [3](../guide/chapters/03-prospective-forecast.html) |
| `\operatorname{pass}_\tau(q_m)` | Thresholded pass indicator on `q_m` | [3](../guide/chapters/03-prospective-forecast.html) |
| `L(C)=aC^b+c` | Fitted pretraining-loss curve; `C` is training compute and `a`, `b`, `c` are fitted constants | [3](../guide/chapters/03-prospective-forecast.html) |
| `\psi` | Fitted forecast parameters | [3](../guide/chapters/03-prospective-forecast.html) |
| `f_\psi`, `\epsilon_m` | Fitted forecast function and its error for member `m` | [3](../guide/chapters/03-prospective-forecast.html) |
| `\Gamma_m` | Interaction contrast measured for family member `m` | [3](../guide/chapters/03-prospective-forecast.html) |
| `z_m` | Declared predictor features for member `m` | [3](../guide/chapters/03-prospective-forecast.html) |
| `G` | Action graph: vertices are controller states, edges are allowed transitions | [4](../guide/chapters/04-permission-reachability.html) |
| `V_0` | Initial vertex set | [4](../guide/chapters/04-permission-reachability.html) |
| `\operatorname{step}` | One-transition successor map on vertex sets | [4](../guide/chapters/04-permission-reachability.html) |
| `\operatorname{Reach}_G(V_0)` | Reachable set | [4](../guide/chapters/04-permission-reachability.html) |
| `\operatorname{Act}(v)` | Candidate actions at vertex `v` | [4](../guide/chapters/04-permission-reachability.html) |
| `\mathcal{G}` | Permission grant rule: maps a set of candidate actions to the permitted subset | [4](../guide/chapters/04-permission-reachability.html) |
| `\operatorname{Allowed}_{\mathcal G}(v)` | Permitted actions after filtering | [4](../guide/chapters/04-permission-reachability.html) |
| `\Pi_{G,v}(p)` | Infinite-cluster probability | [4](../guide/chapters/04-permission-reachability.html) |
| `p_c(G,v)` | Critical probability | [4](../guide/chapters/04-permission-reachability.html) |
| `d` | Branching factor or degree | [4](../guide/chapters/04-permission-reachability.html) |
| `x_t=(c_t,m_t,w_t,b_t)` | Composite agent state realization | [5](../guide/chapters/05-composite-kernel.html) |
| `w_t` | World or environment state | [5](../guide/chapters/05-composite-kernel.html) |
| `P(x_{t+1}\mid x_t)` | Composite transition kernel | [5](../guide/chapters/05-composite-kernel.html) |
| `\operatorname{Mem}` | Memory map from the whole history to the retained memory `m_t`; the update itself is part of `\operatorname{Upd}` | [5](../guide/chapters/05-composite-kernel.html) |
| `\pi_\theta(z,a\mid x)` | Proposal policy: model law times decoder | [5](../guide/chapters/05-composite-kernel.html) |
| `\kappa` | Coarse-graining map | [5](../guide/chapters/05-composite-kernel.html) |
| `H(X)`, `I(X;Y)` | Shannon entropy, mutual information | [5](../guide/chapters/05-composite-kernel.html) |
| `\operatorname{Grant}(g\mid x,u)` | Normalized permission-outcome law, including denial | [5](../guide/chapters/05-composite-kernel.html) |
| `\operatorname{Env}(w',o\mid x,u,g)` | Joint next-world and observation law | [5](../guide/chapters/05-composite-kernel.html) |
| `\operatorname{Upd}(c',m',b'\mid x,u,g,w',o)` | Joint context, memory, and budget update law | [5](../guide/chapters/05-composite-kernel.html) |
| `P_{\mathrm{env}}(x'\mid x,u)` | Controlled transition given a full proposal | [5](../guide/chapters/05-composite-kernel.html) |
| `P_\theta(x'\mid x)` | Closed-loop transition after averaging over proposal policy | [5](../guide/chapters/05-composite-kernel.html) |
| `u=(z,a)` | Full proposal: model output and decoded action | [5](../guide/chapters/05-composite-kernel.html) |

## Symbols introduced after Part I

| Symbol | Meaning | Introduced |
|---|---|---:|
| `u(y)` | Utility of a single outcome | [6](../guide/chapters/06-expected-utility.html) |
| `y` | An outcome of an action | [6](../guide/chapters/06-expected-utility.html) |
| `\mathcal{A}` | The action set available at a state | [6](../guide/chapters/06-expected-utility.html) |
| `\operatorname{EU}(a)` | Expected utility of an action | [6](../guide/chapters/06-expected-utility.html) |
| `\operatorname{CE}` | Certainty equivalent | [6](../guide/chapters/06-expected-utility.html) |
| `\operatorname{Ret}_t` | Return, the discounted sum of future rewards | [7](../guide/chapters/07-finite-horizon-planning.html) |
| `r_t` | Reward received on the transition out of `x_t` | [7](../guide/chapters/07-finite-horizon-planning.html) |
| `\gamma` | Discount factor | [7](../guide/chapters/07-finite-horizon-planning.html) |
| `\pi(a\mid x)` | Stochastic policy | [7](../guide/chapters/07-finite-horizon-planning.html) |
| `V^{\pi}`, `V^{\star}` | State value under a policy, and under an optimal policy | [7](../guide/chapters/07-finite-horizon-planning.html) |
| `Q^{\pi}` | Action value under a policy | [7](../guide/chapters/07-finite-horizon-planning.html) |
| `\Phi(x)` | Local shaping potential | [7](../guide/chapters/07-finite-horizon-planning.html) |
| `\mathcal{X}` | The finite state set | [8](../guide/chapters/08-belief-information.html) |
| `\mathbf{b}_t` | Belief, a distribution over `\mathcal{X}` at time `t` | [8](../guide/chapters/08-belief-information.html) |
| `\mathcal{B}` | The belief simplex, the set of distributions over `\mathcal{X}` | [8](../guide/chapters/08-belief-information.html) |
| `\operatorname{Obs}(o\mid x,a)` | Observation kernel: the chance of seeing `o` on arriving in `x` after `a` | [8](../guide/chapters/08-belief-information.html) |
| `\bar r(\mathbf{b},a)` | Expected reward of action `a` under belief `\mathbf{b}` | [8](../guide/chapters/08-belief-information.html) |
| `J(x',o\mid x,a)` | Filtered joint next-state and observation law | [8](../guide/chapters/08-belief-information.html) |
| `\Gamma_H`, `\alpha` | Finite-horizon policy-vector set and one vector | [8](../guide/chapters/08-belief-information.html) |
| `\operatorname{VOI}(O)` | Value of observing `O` before a declared decision; Chapter 27 writes `\operatorname{VOI}(o)` for one realized observation | [8](../guide/chapters/08-belief-information.html) |
| `g(v)`, `h(v)` | True cost from the start to vertex `v`, and true cost from `v` to the nearest goal | [9](../guide/chapters/09-astar-audit.html) |
| `f(v)` | Cost of the best path constrained to pass through `v` | [9](../guide/chapters/09-astar-audit.html) |
| `\hat g(v)`, `\hat h(v)`, `\hat f(v)` | The computable estimates of each | [9](../guide/chapters/09-astar-audit.html) |
| `\operatorname{cost}(u,v)` | Cost of the edge from `u` to `v` | [9](../guide/chapters/09-astar-audit.html) |
| `s`, `\mathcal{T}` | Start vertex and goal set | [9](../guide/chapters/09-astar-audit.html) |
| `\operatorname{Exp}(A,G)` | Number of vertices algorithm `A` expands on graph `G` | [9](../guide/chapters/09-astar-audit.html) |
| `h(u,v)` | True minimum path cost from `u` to `v`, distinct from the heuristic estimate `\hat h(v)` | [9](../guide/chapters/09-astar-audit.html) |
| `\mathcal{I}_o` | Initiation set of option `o`: the states where the option may start | [10](../guide/chapters/10-option-duration.html) |
| `\pi_o` | Option `o`'s internal policy, mapping execution information to a primitive action | [10](../guide/chapters/10-option-duration.html) |
| `\beta_o` | Option `o`'s termination condition | [10](../guide/chapters/10-option-duration.html) |
| `\mu` | Policy over options: the parent policy that selects which option to run | [10](../guide/chapters/10-option-duration.html) |
| `a_t` | Action selected at step `t`; in Chapter 11, the next action selected after `t` completed pulls | [11](../guide/chapters/11-bounded-exploration.html) |
| `\operatorname{Reg}(T)` | Regret accumulated over `T` rounds | [11](../guide/chapters/11-bounded-exploration.html) |
| `\hat\mu_a` | Empirical mean payoff of action `a` | [11](../guide/chapters/11-bounded-exploration.html) |
| `N_t(a)` | Number of pulls of action `a` among the `t` completed pulls, before the next decision | [11](../guide/chapters/11-bounded-exploration.html) |
| `\operatorname{Gain}(O)` | Decision-relevant information in an observation | [11](../guide/chapters/11-bounded-exploration.html) |
| `\hat V_t(x)` | The agent's current estimate of the value of state `x` | [12](../guide/chapters/12-trajectory-credit.html) |
| `\delta_t` | Temporal-difference error at step `t` | [12](../guide/chapters/12-trajectory-credit.html) |
| `\alpha` | Step size for an update | [12](../guide/chapters/12-trajectory-credit.html) |
| `\lambda` | Weighting between the one-step estimate and the realized outcome | [12](../guide/chapters/12-trajectory-credit.html) |
| `\operatorname{Ret}^{\lambda}_t` | The weighted return that interpolates between them | [12](../guide/chapters/12-trajectory-credit.html) |
| `\operatorname{Pot}(x)` | Bounded shaping potential on declared state | [13](../guide/chapters/13-finite-policy-learning.html) |
| `r'_t, G'_0` | Shaped reward and return; the original reward `r` and the return keep their meaning (Chapter 13 gives the return a local alias for Chapter 7's `\operatorname{Ret}_t`) | [13](../guide/chapters/13-finite-policy-learning.html) |
| `\phi` | Trainable policy parameters, distinct from the frozen model parameters `\theta` | [13](../guide/chapters/13-finite-policy-learning.html) |
| `\hat P(x'\mid x,a)` | Learned transition-model estimate | [14](../guide/chapters/14-transition-model-bound.html) |
| `\widehat{\operatorname{Obs}}` | Learned observation-kernel estimate | [14](../guide/chapters/14-transition-model-bound.html) |
| `\epsilon` | Uniform one-step total-variation model error | [14](../guide/chapters/14-transition-model-bound.html) |
| `\tau_{\text{samp}}` | Sampling temperature of a generative model | [14](../guide/chapters/14-transition-model-bound.html) |
| `R` | Upper bound on the common expected immediate state-action reward | [14](../guide/chapters/14-transition-model-bound.html) |
| `H_{\max}` | Declared finite planning cap | [14](../guide/chapters/14-transition-model-bound.html) |
| `R^\star` | Retained record set chosen under the token budget | [15](../guide/chapters/15-memory-budget.html) |
| `c(m)`, `B`, `\lambda` (Chapter 15) | Raw token cost of record `m`, the token budget, and decision-value units per token | [15](../guide/chapters/15-memory-budget.html) |
| `\varepsilon`, `2\varepsilon` (Chapter 15) | Summary value tolerance and the resulting regret bound | [15](../guide/chapters/15-memory-budget.html) |
| `\operatorname{Cov}(k)` | Coverage at `k`: the chance that at least one of `k` samples is correct | [16](../guide/chapters/16-sample-allocation.html) |
| `\operatorname{Sel}(k)` | Selection at `k`: the chance that the returned sample is correct | [16](../guide/chapters/16-sample-allocation.html) |
| `\widehat c_{\mathrm{success}}` | Total attempt cost divided by authorized confirmed completions | [16](../guide/chapters/16-sample-allocation.html) |
| `\pi(k)` | Measured chance that the selector's top-ranked sample is correct given `k` candidates that contain at least one correct candidate | [16](../guide/chapters/16-sample-allocation.html) |
| `d` | Probability that the selector scores one correct sample above one incorrect sample | [16](../guide/chapters/16-sample-allocation.html) |
| `\operatorname{eff}(T,x)` | State resulting from applying tool `T` in state `x` | [17](../guide/chapters/17-effect-and-retry.html) |
| `\operatorname{resp}(T,x)` | Report returned by tool `T` in state `x` | [17](../guide/chapters/17-effect-and-retry.html) |
| `\operatorname{undo}(T)` | Recovery tool for an effect of `T` | [17](../guide/chapters/17-effect-and-retry.html) |
| `\operatorname{Rep}(x)` | Conservative set of eligible repeat attempts | [17](../guide/chapters/17-effect-and-retry.html) |
| `\operatorname{Ready}(T,x)` | Current authorization and preconditions for a repeat attempt | [17](../guide/chapters/17-effect-and-retry.html) |
| `\operatorname{Absent}(T,x)` | Authoritative terminal non-application of the original attempt | [17](../guide/chapters/17-effect-and-retry.html) |
| `\operatorname{Restored}(T,x)` | Verified recovery of relevant consequences and preconditions | [17](../guide/chapters/17-effect-and-retry.html) |
| `\beta`, `c_{\text{dup}}`, `c_{\text{miss}}` | Belief that the effect already landed, cost of a duplicate effect, and cost of the effect never happening | [17](../guide/chapters/17-effect-and-retry.html) |
| `\operatorname{Exec}_{\mathrm{ui}}(\tilde a\mid x,a)` | Normalized realized-operation law | [18](../guide/chapters/18-interface-freshness.html) |
| `P_{\mathrm{ui}}` | Execution-composed world kernel | [18](../guide/chapters/18-interface-freshness.html) |
| `\operatorname{Act}_{\mathrm{ui}}` | Finite realized-operation set including declared denial/no-effect operations | [18](../guide/chapters/18-interface-freshness.html) |
| `\mathcal A_{\mathrm{rob}}(\mathbf b)` | Intersection of correctly specified authorization sets over belief support | [18](../guide/chapters/18-interface-freshness.html) |
| `\lambda_{\mathrm{ui}}, \operatorname{Fresh}(\Delta)` | Material-change rate and no-invalidating-change probability | [18](../guide/chapters/18-interface-freshness.html) |
| `\mathcal A_{\mathrm{auth}}(x)` | Commands whose protected effect is authorized in state `x` | [18](../guide/chapters/18-interface-freshness.html) |
| `u_i(\pi_1,\pi_2)` | Payoff to party `i` under a pair of policies | [19](../guide/chapters/19-cross-play-transfer.html) |
| `\pi_i^{(s)}` | Party `i` policy from training run `s` | [19](../guide/chapters/19-cross-play-transfer.html) |
| `\operatorname{diag}(M)`, `\operatorname{off}(M)` | Matched-run and cross-run mean returns | [19](../guide/chapters/19-cross-play-transfer.html) |
| `\operatorname{JPC}(M)` | Proportional cross-play loss | [19](../guide/chapters/19-cross-play-transfer.html) |
| `\operatorname{BR}_i(\pi_{-i})` | Best response by party `i` to the other policy | [19](../guide/chapters/19-cross-play-transfer.html) |
| `M` | Matched matrix whose entry `M_{st}` pairs run `s` against run `t` | [19](../guide/chapters/19-cross-play-transfer.html) |
| `\operatorname{Know}_i(F)` | Party `i` knows proposition `F` | [20](../guide/chapters/20-bounded-message-knowledge.html) |
| `\operatorname{MK}_{\mathcal P}^n(F)` | `n` levels of mutual knowledge among party set `\mathcal P` | [20](../guide/chapters/20-bounded-message-knowledge.html) |
| `\operatorname{CK}_{\mathcal P}(F)` | Common knowledge of `F` among party set `\mathcal P` | [20](../guide/chapters/20-bounded-message-knowledge.html) |
| `q_e` | Nonnegative flow on traffic-network edge `e` | [21](../guide/chapters/21-congestion-incentives.html) |
| `\ell_e(q_e)` | Latency incurred on edge `e` at flow `q_e` | [21](../guide/chapters/21-congestion-incentives.html) |
| `\operatorname{TL}(q)` | Total latency of a feasible network flow `q` | [21](../guide/chapters/21-congestion-incentives.html) |
| `q^{\mathrm{NE}}` | Nash-equilibrium flow | [21](../guide/chapters/21-congestion-incentives.html) |
| `q^{\star}` | Total-latency-minimizing flow | [21](../guide/chapters/21-congestion-incentives.html) |
| `\ell^{\mathrm{mc}}_e(q_e)` | Marginal-cost latency imposed by edge `e` | [21](../guide/chapters/21-congestion-incentives.html) |
| `q_{\mathrm{upper}}`, `q_{\mathrm{lower}}`, `q_{\mathrm{middle}}` | Flows on the three directed Braess routes S-U-T, S-L-T, S-U-L-T | [21](../guide/chapters/21-congestion-incentives.html) |
| `\gamma_{\mathrm{cap}}` | Extra-traffic fraction in the bicriteria routing comparison | [21](../guide/chapters/21-congestion-incentives.html) |
| `C` | Declared episode-cost random variable for tail-risk accounting | [22](../guide/chapters/22-risk-authority-contract.html) |
| `\operatorname{CVaR}_{\alpha}(C)` | Conditional value at risk of `C` at declared tail level `\alpha` | [22](../guide/chapters/22-risk-authority-contract.html) |
| `z` | Candidate tail cutoff in CVaR's infimum representation | [22](../guide/chapters/22-risk-authority-contract.html) |
| `B`, `b_t` | Declared bounded-horizon risk budget and remaining budget before decision `t` | [22](../guide/chapters/22-risk-authority-contract.html) |
| `\widehat r_t(a_t)` | Conservative charged risk estimate for action `a_t` at time `t` | [22](../guide/chapters/22-risk-authority-contract.html) |
| `\operatorname{Ret}^{\pi}` | Expected discounted reward under policy `\pi` | [22](../guide/chapters/22-risk-authority-contract.html) |
| `\mathcal I` | Set of states in which a named invariant holds | [22](../guide/chapters/22-risk-authority-contract.html) |
| `\operatorname{Cost}_i^{\pi}` | Expected discounted auxiliary-cost return | [22](../guide/chapters/22-risk-authority-contract.html) |
| `d_i` | Declared limit on auxiliary cost `i` | [22](../guide/chapters/22-risk-authority-contract.html) |
| `\mathcal T` | Declared threat model | [22](../guide/chapters/22-risk-authority-contract.html) |
| `\varepsilon_{\mathrm{safe}}` | Deliberate safety margin | [22](../guide/chapters/22-risk-authority-contract.html) |
| `A_{C_i}^{\pi_k}(s,a)` | Constraint advantage for auxiliary cost `i` | [22](../guide/chapters/22-risk-authority-contract.html) |
| `\epsilon_i` | Largest candidate-policy expected constraint advantage | [22](../guide/chapters/22-risk-authority-contract.html) |
| `\delta` | Ideal CPO step-size bound | [22](../guide/chapters/22-risk-authority-contract.html) |
| `\lambda_{\mathrm{safe}}` | Fixed multiplier between reward and one auxiliary cost | [22](../guide/chapters/22-risk-authority-contract.html) |
| `\mathcal C_{\mathrm{parent}}`, `\mathcal C_{\mathrm{child}}` | Declared capability sets of a delegating parent and a delegated child | [23](../guide/chapters/23-local-security-monitor.html) |
| `M_t`, `e_t` | Monitor's enforcement-layer record at time `t`, and one observed event | [23](../guide/chapters/23-local-security-monitor.html) |
| `\operatorname{Mon}` | Monitor update map from prior record and one observed event to the next record | [23](../guide/chapters/23-local-security-monitor.html) |
| `\delta`, `v`, `r` | Document identity, version, and recipient in the publish predicate | [23](../guide/chapters/23-local-security-monitor.html) |
| `\operatorname{Approved}(M_t)` | Set of `(\delta,v,r)` triples the monitor's current record authorizes for release | [23](../guide/chapters/23-local-security-monitor.html) |
| `\operatorname{Publish}(\delta,v,r,M_t)` | Boolean predicate: is this exact document-version-recipient triple currently approved | [23](../guide/chapters/23-local-security-monitor.html) |
| `\mathcal F` | One declared, finite attack family under a fixed threat model | [23](../guide/chapters/23-local-security-monitor.html) |
| `\operatorname{Risk}(\mathcal F)` | Worst-case violation probability across `\mathcal F` | [23](../guide/chapters/23-local-security-monitor.html) |
| `k` | Number of samples drawn | [24](../guide/chapters/24-matched-capability.html) |
| `p` | Probability that one sample is correct | [24](../guide/chapters/24-matched-capability.html) |
| `N_{\mathrm{eval}}` | Number of evaluated task instances | [24](../guide/chapters/24-matched-capability.html) |
| `\Delta_{\mathrm{match}}(\theta)` | Score difference for frozen model `\theta` between a named benchmark and its matched evaluation | [24](../guide/chapters/24-matched-capability.html) |
| `\zeta` | Declared threshold on a continuous metric when defining a thresholded scale onset | [24](../guide/chapters/24-matched-capability.html) |
| `\operatorname{Onset}_{\zeta}` | First declared family scale at which the thresholded metric reaches `\zeta` | [24](../guide/chapters/24-matched-capability.html) |
| `\mathcal K` | Fixed same-bank task set used to compare coverage with deployed selection | [24](../guide/chapters/24-matched-capability.html) |
| `\widehat{\operatorname{Cov}}_{\mathcal K}(k)`, `\widehat{\operatorname{Sel}}_{\mathcal K}(k)` | Empirical same-bank coverage and deployed-selector success after `k` candidates per task | [24](../guide/chapters/24-matched-capability.html) |
| `\mathcal C`, `\xi` | Finite tested configuration set and one configuration index | [24](../guide/chapters/24-matched-capability.html) |
| `\Pr` | Probability over Equation 24.4's declared sampling or resampling design | [24](../guide/chapters/24-matched-capability.html) |
| `\operatorname{Lower}^{\mathrm{sim}}_{\alpha_{\mathrm{tail}}}(\xi)` | Lower score bound for configuration `\xi` from a procedure with joint coverage across all tested configurations | [24](../guide/chapters/24-matched-capability.html) |
| `\operatorname{SE}_{\mathrm{match}}` | Estimated standard error of a difference of independent bank pass proportions | [24](../guide/chapters/24-matched-capability.html) |
| `\alpha_{\mathrm{tail}}` | Tail probability level for the simultaneous lower-bound guarantee | [24](../guide/chapters/24-matched-capability.html) |
| `\operatorname{LCF}_{\alpha_{\mathrm{tail}}}` | Simultaneous lower confidence frontier across tested configurations | [24](../guide/chapters/24-matched-capability.html) |
| `\phi_t`, `\phi'` | Parent and candidate versions of the agent procedure around frozen weights | [25](../guide/chapters/25-development-guard-gate.html) |
| `\widehat\Delta_G(\phi')`, `G` | Guard-set estimate and its frozen guard cases for the named candidate | [25](../guide/chapters/25-development-guard-gate.html) |
| `\widehat C_G(\phi')`, `\mathcal G` | Guard cost estimate and authority envelope for the proposed release | [25](../guide/chapters/25-development-guard-gate.html) |
| `\tau`, `c`, `\varepsilon_{\rm safe}` | Local uplift threshold, cost limit, and reserved safety margin | [25](../guide/chapters/25-development-guard-gate.html) |
| `D`, `\widehat V_D` | Development set and a procedure's estimated value on it | [25](../guide/chapters/25-development-guard-gate.html) |
| `\mathcal M`, `\Phi_t` | Declared bounded family of procedure changes and the finite candidate collection compared on `D` | [25](../guide/chapters/25-development-guard-gate.html) |
| `m`, `Z_i(\phi')` | Number of guard cases and the paired candidate-minus-parent outcome on guard case `i`, bounded in `[-1,1]` | [25](../guide/chapters/25-development-guard-gate.html) |
| `\Delta(\phi')` | Population mean of `Z_i(\phi')`: the candidate's true uplift, an unknown parameter | [25](../guide/chapters/25-development-guard-gate.html) |
| `\operatorname{Authorized}_{\mathcal G}`, `\operatorname{Rollback}` | Boolean authority predicate for the proposed release and the check for a tested path back to the parent | [25](../guide/chapters/25-development-guard-gate.html) |
| `n`, `c` | Single-task aliases of `n_i`, `c_i`, the source-pool size and the number of passing samples for task `i` | [26](../guide/chapters/26-conditional-bank-ceiling.html) |
| `\operatorname{Del}(d,\Delta)` | Delegation action to destination `d`, with stated maximum delay `\Delta` before a response, expiration, or fallback | [27](../guide/chapters/27-delegation-queue.html) |
| `p_E(x)` | Probability that delegated destination `E` returns a correct resolution at input or state `x` | [27](../guide/chapters/27-delegation-queue.html) |
| `\mathcal R_{\mathrm{auth}}(x)` | Authorized decision routes in state `x` | [27](../guide/chapters/27-delegation-queue.html) |
| `\varrho` | One member of `\mathcal R_{\mathrm{auth}}(x)`, an authorized decision route | [27](../guide/chapters/27-delegation-queue.html) |
| `V(\varrho,x)` | Declared value of authorized route `\varrho` in state `x` | [27](../guide/chapters/27-delegation-queue.html) |

## Chapter 25 local notation

Chapter 25 uses `\phi_t`, `\phi'`, `G`, `\widehat\Delta_G`, `\widehat C_G`, `\tau`,
`c`, `\varepsilon_{\rm safe}`, and `\mathcal G` only for its constructed procedure-release rule.
`\theta` keeps its book-wide meaning: frozen model parameters. These local release symbols do not
rename the book's standing state, action, score, or authority notation.

## Notes on symbols in Chapters 13, 16, and 18

`\operatorname{Pot}(x)` in Chapter 13 is a bounded shaping potential; its terminal boundary affects policy comparisons. Chapter 16's cost per authorized confirmed success is undefined when no run succeeds. In Chapter 18, `\operatorname{Exec}_{\mathrm{ui}}` connects a proposed command to a realized operation. `\mathcal A_{\mathrm{rob}}` retains actions feasible throughout the declared belief support. `\operatorname{Fresh}(\Delta)` describes no material interface change under a stated constant-rate model.

## Using the guide

Local indices, declared aliases, and diagram labels retain their
stated scope; return to the defining chapter for domains and assumptions.

