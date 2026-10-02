#!/usr/bin/env python3
"""Assemble authored chapter laboratories without rewriting their mathematics."""
from __future__ import annotations
import argparse
import hashlib
import html
import json
from pathlib import Path
import pprint
import re
import shutil
import sys
import uuid

ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT.parent
sys.path.insert(0, str(ROOT / "src"))


def markdown(source):
    return {"cell_type": "markdown", "id": uuid.uuid5(uuid.NAMESPACE_URL, source).hex[:12], "metadata": {}, "source": source}


def code(source):
    return {"cell_type": "code", "id": uuid.uuid5(uuid.NAMESPACE_URL, source).hex[:12], "metadata": {},
            "source": source, "outputs": [], "execution_count": None}


BOOTSTRAP = '''from pathlib import Path
import sys, json
LAB_ROOT = next((p for p in [Path.cwd(), *Path.cwd().parents] if (p / "lab-manifest.json").is_file()), None)
if LAB_ROOT is None:
    raise RuntimeError("Open this notebook from the complete extracted laboratory folder.")
sys.path.insert(0, str(LAB_ROOT / "src"))
from math_ai_agents.core import analyze, report_text
from math_ai_agents.plotting import figure_svg
from IPython.display import SVG, display
'''


def notebook(cells, chapter=None):
    return {"nbformat": 4, "nbformat_minor": 5,
            "metadata": {"kernelspec": {"display_name": "Mathematics of AI Agents", "language": "python", "name": "maa-lab"},
                         "language_info": {"name": "python"}, "lab_chapter": chapter}, "cells": cells}


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")


def canonical_registry():
    import yaml
    state = yaml.safe_load((PROJECT / "PROJECT_STATE.yaml").read_text())
    return {int(p["id"].split("-")[1]): p for p in state["pieces"] if p["id"].startswith("chapter-")}


def formula_callouts(text):
    """Return the "What it does" and "Reading the formula" blockquote paragraphs.

    Robust to blockquotes wrapped over several lines and to quote paragraphs
    separated by a bare ">" line or by a blank line.
    """
    paragraphs, current = [], []
    def flush():
        if current:
            paragraphs.append(" ".join(current))
            current.clear()
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith(">"):
            body = stripped.lstrip(">").strip()
            if body:
                current.append(body)
            else:
                flush()
        else:
            flush()
    flush()
    found = []
    for paragraph in paragraphs:
        match = re.match(r"\*\*(?:What it does|Reading the formula)\.\*\*\s*(.+)$", paragraph, re.S)
        if match:
            found.append(match.group(1).strip())
    return found[:2]


def equations(piece):
    source = (PROJECT / piece["path"]).read_text()
    jobs = json.loads((PROJECT / "tmp/proofs/render-jobs.json").read_text())["math"]
    display_jobs = [job for job in jobs if job["kind"] == "DisplayMath"]
    tag_jobs = {}
    for job in display_jobs:
        match = re.search(r"\\tag\{([^}]+)\}", job["tex"])
        if match: tag_jobs[match.group(1)] = job
    def normalized(tex):
        return re.sub(r"\s+", "", tex)
    found = []
    for index, match in enumerate(re.finditer(r"\\\[(.*?)\\\]", source, re.S), 1):
        tex = match.group(1).strip()
        prior = re.search(r"<!--\s*label:\s*([^\s]+)\s*-->\s*$", source[:match.start()])
        label = prior.group(1) if prior else f"{piece['id']}-display-{index}"
        tag = re.search(r"\\tag\{([^}]+)\}", tex)
        number = tag.group(1) if tag else f"un-numbered display {index}"
        job = tag_jobs.get(number) if tag else next((j for j in display_jobs if normalized(j["tex"]) == normalized(tex)), None)
        if job is None:
            raise ValueError(f"No verified offline equation rendition for {label}, {number}.")
        destination = ROOT / "assets/math" / f"{job['id']}.svg"
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(PROJECT / "tmp/proofs/math" / f"{job['id']}.svg", destination)
        following = source[match.end():].split("\\[")[0]
        callouts = formula_callouts(following)
        found.append({"label": label, "number": number, "tex": tex, "asset": str(destination.relative_to(ROOT)), "explanations": callouts})
    return found


def build_chapter(n, piece):
    from math_ai_agents.core import chapter_content
    c = chapter_content(n)
    title = piece["title"]
    eqs = equations(piece)
    stem = f"{n:02d}-{c['slug']}"
    skill_name = f"maa-{n:02d}-{c['slug']}"
    if len(skill_name) >= 64:
        raise ValueError("Skill name too long: " + skill_name)
    path = ROOT / "notebooks" / (stem + ".ipynb")
    roadmap = "\n".join("- " + v for v in c["roadmap"])
    prerequisites = "\n".join("- " + v for v in c["prerequisites"])
    cells = [markdown(f"# Chapter {n}: {title}\n\n{c['opening']}\n\n**Outcome:** {c['outcome']}\n\n{roadmap}\n\n**Guided route:** Run the worked calculation, inspect its figure, change the stated assumption, and try the transfer case. Read the explanations beside each result before opening the answers.\n\n**Deeper route:** First read the mathematics and canonical equation reference. Audit the input contract, predict the changed result, then inspect the shared chapter implementation and solve the questions independently. Both routes use the same calculations and preserve the equations."),
             markdown("## Technical Requirements\n\nPython 3.11 or later, the complete laboratory folder, and the notebook dependencies listed in `requirements-notebooks.txt` (the launcher's **Install notebook tools** choice installs them; see START-HERE). Standard-library chapter commands also support Python 3.10. No API key, model account or network call is used by this experiment.\n\nPrior knowledge:\n\n" + prerequisites),
             markdown("## The question and its mathematics\n\n" + c["math_explanation"]),
             markdown("## A calculation you can run\n\n" + c["method"] + "\n\nThe next cell finds the bundle and imports the same computation used by the chapter skill. It does not change your system Python."), code(BOOTSTRAP),
             markdown("Set the declared inputs below. These are constructed teaching values, not measurements from a production agent. Change a value only after predicting what it should change."),
             code(f"chapter = {n}\ninputs = {pprint.pformat(c['defaults'], width=90, sort_dicts=False)}\nreport = analyze(chapter, inputs)\n# This input was explicitly taken from the teaching fixture.\nreport['evidence_kind'] = 'constructed teaching example'\nprint(report_text(report))"),
             markdown(c["worked_interpretation"] + "\n\nThe plot below uses the calculated quantities. Read each panel's units before comparing its values."),
             code("display(SVG(figure_svg(report)))"),
             markdown(f"**Figure {n}.L1:** Calculated chapter experiment. Each panel labels its input and output units; interpret it under the assumptions printed in the report."),
             markdown("## Change the assumption\n\n" + c["failure_explanation"]),
             code(f"changed_inputs = {pprint.pformat(c['changed'], width=90, sort_dicts=False)}\nchanged = analyze(chapter, changed_inputs)\nchanged['evidence_kind'] = 'constructed changed-assumption example'\nprint(report_text(changed))\ndisplay(SVG(figure_svg(changed)))"),
             markdown(f"**Figure {n}.L2:** The changed-assumption result. Compare the printed quantities and the stated assumptions with the first run. A different input need not imply a causal effect in a deployed agent."),
             markdown("## Try a new case\n\n" + c["transfer_explanation"]),
             code(f"transfer_inputs = {pprint.pformat(c['transfer'], width=90, sort_dicts=False)}\ntransfer = analyze(chapter, transfer_inputs)\ntransfer['evidence_kind'] = 'constructed transfer example'\nprint(report_text(transfer))"),
             markdown("## Apply the method to your inputs\n\n" + "The example file below has the exact input shape the method accepts. Copy it to a new file, replace its values, then point `reader_file` at your copy. Run the cell again. Supplied inputs retain their stated provenance; the program cannot establish that they are representative observations.\n\n" + "\n".join(f"- **{k}:** {v}" for k,v in c["input_fields"].items())),
             code(f"reader_file = LAB_ROOT / 'data/examples/ch{n:02d}.json'\nreader_inputs = json.loads(reader_file.read_text())\nreader_report = analyze(chapter, reader_inputs)\nprint(report_text(reader_report))"),
             markdown("## Questions\n\n" + "\n\n".join(f"{i+1}. {e['question']}" for i,e in enumerate(c["exercises"])) + f"\n\nAnswers: [separate solutions](../solutions/ch{n:02d}.md). Try the calculation before opening them."),
             markdown("## Summary\n\n" + c["summary"] + "\n\nLimits of this experiment:\n\n" + "\n".join("- " + v for v in c["limitations"]) + f"\n\nThe assistant skill is [`{skill_name}`](../skills/{skill_name}/SKILL.md). It uses this notebook's tested computation and input contract."),
             markdown("## Equations from the chapter\n\nThese are the unchanged display equations and their explanations from the canonical chapter. They are a reference for the experiment, not a claim that every equation is numerically implemented by this one method.")]
    for eq in eqs:
        explanation = "\n\n".join(eq["explanations"])
        cells.append(markdown(f"### Equation {eq['number']}\n\n![Equation {eq['number']}](../{eq['asset']})\n\n{explanation}\n\nLaTeX source, preserved for inspection:\n\n```latex\n{eq['tex']}\n```"))
    write_json(path, notebook(cells, n))
    write_json(ROOT / "data/examples" / f"ch{n:02d}.json", c["transfer"])
    solution = f"# Chapter {n}: separate solutions\n\n" + "\n\n".join(f"## Question {i+1}\n\n{e['question']}\n\n{e['answer']}" for i,e in enumerate(c["exercises"]))
    (ROOT / "solutions" / f"ch{n:02d}.md").write_text(solution + "\n")
    entry = {"chapter": n, "title": title, "source_path": piece["path"],
             "source_sha256": hashlib.sha256((PROJECT / piece["path"]).read_bytes()).hexdigest(),
             "notebook": str(path.relative_to(ROOT)), "skill": skill_name,
             "skill_path": f"skills/{skill_name}/SKILL.md", "method": c["slug"],
             "outcome": c["outcome"], "prerequisites": c["prerequisites"], "routes": c["routes"],
             "input_fields": c["input_fields"], "example_input": f"data/examples/ch{n:02d}.json",
             "equations": eqs}
    build_skill(entry, c)
    return entry


def build_skill(entry, content):
    name, n = entry["skill"], entry["chapter"]
    root = ROOT / "skills" / name
    for folder in ("references", "scripts", "agents"):
        (root / folder).mkdir(parents=True, exist_ok=True)
    description = f"{content['outcome']} Use for {', '.join(content['routes'][:3])}."
    skill = f'''---
name: {name}
description: {json.dumps(description)}
---

# {entry['title']}

{content['question']}

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
'''
    (root / "SKILL.md").write_text(skill)
    method = f"# Method\n\n{content['math_explanation']}\n\n{content['method']}\n\nFor worked interpretation and changed assumptions, read [use cases](use-cases.md).\n\n## Limits\n\n" + "\n".join("- " + x for x in content["limitations"])
    (root / "references/method.md").write_text(method + "\n")
    contract = "# Input contract\n\nPass one complete JSON object. Missing fields are not filled with example values.\n\n" + "\n".join(f"- **{k}:** {v}" for k,v in content["input_fields"].items()) + "\n\n## Valid transfer input\n\n```json\n" + json.dumps(content["transfer"], indent=2) + "\n```\n"
    (root / "references/input-contract.md").write_text(contract)
    cases = f"# Use cases\n\n## Worked example\n\n{content['worked_interpretation']}\n\n## Changed assumption\n\n{content['failure_explanation']}\n\n## New inputs\n\n{content['transfer_explanation']}\n\n## Acceptance invariants\n\n" + "\n".join("- " + s for s in content["acceptance_checks"])
    (root / "references/use-cases.md").write_text(cases + "\n")
    write_json(root / "references/chapter.json", entry)
    shutil.copy2(ROOT / "tools/run_skill.py", root / "scripts/run.py")
    interface = f'''interface:
  display_name: {json.dumps(f"Chapter {n}: {entry['title']}")}
  short_description: {json.dumps(f"Calculate and interpret Chapter {n} agent methods")}
  default_prompt: {json.dumps(f"Use ${name} to analyze my supplied inputs and explain the result.")}
policy:
  allow_implicit_invocation: true
'''
    (root / "agents/openai.yaml").write_text(interface)


def build_master(entries):
    root = ROOT / "skills/math-ai-agents"
    for folder in ("references", "scripts", "agents"):
        (root / folder).mkdir(parents=True, exist_ok=True)
    table = "| Chapter | Mathematical purpose | Skill |\n|---|---|---|\n" + "\n".join(f"| {e['chapter']} | {e['outcome']} | `{e['skill']}` |" for e in entries)
    (root / "references/routes.md").write_text("# Route by purpose\n\n" + table + "\n\nPhrase matches from the executable route helper are suggestions. Read the relevant method before committing to an estimand.\n")
    write_json(root / "references/chapter-map.json", entries)
    shutil.copy2(ROOT / "tools/run_skill.py", root / "scripts/run.py")
    (root / "SKILL.md").write_text('''---
name: math-ai-agents
description: Apply the implemented mathematics of AI agents to decisions, planning, memory, tools, coordination, reliability, security, evaluation and delegation. Route to the relevant chapter method or combine compatible methods from this book companion.
---

# Mathematics of AI Agents

Produce a useful calculation, evidence analysis, teaching example or procedure design using the laboratory's implemented chapter methods. Read [routing map](references/routes.md) to identify the primary mathematical task. Load only the chapter skill and references needed for that task; do not load all 27 skills for a simple question.

Choose by the requested outcome and input contract. A reliability question may concern conditional trajectory success, a lost tool acknowledgement, a selector's errors or measured run outcomes. These need different calculations. A reward score cannot establish authorization, and a marginal success rate cannot identify trajectory dependence.

The helper supplies inspectable route suggestions and executes the selected chapter:

```bash
python3 scripts/run.py route "Compare the tool retry with verification"
python3 scripts/run.py run --chapter 17 --input /path/to/trace.json --output /path/to/report.json
python3 scripts/run.py list
```

Resolve the helper relative to the actual skill path. The bundle runtime is located automatically. Read the selected chapter's input contract; do not substitute fixtures for absent user data. For teaching only, `run --chapter N --case example --text` is an explicitly constructed example.

For combined questions, use [workflow boundaries](references/workflows.md). Four packaged workflows are available: reliability, compute-budget, memory-improvement and safe-release. A supplied workflow input maps each required chapter number to a complete input object. Missing objects stop execution instead of silently inserting teaching cases.

```bash
python3 scripts/run.py workflow reliability --input /path/to/chapter-inputs.json --output /path/to/workflow.json
```

For ambiguous questions, identify the few possible estimands and ask one focused question only when the choice changes the result. The route helper is a phrase matcher; it does not replace semantic judgment. Unsupported requests should receive a precise explanation of the missing method or input, not a fabricated guarantee.

Run available calculations, inspect outputs and invariants, then answer with the decision or report the user requested. Explain which methods ran, input provenance, assumptions, uncertainty and limitations. Check compatibility of task definitions, units, populations, budgets and authority before relating reports. Do not average incompatible scores or imply that independent reports form a causal model.

If execution is unavailable, provide the method or a small hand calculation and mark it not executed. External publication, live-system changes and paid calls require the user's actual authorization; this skill adds none. Sequential execution is sufficient and does not require subagents.
''')
    (root / "references/workflows.md").write_text('''# Composed workflows

| Workflow | Chapters | Purpose |
|---|---|---|
| reliability | 5, 17, 24 | Separate trajectory assumptions, tool-effect uncertainty and measured outcomes. |
| compute-budget | 6, 16, 27 | Combine declared value, candidate allocation and timely human review. |
| memory-improvement | 2, 15, 24, 25 | Compare mechanisms, retrieval choices, evaluation and improvement acceptance. |
| safe-release | 4, 17, 18, 22, 23, 27 | Inspect reachability, effect confirmation, interface targeting, constraints, monitor checks and delegation. |

Without --input these run labeled, separate constructed demonstrations. They do not represent one common empirical population or one joint controller. With --input, all required objects must be supplied. Each chapter's input schema remains authoritative. Check those inputs for the shared contract the user's question requires.

The notebook capstone models one constructed release process and records its actual terminal outcomes. Use it when the user needs an integrated worked example; do not confuse the workflow collection of separate methods with that simulator.

Run the integrated example with `python3 scripts/run.py capstone --output /path/to/capstone.json`. To change its declared process, pass `--input` with a complete object matching `data/examples/capstone.json`. The simulation report contains actual constructed run records, sample traces, matched evaluation and limits; it measures no live model or service.
''')
    (root / "agents/openai.yaml").write_text('''interface:
  display_name: "Mathematics of AI Agents"
  short_description: "Route and apply the book's tested agent mathematics"
  default_prompt: "Use $math-ai-agents to select the right method, run my calculation and explain its limits."
policy:
  allow_implicit_invocation: true
''')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--chapters", help="Comma-separated pilot chapters; omit for complete build.")
    args = parser.parse_args()
    selected = [int(x) for x in args.chapters.split(",")] if args.chapters else list(range(1, 28))
    registry = canonical_registry()
    entries = [build_chapter(n, registry[n]) for n in selected]
    write_json(ROOT / "chapter-map.json", entries)
    write_json(ROOT / "lab-manifest.json", {"lab_version": "1.0.0", "book": "The Mathematics of AI Agents", "chapters": len(entries),
                                          "status": "pilot" if args.chapters else "source-build", "canonical_sources": entries})
    build_master(entries)
    print(f"Built {len(entries)} chapter notebooks and skills.")


if __name__ == "__main__":
    main()
