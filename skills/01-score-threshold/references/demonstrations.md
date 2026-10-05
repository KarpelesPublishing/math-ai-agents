# Chapter demonstrations



These four calculations are shared with the notebook and illustrated reader. Read the source section and assumptions before choosing a state.

## C01-D01: The same scores, a moving cutoff

If no score changes, can moving the pass line move the place where a skill seems to arrive?

**Source section:** What did change

**Application:** When a dashboard turns green, ask for the underlying graded scores and the cutoff behind the colour. If moving the cutoff a little moves the date of arrival, the date describes the cutoff as much as the system.

**Assumptions:** The same task, output boundary and environment at every checkpoint, and scores that are exact rather than noisy estimates. Five or four constructed points cannot show whether the true curve is smooth between them. A genuinely sharp change inside the model would also produce a jump, and this picture cannot rule that out.

**Declared default controls:**

```json
{
  "dataset": "gradual",
  "cutoff": 0.5
}
```

**Supported values:**

- `dataset`: ['gradual', 'steep']
- `cutoff`: [0.5, 0.55, 0.6, 0.7]

**Evidence:** constructed teaching example

Constructed example: the five scores and the larger-rise four-score set with its cutoff of 0.70 are the laboratory's declared inputs for this chapter (default and transfer cases), computed with its threshold function; the other cutoffs are values defined for the reader.

## C01-D02: Three places a change can enter, and the loop

If the model's probabilities never change, how much can the reported score move?

**Source section:** Three places a change can enter

**Application:** When two reports of the same model disagree, ask which stage differs: the decoding settings, the scoring rule or the number of attempts. Report the stage that changed, not only the final number.

**Assumptions:** One prompt, three possible responses and independent attempts. The probabilities 0.45, 0.35 and 0.20 and the twenty attempts are the chapter's constructed values; the flat law 0.30, 0.30, 0.40 is a value defined for the reader. Real decoders and evaluators have more settings, attempts can be correlated, and several settings can differ at once.

**Declared default controls:**

```json
{
  "decoder": "greedy",
  "evaluator": "only_a",
  "law": "chapter"
}
```

**Supported values:**

- `decoder`: ['greedy', 'sample', 'attempts']
- `evaluator`: ['only_a', 'evidence']
- `law`: ['chapter', 'flat']

**Evidence:** constructed teaching example

Constructed example: the chapter's constructed distribution of 0.45, 0.35 and 0.20 over three responses and its twenty-attempt budget at probability 0.20; the second law is defined for the reader.

## C01-D03: How exact match manufactures a cliff

How much does a small gain per token change an exact-match score, and how does target length decide it?

**Source section:** Why exact match manufactures a cliff

**Application:** Before reading a flat region at the start of a benchmark curve as no progress, compute what the score would be if per-token quality had improved smoothly. Then decide whether the benchmark can resolve those small values.

**Assumptions:** Tokens succeed independently and each has the same probability q. Real text violates this, so the mechanism is robust but the exact factors are constructed. The expected passes in 100 trials are expected counts, not observed results, and the first-order rule is a small-change approximation.

**Declared default controls:**

```json
{
  "length": 40,
  "step": "low"
}
```

**Supported values:**

- `length`: [5, 20, 40, 100]
- `step`: ['low', 'high', 'wide']

**Evidence:** constructed teaching example

Constructed example: the per-token values 0.90, 0.95 and 0.99 and the target lengths of Table 1.1, computed from Equation (1.4); the coding-assistant case is the chapter's twenty-line example. The budget of 100 trials behind the expected-passes readout is a value defined for the reader.

## C01-D04: Audit a claim before attributing it

Which declarations must be fixed before an emergence claim can be tested, and what does the six-question audit say about two claims?

**Source section:** An emergence audit

**Application:** Before crediting the model for a capability, write down the five declarations and the six audit answers. A blank counterfactual row means the claim has not been tested, whatever the chart shows.

**Assumptions:** The audit rows are the chapter's own worked answers; for the second claim the chapter answers only the components, the coupling and the counterfactual, and this demonstration leaves the other rows blank rather than invent them. Only one declaration is opened at a time here, and the model family and tolerance rows are not offered as the open one.

**Declared default controls:**

```json
{
  "unfixed": "none",
  "claim": "rescoring"
}
```

**Supported values:**

- `unfixed`: ['none', 'axis', 'metric', 'predictor']
- `claim`: ['rescoring', 'benchmark']

**Evidence:** constructed teaching example

Constructed example: the five declarations of Figure 1.2 and the two worked audits of the chapter's emergence audit section, shown as the chapter states them.
