# Start here

This laboratory accompanies *The Mathematics of AI Agents* by Jason Karpeles. It contains a notebook and an assistant skill for every chapter, a master skill, an orientation notebook, a complete document-release example, and a standalone workbook with separate solutions.

The examples use declared local models and fictitious data. They teach calculations and diagnosis; they do not measure a deployed language model or document service. Your own compatible inputs can replace the examples without changing the mathematical method.

## Read without installing anything

1. Extract the complete ZIP. Keep its folders together.
2. Open `guide/index.html` in a browser.
3. Select **Start with one successful calculation**. The expected-utility example should show release preferred at probability 0.8 and abstention preferred at probability 0.6.
4. Choose a chapter, inspect its executed calculation and plots, then attempt its questions before opening the separate solutions.

These are reading pages. Their code and outputs are visible, but changing a page does not execute Python. Equations render from local assets; no account or remote mathematics service is needed. Chapter 18 also has a local browser mock-up, `Companion/release-console.html`, linked from the guide index.

## Run the laboratory on Mac

1. Double-click **Open Laboratory.command** in the extracted folder. A small text menu should appear. If macOS reports that the file is from an unidentified developer or cannot be opened, Control-click the file, choose **Open**, and confirm once; or open Terminal in the extracted folder and run `python3 tools/launch_lab.py`, which shows the same menu. The file is not signed, so this prompt is expected.
2. Choose **Run a chapter example** and enter a number from 1 to 27. A calculated report should appear. This requires Python 3.10 or later but no notebook packages.
3. To edit and run notebook cells, choose **Install notebook tools** once. This creates a dedicated `.venv` inside the extracted folder. It does not modify system Python. The tested notebook stack requires Python 3.11 or later; first setup may need a network connection to obtain dependencies. The package list is `requirements-notebooks.txt` (numpy, matplotlib, nbformat, nbclient, ipykernel and JupyterLab); the launcher installs it for you.
4. Choose **Open Jupyter notebooks**. In the browser, open `notebooks/00-start-here.ipynb`, then select **Run → Run All Cells**. The utility checks should finish without errors. JupyterLab is installed as version 4.x without an exact pin, and the delivery did not test its browser transport, so report any launch problem.

The launcher uses the dedicated environment when one exists. Keep the folder in a stable location after installing skills. You can keep your own input files and reports in a separate `reader-output` folder.

## Windows and Linux

On Windows, double-click **Open Laboratory.bat** with a supported Python installed. If Python is not found, the file opens the reading guide and tells you to install Python. The same menu offers examples, setup and notebooks. You can always read `guide/index.html` without Python.

On Linux, or when using a terminal on any platform, run these commands from the extracted folder:

```bash
python3 tools/launch_lab.py
```

For notebook setup:

```bash
python3 tools/setup_lab.py
```

On Windows, use `py -3` in place of `python3` if that is how Python was installed. Platform-specific launch and installation acceptance is reported in the verification record; successful Python calculations do not establish a tested Windows or Linux graphical launch.

## Use chapter skills with an assistant

1. In the launcher, choose **Install the 28 skills for Codex**.
2. Read the displayed installation directory and confirm the installation. Existing skills with matching names are preserved.
3. Restart the assistant so it can refresh skill discovery.
4. Ask: “Use `$math-ai-agents` to compare verification with retry using this trace.” Supply the trace when the method needs it. For a teaching example, ask explicitly for a constructed example.

The master selects methods by the mathematical question. Chapter skills use the same computations as the notebooks. Each skill has an input contract and worked use cases. A report should contain a result, assumptions, limitations, and an execution receipt when a computation actually ran.

The launcher targets Codex's user skill directory. Other assistants can read the same `SKILL.md` instructions, but their discovery mechanisms may differ. No MCP server, hosted model or API key is required by these calculations. Installing a skill does not supply authorization to publish, change a live system, or contact a reviewer.

For uninstalling, choose **Remove unmodified installed skills**. Skills you changed are retained, and notebook files and reader data are not removed.

## Bring your own inputs

Every chapter has a JSON example in `data/examples/`. Its notebook explains each field. Copy that example to a new file and replace the values. Do not overwrite the original fixture if you want to preserve the worked result.

The notebook's **Apply the method to your inputs** cell reads a local file and computes its report. Change `reader_file` to your copy, then run the cell. A valid JSON input is not evidence that its probabilities are calibrated, its runs representative, or its authority current. Those remain part of your contract.

A chapter helper can also run without Jupyter:

```bash
python3 skills/maa-06-expected-utility/scripts/run.py --input my-choice.json --output reader-output/choice-report.json
```

The master helper lists available methods, suggests routes, executes selected methods, and runs the integrated capstone:

```bash
python3 skills/math-ai-agents/scripts/run.py list
python3 skills/math-ai-agents/scripts/run.py route "Analyze the lost acknowledgement and retry"
python3 skills/math-ai-agents/scripts/run.py capstone --output reader-output/capstone.json
```

Route suggestions are phrase matches. The assistant still needs to check the intended result and the method's assumptions. Composed workflows report methods separately; they do not silently combine incompatible scores into a guarantee.

## Recover from setup problems

| What happened | Action and expected result |
|---|---|
| Python cannot be found | Read the guide immediately; install a supported Python before running calculations. Reopen the launcher afterward. |
| Notebook setup stopped during installation | Check the connection and rerun **Install notebook tools**. Existing notebooks and inputs remain intact. |
| A notebook cannot find the bundle | Open it from the complete extracted folder rather than copying one notebook alone. The bundle manifest, content and source folders must remain together. |
| The assistant says its runtime is missing | Restore the extracted folder to its installed location, or reinstall skills from its new location after reviewing the existing skill copies. The installer preserves collisions rather than overwriting them. |
| An input is rejected | Compare the field names, types, probability sums and units with the chapter's input contract. Quoted Boolean strings are not Boolean values. |
| A result is unavailable or null | Check whether the data identify that quantity. Zero successes, absent pairs or missing costs do not become zero estimates. |
| A changed parameter appears to do nothing | Restart the notebook kernel and run cells in order. Check which experiment input was changed and whether the method actually uses that field. |

## Verification and limits

The delivery's notebook execution receipt identifies the actual interpreter, fresh-kernel method, code cells and hashes. Independent mathematical checks and skill-use reviews are reported separately. This environment's socket restrictions mean normal browser/server notebook launch is a different acceptance scope from the executed notebook cells. Human reader acceptance and any untested host or operating system remain explicitly unperformed.

For details about the notebook format and execution, see the official [Jupyter notebook format](https://nbformat.readthedocs.io/en/latest/format_description.html), [notebook execution documentation](https://nbclient.readthedocs.io/en/latest/client.html), and [JupyterLab installation guide](https://jupyterlab.readthedocs.io/en/stable/getting_started/installation.html).
