---
name: maa-05-composite-kernel
description: "Compose a chooser and tool kernel, then separate marginal from trajectory reliability. Use for compose frozen chooser tool kernel, conditional versus marginal trajectory reliability, shared failure long-run construction."
---

# What the Model Becomes Inside an Agent

What system does a frozen chooser become when its surrounding kernel changes?

Use this skill to apply Chapter 5 of *The Mathematics of AI Agents* to the user's own inputs and return the calculation or trace report the chapter supports. Read [method and assumptions](references/method.md) first, then the [input contract](references/input-contract.md) when preparing the user's data. [Worked use cases](references/use-cases.md) show the default case, a changed assumption and a transfer case. The chapter notebook, [`notebooks/05-composite-kernel.ipynb`](../../notebooks/05-composite-kernel.ipynb), runs the same computation step by step with figures.

## Apply it to the user's inputs

1. Restate the decision or quantity the user wants, and check that this chapter's method computes it. If it does not, say which quantity is missing and suggest the master skill, `math-ai-agents`, for routing.
2. Collect the fields listed in the input contract. Ask for any that are missing; do not fill gaps with the teaching values.
3. Validate the shape: units, ranges, probabilities that sum to one, and aligned lists, as the contract requires.
4. Run the calculation, or work it by hand for a small case, then inspect the returned quantities, assumptions and limitations before writing the answer.
5. Deliver the requested decision, calculation, trace or procedure, not a chapter summary. Say which method ran and what the inputs can and cannot establish.

## Run the computation

From a clone of the repository, with the package installed (`pip install -e .`):

```bash
python -m math_ai_agents run --chapter 5 --case example --text
python -m math_ai_agents run --chapter 5 --input my-inputs.json --output report.json
```

`--case changed` and `--case transfer` run the chapter's other constructed cases. `data/examples/ch05.json` in the repository has the exact input shape; copy it and replace the values. Add `--figure chart.svg` to save the chapter figure (needs matplotlib).

Input values may be observations or judgments; their presence in a JSON file does not establish their provenance, representativeness or causal meaning. If code execution is unavailable, give a hand calculation or the precise method and label it as not executed. A capability or utility calculation never supplies permission for an external action.
