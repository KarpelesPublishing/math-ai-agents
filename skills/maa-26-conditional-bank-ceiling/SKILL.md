---
name: maa-26-conditional-bank-ceiling
description: "Separate bank oracle coverage, actual choice, and permission-filtered success. Use for finite candidate bank oracle ceiling, actual selector capability extraction, permission-filtered deployment coverage."
---

# How Much More Could the System Become?

How much capability exists in this finite candidate bank, and how much can selection deploy?

Use this skill to produce the chapter's supported calculation or trace report from declared inputs. Read [method and assumptions](references/method.md), then [input contract](references/input-contract.md) when preparing user data. The canonical chapter source and its equation locators are recorded in [chapter reference](references/chapter.json).

For teaching, start from `--case example`; for a changed assumption use `--case changed`. For supplied inputs, validate their shape against the contract and pass `--input`. Do not silently replace missing user data with fictitious values.

Run the bundled helper with the available Python interpreter:

```bash
python3 scripts/run.py --case example --text
python3 scripts/run.py --input /path/to/inputs.json --output /path/to/report.json
```

Paths to the helper are relative to this skill directory. In a shell, resolve them from the actual installed skill path rather than assuming the current directory. The helper locates the matching bundle automatically. Figure export is optional and requires its notebook dependencies; use `--figure /path/to/chart.svg` with the bundle's notebook interpreter.

Inspect the calculated quantities, assumptions and limitations before writing the answer. Deliver the requested decision, calculation, trace or procedure, not a chapter summary. State which input contract and method ran. Input values may be observations or judgments; their presence in JSON does not verify their provenance, representativeness or causal meaning.

For transfer examples and failures, read [worked use cases](references/use-cases.md). These support diagnosis rather than replacing the user's question.

If Python execution is unavailable, give a tractable hand calculation or the precise method, and label it as not executed. If the runtime is missing, identify that installation problem rather than inventing output. A capability or utility calculation never supplies permission for an external action.

For any of the chapter's four illustrated demonstrations, read [demonstrations and controls](references/demonstrations.md). They reproduce the matching notebook and browser calculation, including the figure and worked steps. List them with `python3 scripts/run.py demo-list`; execute one with `python3 scripts/run.py demo --id C26-D01 --text`. Pass `--input` with a complete control object to select another declared state. Omitted input chooses the documented default. These demonstrations require the declared notebook tools; the original chapter calculation above remains a standard-library method.
