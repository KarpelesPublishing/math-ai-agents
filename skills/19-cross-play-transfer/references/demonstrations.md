# Chapter demonstrations



These four calculations are shared with the notebook and illustrated reader. Read the source section and assumptions before choosing a state.

## C19-D01: Diagonal against off-diagonal

How much of a score is lost when a policy meets a partner from another training run instead of its own, and what did the fix change?

**Source section:** The instrument

**Application:** When two components of a system were developed together, evaluate them also against independently developed replacements, and report the diagonal, the off-diagonal and the loss, not only the diagonal.

**Assumptions:** The statistic is meaningful only when the diagonal mean is positive, and it compares particular pairings under one procedure. It is not a universal measure of cooperation and does not show why a gap appears. A small loss does not show the policies are independent or interchangeable. The fix view uses only losses the chapter prints, plus one subtraction for the small4 full-strategy loss.

**Declared default controls:**

```json
{
  "task": "small2",
  "view": "means"
}
```

**Supported values:**

- `task`: ['small2', 'small3', 'small4', 'gathering']
- `view`: ['means', 'fix']

**Evidence:** source-reported measurements with derived comparisons

Values the chapter prints for three Laser Tag maps and two control tasks (the diagonal and off-diagonal means, and in the fix view its printed losses and reductions), plus recomputations marked as such, arranged here as a constructed teaching example; the loss is computed with the laboratory's cross-play function.

## C19-D02: A best-response cycle

If each party always plays its best answer to the other's current move, does the sequence settle?

**Source section:** A cycle, worked

**Application:** When two adapting components keep re-tuning to each other, track a fixed set of evaluation partners rather than only the latest partner, because progress against the latest one can be undone by the next update.

**Assumptions:** A constructed zero-sum game with one-step pure best responses, ties paying 0 (a choice made for this reader), and no noise. Some games converge under the same rule, and other update rules behave differently. The cycle shows that convergence is not guaranteed; it does not explain the transfer losses in Demonstration 1.

**Declared default controls:**

```json
{
  "updates": 6,
  "start": "A"
}
```

**Supported values:**

- `updates`: [2, 4, 6, 12]
- `start`: ['A', 'B', 'C']

**Evidence:** constructed teaching example

Constructed example: the three-option game and the six-update trace described in the chapter's worked cycle, with ties defined by this reader.

## C19-D03: Return on depth

How much of the available reduction in transfer loss does each added stretch of the fix buy?

**Source section:** How much of the method is doing the work

**Application:** Before paying for more depth in a training procedure, measure the loss at two or three intermediate depths and compare the points each step buys with its cost.

**Assumptions:** One method on one map from one paper. Level ten is the printed reduction 56.7 subtracted from the baseline. The flattening is observed at three tested depths, not explained, and it may not appear on other maps, with other methods, or for other counterparties.

**Declared default controls:**

```json
{
  "depth": "l3",
  "view": "loss"
}
```

**Supported values:**

- `depth`: ['base', 'l3', 'l5', 'l10']
- `view`: ['loss', 'reduction', 'step']

**Evidence:** source-reported measurements with derived comparisons

Constructed example: the chapter's printed small4 baseline and level three and five losses, and the printed level-ten reduction, used as a teaching example.

## C19-D04: Which partners will it meet?

If the diagonal favors one policy, can the partners you expect to meet make another policy the better choice?

**Source section:** Self-play is the diagonal

**Application:** Before choosing a component, write down the partner distribution you expect in use, and check whether the ranking survives plausible changes to it, instead of ranking by the diagonal.

**Assumptions:** Two constructed matrices and declared partner mixes; the weighted average over partners is this laboratory's way of asking the deployment question, not a formula printed in the chapter. It assumes the matrix entries share one success definition, and that partners do not change how they behave once a policy is chosen.

**Declared default controls:**

```json
{
  "matrix": "two",
  "mix": "target"
}
```

**Supported values:**

- `matrix`: ['two', 'three']
- `mix`: ['target', 'changed', 'tie', 'known']

**Evidence:** constructed teaching example

Constructed example: the laboratory's default two-policy matrix with its default and changed partner weights, and its transfer three-policy matrix with the transfer weights, computed with the laboratory's cross-play function.
