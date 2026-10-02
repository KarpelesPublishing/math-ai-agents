# The Mathematics of AI Agents: laboratory companion

A working companion by Jason Karpeles: 27 chapter laboratories, 27 chapter skills, one master skill, an orientation, a document-release capstone, and a workbook with separate solutions. The experiments use local declared models and constructed data. They make no measured claim about deployed agents.

Open [the reading guide](guide/index.html) to inspect executed calculations and charts without installing Python. Open [the illustrated readers](readers/index.html) for a chapter-by-chapter picture reader with four interactive demonstrations per chapter. Read [Start here](START-HERE.md) for the launcher, notebooks, skills, reader inputs and recovery instructions. On Mac, double-click **Open Laboratory.command**.

## What is included

- `notebooks/`: 27 chapter notebooks, orientation 00 and capstone 28, with executed outputs.
- `skills/`: the 27 chapter methods and the `math-ai-agents` master router.
- `src/math_ai_agents/`: the shared computation used by notebooks and skills.
- `content/` and `data/examples/`: authored explanations and editable JSON inputs.
- `guide/`: offline reading pages and a field guide. Each chapter page links to its illustrated reader.
- `readers/`: 27 illustrated chapter readers and an index (`readers/index.html`). They need only a browser: no Python, no network, no account. Rebuilt by `tools/readers/build_readers.py`; see `MAINTAINING.md`.
- `workbook/`: questions, separate answers, notation and the preserved original workbench.
- `assets/`: equation SVGs and local mathematics rendering, with its license.
- `tests/`: independent mathematical checks and runtime checks.
- `verification/`: delivery evidence and its explicit acceptance limits.

Notebook execution requires Python 3.11 or later and the notebook packages installed through the launcher. Standard-library chapter helpers support Python 3.10. First notebook setup may need a network connection; ordinary calculations call no remote service and require no API key.

For a terminal example, run `python3 skills/maa-06-expected-utility/scripts/run.py --case example --text`. For reader data, pass `--input your-input.json --output reader-output/report.json`. The master helper supports `list`, `route`, `run`, `workflow` and `capstone`; its skill explains how to choose a method and preserve the evidence boundary.

## Preserved probes

The six previous probes and the release console (`Companion/release-console.html`, also linked from the guide index and the Chapter 18 notebook) remain included. Their original commands run from this bundle root, using `scripts/` and the compatibility fixtures in `Companion/fixtures/`. See [the original probe guide](legacy/README.md). The original two companion ZIPs remain separate editions alongside the new unified package.

The master covers the methods implemented here. Its route helper offers phrase suggestions; an assistant must still check the intended calculation, required inputs, units, assumptions and authority. Installation prepares discoverable skill directories; actual discovery depends on the assistant host.
