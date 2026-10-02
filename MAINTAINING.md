# Maintaining the laboratory

The supported reader distribution is the complete extracted laboratory folder. Its helpers locate `src/`, `content/` and `lab-manifest.json` together. The ZIP is not a standalone Python wheel; installing a wheel alone is not an accepted distribution path.

Run standard-library verification from the bundle root:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests
```

On Windows, set `PYTHONPATH` to `src` using the shell's environment syntax before running `py -3 -m unittest discover -s tests`.

The executed notebooks and shared computations can be rerun from this complete bundle. After installing notebook dependencies, use:

```bash
.venv/bin/python tools/execute_notebooks.py --receipt reader-output/my-execution.json
```

This runner uses a fresh process and an in-process Jupyter kernel for each notebook. It does not test JupyterLab's browser/server transport. It replaces saved outputs in the notebooks, so make a copy first if you want to preserve the delivery's outputs. The in-process kernel sends `print` output as stream messages with an empty parent header, so the runner accepts unparented messages for the running cell and refuses to save a notebook in which a cell that prints has no captured stream output. The test `test_saved_notebooks_keep_printed_output` checks the saved notebooks for the same defect; set `MAA_NOTEBOOK_DIR` to test a scratch copy. Reports identify the actual interpreter, source hashes, execution status and elapsed time.

The publishing builders `build_materials.py`, `build_extras.py` and `export_pdfs.py` also require the canonical book project, its project state, fonts and verified local MathJax rendering tools. Those authoring inputs are outside the reader ZIP. Readers receive the completed notebooks, PDFs, authored content, mathematical modules and tests; running examples does not require the publishing builders.

Keep chapter content, computational schemas, input examples, notebook explanations and skill references synchronized when changing a method. Preserve canonical notation and source equations. Record mathematical corrections as new receipts rather than replacing historical reviews. Run independent analytical or adverse checks that test the conclusion, then execute affected notebooks from fresh kernels and regenerate reading pages. Regenerate the portable archive and its integrity manifest only after those checks pass, and build the ZIP only through `tools/package_lab.py`, which excludes `.venv`, `.jupyter`, `.local-state` and `reader-output`. The legacy probe fixtures, expected outputs and release console live only under `Companion/` (the paths the printed workbench commands use); do not keep a second copy at the bundle root, and run the test suite, which compares the probes with their expected outputs.

After rebuilding notebooks, rerun `tools/export_reading.py` so the reading pages show the saved printed output, and recopy `tools/run_skill.py` into every skill by running `tools/build_materials.py`.

The master route helper is an inspectable phrase matcher. The assistant skill chooses methods by the question and input contract. Do not interpret a phrase-match score as semantic accuracy or a guarantee that the chosen method applies.
