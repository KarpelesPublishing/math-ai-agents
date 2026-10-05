# Chapter demonstrations



These four calculations are shared with the notebook and illustrated reader. Read the source section and assumptions before choosing a state.

## C02-D01: Four cells, one contrast

Given the four scores for neither, p only, i only and both, how much did the pair add beyond its two isolated gains, and when may that be read as a share?

**Source section:** Why all four cells

**Application:** When a team reports that two components together beat each alone, ask for the neither score, compute Gamma, check that the budgets match and say which scale the scores are on. Only then can anyone say whether the pair is better than its parts or merely the sum of them.

**Assumptions:** Everything except the two switched operations is held fixed: the same model, task distribution, scoring rule and removal controls. The scores are constructed teaching values and stipulated means, not noisy estimates. If the four conditions quietly differ in other ways, the arithmetic still balances but the number answers a different question. Cubing the scores is a change of scale defined for this reader.

**Declared default controls:**

```json
{
  "case": "table",
  "run": "matched"
}
```

**Supported values:**

- `case`: ['table', 'additive', 'second', 'workbench']
- `run`: ['matched', 'doubled', 'cubed']

**Evidence:** constructed teaching example

Constructed example: the baseline 0.20 and Table 2.1 scores, the second (negative) example and the workbench pair I.1 and I.3 (0.40, 0.52, 0.49 with the joint score 0.73 under a doubled allowance and 0.58 after a matched rerun) are the book's own constructed numbers; the additive case is the book's additive prediction 0.35. Computed with the laboratory's four-cell function.

## C02-D02: Why the neither cell matters

Two systems both score 0.80 with the pair on. Can their contrasts differ, and what goes wrong if the neither score is skipped?

**Source section:** Why all four cells

**Application:** When comparing two systems with the same headline score, put the baseline next to the contrast. A large intact score with a high baseline can hide a small contribution from the pair.

**Assumptions:** The same score scale and the same controls for both systems. System A and the 0.70 case of System B are the book's Figure 2.3 values; the other baselines are defined for this reader. A smaller contrast does not make a system worse: the choice between systems also depends on reliability and cost.

**Declared default controls:**

```json
{
  "baseline_b": 0.7,
  "method": "four"
}
```

**Supported values:**

- `baseline_b`: [0.3, 0.5, 0.7]
- `method`: ['four', 'three']

**Evidence:** constructed teaching example

Constructed example: System A and System B at baseline 0.70 are the book's Figure 2.3 values; the other baselines are defined for this reader. Computed with the laboratory's four-cell function.

## C02-D03: The maple-river route and a leaking removal control

What do the two operations do in the maple-river route, and what happens to the contrast when the control for p still lets p's influence through?

**Source section:** What the experiment has to hold still

**Application:** Before running the four cells, write down what replaces each operation and test that the replacement really removes the information under test. Declare the control and use the same one in all four cells.

**Assumptions:** Table 2.1's four scores are taken as the clean-control values. The leak model, a straight mix between the clean cell and the matching p-on cell, is defined for this reader and is not a measurement. The chapter says zero, mean and resampled removal give three different numbers and none is the true one; this demonstration does not model them.

**Declared default controls:**

```json
{
  "cell": "neither",
  "leak": 0.0
}
```

**Supported values:**

- `cell`: ['neither', 'p', 'i', 'both']
- `leak`: [0.0, 0.5, 1.0]

**Evidence:** constructed teaching example

Constructed example: the four scores are the book's Table 2.1 and the route is the chapter's maple river example of Figure 2.1; the surviving-share model is defined for this reader.

## C02-D04: Is the contrast clearly different from zero?

How many trials per cell does it take before a contrast of 0.05 or 0.15 is clearly different from zero, and what does searching many pairs do?

**Source section:** What the experiment has to hold still

**Application:** Before running a four-cell comparison, decide the smallest contrast that matters and size the trials so that its interval would exclude zero. Name the pair before measuring it and report the contrast with an interval, not alone.

**Assumptions:** Independent cells with equal spread, a normal approximation and a spread of 0.4 defined for this reader. The interval shown is centred on the true amount; a real run would scatter around it. Cells measured on the same prompts are correlated, which changes the factor of 2 but not the lesson. The expected count of positive chance clears adds the null chance 0.025 across pairs; that expectation does not require independent pairs. Dependence between pairs changes the variability of the count and the probability of at least one chance clear.

**Declared default controls:**

```json
{
  "trials": 100,
  "true_contrast": 0.15,
  "pairs": 1
}
```

**Supported values:**

- `trials`: [100, 400, 1600]
- `true_contrast`: [0.05, 0.15]
- `pairs`: [1, 73536]

**Evidence:** constructed teaching example

Constructed example: the spread 0.4, the trial counts and the true contrasts are values defined for this reader; the cells use Table 2.1 for the three lower scores. The factor of 2 and the 384 heads with roughly seventy thousand pairs are the chapter's own.
