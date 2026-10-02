# Illustrated reader contract

This document is for anyone authoring one chapter reader. Read it once, copy the Chapter 6 module as your starting point, and run the check until it is clean. You should not need to ask anyone a question; if something here is ambiguous, follow the Chapter 6 module, which passes every check.

The document has three parts:

- **Part A, engine contract.** What any project must supply to the reader engine: the `CHAPTER` schema, the figure function contract, the configuration file, the checks and the budgets. Nothing in Part A is specific to this book.
- **Part B, this book's choices.** *The Mathematics of AI Agents*: where the chapter text lives, how equations are verified, file names, the commands, and the Chapter 6 worked example.
- **Part C, adopting the engine in a new book.**

A Definition of Done checklist closes the document.

## Layout

```
tools/readers/
  engine/                     project independent; no reference to this book
    build_readers.py          CLI: validator and builder
    readerkit.py              helpers that chapter modules may import
    templates/chapter.html.j2 one reader page
    templates/index.html.j2   the readers index
    static/reader.js          swaps precomputed states (no network)
    static/reader.css
    dom_harness.js            Node DOM harness used by the tests
  reader.config.json          this book's project layer (one file)
  build_readers.py            wrapper: engine CLI with this book's config
  chapters/chNN.py            one authored module per chapter (you write one)
  CONTRACT.md                 this file
readers/                      build output (do not edit by hand)
  index.html
  NN-slug/reader.html
tests/
  test_readers_engine.py      engine tests on a synthetic two-chapter book
  reader_fixture/             that synthetic book
  test_readers_ch06.py        pilot chapter tests (copy for your chapter)
```


# Part A. Engine contract (any project)

## A1. How a reader works

A chapter module defines `CHAPTER`, a dictionary with exactly four demonstrations. Each demonstration names a figure function and lists one to three controls, each with two to four discrete values. The builder calls the figure function once for **every** combination of control values, checks each result, saves each figure as a cleaned SVG, and embeds every state (figure, metrics, interpretation) in one HTML file. A small script swaps the displayed state when a reader changes a select. Without scripts the page still shows every default state, with the selects disabled and a `<noscript>` note. Reading needs no network, no Python and no server.

## A2. The `CHAPTER` schema

All fields are required and must be non-empty unless marked optional.

```python
CHAPTER = {
    "number": 6,                        # int, equal to the module file number (ch06.py)
    "title": "The Price of a Choice",   # chapter title as printed
    "subtitle": "...",                  # one sentence shown under the title
    "summary": "...",                   # two or three sentences introducing the four demonstrations
    "demos": [ DEMO, DEMO, DEMO, DEMO ],# exactly four
}

DEMO = {
    "id": "C06-D01",            # C<chapter two digits>-D<position two digits>, in order D01..D04
    "title": "...",             # short, plain language
    "question": "...?",         # the concrete question the figure answers
    "equations": [r"..."],      # one or more TeX strings that appear in the chapter (see A6)
    "symbols": "...",           # every symbol and unit in the equations and figure, in words
    "prediction": "...",        # what to predict before touching a control
    "explanation": "...",       # two to four sentences: how the equation produces the picture
    "application": "...",       # one honest use of the idea
    "assumptions": "...",       # where the conclusion applies and where it does not
    "check": "...?",            # a transfer question; MUST end with a question mark
    "answer": "...",            # its answer with the arithmetic or reason
    "provenance": "Constructed example: ...",  # must contain the project's provenance word
    "source_section": "The decision rule",     # exact heading text in the chapter file
    "source_anchor": "the-decision-rule",      # slug of source_section (lowercase, hyphens)
    "controls": [CONTROL, ...], # one to three controls
    "function": "three_actions_picture",       # name of a function defined in the module
}

CONTROL = {
    "key": "day_cost",          # lowercase identifier; also a keyword parameter of the function
    "label": "Cost of a day of delay (escalation)",  # visible label, plain words
    "values": [10, 40],         # 2 to 4 distinct values: int, float or str
    "default": 40,              # must be one of values
    "value_labels": [...],      # optional: display text per value (needed for str codes)
}
```

The product of the number of values over a demonstration's controls is its number of states. It must not exceed the state budget (8 by default). Examples: 4 x 2 = 8 is allowed; 3 x 3 = 9 is not.

## A3. The figure function

```python
def name(**controls) -> tuple[matplotlib.figure.Figure, dict, str]:
    ...
    return fig, metrics, interpretation
```

- **Arguments.** One keyword parameter per control key. It receives the raw value from `values` (not the label).
- **Figure.** A Matplotlib figure. Use `readerkit.new_figure()` (one panel 6.6 x 4.3 in, two panels 10.4 x 4.3 in). Do not close it; do not call `plt.show()`. The builder applies the house style (11.5 point text, 10.5 point ticks) before every call.
- **Metrics.** A non-empty dict of label to display value. Values are `str`, `int` or `float`. Pre-format numbers as strings (`readerkit.fmt(x, 2)`) so the number of decimals is deliberate. Never return `None`, `bool`, NaN or infinity: write `undefined (reason)` with `readerkit.undefined("no case is answered")`.
- **Interpretation.** One paragraph about **this** state. It must contain a hand-sized calculation a reader can redo with a pencil, written in ASCII: `0.85 x 100 + 0.15 x 0 - 0 = 85.0`. Use `x` for multiplication, `/` for division and `sqrt(...)` for square roots. Wrap negative numbers in parentheses inside sums (`readerkit.signed`).
- **Determinism.** Same inputs, same output. If you need randomness, fix a seed inside the function and say so in `assumptions`. Prefer exact grids and closed forms.
- **Imports.** `math`, `numpy`, `matplotlib`, `readerkit`, plus any module listed through the configuration's `python_paths`. Do not read files.

The figure, metrics and interpretation for every state are checked:

| Check | Rule |
|-|-|
| Runs | Every combination runs without an exception. |
| Return shape | `(Figure, non-empty dict, non-empty str)`. |
| Axis labels | Every visible axes has a non-empty x label and y label. |
| Finite data | Lines, scatter offsets, bars and images contain no NaN or infinity. Leave undefined points out and say so. |
| Metrics | Display values are finite; no `nan`, `inf` words in metrics or interpretation. |
| Text size | Every visible figure text is at least 9.5 points (house size 10.5 to 12). |
| Labels | Text labels in one axes do not overlap each other or a legend, and stay inside the plotting area. |
| Hand calculation | Interpretation or a metric contains `number op number ... = number`. |
| Text rules | No em dash, en dash, unicode minus or double hyphen; no dependency names; no empirical-claim phrases. |

## A4. Helpers in `readerkit`

| Helper | Use |
|-|-|
| `PALETTE` | `ink`, `teal`, `gold`, `navy`, `terracotta`, `olive`, `grey`, `light`; good contrast on white. |
| `new_figure(ncols=1, width=None, height=4.3)` | Constrained-layout figure with a light grid; returns `(fig, ax)` or `(fig, (ax1, ax2))`. |
| `fmt(x, digits=2)` | Fixed decimals, no `-0`; `None` gives `undefined`; NaN raises. |
| `signed(x, digits)` | Like `fmt`, but negatives in parentheses, for written sums. |
| `undefined(reason)` | `"undefined (reason)"`. |
| `argmax_set(scores, tol)` | All names within `tol` of the maximum, to report ties honestly. |
| `is_tie(a, b, tol)` | Equality within a tolerance. |
| `label_point(ax, x, y, text, color, dx, dy, ha, va)` | Direct label offset in points, 10.5 point text. |

Direct labels beat legends. Put a white box behind a label that sits on a line: `label_point(...).set_bbox({"boxstyle": "round,pad=0.2", "fc": "white", "ec": "none", "alpha": 0.9})`. Keep long prose out of the figure; the interpretation carries it.

## A5. Configuration file

All paths are relative to `project.root`, which is relative to the configuration file. Keys:

| Key | Required | Meaning |
|-|-|-|
| `project.root` | yes | Project root. |
| `branding.book_title`, `branding.series_line` | yes | Book title; the line shown above every chapter title and as the index title. |
| `branding.author`, `lang`, `index_title`, `index_lead`, `index_back_href`, `index_back_label`, `constructed_notice`, `footer_note` | no | Further page text. |
| `chapter_modules` | yes | Directory of `chNN.py` modules. |
| `module_pattern` | no | Default `ch{number:02d}.py`. |
| `output_dir` | no | Default `readers`. |
| `python_paths` | no | Extra import directories for chapter modules (shared project code). |
| `chapter_list` | yes | Either `{"inline": [{"number", "title", "slug", ...}]}` or `{"path", "items_key", "fields": {"number", "title", "slug"}, "slug_mode": "value" or "path_stem", "equations": {"field", "tex", "asset"}}`. Every listed chapter appears on the index; unbuilt ones say "In preparation" and are not linked. |
| `canonical_text` | no | How to find the chapter text: `manifest` (`path`, `base`, `list_key`, `id_key`, `id_format`, `path_key`), and/or `paths` (`{"6": "..."}`, with `base`), and/or `field` (`field_base`) from the chapter list; `forbidden` substrings that must never be used; `required` (default false: a missing file skips the heading check with a note). |
| `links` | no | `index`, `notebook`, `skill`, `guide`: `{"href": pattern, "label": text, "require_target": true}`. Patterns use `{slug}`, `{number}`, `{number02}` and any string field of the chapter list entry. A link whose target file does not exist is omitted with a note, so a project without notebooks or skills still builds. |
| `math.mathjax_script` | no | Relative path to a local MathJax `tex-svg.js`, used only for equations that have no pre-rendered SVG asset. |
| `budgets` | no | `demos_per_chapter` 4, `max_states_per_demo` 8, `min_values_per_control` 2, `max_values_per_control` 4, `max_reader_bytes` 2500000, `max_total_bytes` 45000000, `min_font_points` 9.5. |
| `text_rules` | no | `provenance_must_include`, `forbidden_terms`, `empirical_phrases`. |
| `style` | no | `colors` (cycle) and `rcparams` overrides. |

## A6. Equations

Each string in a demo's `equations` must match, after normalization, either an equation in the canonical chapter text or an equation recorded in the chapter list. Normalization removes whitespace, braces, `\tag{...}`, the spacing commands `\, \; \: \! \quad \qquad`, and trailing `.`, `,` or `;`. Equations searched in the chapter text: display `\[...\]` and `$$...$$`, inline `\(...\)`, `$...$`, and backtick spans. Anything else is rejected, so you cannot paraphrase or invent a formula. Copy the TeX from the chapter, drop the `\tag`, and keep the rest.

Rendering: if the chapter list records an SVG asset for the equation, the SVG is embedded (works with no script at all, `alt` holds the TeX). Otherwise the TeX is placed in `\[...\]` for the local MathJax file named in the configuration; without scripts, readers see the TeX source.

## A7. Commands

```
python engine/build_readers.py --config reader.config.json --chapters N --check   # validate, render in memory, write nothing
python engine/build_readers.py --config reader.config.json --chapters N           # build reader N and refresh the index
python engine/build_readers.py --config reader.config.json --chapters all         # every authored module
python engine/build_readers.py --config reader.config.json --chapters N --out DIR # build elsewhere
```

`--check` exits 1 and lists every problem with its demonstration and state. The builder needs numpy, matplotlib and jinja2 and stops with a clear message if one is missing. Output is byte-reproducible: fixed SVG hash salt, no dates, no creator metadata, sorted JSON.

## A8. Engine tests

`node engine/dom_harness.js READER.html` parses the page, checks the no-script view (default figure, alt text containing the interpretation, metrics, labelled and disabled selects, noscript note, skip link, heading order, `aria-live`), then runs the page's own script and drives every select through every state, comparing image, alt text, metrics, interpretation and selected values, and checks the reset button. It is a controlled harness, not a browser.


# Part B. This book's choices (*The Mathematics of AI Agents*)

## B1. Files and names

- Your module: `tools/readers/chapters/chNN.py`, for example `ch14.py`.
- Output: `readers/NN-slug/reader.html`, where `NN-slug` is the notebook stem in `chapter-map.json` (`06-expected-utility`, `14-transition-model-bound`). You never type it; the configuration derives it.
- Demonstration ids: `C14-D01` to `C14-D04`.
- Your test: `tests/test_readers_chNN.py`, modelled on `tests/test_readers_ch06.py`.
- Do not edit the engine, `reader.config.json`, other chapters, the notebooks, `chapter-map.json`, the guide, README files, manifests or manuscript files. If the engine blocks something legitimate, report it instead of working around it.

## B2. The chapter text

Use only the canonical chapter. The configuration resolves it from `Build/holistic-review-manuscript.manifest.json` (key `chapter-NN`):

- Chapters 1 to 5: `Manuscript/revisions/part-i-v2/01...05-*.md`.
- Chapters 6 to 27: `Manuscript/part-ii` to `Manuscript/part-vi`.
- `Manuscript/chapters/` holds superseded drafts. Never read or cite them; the builder rejects that path.

`source_section` must be the exact text of a `#`, `##` or `###` heading in that file (for example `The cost of declining, measured`), and `source_anchor` its slug (`the-cost-of-declining-measured`).

## B3. Equations for this book

`chapter-map.json` records each chapter's display equations with pre-rendered SVGs in `assets/math`; use those when you can, because they render with no script. Some chapters have only one or two display equations (Chapter 15 has one, Chapter 20 has two). Then use the chapter's inline math (`$...$` or backtick TeX in the chapter file), which the validator also accepts and which renders through the laboratory's local MathJax copy. Two demonstrations may show the same equation. Never write an equation that is not in the chapter.

## B4. Shared calculations

`python_paths` puts `src` on the import path, so your module can and should import the laboratory's own chapter computation, for example `from math_ai_agents.chapters.ch14 import evaluate`, and call it for the numbers you plot. That keeps the reader, the notebook and the chapter skill in agreement. Read `src/math_ai_agents/chapters/chNN.py`, `content/chNN.json` (its `defaults`, `changed` and `transfer` cases) and `notebooks/NN-*.ipynb` before designing demonstrations. Where the lab function does not cover a picture, compute it directly with numpy and, if possible, assert agreement with the lab function on one case (Chapter 6, Demonstration 4 does this for all 100 cases).

The laboratory environment is `Companion/.venv` (numpy 2.4.6, matplotlib 3.11.1, jinja2 3.1.6). **scipy is not installed**; do not import it.

## B5. Honesty rules

- Every example is constructed. `provenance` must contain the word "constructed" and say where the values come from (the book's table, the chapter's worked example, or values defined for the reader).
- Do not state or imply a measurement of any real agent, model, product, team or study. No percentages "from practice", no "typically", no invented citations. The book's values are fine when you name the table or section that holds them.
- When the mathematics is undefined in a state (a tie, division by zero, no case selected), show that state and say so in words. Never substitute 0 or hide the state. Chapter 6 shows an exact tie (89 = 89) and says Equation (6.3) does not break it.
- `assumptions` states the conditions the conclusion needs and one way it can fail.

## B6. Writing style

- Plain language for a reader who knows algebra but not the field. Define every symbol in `symbols` and every term on first use.
- No em dashes, en dashes or double hyphens anywhere, including figure text. Use commas, colons, parentheses or full stops. ASCII hyphen only, as in `break-even`.
- Do not mention software: not Python, numpy, matplotlib, notebook cells or code. Link text to the notebook and skill is supplied by the template.
- Predictions are specific and checkable by changing one control ("Make a wrong answer cost 9 instead of 4. Does coverage go up or down?").
- Hand calculations are short enough to redo with a pencil and use the state's own numbers.
- Check questions transfer the idea to a value not shown by default, and the answer includes its arithmetic.

## B7. Choosing four demonstrations

Pick four distinct ideas from the chapter, in chapter order, each tied to a section heading. Good patterns: a worked table or example from the book with one value varied; a threshold or break-even value; a comparison of shapes or regimes; a failure or boundary case. Two controls of 2 to 4 values, or one control of 3 or 4 values, is usually right. Every control must change the figure (the harness fails a demonstration whose states all show the same image).

## B8. Commands for one chapter

From `Companion/`:

```
.venv/bin/python tools/readers/build_readers.py --chapters 14 --check
.venv/bin/python tools/readers/build_readers.py --chapters 14
node tools/readers/engine/dom_harness.js readers/14-transition-model-bound/reader.html
PYTHONPATH=src python3 -m unittest tests.test_readers_ch14
PYTHONPATH=src python3 -m unittest discover -s tests          # whole lab suite must stay green
```

Then look at your figures. Extract them and open them as images:

```
.venv/bin/python - <<'EOF'
import re, json, base64
page = open('readers/14-transition-model-bound/reader.html').read()
data = json.loads(re.search(r'<script id="reader-data" type="application/json">(.*?)</script>', page, re.S).group(1))
for d in data['demos']:
    for key, s in d['states'].items():
        open(f"/tmp/{d['id']}_{key.replace(',', '-')}.svg", 'wb').write(base64.b64decode(s['image'].split(',', 1)[1]))
EOF
rsvg-convert /tmp/C14-D01_0-0.svg -o /tmp/C14-D01_0-0.png   # or open the SVG in a browser
```

Check every state, not only the default: labels on lines, labels near edges, extreme values, ties.

## B9. The worked example: Chapter 6

`tools/readers/chapters/ch06.py` is the reference module. Its structure:

```python
from math_ai_agents.chapters.ch06 import evaluate        # the lab's own calculation
from readerkit import PALETTE, argmax_set, fmt, label_point, new_figure, signed

EQ_ARGMAX = r"a^{\star}=\arg\max_{a\in\mathcal{A}}\operatorname{EU}(a)"   # Equation (6.3), \tag dropped

def hour_price_picture(hour_cost=5, release_support=0.85):
    actions = release_actions(0, 40, hour_cost=hour_cost, release_support=release_support)[:2]
    scores = lab_scores(actions)                          # evaluate() computes both expected utilities
    release, evidence = scores["Release now"], scores["Request evidence"]
    break_even = 0.97 * 100 - release_support * 100
    fig, ax = new_figure(height=4.1)
    ...                                                   # two lines, break-even line, direct labels
    ax.set_xlabel("Price of one hour of delay (utility points)")
    ax.set_ylabel("Expected utility")
    if math.isclose(evidence, release, abs_tol=1e-9):    # a tie is stated, not hidden
        verdict = "The two actions tie exactly, so Equation (6.3) has two maximizers ..."
    ...
    metrics = {"Release now": fmt(release, 1), "Request evidence": fmt(evidence, 1),
               "Break-even hour price": fmt(break_even, 1), "Chosen": chosen}
    interpretation = (f"Break-even price = 0.97 x 100 - {fmt(release_support, 2)} x 100 = ... = {fmt(break_even, 1)} "
                      f"points per hour. At {fmt(hour_cost, 0)} points, request evidence scores 97.0 - ... {verdict} ...")
    return fig, metrics, interpretation
```

and its demonstration entry:

```python
{
    "id": "C06-D02",
    "title": "Elicit one number: the price of an hour",
    "question": "Between releasing now and requesting evidence, what single number decides the choice?",
    "equations": [EQ_ARGMAX],
    "symbols": "EU(a) is the expected utility of action a. Releasing now succeeds with the chosen support probability; ...",
    "prediction": "If an hour of delay is worth exactly 12 points, which action does Equation (6.3) choose?",
    "explanation": "Requesting evidence scores 97 minus the price of an hour; releasing now scores 100 times its support probability. ...",
    "application": "When a decision depends on a value nobody has written down, compute the threshold at which the decision flips ...",
    "assumptions": "Two actions, utilities on the Table 6.1 scale, and delay priced additively. ... A tie is reported as a tie ...",
    "check": "If releasing now had support probability 0.90, what hour price would make the two actions tie?",
    "answer": "97 - 90 = 7 points. Below 7 requesting evidence wins; above 7 releasing now wins.",
    "provenance": "Constructed example: the book's Table 6.1 values, computed with the laboratory's expected-utility function.",
    "source_section": "Eliciting one number",
    "source_anchor": "eliciting-one-number",
    "controls": [
        {"key": "hour_cost", "label": "Price of an hour of delay", "values": [3, 5, 12, 15], "default": 5},
        {"key": "release_support", "label": "Support probability when releasing now", "values": [0.85, 0.9], "default": 0.85},
    ],
    "function": "hour_price_picture",
}
```

The four Chapter 6 demonstrations:

| Id | Section | Equations | Controls (states) | What changes |
|-|-|-|-|-|
| C06-D01 | The decision rule | (6.2), (6.3) | unsupported utility 0, -100, -400; day cost 10, 40 (6) | Table 6.1 expected utilities; the winner; an exact tie at -100 and 10 |
| C06-D02 | Eliciting one number | (6.3) | hour price 3, 5, 12, 15; release support 0.85, 0.90 (8) | Break-even hour price 12 or 7; a tie at 12 |
| C06-D03 | A worked certainty equivalent | (6.4), (6.2) | curve square root, line, square; win probability 0.5, 0.8 (6) | Certainty equivalent 25, 50, 70.71 (and 64, 80, 89.44) |
| C06-D04 | The cost of declining, measured | (6.3), (6.2) | wrong answer -1, -4, -9; declining -0.5, 0 (6) | Threshold t = (d - w) / (1 - w), coverage, error rate among answered cases |

`tests/test_readers_ch06.py` shows the expected test style: it recomputes every displayed number from the chapter's arithmetic (not from the module), checks the book's own values (85.0, 92.0, 59.5; 25, 80, 57.5; certainty equivalent 25), checks the equations against `chapter-map.json`, the links, the text rules, runs the DOM harness, and rebuilds the chapter to prove the committed reader is current and reproducible.

## B10. Common failure modes

| Symptom from `--check` | Fix |
|-|-|
| `equation not found` | Copy the TeX from the chapter file or `chapter-map.json`; drop only `\tag{...}`. Do not rewrite symbols. |
| `source_section ... is not a heading` | Use the exact heading text, including punctuation and capitals. |
| `source_anchor must be ...` | Use the slug printed in the message. |
| `N control combinations; at most 8` | Remove a value or a control. |
| `no hand-sized calculation` | Add an ASCII sum such as `0.8 x 10 = 8.0` with the state's numbers to the interpretation. |
| `labels overlap` / `extends outside the plotting area` | Move or shorten the label, change `ha`, split into two lines, or widen limits. Test every state: labels move with the data. |
| `text ... is 8.0 pt` | Do not shrink text below 9.5 points; shorten it instead. |
| `metric value is NaN` / `contains NaN or inf` | Detect the undefined case and return `undefined (reason)`. |
| `mentions the software dependency` | Remove words like Python or numpy from reader text. |
| `contains em dash` / `double hyphen` | Rewrite with a comma, colon or parentheses; check f-strings and figure titles too. |
| `provenance must say 'constructed'` | Start provenance with "Constructed example:". |
| Harness: `every state shows the same figure` | A control that changes nothing visible must be removed or must change the figure. |
| Fresh-build test fails | Rebuild your chapter after the last edit; never hand-edit `readers/`. |


# Part C. Adopting the engine in a new book

1. Copy `engine/` unchanged into the new project (for example `tools/readers/engine/`).
2. Write `reader.config.json`: branding, `chapter_modules`, `output_dir`, a `chapter_list` (inline is simplest), and optionally `canonical_text`, `links`, `math`, `python_paths` and `budgets`. Omit `links` entries the project does not have; the reader simply has fewer links.
3. Author `chapters/chNN.py` modules to Part A.
4. Run `python engine/build_readers.py --config reader.config.json --chapters N --check`, then build.
5. Copy `tests/test_readers_engine.py` and `tests/reader_fixture/` to keep the engine tests, and write one hand-check test per chapter.
6. Write the project's own Part B: where its chapter text is, what is forbidden, and which shared code chapter modules may import.

Dependencies: numpy, matplotlib and jinja2 for building; Node only for the DOM harness test. The reference implementation this engine was ported from also used pandoc (equations), nbformat, nbclient and ipykernel (notebook generation); the engine needs none of them because it does not generate notebooks and uses pre-rendered or locally typeset equations.


# Definition of Done (one chapter)

- [ ] `tools/readers/chapters/chNN.py` defines `CHAPTER` with exactly four demonstrations, ids `CNN-D01` to `CNN-D04`, in chapter order.
- [ ] Every equation is copied from the canonical chapter (or `chapter-map.json`) and passes the equation check.
- [ ] Every `source_section` is a real heading in the canonical chapter file (never `Manuscript/chapters/`).
- [ ] Numbers come from the laboratory's chapter function where it covers them.
- [ ] Each control has 2 to 4 values; each demonstration has at most 8 states; every control visibly changes the figure.
- [ ] Every state's interpretation has a hand calculation with that state's numbers.
- [ ] Undefined cases and ties are shown and named, not hidden or replaced.
- [ ] All examples are labelled constructed; no empirical claim is made.
- [ ] No em dashes, en dashes, double hyphens or dependency names anywhere, including figure text.
- [ ] `--check` is clean; the chapter is built; the reader is under 2.5 MB.
- [ ] Every state's figure was looked at: labels legible, no overlaps, nothing clipped.
- [ ] `node tools/readers/engine/dom_harness.js readers/NN-slug/reader.html` passes.
- [ ] `tests/test_readers_chNN.py` recomputes the displayed numbers independently and passes.
- [ ] `PYTHONPATH=src python3 -m unittest discover -s tests` is green.
