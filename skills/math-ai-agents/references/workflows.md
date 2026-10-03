# Composed workflows

| Workflow | Chapters | Purpose |
|---|---|---|
| reliability | 5, 17, 24 | Separate trajectory assumptions, tool-effect uncertainty and measured outcomes. |
| compute-budget | 6, 16, 27 | Combine declared value, candidate allocation and timely human review. |
| memory-improvement | 2, 15, 24, 25 | Compare mechanisms, retrieval choices, evaluation and improvement acceptance. |
| safe-release | 4, 17, 18, 22, 23, 27 | Inspect reachability, effect confirmation, interface targeting, constraints, monitor checks and delegation. |

Without `--input` these run labeled, separate constructed demonstrations. They do not represent one common empirical population or one joint controller. With `--input`, all required objects must be supplied. Each chapter's input schema remains authoritative. Check those inputs for the shared contract the user's question requires.

The notebook capstone models one constructed release process and records its actual terminal outcomes. Use it when the user needs an integrated worked example; do not confuse the workflow collection of separate methods with that simulator.

Run the integrated example with `python -m math_ai_agents capstone --output capstone.json`, or open `notebooks/28-document-release-capstone.ipynb`. To change its declared process, pass `--input` with a complete object matching `data/examples/capstone.json`. The simulation report contains actual constructed run records, sample traces, matched evaluation and limits; it measures no live model or service.
