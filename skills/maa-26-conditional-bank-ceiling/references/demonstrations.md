# Chapter demonstrations



These four calculations are shared with the notebook and illustrated reader. Read the source section and assumptions before choosing a state.

## C26-D01: A bank is a finite object, and its pool depends on how it was sampled

For fixed pools of ten programs per task, how often does a random subset contain a pass, how does that differ from an independent-draw guess, and how does the sampling rule change the answer?

**Source section:** Stage two: a bank is a finite object

**Application:** When a report gives a pass@k number, ask for the pool size n, the per-task pass counts, the subset size k and the sampling settings. Without them you cannot tell an exact pool calculation from an extrapolation, or compare two banks made at different temperatures.

**Assumptions:** Pools of ten programs, labels fixed by the declared tests, subsets chosen uniformly without replacement. The two four-task banks are constructed to show the direction the chapter reports for temperature; they are not measurements. The result says nothing about programs outside the pool, other prompts or adaptive retries. If the ten programs repeat one wrong approach the labels are strongly correlated, and the pool still has exactly this coverage but little useful variety. The chapter's pools of 200 programs per task are too large for a pencil check and are not shown.

**Declared default controls:**

```json
{
  "pool": "chapter",
  "subset": 3
}
```

**Supported values:**

- `pool`: ['chapter', 'low', 'high']
- `subset`: [1, 3, 5, 8]

**Evidence:** constructed teaching example

Constructed example: the book's ten-candidate worked subset calculation (2 passing, size 3) and two constructed four-task banks that differ in how concentrated the passes are.

## C26-D02: Coverage is a ceiling, and each rung can only lose success

Can any selector return a correct candidate more often than the bank contains one, and where does each task's success get lost on the way to deployment?

**Source section:** Stage three: oracle coverage is an information ceiling

**Application:** Before buying a better ranker, compute coverage on the bank you already have. If coverage is low, the generator, its context or its tools are the limit. Keep permission filtering out of correctness labels so a denied correct answer is not counted as a model error.

**Assumptions:** Small constructed banks with fixed task weights and pass labels from one evaluator. The oracle selector uses information a deployed system may not have. The ceiling holds only for this bank and evaluator; a new candidate or a different evaluator changes the object being bounded. Adding a candidate cannot lower coverage, because a covered task stays covered.

**Declared default controls:**

```json
{
  "bank": "diag",
  "selector": "notebook",
  "deploy": "all"
}
```

**Supported values:**

- `bank`: ['diag', 'prefix', 'xfer']
- `selector`: ['notebook', 'oracle']
- `deploy`: ['all', 'denied']

**Evidence:** constructed teaching example

Constructed example: the laboratory's default, changed and transfer banks, computed with the laboratory's own bank-ceiling function, plus a two-candidate prefix of the default bank.

## C26-D03: What actual selection leaves behind

Where does a coverage and selection pair sit against the ceiling, how large is the gap, and what does the gap point at?

**Source section:** Stage four: what actual selection leaves behind

**Application:** Report delivered selection and the same-bank unit-test result side by side. Ask what part of the gap a practical intervention could collect under the deployment contract, then compare that gain with cost, latency, error, safety risk and permissions.

**Assumptions:** The Codex percentages are the chapter's reported figures for one experiment, used as given and not re-measured, and they hold only for that generator, bank and tests. The collected share is a planning what-if with no data behind it. The two constructed pairs exist only to show the other two readings. Collecting any of the gap needs evidence available before the outcome is known, which a deployment may not have.

**Declared default controls:**

```json
{
  "point": "codexs",
  "share": 0.5
}
```

**Supported values:**

- `point`: ['codexs', 'codex12', 'near', 'low']
- `share`: [0, 0.5, 1.0]

**Evidence:** source-reported measurements and constructed comparisons

Constructed example: the chapter's reported Codex percentages used as given, two constructed coverage and selection pairs, and a hypothetical collected share defined for this reader.

## C26-D04: A saturation forecast depends on the curve

If three observed coverage points are fitted by three different curves, do they agree about the limit, and about whether a larger bank or a better selector has more room?

**Source section:** A saturation forecast

**Application:** Use a saturation curve to plan capacity inside a stated budget, and report the fitted family with it. When generation adds little coverage while selection stays far below coverage, the next increment of budget has two destinations: more candidates or a better way to judge the ones already present. Do not read the limit as a bound on what a changed prompt, tool or generator could reach.

**Assumptions:** The chapter's constructed fixed-generator saturation curve: three made-up coverage points on one declared task bank. With more points or a physical reason for one family, the choice could narrow, but this example has neither. A changed generator, selector or task distribution gives a different curve, so no limit here is a bound on an open design space. The selected success values are hypothetical, and the comparison of rooms does not price latency, cost or work.

**Declared default controls:**

```json
{
  "family": "exp",
  "selector": "far"
}
```

**Supported values:**

- `family`: ['exp', 'hyp', 'pow']
- `selector`: ['near', 'far']

**Evidence:** constructed teaching example

Constructed example: the chapter's constructed coverage points (0.40, 0.55, 0.63 at 10, 25, 50 samples) fitted exactly by three curve families, with a hypothetical selected success defined for this reader.
