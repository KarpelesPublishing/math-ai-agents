#!/usr/bin/env python3
"""Build orientation, integrated capstone and separate teaching documents."""
from __future__ import annotations
import json
import re
from pathlib import Path
import pprint
import shutil
import sys

from build_materials import ROOT, PROJECT, markdown, code, notebook, write_json, BOOTSTRAP
sys.path.insert(0, str(ROOT / "src"))
from math_ai_agents.capstone import DEFAULTS

BOOK_IDENTITY = "The Mathematics of Artificial Intelligence Agents\n\nA Readable Guide to Decisions, Planning, Memory, Tools, Learning, and Cooperation\n\n"


def orientation():
    cells = [markdown('''# Start here: one choice, two columns

A release controller has evidence, but evidence alone cannot tell it whether to act. It also needs to know what the consequences are worth. The first experiment separates those two questions, then makes a choice small enough to check by hand.

The laboratory follows all 27 chapters of *The Mathematics of Artificial Intelligence Agents*. Every chapter has a notebook, a skill and a documented input shape. The notebooks teach the calculation; the skills let an assistant apply the same computation to a new case. The master skill helps select the method. Neither format supplies information that the inputs do not contain.

This orientation gives one successful run. It also shows how to find the changed-assumption experiment, the separate solutions, and the local reading guide.

- Prepare the notebook and inspect its inputs.
- Calculate expected utility and reverse the choice.
- Find a chapter or assistant skill.
- Record what a result actually establishes.'''),
             markdown('''## Technical Requirements

For notebooks, use Python 3.11 or later and the dependencies installed by the launcher. For the chapter calculations without notebooks, Python 3.10 or later is enough. Keep the complete extracted folder together. No API key or model subscription is required.

On Mac, double-click **Open Laboratory.command**. Choose **Install notebook tools** once, then **Open Jupyter notebooks**. The first installation may need a network connection to obtain packages. Later examples run locally. If you want to read before installing anything, open `guide/index.html`.

In Jupyter, open this notebook and choose **Run → Run All Cells**. Each code cell should finish without a traceback. The cell below locates the complete bundle and imports its computations.'''), code(BOOTSTRAP),
             markdown('''## Calculate before choosing

Suppose release succeeds with probability 0.8. Success is worth 10 utility units; failure is worth -30. Attempting release costs 1 unit. Declining has utility zero. These values are stipulated for this example, not measured facts or an objective valuation.

The release utility is `0.8 × 10 + 0.2 × (-30) - 1 = 1`. Declining has utility zero, so the declared rule prefers release. The probability is a belief about the outcome; the utilities express how much the outcome matters. Keep those columns separate.

The next cell performs that same calculation. The labels identify actions; the probabilities in each row must sum to one.'''),
             code('''choice = {"actions": [
    {"name": "release", "probabilities": [0.8, 0.2], "utilities": [10, -30], "cost": 1},
    {"name": "abstain", "probabilities": [1.0], "utilities": [0], "cost": 0}
]}
first = analyze(6, choice)
first['evidence_kind'] = 'constructed teaching example'
print(report_text(first))
assert first['result']['metrics']['selected_action'] == 'release'
display(SVG(figure_svg(first)))'''),
             markdown('''**Figure 0.1:** The declared actions and their probability sensitivity. A higher value ranks an action under these utilities; it does not authorize release.

## Change what you know

Now lower the release-success probability to 0.6 while keeping the same outcome values and cost. Before running the next cell, calculate the new expected utility. It is `6 - 12 - 1 = -7`, so the preferred action should change to abstention.

The code copies the input before changing it. Your original example remains available for comparison.'''),
             code('''import copy
less_certain = copy.deepcopy(choice)
less_certain['actions'][0]['probabilities'] = [0.6, 0.4]
second = analyze(6, less_certain)
second['evidence_kind'] = 'constructed changed-assumption example'
print(report_text(second))
assert second['result']['metrics']['selected_action'] == 'abstain' '''),
             markdown('''## Find the method you need

Chapter notebooks are numbered in reading order. The chapter skill listed at the end of each notebook takes a documented JSON object and returns the same calculation. Use `data/examples/ch06.json` as a valid shape, then save your own copy with your own values.

The master skill, `math-ai-agents`, routes by mathematical purpose. A request about a failing sequence may need a trajectory model, a tool-effect trace or an evaluation of observed runs. Those are different inputs and different conclusions. The small helper below offers suggestions; an assistant must still check the requested outcome and assumptions.'''),
             code('''from math_ai_agents.routing import suggest
print(json.dumps(suggest('Compare the retry with verification after a lost acknowledgement'), indent=2))'''),
             markdown('''## Continue through the book

Start with Chapters 1 through 5 to distinguish model capability, measurement and assembled agent behavior. Chapters 6 through 13 develop decisions, beliefs, planning and learning. Chapters 14 through 18 study models, memory, computation, tool effects and interfaces. Chapters 19 through 21 study counterparties and institutions. Chapters 22 through 27 separate authority, security, measured capability, improvement and human delegation.

For a complete constructed controller, open `28-document-release-capstone.ipynb`. For hand calculations without a notebook, read the standalone workbook. Answers remain in the separate solutions so you can attempt the questions first.

## Summary

You calculated one action's value, changed a belief and saw the choice reverse. Nothing in that calculation established a probability estimate, chose a utility scale or granted permission. The rest of the laboratory keeps that separation visible as the system becomes larger. A useful result names its inputs, computes what follows from them, and stops where their warrant stops.''')]
    write_json(ROOT / "notebooks/00-start-here.ipynb", notebook(cells))


def capstone():
    cells = [markdown('''# One request through the document-release controller

The controller is asked to release v2. Preparing the document involves several steps. The screen may move, a retrieved instruction may be untrusted, approval may be absent, and a successful service call may lose its acknowledgement. Each complication belongs to a different part of the book. The final question is whether the intended document was released once, with current authority and confirmation.

This notebook runs a fictitious simulated process. A baseline and a guarded procedure face the same environmental draws on each run. The baseline reuses a coordinate and retries a lost acknowledgement. The guarded procedure refreshes its target, rejects the modeled injection, obtains required approval and verifies an uncertain effect. Their terminal records support a matched comparison under the declared simulation law.

- Declare the process, authority and outcome.
- Follow a request into its effect and receipt.
- Compare completed trajectories and costs.
- Change the deadline and diagnose the new failures.
- Export records and check the evidence boundary.'''),
             markdown('''## Technical Requirements

Use the same Python 3.11 notebook environment as the chapter laboratories. The computation itself uses the standard library. There is no screenshot model, language model, network service or real human reviewer.

Prior knowledge: expected utility and budgets from Chapters 6 and 16; effect versus receipt from Chapter 17; stale coordinates from Chapter 18; current authority and untrusted input from Chapters 22 and 23; matched evaluation and delegation from Chapters 24 and 27.'''),
             code(BOOTSTRAP + "\nfrom math_ai_agents.capstone import simulate\n"),
             markdown('''## A declared process

An independent preparation step succeeds with probability `step_success`, conditional on no shared preparation failure. The separate `shared_failure` variable can invalidate the whole preparation. The two quantities cannot be collapsed into a marginal step probability and then multiplied without changing the model.

The fictitious environment also draws layout staleness, injection, acknowledgement loss, approval availability and reviewer availability. Those draws are generated before either procedure acts, so the pairing refers to the same run conditions. The guards themselves are assumed correct in this construction. Their accuracy is an input assumption, not something this experiment has measured.

Success means exactly one intended effect, current authority and confirmation. An unconfirmed effect is pending. A duplicate effect is a failure under this contract even if the document was released. Denials and preparation failures remain in the denominator. Costs and elapsed time are separate ledgers; a review can miss a deadline even when its monetary cost fits the budget.'''),
             code(f"parameters = {pprint.pformat(DEFAULTS, sort_dicts=False)}\nexperiment = simulate(parameters)\nprint(json.dumps(experiment['metrics'], indent=2))"),
             markdown('''## Inspect a trajectory

The next cell shows the first few paired traces. The fields describe events generated by this program, not beliefs inferred from external logs. An effect row says what the fictitious service did. A verify row says what the controller subsequently observed. The review owner has authority to approve the intended v2; approval is not manufactured by increasing reward.

Read one baseline and one guarded trace with the same run number. Identify the first point at which their actions differ. Then inspect the terminal record rather than judging the proposal text.'''),
             code("print(json.dumps(experiment['sample_traces'][:4], indent=2))"),
             markdown('''## Count completion, not confidence

The first panel isolates the conditional independent preparation calculation. It leaves the separate shared-failure draw visible in the input contract. The second panel reports the actual terminal completion fractions from the simulated runs. Those fractions include the controller's interface, authority, verification and deadline rules.

These panels answer different questions. Multiplying a step average would not reproduce the second panel's process, because review, retry and confirmation change the possible trajectories.'''),
             code("capstone_report = {'chapter': 28, 'method': 'document-release-capstone', 'result': experiment}\ndisplay(SVG(figure_svg(capstone_report)))"),
             markdown('''**Figure 28.1:** Conditional preparation survival and recorded terminal completion. The controller fraction is a constructed sample, not an estimate of a deployed agent.

## Compare matched procedures

Chapter 24's actual computation is applied to the terminal records. Each run has a task identifier, a procedure identifier and a shared run identifier. A matched difference uses those common identifiers; unpaired records cannot quietly become matched evidence. Mean cost includes failures because every attempted trajectory consumes the declared process's resources.

The guarded procedure changes several mechanisms at once. The comparison can measure the combined change under this generator. It cannot attribute an improvement to memory, review or a monitor individually. That would require matched ablations such as Chapter 2's four-cell design.'''),
             code("print(report_text(experiment['evaluation']))"),
             markdown('''## Let waiting consume the deadline

Reduce the deadline to two time units. Preparation and a release attempt can consume the whole allowance; review or verification may then have no time to complete. This changes the feasible paths, not merely the score attached to them.

Predict which outcome counts will rise. Run the next cell, inspect the failure names, and decide whether the correct response is a different policy, a longer deadline or a different task contract. Do not remove failures from the denominator to make the controller look better.'''),
             code("short_deadline = dict(parameters, deadline=2.0)\nlate = simulate(short_deadline)\nprint(json.dumps(late['metrics'], indent=2))\ndisplay(SVG(figure_svg({'chapter': 28, 'method': 'short-deadline-capstone', 'result': late})))"),
             markdown('''**Figure 28.2:** The same constructed procedures under the shorter deadline. Authority and exactly-once completion remain part of success.

## Export and transfer

The report records all terminal outcomes and a few readable traces. Save it below to inspect the inputs, run records and matched analysis outside the notebook. The master skill can run the same capstone with a complete input object, or apply individual chapter methods to compatible records. A collection of independent chapter demonstrations is different from this one integrated process.

For a new experiment, copy `data/examples/capstone.json`, change the approval probability or review delay, and pass that object to `simulate`. Preserve the success definition when comparing procedures. If you change the meaning of success, explain the new estimand before comparing its numbers.'''),
             code("output = LAB_ROOT / 'reader-output' / 'capstone-report.json'\noutput.parent.mkdir(exist_ok=True)\noutput.write_text(json.dumps(experiment, indent=2))\nprint('Saved:', output.name)"),
             markdown('''## Questions

1. If all preparation steps are perfect, why can terminal completion still be below one?
2. Which inputs describe the world, and which branches describe the controller's policy?
3. What would need to change before the results supported a claim about an actual agent?

Answers are in `solutions/capstone.md`.

## Summary

The final record depends on more than a proposal or a per-step accuracy. The controller needs a usable target, current approval, an effect contract, enough time to confirm the effect, and a specified no-response policy. You can inspect those dependencies here because the transition process is declared. Deployment requires evidence for the process being claimed, rather than treating this constructed example as that evidence.''')]
    write_json(ROOT / "notebooks/28-document-release-capstone.ipynb", notebook(cells, 28))
    write_json(ROOT / "data/examples/capstone.json", DEFAULTS)
    (ROOT / "solutions/capstone.md").write_text('''# Capstone solutions

1. Perfect preparation does not remove stale targeting, injected instructions, absent approval, unavailable review, acknowledgement loss, budget limits or deadlines. Success requires one intended, authorized and confirmed effect.
2. Probabilities for preparation, shared failure, layout, injection, acknowledgement and availability declare the environment. Refreshing, blocking, reviewing, retrying and verifying are policy branches. A reviewer capability and a perfect guard are assumptions of the construction.
3. A deployment claim requires an explicit task/population contract, actual effect and authority observations, representative runs, justified dependence assumptions, measured guard/reviewer behavior, resource accounting and an appropriate comparison. The simulation's exact rules cannot be silently attributed to a real system.
''')


def _show(value):
    """Compact single-line rendering of one input value for the standalone workbook."""
    if isinstance(value, list) and len(value) > 10 and all(isinstance(x, (int, float)) for x in value) and len(set(value)) == 1:
        return f"{json.dumps(value[0])} repeated {len(value)} times"
    return json.dumps(value)


WORKBOOK_OMIT = {5: {"assemblies": "five assembly variants used only by the notebook figure; see the guide page"}}


def inputs_block(n, c, guide_page):
    """Print every input the three cases need, so the questions can be worked from the workbook alone."""
    omit = WORKBOOK_OMIT.get(n, {})
    lines = [f"**Inputs.** All values are constructed. Reading page and notebook: [{guide_page}](../guide/chapters/{guide_page}). The questions below refer to these three cases.", "",
             "Field meanings:", ""]
    lines += [f"- `{k}`: {v}" for k, v in c["input_fields"].items() if k not in omit]
    default = {k: v for k, v in c["defaults"].items() if k not in omit}
    lines += ["", "Default case:", "", "```text"] + [f"{k} = {_show(v)}" for k, v in default.items()] + ["```"]
    for label, key in (("Changed case", "changed"), ("Transfer case", "transfer")):
        case = c[key]
        diff = {k: v for k, v in case.items() if k not in omit and c["defaults"].get(k, object()) != v}
        lines += ["", f"{label} (any field not listed keeps its default value):", "", "```text"] + [f"{k} = {_show(v)}" for k, v in diff.items()] + ["```"]
    if omit:
        lines += ["", "Not printed: " + "; ".join(f"`{k}` ({why})" for k, why in omit.items()) + "."]
    return "\n".join(lines)


def capstone_questions():
    """Read the capstone question list from the generated notebook so the two documents cannot drift."""
    nb = json.loads((ROOT / "notebooks/28-document-release-capstone.ipynb").read_text())
    for cell in nb["cells"]:
        text = "".join(cell["source"]) if cell["cell_type"] == "markdown" else ""
        if "## Questions\n\n" in text:
            block = text.split("## Questions\n\n", 1)[1].split("\n\n", 1)[0]
            return [line for line in block.splitlines() if re.match(r"\d+\. ", line)]
    raise ValueError("capstone questions not found in notebook 28")


def workbook():
    original = (PROJECT / "Manuscript/back-matter/mathematical-workbench.md").read_text()
    target = ROOT / "workbook"
    target.mkdir(exist_ok=True)
    (target / "original-mathematical-workbench.md").write_text(original)
    problems, remainder = original.split("## Worked Solutions", 1)
    old_solutions, controller = remainder.split("## One document request through the controller", 1)
    controller, expansion = controller.split("## Expansion solutions", 1)
    expansion, runnotes = expansion.split("## Running the expansion probes", 1)
    students = "# Laboratory workbook\n\n" + BOOK_IDENTITY + "The original 23 workbench problems and the closing task are preserved below. Each chapter section then prints the inputs for its default, changed and transfer cases, so its questions can be worked without opening a notebook. The three capstone questions follow the chapter sections. All values are constructed unless a question explicitly says otherwise. Use the separate solutions after attempting a problem.\n\n" + problems.replace("# Mathematical Workbench", "## Original Mathematical Workbench", 1)
    answers = "# Separate workbook solutions\n\n" + BOOK_IDENTITY + "## Original worked solutions\n" + old_solutions + "\n## Original expansion solutions\n" + expansion
    pages = {e["chapter"]: Path(e["notebook"]).stem + ".html" for e in json.loads((ROOT / "chapter-map.json").read_text())}
    for p in sorted((ROOT / "content").glob("ch??.json")):
        n = int(p.stem[2:]); c = json.loads(p.read_text())
        students += f"\n\n## Chapter {n}: {c['question']}\n\n" + inputs_block(n, c, pages[n]) + "\n\nQuestions:\n\n" + "\n\n".join(f"{i+1}. {e['question']}" for i,e in enumerate(c["exercises"]))
        answers += "\n\n" + (ROOT / "solutions" / f"ch{n:02d}.md").read_text().replace("# Chapter", "## Chapter", 1)
    students += "\n\n## Capstone: the document-release controller\n\nThese questions accompany notebook 28. They need no inputs beyond the process described in `data/examples/capstone.json`.\n\n" + "\n\n".join(capstone_questions())
    answers += "\n\n" + (ROOT / "solutions" / "capstone.md").read_text().replace("# Capstone solutions", "## Capstone solutions", 1)
    students += "\n\n## Running and inspecting the original controller\n" + controller + "\n## Running the original expansion probes\n" + runnotes
    (target / "workbook.md").write_text(students)
    (target / "solutions.md").write_text(answers)
    notation = (PROJECT / "Manuscript/front-matter/03-notation-guide.md").read_text()
    (ROOT / "reference-sources").mkdir(exist_ok=True)
    (ROOT / "reference-sources/notation-guide.md").write_text(notation)
    entries = json.loads((ROOT / "chapter-map.json").read_text())
    routes = {entry["chapter"]: "../guide/chapters/" + Path(entry["notebook"]).stem + ".html" for entry in entries}
    notation = re.sub(r"\[([0-9]+)\]\([^)]*\.md\)", lambda m: "[" + m.group(1) + "](" + routes[int(m.group(1))] + ")", notation)
    note = "Chapter links in this companion copy open the corresponding laboratory reading page. The symbols and explanations are retained from the book; its original notation source is preserved in reference-sources/notation-guide.md.\n\n"
    notation = notation.replace("# Notation Guide\n\n", "# Notation Guide\n\n" + BOOK_IDENTITY + note, 1)
    # Prose symbols must match the tables: print the Greek letters as LaTeX, not raw ASCII names.
    notation = notation.replace("`Gamma(A;B)`", "`\\Gamma(A;B)`").replace("`rho_Gamma`", "`\\rho_\\Gamma`")
    (target / "notation-guide.md").write_text(notation)


if __name__ == "__main__":
    orientation(); capstone(); workbook()
    print("Built orientation, capstone, workbook, separate solutions and notation reference.")
