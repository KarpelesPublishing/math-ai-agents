# The Mathematics of AI Agents: companion notebooks and skills

Companion material for *The Mathematics of AI Agents* by Jason Karpeles. Each chapter has a
Jupyter notebook that reproduces its calculations and figures, and a skill
that an AI assistant can use to teach the chapter.

Interactive version: https://karpeles.com/companions/math-ai-agents/
About the book: https://karpeles.com/publishing/math-ai-agents

## What is here

- `notebooks/`: one notebook per chapter, already run, so the results show on GitHub. `00-start-here.ipynb` is a short orientation and `28-document-release-capstone.ipynb` combines the chapters in one constructed release process.
- `skills/`: a master skill for the book (`skills/math-ai-agents/`) and one skill per chapter.
- `src/math_ai_agents/`: the shared computation used by the notebooks and skills.
- `content/` and `data/examples/`: chapter explanations and editable JSON inputs, one example file per chapter.
- `solutions/`: answers to the questions at the end of each notebook.
- `assets/math/`: the chapter equations as images, shown in the notebooks.
- `tests/`: independent checks of each chapter's mathematics.

The experiments use declared models and constructed data. They make no measured claim about deployed agents.

## Run the notebooks

You need Python 3.11 or later.

    pip install -r requirements.txt
    jupyter lab

Run the install command from the top folder of the repository: it also installs the `math_ai_agents` package from `src/`. Open any notebook in `notebooks/` and choose Run All.

To run a chapter's calculation without Jupyter, or on your own inputs:

    python -m math_ai_agents list
    python -m math_ai_agents run --chapter 6 --case example --text
    python -m math_ai_agents run --chapter 6 --input my-inputs.json --output report.json

Copy `data/examples/ch06.json` (or the file for your chapter) to get the exact input shape, then replace the values. To run the checks: `python -m unittest discover -s tests`.

## Use the skills

Each folder in `skills/` is a skill. Copy a folder into `~/.claude/skills/` (or your agent's skills folder), for example:

    cp -r skills/math-ai-agents ~/.claude/skills/math-ai-agents
    cp -r skills/06-expected-utility ~/.claude/skills/maa-06-expected-utility

Start with the master skill: it routes a question to the right chapter. The skills run their calculations with the `math_ai_agents` package, so keep a clone of this repository installed as above.

## Copyright

Copyright Jason Karpeles. The code in this repository is released under the MIT License (see `LICENSE`).
