# Chapter demonstrations



These four calculations are shared with the notebook and illustrated reader. Read the source section and assumptions before choosing a state.

## C14-D01: The score inside the model against the score in the world

If you pick the setting that scores best inside the learned model, how does it do in the actual environment?

**Source section:** The knob the authors added, and what it bought

**Application:** When a system proposes an action, predicts its outcome and scores itself on the prediction, it is reading the left column. Hold out some real outcomes and keep the second column, however small, and compare the two.

**Assumptions:** The scores are the chapter's reported numbers for one game setup and one training and evaluation procedure, each with its own variability (spreads were reported for 0.10 and 1.15 here). They show that the two evaluations can come apart, not a general temperature rule and not a measure of epsilon.

**Declared default controls:**

```json
{
  "temperature": 0.1,
  "judge": "dream"
}
```

**Supported values:**

- `temperature`: [0.1, 1.0, 1.15, 1.3]
- `judge`: ['dream', 'real']

**Evidence:** source-reported game scores with a constructed judging comparison

Constructed example (reported values in a constructed comparison): the scores are copied from the chapter's temperature table (reported by the cited paper for one game setup); the judging rule and the comparison are defined for this reader.

## C14-D02: One step of error, compounded, against the actual error

How large can the value error become when a small one-step error compounds, and how large is it in a constructed model?

**Source section:** What one step of error becomes

**Application:** Before trusting a long imagined rollout, divide the bound by the largest possible value. If the share is near or above 1, the guarantee has nothing to say. If the model cannot be improved, consult the world more often.

**Assumptions:** The bound needs a fixed behaviour, the same expected immediate reward in model and world, rewards in [0, R], and error at most epsilon for every state and action that behaviour reaches. The kernels are the laboratory's constructed two-state defaults, so the actual error is that of one small model, not a general rate. A single number can also hide where the model is bad.

**Declared default controls:**

```json
{
  "case": "default",
  "discount": 0.9
}
```

**Supported values:**

- `case`: ['default', 'changed', 'transfer', 'percent']
- `discount`: [0.5, 0.9, 0.99]

**Evidence:** constructed teaching example

Constructed example: the laboratory's default, changed and transfer cases (kernels (0.90, 0.10), (0.20, 0.80) and model rows shifted by 0.02, horizons 5 and 20, identical kernels with rewards 1 and 2) and the chapter's 0.01 illustration, all computed with the laboratory's transition-model function.

## C14-D03: The optimizer finds where the model is generous, and the gap decides

A model can be wrong about every action value and still choose correctly, or be right about eleven tools and choose the twelfth. What decides which?

**Source section:** The number that actually matters

**Application:** Judge a planning model against the decision it serves, not against a single accuracy figure. Ask how large the gap is between the best option and the next one, compare twice the value error to it in the same units, and check whether the errors are concentrated on options the optimizer will rank.

**Assumptions:** Twelve options with constructed values, a uniform bound on the action-value error, and three hand-made error patterns. The chapter adds that this bound is an extra assumption: Equation (14.2) bounds state values and does not supply it. The test 2 x error < gap is sufficient, not necessary, so a failed test leaves the ranking undecided rather than wrong.

**Declared default controls:**

```json
{
  "pattern": "shared",
  "error": 0.05
}
```

**Supported values:**

- `pattern`: ['shared', 'favorable', 'adversarial']
- `error`: [0.05, 0.15, 0.3, 0.9]

**Evidence:** constructed teaching example

Constructed example: twelve option values defined for this reader (best 0.90, runner-up 0.60), with error patterns that illustrate the chapter's ranking argument and its eleven-right, one-wrong tool example.

## C14-D04: How many imagined steps are certified

Given the model error, the reward range and the action gap, how many steps ahead can the certificate vouch for?

**Source section:** How many steps a model is good for

**Application:** Use the certified horizon to set how many steps an agent commits to before it observes the world again. Plan that many, execute a few, look, and replan, rather than emitting a long plan against an error nobody measured.

**Assumptions:** A finite covered domain, equal expected immediate rewards in model and world, the same initial state and fixed behaviour, uniform error epsilon, zero terminal continuation and a declared gap. The R = 10 case uses the chapter's priced plan, where a logged prediction miss rate is declared a conservative proxy for epsilon, which is not the same thing. A failed test is inconclusive, not proof of a wrong decision, and the inputs are usually not measured.

**Declared default controls:**

```json
{
  "scenario": "r1",
  "error": 0.02
}
```

**Supported values:**

- `scenario`: ['r1', 'r1small', 'r10']
- `error`: [0.01, 0.02, 0.04, 0.08]

**Evidence:** constructed teaching example

Constructed example: the chapter's Figure 14.2 gaps (R = 1, epsilon 0.02, gaps 0.2 and 0.5) and its priced twenty-step plan (R = 10, gap 2, epsilon 0.08 and 0.01); the other error values are defined for this reader, and each curve is checked against the laboratory's finite-horizon bound.
