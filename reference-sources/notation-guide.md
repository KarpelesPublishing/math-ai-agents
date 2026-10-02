# Notation Guide

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
- Probability is `\Pr` and expectation is `\mathbb E`. The operator `\mathbb E` carries only that meaning; a plain `E` used as a subscript label, such as a delegated destination in Chapter 27, names a thing and is not an operator.
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
| `K_\theta(z\mid c)` | Model conditional law over outputs given context | [1](../revisions/part-i-v2/01-when-a-score-becomes-a-skill.md) |
| `U_\mathcal V(S)` | Population task score of assembly `S` | [1](../revisions/part-i-v2/01-when-a-score-becomes-a-skill.md) |
| `\widehat U_\mathcal V(S)` | Finite-sample estimate of that task score | [1](../revisions/part-i-v2/01-when-a-score-becomes-a-skill.md) |
| `\operatorname{dec}` | Decoding map from a distribution to a candidate output | [1](../revisions/part-i-v2/01-when-a-score-becomes-a-skill.md) |
| `\operatorname{eval}_\tau` | Evaluator with threshold, parser, or tolerance `\tau` | [1](../revisions/part-i-v2/01-when-a-score-becomes-a-skill.md) |
| `\theta` | Model parameters, frozen unless a chapter says otherwise | [1](../revisions/part-i-v2/01-when-a-score-becomes-a-skill.md) |
| `\mathbb E` | Expectation (the only meaning of blackboard-bold `E`; a plain subscript label such as Chapter 27's `p_E` is not this operator) | [1](../revisions/part-i-v2/01-when-a-score-becomes-a-skill.md) |
| `\mathcal V` | Declared evaluation contract: task distribution, scoring rule and units, sampling settings, budget, and stopping rule | [1](../revisions/part-i-v2/01-when-a-score-becomes-a-skill.md) |
| `q`, `n` | Per-token success probability and target length in the exact-match example, so the score is `q^n` | [1](../revisions/part-i-v2/01-when-a-score-becomes-a-skill.md) |
| `\Gamma(A;B)` | Interaction contrast between component sets | [2](../revisions/part-i-v2/02-where-the-ability-lives.md) |
| `\rho_\Gamma` | Interaction share of total joint gain | [2](../revisions/part-i-v2/02-where-the-ability-lives.md) |
| `q_m` | Per-attempt success probability for family member `m` | [3](../revisions/part-i-v2/03-the-smooth-curve-and-the-sudden-skill.md) |
| `\operatorname{pass}_\tau(q_m)` | Thresholded pass indicator on `q_m` | [3](../revisions/part-i-v2/03-the-smooth-curve-and-the-sudden-skill.md) |
| `L(C)=aC^b+c` | Fitted pretraining-loss curve; `C` is training compute and `a`, `b`, `c` are fitted constants | [3](../revisions/part-i-v2/03-the-smooth-curve-and-the-sudden-skill.md) |
| `\psi` | Fitted forecast parameters | [3](../revisions/part-i-v2/03-the-smooth-curve-and-the-sudden-skill.md) |
| `f_\psi`, `\epsilon_m` | Fitted forecast function and its error for member `m` | [3](../revisions/part-i-v2/03-the-smooth-curve-and-the-sudden-skill.md) |
| `\Gamma_m` | Interaction contrast measured for family member `m` | [3](../revisions/part-i-v2/03-the-smooth-curve-and-the-sudden-skill.md) |
| `z_m` | Declared predictor features for member `m` | [3](../revisions/part-i-v2/03-the-smooth-curve-and-the-sudden-skill.md) |
| `G` | Action graph: vertices are controller states, edges are allowed transitions | [4](../revisions/part-i-v2/04-the-path-from-prediction-to-action.md) |
| `V_0` | Initial vertex set | [4](../revisions/part-i-v2/04-the-path-from-prediction-to-action.md) |
| `\operatorname{step}` | One-transition successor map on vertex sets | [4](../revisions/part-i-v2/04-the-path-from-prediction-to-action.md) |
| `\operatorname{Reach}_G(V_0)` | Reachable set | [4](../revisions/part-i-v2/04-the-path-from-prediction-to-action.md) |
| `\operatorname{Act}(v)` | Candidate actions at vertex `v` | [4](../revisions/part-i-v2/04-the-path-from-prediction-to-action.md) |
| `\mathcal{G}` | Permission grant rule: maps a set of candidate actions to the permitted subset | [4](../revisions/part-i-v2/04-the-path-from-prediction-to-action.md) |
| `\operatorname{Allowed}_{\mathcal G}(v)` | Permitted actions after filtering | [4](../revisions/part-i-v2/04-the-path-from-prediction-to-action.md) |
| `\Pi_{G,v}(p)` | Infinite-cluster probability | [4](../revisions/part-i-v2/04-the-path-from-prediction-to-action.md) |
| `p_c(G,v)` | Critical probability | [4](../revisions/part-i-v2/04-the-path-from-prediction-to-action.md) |
| `d` | Branching factor or degree | [4](../revisions/part-i-v2/04-the-path-from-prediction-to-action.md) |
| `x_t=(c_t,m_t,w_t,b_t)` | Composite agent state realization | [5](../revisions/part-i-v2/05-what-the-model-becomes-inside-an-agent.md) |
| `w_t` | World or environment state | [5](../revisions/part-i-v2/05-what-the-model-becomes-inside-an-agent.md) |
| `P(x_{t+1}\mid x_t)` | Composite transition kernel | [5](../revisions/part-i-v2/05-what-the-model-becomes-inside-an-agent.md) |
| `\operatorname{Mem}` | Memory map from the whole history to the retained memory `m_t`; the update itself is part of `\operatorname{Upd}` | [5](../revisions/part-i-v2/05-what-the-model-becomes-inside-an-agent.md) |
| `\pi_\theta(z,a\mid x)` | Proposal policy: model law times decoder | [5](../revisions/part-i-v2/05-what-the-model-becomes-inside-an-agent.md) |
| `\kappa` | Coarse-graining map | [5](../revisions/part-i-v2/05-what-the-model-becomes-inside-an-agent.md) |
| `H(X)`, `I(X;Y)` | Shannon entropy, mutual information | [5](../revisions/part-i-v2/05-what-the-model-becomes-inside-an-agent.md) |
| `\operatorname{Grant}(g\mid x,u)` | Normalized permission-outcome law, including denial | [5](../revisions/part-i-v2/05-what-the-model-becomes-inside-an-agent.md) |
| `\operatorname{Env}(w',o\mid x,u,g)` | Joint next-world and observation law | [5](../revisions/part-i-v2/05-what-the-model-becomes-inside-an-agent.md) |
| `\operatorname{Upd}(c',m',b'\mid x,u,g,w',o)` | Joint context, memory, and budget update law | [5](../revisions/part-i-v2/05-what-the-model-becomes-inside-an-agent.md) |
| `P_{\mathrm{env}}(x'\mid x,u)` | Controlled transition given a full proposal | [5](../revisions/part-i-v2/05-what-the-model-becomes-inside-an-agent.md) |
| `P_\theta(x'\mid x)` | Closed-loop transition after averaging over proposal policy | [5](../revisions/part-i-v2/05-what-the-model-becomes-inside-an-agent.md) |
| `u=(z,a)` | Full proposal: model output and decoded action | [5](../revisions/part-i-v2/05-what-the-model-becomes-inside-an-agent.md) |

## Symbols introduced after Part I

| Symbol | Meaning | Introduced |
|---|---|---:|
| `u(y)` | Utility of a single outcome | [6](../part-ii/06-the-price-of-a-choice.md) |
| `y` | An outcome of an action | [6](../part-ii/06-the-price-of-a-choice.md) |
| `\mathcal{A}` | The action set available at a state | [6](../part-ii/06-the-price-of-a-choice.md) |
| `\operatorname{EU}(a)` | Expected utility of an action | [6](../part-ii/06-the-price-of-a-choice.md) |
| `\operatorname{CE}` | Certainty equivalent | [6](../part-ii/06-the-price-of-a-choice.md) |
| `\operatorname{Ret}_t` | Return, the discounted sum of future rewards | [7](../part-ii/07-the-equation-that-looks-ahead.md) |
| `a_t` | Action taken at time `t` | [7](../part-ii/07-the-equation-that-looks-ahead.md) |
| `r_t` | Reward received on the transition out of `x_t` | [7](../part-ii/07-the-equation-that-looks-ahead.md) |
| `\gamma` | Discount factor | [7](../part-ii/07-the-equation-that-looks-ahead.md) |
| `\pi(a\mid x)` | Stochastic policy | [7](../part-ii/07-the-equation-that-looks-ahead.md) |
| `V^{\pi}`, `V^{\star}` | State value under a policy, and under an optimal policy | [7](../part-ii/07-the-equation-that-looks-ahead.md) |
| `Q^{\pi}`, `Q^{\star}` | Action value | [7](../part-ii/07-the-equation-that-looks-ahead.md) |
| `\Phi(x)` | Local shaping potential | [7](../part-ii/07-the-equation-that-looks-ahead.md) |
| `\mathcal{X}` | The finite state set | [8](../part-ii/08-acting-in-the-dark.md) |
| `\mathbf{b}_t` | Belief, a distribution over `\mathcal{X}` at time `t` | [8](../part-ii/08-acting-in-the-dark.md) |
| `\mathcal{B}` | The belief simplex, the set of distributions over `\mathcal{X}` | [8](../part-ii/08-acting-in-the-dark.md) |
| `\operatorname{Obs}(o\mid x,a)` | Observation kernel: the chance of seeing `o` on arriving in `x` after `a` | [8](../part-ii/08-acting-in-the-dark.md) |
| `\bar r(\mathbf{b},a)` | Expected reward of action `a` under belief `\mathbf{b}` | [8](../part-ii/08-acting-in-the-dark.md) |
| `J(x',o\mid x,a)` | Filtered joint next-state and observation law | [8](../part-ii/08-acting-in-the-dark.md) |
| `\Gamma_H`, `\alpha` | Finite-horizon policy-vector set and one vector | [8](../part-ii/08-acting-in-the-dark.md) |
| `\operatorname{VOI}(O)` | Value of observing `O` before a declared decision; Chapter 27 writes `\operatorname{VOI}(o)` for one realized observation | [8](../part-ii/08-acting-in-the-dark.md) |
| `g(v)`, `h(v)` | True cost from the start to vertex `v`, and true cost from `v` to the nearest goal | [9](../part-iii/09-searching-the-future.md) |
| `f(v)` | Cost of the best path constrained to pass through `v` | [9](../part-iii/09-searching-the-future.md) |
| `\hat g(v)`, `\hat h(v)`, `\hat f(v)` | The computable estimates of each | [9](../part-iii/09-searching-the-future.md) |
| `\operatorname{cost}(u,v)` | Cost of the edge from `u` to `v` | [9](../part-iii/09-searching-the-future.md) |
| `s`, `\mathcal{T}` | Start vertex and goal set | [9](../part-iii/09-searching-the-future.md) |
| `\operatorname{Exp}(A,G)` | Number of vertices algorithm `A` expands on graph `G` | [9](../part-iii/09-searching-the-future.md) |
| `h(u,v)` | True minimum path cost from `u` to `v`, distinct from the heuristic estimate `\hat h(v)` | [9](../part-iii/09-searching-the-future.md) |
| `\mathcal{I}_o` | Initiation set of option `o`: the states where the option may start | [10](../part-iii/10-plans-within-plans.md) |
| `\pi_o` | Option `o`'s internal policy, mapping execution information to a primitive action | [10](../part-iii/10-plans-within-plans.md) |
| `\beta_o` | Option `o`'s termination condition | [10](../part-iii/10-plans-within-plans.md) |
| `\mu` | Policy over options: the parent policy that selects which option to run | [10](../part-iii/10-plans-within-plans.md) |
| `\operatorname{Reg}(T)` | Regret accumulated over `T` rounds | [11](../part-iii/11-the-mathematics-of-curiosity.md) |
| `\hat\mu_a` | Empirical mean payoff of action `a` | [11](../part-iii/11-the-mathematics-of-curiosity.md) |
| `N_t(a)` | Number of pulls of action `a` among the `t` completed pulls, before the next decision | [11](../part-iii/11-the-mathematics-of-curiosity.md) |
| `\operatorname{Gain}(O)` | Decision-relevant information in an observation | [11](../part-iii/11-the-mathematics-of-curiosity.md) |
| `\hat V_t(x)` | The agent's current estimate of the value of state `x` | [12](../part-iii/12-credit-for-consequences.md) |
| `\delta_t` | Temporal-difference error at step `t` | [12](../part-iii/12-credit-for-consequences.md) |
| `\alpha` | Step size for an update | [12](../part-iii/12-credit-for-consequences.md) |
| `\lambda` | Weighting between the one-step estimate and the realized outcome | [12](../part-iii/12-credit-for-consequences.md) |
| `\operatorname{Ret}^{\lambda}_t` | The weighted return that interpolates between them | [12](../part-iii/12-credit-for-consequences.md) |
| `\operatorname{Pot}(x)` | Bounded shaping potential on declared state | [13](../part-iii/13-learning-to-choose.md) |
| `r'_t, G'_0` | Shaped reward and return; original r and G retain meaning | [13](../part-iii/13-learning-to-choose.md) |
| `\phi` | Trainable policy parameters, distinct from the frozen model parameters `\theta` | [13](../part-iii/13-learning-to-choose.md) |
| `\hat P(x'\mid x,a)` | Learned transition-model estimate | [14](../part-iv/14-building-a-world-inside.md) |
| `\widehat{\operatorname{Obs}}` | Learned observation-kernel estimate | [14](../part-iv/14-building-a-world-inside.md) |
| `\epsilon` | Uniform one-step total-variation model error | [14](../part-iv/14-building-a-world-inside.md) |
| `\tau_{\text{samp}}` | Sampling temperature of a generative model | [14](../part-iv/14-building-a-world-inside.md) |
| `R` | Upper bound on the common expected immediate state-action reward | [14](../part-iv/14-building-a-world-inside.md) |
| `H_{\max}` | Declared finite planning cap | [14](../part-iv/14-building-a-world-inside.md) |
| `R^\star` | Retained record set chosen under the token budget | [15](../part-iv/15-what-an-agent-should-remember.md) |
| `c(m)`, `B`, `\lambda` (Chapter 15) | Raw token cost of record `m`, the token budget, and decision-value units per token | [15](../part-iv/15-what-an-agent-should-remember.md) |
| `\varepsilon`, `2\varepsilon` (Chapter 15) | Summary value tolerance and the resulting regret bound | [15](../part-iv/15-what-an-agent-should-remember.md) |
| `\operatorname{Cov}(k)` | Coverage at `k`: the chance that at least one of `k` samples is correct | [16](../part-iv/16-thought-as-search.md) |
| `\operatorname{Sel}(k)` | Selection at `k`: the chance that the returned sample is correct | [16](../part-iv/16-thought-as-search.md) |
| `\widehat c_{\mathrm{success}}` | Total attempt cost divided by authorized confirmed completions | [16](../part-iv/16-thought-as-search.md) |
| `\pi(k)` | Measured chance that the selector's top-ranked sample is correct given `k` candidates | [16](../part-iv/16-thought-as-search.md) |
| `d` | Probability that the selector scores one correct sample above one incorrect sample | [16](../part-iv/16-thought-as-search.md) |
| `\operatorname{eff}(T,x)` | State resulting from applying tool `T` in state `x` | [17](../part-iv/17-state-and-consequence.md) |
| `\operatorname{resp}(T,x)` | Report returned by tool `T` in state `x` | [17](../part-iv/17-state-and-consequence.md) |
| `\operatorname{undo}(T)` | Recovery tool for an effect of `T` | [17](../part-iv/17-state-and-consequence.md) |
| `\operatorname{Rep}(x)` | Conservative set of eligible repeat attempts | [17](../part-iv/17-state-and-consequence.md) |
| `\operatorname{Ready}(T,x)` | Current authorization and preconditions for a repeat attempt | [17](../part-iv/17-state-and-consequence.md) |
| `\operatorname{Absent}(T,x)` | Authoritative terminal non-application of the original attempt | [17](../part-iv/17-state-and-consequence.md) |
| `\operatorname{Restored}(T,x)` | Verified recovery of relevant consequences and preconditions | [17](../part-iv/17-state-and-consequence.md) |
| `\beta`, `c_{\text{dup}}`, `c_{\text{miss}}` | Belief that the effect already landed, cost of a duplicate effect, and cost of the effect never happening | [17](../part-iv/17-state-and-consequence.md) |
| `\operatorname{Exec}_{\mathrm{ui}}(\tilde a\mid x,a)` | Normalized realized-operation law | [18](../part-iv/18-when-an-action-has-coordinates.md) |
| `P_{\mathrm{ui}}` | Execution-composed world kernel | [18](../part-iv/18-when-an-action-has-coordinates.md) |
| `\operatorname{Act}_{\mathrm{ui}}` | Finite realized-operation set including declared denial/no-effect operations | [18](../part-iv/18-when-an-action-has-coordinates.md) |
| `\mathcal A_{\mathrm{rob}}(\mathbf b)` | Intersection of correctly specified authorization sets over belief support | [18](../part-iv/18-when-an-action-has-coordinates.md) |
| `\lambda_{\mathrm{ui}}, \operatorname{Fresh}(\Delta)` | Material-change rate and no-invalidating-change probability | [18](../part-iv/18-when-an-action-has-coordinates.md) |
| `\mathcal A_{\mathrm{auth}}(x)` | Commands whose protected effect is authorized in state `x` | [18](../part-iv/18-when-an-action-has-coordinates.md) |
| `u_i(\pi_1,\pi_2)` | Payoff to party `i` under a pair of policies | [19](../part-v/19-when-another-mind-becomes-part-of-the-world.md) |
| `\pi_i^{(s)}` | Party `i` policy from training run `s` | [19](../part-v/19-when-another-mind-becomes-part-of-the-world.md) |
| `\operatorname{diag}(M)`, `\operatorname{off}(M)` | Matched-run and cross-run mean returns | [19](../part-v/19-when-another-mind-becomes-part-of-the-world.md) |
| `\operatorname{JPC}(M)` | Proportional cross-play loss | [19](../part-v/19-when-another-mind-becomes-part-of-the-world.md) |
| `\operatorname{BR}_i(\pi_{-i})` | Best response by party `i` to the other policy | [19](../part-v/19-when-another-mind-becomes-part-of-the-world.md) |
| `M` | Matched matrix whose entry `M_{st}` pairs run `s` against run `t` | [19](../part-v/19-when-another-mind-becomes-part-of-the-world.md) |
| `\operatorname{Know}_i(F)` | Party `i` knows proposition `F` | [20](../part-v/20-messages-beliefs-and-consensus.md) |
| `\operatorname{MK}_{\mathcal P}^n(F)` | `n` levels of mutual knowledge among party set `\mathcal P` | [20](../part-v/20-messages-beliefs-and-consensus.md) |
| `\operatorname{CK}_{\mathcal P}(F)` | Common knowledge of `F` among party set `\mathcal P` | [20](../part-v/20-messages-beliefs-and-consensus.md) |
| `q_e` | Nonnegative flow on traffic-network edge `e` | [21](../part-v/21-markets-teams-and-institutions.md) |
| `\ell_e(q_e)` | Latency incurred on edge `e` at flow `q_e` | [21](../part-v/21-markets-teams-and-institutions.md) |
| `\operatorname{TL}(q)` | Total latency of a feasible network flow `q` | [21](../part-v/21-markets-teams-and-institutions.md) |
| `q^{\mathrm{NE}}` | Nash-equilibrium flow | [21](../part-v/21-markets-teams-and-institutions.md) |
| `q^{\star}` | Total-latency-minimizing flow | [21](../part-v/21-markets-teams-and-institutions.md) |
| `\ell^{\mathrm{mc}}_e(q_e)` | Marginal-cost latency imposed by edge `e` | [21](../part-v/21-markets-teams-and-institutions.md) |
| `q_{\mathrm{upper}}`, `q_{\mathrm{lower}}`, `q_{\mathrm{middle}}` | Flows on the three directed Braess routes S-U-T, S-L-T, S-U-L-T | [21](../part-v/21-markets-teams-and-institutions.md) |
| `\gamma_{\mathrm{cap}}` | Extra-traffic fraction in the bicriteria routing comparison | [21](../part-v/21-markets-teams-and-institutions.md) |
| `C` | Declared episode-cost random variable for tail-risk accounting | [22](../part-vi/22-safe-enough-to-act.md) |
| `\operatorname{CVaR}_{\alpha}(C)` | Conditional value at risk of `C` at declared tail level `\alpha` | [22](../part-vi/22-safe-enough-to-act.md) |
| `z` | Candidate tail cutoff in CVaR's infimum representation | [22](../part-vi/22-safe-enough-to-act.md) |
| `B`, `b_t` | Declared bounded-horizon risk budget and remaining budget before decision `t` | [22](../part-vi/22-safe-enough-to-act.md) |
| `\widehat r_t(a_t)` | Conservative charged risk estimate for action `a_t` at time `t` | [22](../part-vi/22-safe-enough-to-act.md) |
| `\operatorname{Ret}^{\pi}` | Expected discounted reward under policy `\pi` | [22](../part-vi/22-safe-enough-to-act.md) |
| `\mathcal I` | Set of states in which a named invariant holds | [22](../part-vi/22-safe-enough-to-act.md) |
| `\operatorname{Cost}_i^{\pi}` | Expected discounted auxiliary-cost return | [22](../part-vi/22-safe-enough-to-act.md) |
| `d_i` | Declared limit on auxiliary cost `i` | [22](../part-vi/22-safe-enough-to-act.md) |
| `\mathcal T` | Declared threat model | [22](../part-vi/22-safe-enough-to-act.md) |
| `\varepsilon_{\mathrm{safe}}` | Deliberate safety margin | [22](../part-vi/22-safe-enough-to-act.md) |
| `A_{C_i}^{\pi_k}(s,a)` | Constraint advantage for auxiliary cost `i` | [22](../part-vi/22-safe-enough-to-act.md) |
| `\epsilon_i` | Largest candidate-policy expected constraint advantage | [22](../part-vi/22-safe-enough-to-act.md) |
| `\delta` | Ideal CPO step-size bound | [22](../part-vi/22-safe-enough-to-act.md) |
| `\lambda_{\mathrm{safe}}` | Fixed multiplier between reward and one auxiliary cost | [22](../part-vi/22-safe-enough-to-act.md) |
| `\mathcal C_{\mathrm{parent}}`, `\mathcal C_{\mathrm{child}}` | Declared capability sets of a delegating parent and a delegated child | [23](../part-vi/23-when-the-environment-gives-instructions.md) |
| `M_t`, `e_t` | Monitor's enforcement-layer record at time `t`, and one observed event | [23](../part-vi/23-when-the-environment-gives-instructions.md) |
| `\operatorname{Mon}` | Monitor update map from prior record and one observed event to the next record | [23](../part-vi/23-when-the-environment-gives-instructions.md) |
| `\delta`, `v`, `r` | Document identity, version, and recipient in the publish predicate | [23](../part-vi/23-when-the-environment-gives-instructions.md) |
| `\operatorname{Approved}(M_t)` | Set of `(\delta,v,r)` triples the monitor's current record authorizes for release | [23](../part-vi/23-when-the-environment-gives-instructions.md) |
| `\operatorname{Publish}(\delta,v,r,M_t)` | Boolean predicate: is this exact document-version-recipient triple currently approved | [23](../part-vi/23-when-the-environment-gives-instructions.md) |
| `\mathcal F` | One declared, finite attack family under a fixed threat model | [23](../part-vi/23-when-the-environment-gives-instructions.md) |
| `\operatorname{Risk}(\mathcal F)` | Worst-case violation probability across `\mathcal F` | [23](../part-vi/23-when-the-environment-gives-instructions.md) |
| `k` | Number of samples drawn | [24](../part-vi/24-how-much-capability-have-we-extracted.md) |
| `p` | Probability that one sample is correct | [24](../part-vi/24-how-much-capability-have-we-extracted.md) |
| `N_{\mathrm{eval}}` | Number of evaluated task instances | [24](../part-vi/24-how-much-capability-have-we-extracted.md) |
| `\Delta_{\mathrm{match}}(\theta)` | Score difference for frozen model `\theta` between a named benchmark and its matched evaluation | [24](../part-vi/24-how-much-capability-have-we-extracted.md) |
| `\zeta` | Declared threshold on a continuous metric when defining a thresholded scale onset | [24](../part-vi/24-how-much-capability-have-we-extracted.md) |
| `\operatorname{Onset}_{\zeta}` | First declared family scale at which the thresholded metric reaches `\zeta` | [24](../part-vi/24-how-much-capability-have-we-extracted.md) |
| `\mathcal K` | Fixed same-bank task set used to compare coverage with deployed selection | [24](../part-vi/24-how-much-capability-have-we-extracted.md) |
| `\widehat{\operatorname{Cov}}_{\mathcal K}(k)`, `\widehat{\operatorname{Sel}}_{\mathcal K}(k)` | Empirical same-bank coverage and deployed-selector success after `k` candidates per task | [24](../part-vi/24-how-much-capability-have-we-extracted.md) |
| `\mathcal C`, `\xi` | Finite tested configuration set and one configuration index | [24](../part-vi/24-how-much-capability-have-we-extracted.md) |
| `\Pr` | Probability over Equation 24.4's declared sampling or resampling design | [24](../part-vi/24-how-much-capability-have-we-extracted.md) |
| `\operatorname{Lower}^{\mathrm{sim}}_{\alpha_{\mathrm{tail}}}(\xi)` | Lower score bound for configuration `\xi` from a procedure with joint coverage across all tested configurations | [24](../part-vi/24-how-much-capability-have-we-extracted.md) |
| `\operatorname{SE}_{\mathrm{match}}` | Estimated standard error of a difference of independent bank pass proportions | [24](../part-vi/24-how-much-capability-have-we-extracted.md) |
| `\alpha_{\mathrm{tail}}` | Tail probability level for the simultaneous lower-bound guarantee | [24](../part-vi/24-how-much-capability-have-we-extracted.md) |
| `\operatorname{LCF}_{\alpha_{\mathrm{tail}}}` | Simultaneous lower confidence frontier across tested configurations | [24](../part-vi/24-how-much-capability-have-we-extracted.md) |
| `\phi_t`, `\phi'` | Parent and candidate versions of the agent procedure around frozen weights | [25](../part-vi/25-improving-an-agent-without-trusting-the-improvement.md) |
| `\widehat\Delta_G(\phi')`, `G` | Guard-set estimate and its frozen guard cases for the named candidate | [25](../part-vi/25-improving-an-agent-without-trusting-the-improvement.md) |
| `\widehat C_G(\phi')`, `\mathcal G` | Guard cost estimate and authority envelope for the proposed release | [25](../part-vi/25-improving-an-agent-without-trusting-the-improvement.md) |
| `\tau`, `c`, `\varepsilon_{\rm safe}` | Local uplift threshold, cost limit, and reserved safety margin | [25](../part-vi/25-improving-an-agent-without-trusting-the-improvement.md) |
| `D`, `\widehat V_D` | Development set and a procedure's estimated value on it | [25](../part-vi/25-improving-an-agent-without-trusting-the-improvement.md) |
| `\mathcal M`, `\Phi_t` | Declared bounded family of procedure changes and the finite candidate collection compared on `D` | [25](../part-vi/25-improving-an-agent-without-trusting-the-improvement.md) |
| `m`, `Z_i(\phi')` | Number of guard cases and the paired candidate-minus-parent outcome on guard case `i`, bounded in `[-1,1]` | [25](../part-vi/25-improving-an-agent-without-trusting-the-improvement.md) |
| `\Delta(\phi')` | Population mean of `Z_i(\phi')`: the candidate's true uplift, an unknown parameter | [25](../part-vi/25-improving-an-agent-without-trusting-the-improvement.md) |
| `\operatorname{Authorized}_{\mathcal G}`, `\operatorname{Rollback}` | Boolean authority predicate for the proposed release and the check for a tested path back to the parent | [25](../part-vi/25-improving-an-agent-without-trusting-the-improvement.md) |
| `n`, `c` | Single-task aliases of `n_i`, `c_i`, the source-pool size and the number of passing samples for task `i` | [26](../part-vi/26-how-much-more-could-the-system-become.md) |
| `\operatorname{Del}(d,\Delta)` | Delegation action to destination `d`, with stated maximum delay `\Delta` before a response, expiration, or fallback | [27](../part-vi/27-the-mathematics-of-delegation.md) |
| `p_E(x)` | Probability that delegated destination `E` returns a correct resolution at input or state `x` | [27](../part-vi/27-the-mathematics-of-delegation.md) |
| `\mathcal R_{\mathrm{auth}}(x)` | Authorized decision routes in state `x` | [27](../part-vi/27-the-mathematics-of-delegation.md) |
| `\varrho` | One member of `\mathcal R_{\mathrm{auth}}(x)`, an authorized decision route | [27](../part-vi/27-the-mathematics-of-delegation.md) |
| `V(\varrho,x)` | Declared value of authorized route `\varrho` in state `x` | [27](../part-vi/27-the-mathematics-of-delegation.md) |

## Chapter 25 local notation

Chapter 25 uses `\phi_t`, `\phi'`, `G`, `\widehat\Delta_G`, `\widehat C_G`, `\tau`,
`c`, `\varepsilon_{\rm safe}`, and `\mathcal G` only for its constructed procedure-release rule.
`\theta` keeps its book-wide meaning: frozen model parameters. These local release symbols do not
rename the book's standing state, action, score, or authority notation.

## Symbols in the focused expansion

`\operatorname{Pot}(x)` in Chapter 13 is a bounded shaping potential; its terminal boundary affects policy comparisons. Chapter 16's cost per authorized confirmed success is undefined when no run succeeds. In Chapter 18, `\operatorname{Exec}_{\mathrm{ui}}` connects a proposed command to a realized operation. `\mathcal A_{\mathrm{rob}}` retains actions feasible throughout the declared belief support. `\operatorname{Fresh}(\Delta)` describes no material interface change under a stated constant-rate model.

## Using the guide

Local indices, declared aliases, and diagram labels retain their
stated scope; return to the defining chapter for domains and assumptions.

