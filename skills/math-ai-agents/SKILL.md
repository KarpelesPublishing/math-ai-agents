---
name: math-ai-agents
description: Apply the implemented mathematics of AI agents to decisions, planning, memory, tools, coordination, reliability, security, evaluation and delegation. Route to the relevant chapter method or combine compatible methods from this book companion.
---

# The Mathematics of Artificial Intelligence Agents

Produce a useful calculation, evidence analysis, teaching example or procedure design using the laboratory's implemented chapter methods. Read [routing map](references/routes.md) to identify the primary mathematical task. Load only the chapter skill and references needed for that task; do not load all 27 skills for a simple question.

Choose by the requested outcome and input contract. A reliability question may concern conditional trajectory success, a lost tool acknowledgement, a selector's errors or measured run outcomes. These need different calculations. A reward score cannot establish authorization, and a marginal success rate cannot identify trajectory dependence.

The helper supplies inspectable route suggestions and executes the selected chapter:

```bash
python3 scripts/run.py route "Compare the tool retry with verification"
python3 scripts/run.py run --chapter 17 --input /path/to/trace.json --output /path/to/report.json
python3 scripts/run.py list
python3 scripts/run.py demo-list --chapter 17
python3 scripts/run.py demo --chapter 17 --id C17-D01 --text
```

Resolve the helper relative to the actual skill path. The bundle runtime is located automatically. Read the selected chapter's input contract; do not substitute fixtures for absent user data. For teaching only, `run --chapter N --case example --text` is an explicitly constructed example.

For a figure or worked calculation from the browser reader, use the [demonstration routing map](references/demonstrations.md). Every chapter has four matching notebook demonstrations. The `demo` command accepts `--input` with a complete object of the declared controls, and `--figure` for SVG output. Read the chapter demonstration's assumptions and source section; the original `run` command and the new `demo` command have distinct input contracts.

For combined questions, use [workflow boundaries](references/workflows.md). Four packaged workflows are available: reliability, compute-budget, memory-improvement and safe-release. A supplied workflow input maps each required chapter number to a complete input object. Missing objects stop execution instead of silently inserting teaching cases.

```bash
python3 scripts/run.py workflow reliability --input /path/to/chapter-inputs.json --output /path/to/workflow.json
```

For ambiguous questions, identify the few possible estimands and ask one focused question only when the choice changes the result. The route helper is a phrase matcher; it does not replace semantic judgment. Unsupported requests should receive a precise explanation of the missing method or input, not a fabricated guarantee.

Run available calculations, inspect outputs and invariants, then answer with the decision or report the user requested. Explain which methods ran, input provenance, assumptions, uncertainty and limitations. Check compatibility of task definitions, units, populations, budgets and authority before relating reports. Do not average incompatible scores or imply that independent reports form a causal model.

If execution is unavailable, provide the method or a small hand calculation and mark it not executed. External publication, live-system changes and paid calls require the user's actual authorization; this skill adds none. Sequential execution is sufficient and does not require subagents.
