# Chapter demonstrations



These four calculations are shared with the notebook and illustrated reader. Read the source section and assumptions before choosing a state.

## C16-D01: Sampling fills the bank, but a blind pick ignores it

How many samples does it take to have a correct answer somewhere, what does a random pick from them deliver, and what if the chance is concentrated on a few problems?

**Source section:** What sampling buys

**Application:** Before buying more samples for a task, ask what picks among them. If the answer is nothing, the extra samples raise the number of correct candidates but not the number delivered. Measure bank coverage directly, by sampling repeated banks under one declared procedure, rather than inferring it from p.

**Assumptions:** Within each problem, samples are independent and share one correctness chance. The overconfident setting is a constructed illustration of the chapter's statement that p can be near zero for many problems, not a model of any training run; the chapter's Figure 16.1 is schematic and compares different sampling procedures, so it does not isolate candidate count as the cause. The values of p are constructed; they do not describe any real model.

**Declared default controls:**

```json
{
  "spread": "shared",
  "p": 0.2,
  "k": 10
}
```

**Supported values:**

- `spread`: ['shared', 'thin']
- `p`: [0.05, 0.2, 0.3]
- `k`: [10, 100]

**Evidence:** constructed teaching example

Constructed example: the chapter's p = 0.2, 0.05 and 0.3 arithmetic (coverage 0.89 and 0.99 at 10 and 20 samples for p = 0.2, 0.40 and 0.99 at 10 and 100 for p = 0.05, gains 0.30, 0.07 and under 0.001 at samples 1, 5 and 20 for p = 0.3), computed directly from the equations; the overconfident setting is defined for this reader.

## C16-D02: The selector turns coverage into delivery

How much of the coverage reaches the user under a budget and a deadline, and what changes when the samples share one failure or the limits are tight?

**Source section:** The selector needs its own measured success rate

**Application:** Report coverage and delivery as separate numbers on the same tasks. If coverage is high and delivery low, work on the selector; if coverage itself is low, no selector can help. Keep infeasible rows in the record, as the companion's probe does, and say when none is feasible instead of exceeding a hard limit.

**Assumptions:** A constant selector success is a constructed simplification. The book stresses that a real selector's success must be measured on banks of the size and kind in use, because it depends on ties, on the number of correct answers and on dependence. The shared-failure state is an extreme case chosen to show the boundary; there the selector setting has no effect. Time is serial and the costs are constructed. The rule that a shared failure makes selection equal coverage is the laboratory's and the workbook's convention; the chapter itself states only that dependence breaks Equation (16.1). The no-feasible state uses a budget of 0.5, defined for this reader.

**Declared default controls:**

```json
{
  "setting": "default",
  "selector": 0.9
}
```

**Supported values:**

- `setting`: ['default', 'shared', 'transfer', 'none']
- `selector`: [0.5, 0.9, 1.0]

**Evidence:** constructed teaching example

Constructed example: the laboratory's sample-allocation function with the notebook's default (p = 0.4, selector 0.9, counts 1, 2, 3 and 5, limits 6 and 6), changed (one shared failure) and transfer cases (p = 0.7, selector 0.5, costs 2 and 3, limits 3 and 6, counts 1, 2 and 4), and the workbook's question about an allocation set with no feasible row (a budget of 0.5, defined for this reader).

## C16-D03: Length, volume or a selector: spending sixty units

With 60 units of compute, does it matter more to think longer, to sample more, or to pay for a selector?

**Source section:** Three levers, one budget

**Application:** When splitting a fixed budget, price every lever in one unit and compute delivery for each combination. Do the arithmetic before arguing about whether longer reasoning or more samples is the better lever.

**Assumptions:** The costs, the two p values and the selector successes are constructed; the book states them to show the ordering, not as results for any real system. Selector success is held constant across bank sizes here. A selector that ranks correct answers below wrong ones, as in the 0.15 state, can do worse than not selecting.

**Declared default controls:**

```json
{
  "selector": "book",
  "long_p": 0.35
}
```

**Supported values:**

- `selector`: ['book', 'strong', 'weak', 'worse']
- `long_p`: [0.35, 0.25]

**Evidence:** constructed teaching example

Constructed example: the chapter's sixty-unit construction (Figure 16.3), including its stipulated selector values 0.73 and 0.785, with the other selector values and the second long-chain p defined for this reader.

## C16-D04: What a completed task costs, and who is allowed to be slow

Which procedure is cheapest per authorized success once a completion floor and a deadline rule some out, and what does the ratio do when nothing succeeds?

**Source section:** What the budget actually buys

**Application:** When reporting an efficiency ratio, count every attempt's cost, count only runs that met the declared completion contract, and state the constraints the ratio does not capture. Report a zero denominator as undefined, with the attempted-task count and the total cost.

**Assumptions:** Three constructed procedures with known costs, completion rates and response times. Real rates must be estimated on matching tasks, and a ratio from a small sample is a different object from the underlying rate. The two observed attempts describe a sample, not the population ratios. The Pareto statement is about the three procedures as stated; it does not pick one for a particular deadline or authority contract.

**Declared default controls:**

```json
{
  "deadline": 10,
  "required": 0.75,
  "evidence": "declared"
}
```

**Supported values:**

- `deadline`: [3, 10]
- `required`: [0.5, 0.75, 0.82]
- `evidence`: ['declared', 'observed']

**Evidence:** constructed teaching example

Constructed example: the chapter's three procedures (costs 1, 1.5, 2; completion 60, 80, 85 percent; response 1, 2, 5 seconds; failure loss 20) and workbench problem E.4 (two attempts costing 2 and 3, neither successful), with the deadline and completion floor varied. The costs and completion rates come from the section named above; the response times, deadlines and the loss of 20 per failure come from the section "Waiting changes the allocation".
