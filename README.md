# The Mathematics of Artificial Intelligence Agents: companion notebooks and skills

*A Readable Guide to Decisions, Planning, Memory, Tools, Learning, and Cooperation*

Companion material for *The Mathematics of Artificial Intelligence Agents* by Jason Karpeles. Each chapter has a
Jupyter notebook that reproduces its calculations and figures, and a skill
that an AI assistant can use to teach the chapter.

Interactive version: https://karpeles.com/companions/math-ai-agents/
About the book: https://karpeles.com/publishing/math-ai-agents

## What is here

- `notebooks/`: one notebook per chapter, already run, so the results show on GitHub; orientation and a document-release capstone are included.
- `skills/`: a master skill for the book and one skill per chapter.
- Numeric chapter folders preserve existing skill links; `maa-` folders hold the same canonical skills used by the installer.
- `src/`, `tools/`, `data/`, and `tests/`: shared calculations, teaching inputs, and checks.
- `content/`, `assets/`, and `solutions/`: explanations, equations, figures and separate worked answers.

Examples identify constructed teaching inputs and source-reported measurements. Their assumptions and limits are stated with each calculation.

## Run the notebooks

You need Python 3.11 or later.

    pip install -r requirements.txt
    jupyter lab

Open any notebook in `notebooks/` and choose Run All. Keep the companion folders together.
For terminal commands, install the local package from the repository root:

    pip install -e .
    python -m math_ai_agents list
    python -m math_ai_agents run --chapter 6 --case example --text
    python -m math_ai_agents run --chapter 6 --input my-inputs.json --output report.json

Copy `data/examples/ch06.json`, or the file for your chapter, to get the input shape, then replace the values. The matching web demonstrations also run from the terminal:

    python -m math_ai_agents demo-list --chapter 6
    python -m math_ai_agents demo --chapter 6 --id C06-D01 --text

Run the checks with `python -m unittest discover -s tests`.

## Use the skills

Start with `skills/math-ai-agents/`, the master skill. It routes a question to a chapter method or demonstration. Each chapter skill names its equations, notebook and input contract.
Keep the repository together and use the same Python environment as the notebooks. Run the supplied installer from the repository root, for example:

    python tools/install_skills.py --target ~/.claude/skills

For Codex, use `--target ~/.codex/skills`. The installer selects the 28 canonical skills without duplicating numeric compatibility folders and records their runtime location. Keep the repository at that location. Existing skill folders are preserved. Run `python tools/install_skills.py --help` for its destination options.

## Copyright

Copyright Jason Karpeles. The code in this repository is released under the MIT License (see `LICENSE`).
