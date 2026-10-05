# Chapter demonstrations



These four calculations are shared with the notebook and illustrated reader. Read the source section and assumptions before choosing a state.

## C11-D01: Regret: what never looking again costs

How fast does the shortfall against an all-knowing agent grow under the rules that always exploit, always rotate, explore with optimism or sample from a belief?

**Source section:** Putting numbers on the two failures

**Application:** When a team reports a success rate for a deployed agent, ask how much of its action set it has sampled recently. Regret itself needs the true means, which a deployed agent does not have, so this is the question that can be asked. An agent that took one action thousands of times and the alternatives twice may have stopped measuring.

**Assumptions:** Independent fixed success probabilities and one seeded run per rule, so each curve is one draw of luck: it is not a policy performance estimate and not the expectation in Equation (11.1). The table's 200-seed means describe this constructed world; they do not estimate performance in a deployed environment. Regret here is pseudo-regret, computed from the known means, which a deployed agent does not have. The stuck and rotate lines are closed forms. Real tools change over time, which this model does not cover.

**Declared default controls:**

```json
{
  "world": "book",
  "scale": "own"
}
```

**Supported values:**

- `world`: ['book', 'default', 'swapped', 'three']
- `scale`: ['own', 'ten']

**Evidence:** constructed teaching example

Constructed example: the book's invented success rates 0.78 and 0.90 and its 1,000-task comparison, and the notebook's default, swapped and three-arm worlds; every curve is one seeded run computed with the laboratory's bandit function.

## C11-D02: Optimism: why a thin record gets another call

Why does a tool with a poor record and few pulls get called again, and what changes that?

**Source section:** A proved rule and ten constructed pulls

**Application:** When a controller must choose among components with thin records, an index of this shape gives a written reason for each call, which can be audited, instead of a vague claim that the system is curious.

**Assumptions:** The table's rewards are the book's invented alternating sequence (A returns 1, 0, 1, 0, and so on; B returns 0, 1, 0, 1), not a test of the stochastic guarantee. Each tool is pulled once first, ties go to A, and the bonus uses unrounded values. Changing c changes the rule; the book's guarantee is stated for c equal to the square root of two with rewards in [0, 1]. The trapped controller and the workbench problem are single decisions given counts and means, not runs.

**Declared default controls:**

```json
{
  "situation": "p4",
  "c": 1.4142135623730951
}
```

**Supported values:**

- `situation`: ['p4', 'p5', 'trap', 'bench']
- `c`: [1.4142135623730951, 1.0, 0.5]

**Evidence:** constructed teaching example

Constructed example: the chapter's ten-pull table with c equal to the square root of two (invented teaching rewards), the chapter's trapped controller (18 pulls with 14 successes, 2 pulls with none) and the original workbench problem III.1 (80 and 20 pulls); the values of c other than the square root of two are defined for this reader.

## C11-D03: Information gain is not decision value

Can a check remove uncertainty about a claim and still be worth exactly nothing?

**Source section:** The condition that makes information worthless

**Application:** Before paying for a check, write down which action follows each possible report. If it is the same action every time, the check is decoration, however interesting its output.

**Assumptions:** A symmetric check (equally accurate on supported and unsupported claims), a single decision between releasing and requesting evidence, and a belief that the stated prior and accuracy are correct. Accuracy and prior here are constructed; a real check may be biased in one direction, which this model does not cover.

**Declared default controls:**

```json
{
  "accuracy": 0.85,
  "prior": 0.85
}
```

**Supported values:**

- `accuracy`: [0.6, 0.7, 0.85, 0.95]
- `prior`: [0.5, 0.85, 0.97]

**Evidence:** constructed teaching example

Constructed example: the book's release score 85 and evidence score 92 (Table 6.1 values); the checks, their accuracies and the priors are defined for this reader.

## C11-D04: A worked price for one observation

How much is one call to a classifier worth, and how can the same classifier be worth zero in one decision and something in another?

**Source section:** A worked price for one observation

**Application:** Price a verification step against the specific decision it feeds. The same step, with the same accuracy and cost, can be a bargain for one decision and worthless for another. Before spending any budget, also check whether the system already holds the answer in a log it failed to structure: free information should always be used.

**Assumptions:** One decision, one observation, a coherent probability model, and a gross value that ignores any later decisions the observation could also inform. The conditional release scores are the book's constructed values; a real classifier's scores would have to be estimated, and a wrong estimate can flip the verdict.

**Declared default controls:**

```json
{
  "shift": 10,
  "call_cost": 0
}
```

**Supported values:**

- `shift`: [0, 5, 10, 15]
- `call_cost`: [0, 2, 2.3333333333333335]

**Evidence:** constructed teaching example

Constructed example: the book's worked classifier (flag one third, release scores 75 and 90, evidence 92, shift 10 giving 7/3); the other shifts and costs are defined for this reader.
