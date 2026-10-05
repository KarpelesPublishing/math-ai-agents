# Chapter demonstrations



These four calculations are shared with the notebook and illustrated reader. Read the source section and assumptions before choosing a state.

## C03-D01: Fit small runs, forecast a run that is not there yet

If a curve of the form in Equation (3.1) is fitted to small runs, how does the miss on a much larger run depend on how far away it is and on whether the runs share a recipe?

**Source section:** The forecast model

**Application:** When a team reports that a fitted curve predicted a bigger run, ask how far the held-out run sat from the largest run used in the fit, whether the runs really belong to one documented family, and whether the forecast was recorded first. A small miss across one power of ten and the same miss across four are different achievements.

**Assumptions:** The true curve has exactly the form in Equation (3.1), which is assumed here and is not guaranteed for any real family; the book calls the relation measured, not derived. The wiggle and the shift are fixed constructed patterns, not random noise, and the exponent search covers b from -1.000 to -0.010 in steps of 0.001. The fitted a and c are rounded to three decimals before they are added. If the true curve had a different shape, the miss could be larger than shown.

**Declared default controls:**

```json
{
  "decades": 2,
  "runs": "wiggle"
}
```

**Supported values:**

- `decades`: [1, 2, 3, 4]
- `runs`: ['exact', 'wiggle', 'silent']

**Evidence:** constructed teaching example

Constructed example: a loss curve of the form in Equation (3.1) with constants defined for this reader. It is a schematic of the shape of the chapter's GPT-4 loss forecast and is not that report's data.

## C03-D02: The commitment boundary and the registered interval

Given three development measurements and a stated error bound, what point and interval does the team register, what does each possible result say, and what changes if the forecast is rewritten after the result is seen?

**Source section:** A constructed forecast example

**Application:** Write the point forecast and an interval with a stated construction before the held-out member exists. A point alone hides how much uncertainty the team knew it had, and an interval that is declared in advance can be missed, which is what makes a hit mean something.

**Assumptions:** The guarantee is conditional: the true relation is a straight line and every observation is within the stipulated bound of it. The three development points do not prove either. This is a worst-case interval, not a claimed 95 percent coverage rate, and one hit does not establish that the assumptions will keep holding. A nominal 95 percent procedure, unlike this bound, is allowed to miss.

**Declared default controls:**

```json
{
  "observed": 0.43,
  "commitment": "kept"
}
```

**Supported values:**

- `observed`: [0.3, 0.36, 0.43, 0.5]
- `commitment`: ['kept', 'refit', 'posthoc']

**Evidence:** constructed teaching example

Constructed example: the chapter's own worked forecast (points 1, 2, 3 with contrasts 0.10, 0.21, 0.29; interval half-width 0.066667 and the held-out result 0.43), with the other observed results and the after-the-fact choices defined for this reader.

## C03-D03: Smooth ability, abrupt score

When does a sudden jump in a reported pass-or-fail score reflect a sudden change in the model, and when only the cutoff?

**Source section:** Smooth ability, abrupt score

**Application:** For any new family, record q beside the thresholded verdict and read the pair. If only the verdict is kept, a flat early stretch can be mistaken for no progress, and a jump can be mistaken for a change inside the model.

**Assumptions:** q is treated as known; in practice it is estimated from repeated attempts and carries sampling error. The four curves are constructed illustrations, and a graded measure does not guarantee smooth capability in an arbitrary model. A sharp rise in q is evidence of concentrated change in measured behavior, not proof of a phase transition.

**Declared default controls:**

```json
{
  "profile": "jump",
  "tau": 0.5
}
```

**Supported values:**

- `profile`: ['latent', 'jump', 'onset', 'none']
- `tau`: [0.5, 0.8]

**Evidence:** constructed teaching example

Constructed example: four success-probability curves and two thresholds defined for this reader to match the chapter's four profiles. No real model is measured.

## C03-D04: Declare the family before the outcomes arrive

Why does it matter that the shape of the fitted relation is fixed before the held-out results are visible?

**Source section:** The eight-step protocol

**Application:** Before a held-out result exists, write down the family, the transformation and the rule for choosing among several shapes, and file that with the forecast. Afterwards report the residual whether or not it is flattering.

**Assumptions:** Three development points and two test points, with only two candidate shapes. Both families fit three points reasonably well, which is exactly why the choice between them is a free parameter worth declaring. The demonstration cannot detect a family chosen in private after the outcomes; that is a matter of procedure. The outcomes other than the laboratory's own are defined for this reader.

**Declared default controls:**

```json
{
  "data": "default",
  "family": "linear",
  "outcome": "faster"
}
```

**Supported values:**

- `data`: ['default', 'transfer']
- `family`: ['linear', 'log']
- `outcome`: ['extended', 'faster', 'flattening']

**Evidence:** constructed teaching example

Constructed example: the laboratory's development points (1, 0.2), (2, 0.3), (3, 0.4) with test scales 4 and 5, and its log-shaped transfer data (1, 0), (2, 0.6931), (4, 1.3863) with test scales 8 and 16; the outcomes other than the transfer case's continuation are defined for this reader.
