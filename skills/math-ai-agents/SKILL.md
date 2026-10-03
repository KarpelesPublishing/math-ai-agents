---
name: math-ai-agents
description: Apply the implemented mathematics of AI agents to decisions, planning, memory, tools, coordination, reliability, security, evaluation and delegation. Route to the relevant chapter method or combine compatible methods from The Mathematics of AI Agents.
---

# The Mathematics of AI Agents

Produce a useful calculation, evidence analysis, teaching example or procedure design using the methods implemented for the book's 27 chapters. Read the [routing map](references/routes.md) to identify the primary mathematical task, then load only the chapter skill needed for that task; do not load all 27 skills for a simple question. Each chapter skill lives in `skills/NN-<method>/` and points to its notebook in `notebooks/`.

Choose by the requested outcome and the input contract. A reliability question may concern conditional trajectory success, a lost tool acknowledgement, a selector's errors or measured run outcomes. These need different calculations. A reward score cannot establish authorization, and a marginal success rate cannot identify trajectory dependence.

## Run the methods

From a clone of the repository, with the package installed (`pip install -e .`):

```bash
python -m math_ai_agents list
python -m math_ai_agents route "Compare the tool retry with verification"
python -m math_ai_agents run --chapter 17 --input trace.json --output report.json
```

Read the selected chapter's input contract; do not substitute teaching values for absent user data. For teaching only, `run --chapter N --case example --text` runs an explicitly constructed example. The route command is a phrase matcher; it offers suggestions and does not replace judgment about which quantity the user needs.

## Combined questions

For questions that span chapters, use the [workflow boundaries](references/workflows.md). Four composed workflows are available: reliability, compute-budget, memory-improvement and safe-release. A supplied workflow input maps each required chapter number to a complete input object. Missing objects stop execution instead of silently inserting teaching cases.

```bash
python -m math_ai_agents workflow reliability --input chapter-inputs.json --output workflow.json
```

The integrated release controller in `notebooks/28-document-release-capstone.ipynb` is one constructed process; it is different from a collection of separate chapter methods.

## Answer the question

For ambiguous questions, identify the few possible quantities the user might mean and ask one focused question only when the choice changes the result. Unsupported requests should receive a precise explanation of the missing method or input, not a fabricated guarantee.

Run the calculations, inspect outputs and invariants, then answer with the decision or report the user asked for. Explain which methods ran, where the inputs came from, and the assumptions, uncertainty and limitations. Check that task definitions, units, populations, budgets and authority are compatible before relating reports. Do not average incompatible scores or imply that independent reports form a causal model.

If code execution is unavailable, provide the method or a small hand calculation and mark it not executed. External publication, live-system changes and paid calls require the user's actual authorization; this skill adds none.
