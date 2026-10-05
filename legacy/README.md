# Mathematical probes for The Mathematics of Artificial Intelligence Agents

These are constructed teaching experiments. They do not measure a language model, visual model, production tool, or real document service. Every effect is local and fictitious.

Use Python 3.10 or later on Windows, macOS, or Linux. No dependencies, model accounts, or network calls are required. Extract the archive, open a terminal in its root folder, and run the commands below. On Windows, substitute `py -3` for `python3` where appropriate.

## Commands and interpretation

| Probe | Command | What to inspect |
|---|---|---|
| Existing release simulator | `python3 scripts/document_release_simulator.py --manifest Companion/fixtures/release-probe.json` | Current versus stale approval |
| Computer use | `python3 scripts/computer_use_probe.py --manifest Companion/fixtures/computer-use.json` | Command target, effect, denial, pending confirmation |
| Learning | `python3 scripts/agent_learning_probe.py --manifest Companion/fixtures/learning.json` | Actual policy updates; exact expectations apart from sampled evaluation |
| Orchestration | `python3 scripts/orchestration_probe.py --manifest Companion/fixtures/orchestration.json` | Elapsed time, total work, common-cause failures, capability intersection |
| Resources | `python3 scripts/resource_allocation_probe.py --manifest Companion/fixtures/resources.json` | Feasible choices, Pareto frontier, undefined ratio at zero successes |
| Evaluation | `python3 scripts/evaluation_probe.py --manifest Companion/fixtures/evaluation.json` | Task-level repetitions versus powers of the mean; observed subset fractions |

Expected outputs are in `Companion/expected/`. Compare them with each command's JSON output. Training and evaluation use separate deterministic random streams, not a real held-out population of user requests. Exact quantities come from the declared two-action model; sampled outcomes fluctuate when seeds change. Python's random-stream details can differ between interpreter implementations, so cross-version comparisons should prioritize mathematical invariants over exact sampled floats.

Manifest authority and acknowledgement fields must be JSON Booleans (`true` or `false`), not quoted strings. Costs and durations must be finite and nonnegative; counts and capacities must be positive integers. Invalid inputs are rejected.

## Visual console

Open `Companion/release-console.html` in a browser. Swap the current rows, then replay the saved coordinate. With permission checking enabled, the wrong target is denied. Disable the check to inspect the fictitious unauthorized effect. Refresh the observation and repeat. Compare identifier-based and version-bound requests. The mock-up illustrates target binding and stale state; it contains no screenshot recognition model.

The orchestration example times the two evidence checks and supervisor dispatch/combine stage. Final verification duration is excluded from both elapsed times; the declared total work costs include verification. These are stage timings, not complete end-to-end completion times.

## Matched changes

Change one fixture field at a time. Set orchestration service capacity to one to remove parallel execution. Set shared failure to zero to recover independent failures. Change the resource deadline from three to ten. Request more evaluation repetitions than recorded runs to obtain an unavailable subset metric. Preserve the task and authority contract when comparing procedures.

The original release simulator's `fixed` and `trained` labels do not train a policy. Actual finite-policy updates live in the new learning probe. Neither probe can grant authority through a reward update.

## Reading routes

Computer use accompanies Chapter 18. Learning accompanies Chapter 13; resources Chapter 16; orchestration Chapters 19 through 21; evaluation Chapter 24. Expansion problems E.1 through E.5 in the Mathematical Workbench give hand calculations and separate solutions.
