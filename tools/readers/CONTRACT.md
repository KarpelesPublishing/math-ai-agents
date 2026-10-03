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
    static/reader.css         neutral base look (structure and accessibility rules only)
    dom_harness.js            Node DOM harness used by the tests
  reader.config.json          this book's project layer (one file)
  build_readers.py            wrapper: engine CLI with this book's config
  chapters/chNN.py            one authored module per chapter (you write one)
  CONTRACT.md                 this file
theme/reader-theme.css        this book's look (theme_css), inlined after the base style
readers/                      build output (do not edit by hand)
  index.html
  NN-slug/reader.html
tests/
  test_readers_engine.py      engine tests on a synthetic book (chapter 4 uses every optional field)
  reader_fixture/             that synthetic book (with a tiny theme and the pager on)
  test_readers_ch06.py        pilot chapter tests (copy for your chapter)
```


# Part A. Engine contract (any project)

## A1. How a reader works

A chapter module defines `CHAPTER`, a dictionary with exactly four demonstrations. Each demonstration names a figure function and lists one to three controls, each with two to four discrete values. The builder calls the figure function once for **every** combination of control values, checks each result, saves each figure as a cleaned SVG, and embeds every state (figure, metrics, interpretation) in one HTML file. A small script swaps the displayed state when a reader changes a select. Without scripts the page still shows every default state, with the selects disabled and a `<noscript>` note. Reading needs no network, no Python and no server.

### A1.1 Narrow screens (engine 1.3.0)

A figure is never shrunk below the width at which its body text stays legible. For every state the builder reads the saved SVG: its `viewBox` width W is in points and its text sizes are in the same units, so text renders at size x (rendered width / W) CSS pixels. Taking the body size B as the smallest declared text size at or above `min_font_points` (sub- and superscripts are smaller by design), the state's `min_width` is ceil(W x `min_rendered_text_px` / B) CSS pixels, capped at the drawing's natural width (W x 4/3). With the defaults (9 px, house tick size 10.5) a two-panel figure 760 points wide gets 652 px and a one-panel figure 486 points wide gets 417 px. The value is written on the figure image (`style="min-width:652px"`) and in the state data, and the script rewrites it on every state change. On a wide screen the figure fills the column as before; on a phone the figure keeps its minimum width inside the focusable `.figure-frame`, which scrolls sideways, and a visible line above the figure, "Scroll sideways for the whole figure", appears only when the frame actually overflows (without scripts it shows on screens up to 760 px). The old fixed rule `.plot img{min-width:520px}` is gone.

Equation images shrink with the column down to `min_equation_scale` (0.6) of their natural width (`style="width:Wem;min-width:0.6Wem"`), then the equation scrolls sideways inside `.equation` and the line "Scroll sideways for the whole equation" appears under the equations of that demonstration. At 360 px wide no reader page scrolls sideways as a whole: only figure frames and wide equations do. (Under engine 1.3.0 the demonstration bar also scrolled; since 1.4.0 the base look wraps it, and a theme decides how it lays out.)

### A1.2 Look: neutral base and project themes (engine 1.4.0)

Structure and skin are separate. The engine's `static/reader.css` is a neutral base: serif text on paper, plain links, bordered controls. It carries every rule that structure, legibility and accessibility depend on: the figure frame and its sideways-scroll hints, the equation shrink and scroll rules, the white plate behind equation images when a page is dark (equation images have dark ink; the plate rule applies under `prefers-color-scheme: dark` unless `data-theme="light"` is set on the root, and under `data-theme="dark"`), the stepper, prediction, panel, steps, ask-skill and pager layouts, focus outlines, the skip link, the narrow-screen rules and print rules. It has no look of its own beyond that: no hero header, gradients, pills or shadows, and no dark palette.

A project gives its readers a look with `theme_css` (A5): one stylesheet whose text the builder inlines as `<style id="book-theme">` right after the base `<style>` in every chapter page and in the index page, so it overrides the base by order alone. A theme only restyles; it never changes content or markup, and the DOM harness never looks at it. To swap a book's look, change the `theme_css` file (or point `theme_css` at another file) and rebuild; nothing else changes. Remove `theme_css` and the readers fall back to the neutral base.

The builder refuses a theme (the build stops with the reason) when the file is missing, uses `@import`, loads any `url(...)` that is not a `data:` URI, names a network address outside a comment, or contains `</style`. Readers stay single files that work offline.

The markup a theme can rely on (stable since 1.4.0): `header` holding `nav.nav` (first link "All chapters"), `p.eyebrow`, `h1`, `p.lead`, an unclassed `p` (the chapter summary), `p.notice`, the optional `aside.ask-skill` (`h2`, `p.ask-skill-name`, `p.ask-prompt`) and `nav.chapter-nav` (links "1. Title"); `main` holding `section.demo` cards (`p.demo-number`, `h2`, `p.question`, `div.formula` with `p.equation` and `p.symbols`, `p.prediction`, `fieldset.predict-options`, `p.prediction-feedback` with `is-correct`/`is-incorrect`, `div.controls` with `div.control`, `button.reset` and `div.stepper`, `figure.plot` with `p.figure-hint`, `div.figure-frame` and `figcaption`, `dl.metrics`, `p.interpretation`, `div.steps-panel`, `div.columns` of `div.note`, `details.misconception`, `details.scope-note`, `details` with `div.answer`, `p.source`), then the optional `nav.chapter-pager`; and `footer`. The index page has `header`, `ol.catalog` of `li.chapter-card` and `footer`.

With `"pager": true` every chapter page ends its `main` with

```
<nav class="chapter-pager" aria-label="Previous and next chapter"><a class="prev" href="../PREV-SLUG/reader.html"><span>&#8592; Chapter N</span><b>Title</b></a><a class="next" href="../NEXT-SLUG/reader.html"><span>Chapter M &#8594;</span><b>Title</b></a></nav>
```

Neighbours are taken in chapter list order (the loaded list, sorted by chapter number) among chapters that have an authored module, so a chapter still in preparation is skipped and a build with the out option or of a subset of chapters gives the same bytes. The first chapter has only `a.next`, the last only `a.prev`.

## A2. The `CHAPTER` schema

All fields are required and must be non-empty unless marked optional.

```python
CHAPTER = {
    "number": 6,                        # int, equal to the module file number (ch06.py)
    "title": "The Price of a Choice",   # chapter title as printed
    "subtitle": "...",                  # one sentence shown under the title
    "summary": "...",                   # two or three sentences introducing the four demonstrations
    "demos": [ DEMO, DEMO, DEMO, DEMO ],# exactly four
    "ask_skill": {"prompt": "..."},     # optional (engine 1.2.0), see A2.1
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
    # optional (engine 1.2.0), see A2.1:
    "misconception": {"title": "...", "text": "..."},
    "scope_note": {"text": "...", "source_section": "..."},
    "prediction_options": ["...", "..."], "prediction_answer": 0,
    "prediction_feedback": {"correct": "...", "incorrect": "..."},
    "stepper": "day_cost",                     # a control key
}

CONTROL = {
    "key": "day_cost",          # lowercase identifier; also a keyword parameter of the function
    "label": "Cost of a day of delay (escalation)",  # visible label, plain words
    "values": [10, 40],         # 2 to 4 distinct values: int, float or str
    "default": 40,              # must be one of values
    "value_labels": [...],      # optional: display text per value (needed for str codes)
}
```

The product of the number of values over a demonstration's controls is its number of states. It must not exceed the state budget (12 by default since engine 1.2.0; it was 8). Examples: 4 x 3 = 12 and 3 x 2 x 2 = 12 are allowed; 4 x 4 = 16 is not. The other limits are unchanged: one to three controls, two to four values each.

Any key not listed here (required or optional) is an error, so a misspelled optional field such as `misconceptions` is caught instead of silently ignored.

### A2.1 Optional fields (engine 1.2.0)

Every optional field may be left out; a chapter without them builds exactly as before. All their text obeys the same text rules as other prose (no em dash, en dash, unicode minus or double hyphen; no dependency names; no empirical-claim phrases).

| Field | Where | Schema | Rendered as |
|-|-|-|-|
| `ask_skill` | `CHAPTER` | `{"prompt": str}` (no other keys) | A callout "Ask the chapter skill" under the chapter introduction: the chapter's skill name (linked to the skill when the configuration's `links.skill` target exists) and the prompt. The skill name is the chapter list's `skill` field (or the field named in `chapter_list.fields.skill`); `ask_skill` on a chapter without one is an error. |
| `misconception` | `DEMO` | `{"title": str, "text": str}` | A closed `<details>` panel, "Common wrong turn: <title>", with the text inside. Use only a wrong turn the chapter itself names. |
| `scope_note` | `DEMO` | `{"text": str, "source_section": str}` | A closed `<details>` panel, "What this does not settle", with the text and `Chapter N source: "<source_section>".` The builder checks `source_section` against the canonical chapter text: it must be a heading (exact, as for the demo's `source_section`) or a phrase of at least 4 words that appears in the text (case, emphasis marks and line breaks ignored). Without canonical text the note is rejected, because its source cannot be confirmed. Take the content from the chapter's own section; never invent a limit. |
| `prediction_options`, `prediction_answer`, `prediction_feedback` | `DEMO` | all three together: a list of 2 to 4 distinct non-empty strings; the int index of the correct option; `{"correct": str, "incorrect": str}` | A radio group "Your prediction" under the existing `prediction` paragraph (which stays the prompt) and an empty feedback line (`aria-live="polite"`). Choosing an option writes `Correct. <correct>` or `Not quite. <incorrect>`. Radios are disabled until the script runs. Without these fields the prediction is the paragraph alone, as before. The prediction must still be checkable by changing a control (B6): the feedback says which control shows the answer. |
| `stepper` | `DEMO` | the `key` of one of the demonstration's controls | Back and Next buttons beside the selects that move that control's select one value down or up (no wrap: Back is disabled at the first value, Next at the last) and a status line, `Step 2 of 4: <label>: <value>`, announced through `aria-live="polite"`. Hidden until the script runs. Reset returns it to the default. |
| `steps` | each state (figure function return, see A3) | list of 2 to 8 non-empty strings, each at most 240 characters | A numbered "Worked steps" panel under the interpretation, replaced on every state change. If any state of a demonstration returns steps, every state must. Steps are computed text: like the interpretation they may not contain `nan` or `inf`. |

## A3. The figure function

```python
def name(**controls) -> tuple[matplotlib.figure.Figure, dict, str]:
    ...
    return fig, metrics, interpretation
    # or, with alt text written for this state's figure (engine 1.1.0 and later):
    return fig, metrics, interpretation, alt
    # or, with alt text and/or worked steps (engine 1.2.0 and later); either key may be left out:
    return fig, metrics, interpretation, {"alt": alt, "steps": ["...", "..."]}
```

- **Arguments.** One keyword parameter per control key. It receives the raw value from `values` (not the label).
- **Figure.** A Matplotlib figure. Use `readerkit.new_figure()` (one panel 6.6 x 4.3 in, two panels 10.4 x 4.3 in). Do not close it; do not call `plt.show()`. The builder applies the house style (11.5 point text, 10.5 point ticks) before every call.
- **Metrics.** A non-empty dict of label to display value. Values are `str`, `int` or `float`. Pre-format numbers as strings (`readerkit.fmt(x, 2)`) so the number of decimals is deliberate. Never return `None`, `bool`, NaN or infinity: write `undefined (reason)` with `readerkit.undefined("no case is answered")`.
- **Interpretation.** One paragraph about **this** state. It must contain a hand-sized calculation a reader can redo with a pencil, written in ASCII: `0.85 x 100 + 0.15 x 0 - 0 = 85.0`. Use `x` for multiplication, `/` for division and `sqrt(...)` for square roots. Wrap negative numbers in parentheses inside sums (`readerkit.signed`).
- **Worked steps (optional).** Give the fourth return value as a dict, `{"alt": str, "steps": [str, ...]}`, with only the keys you need. `steps` is 2 to 8 short strings, each a step of the hand calculation for **this** state ("Rise per step r = 15 cm.", "Height h = 2 x 15 = 30 cm."). Split them from the interpretation's calculation rather than writing new arithmetic; the interpretation still needs its own hand calculation. All states of a demonstration return steps, or none do.
- **Alt text (optional).** A fourth return value, a non-empty `str` (or the `alt` key of the dict form), describes what this state's figure shows for a reader who cannot see it (for example "Two curves; the selected-success curve sits on the dashed blind line at 0.40 for every k."). The image's `alt` becomes `Figure: <demo title>. <alt>`. Without it the `alt` is `Figure: <demo title>. <interpretation>`, as before. Alt text obeys the text rules.
- **Determinism.** Same inputs, same output. If you need randomness, fix a seed inside the function and say so in `assumptions`. Prefer exact grids and closed forms.
- **Imports.** `math`, `numpy`, `matplotlib`, `readerkit`, plus any module listed through the configuration's `python_paths`. Do not read files.

The figure, metrics and interpretation for every state are checked:

| Check | Rule |
|-|-|
| Runs | Every combination runs without an exception. |
| Return shape | `(Figure, non-empty dict, non-empty str)`, or the same with a fourth value: a non-empty `str` (alt text) or a dict with only `alt` (non-empty str) and/or `steps`. |
| Worked steps | 2 to 8 non-empty strings of at most 240 characters, text rules, no `nan`/`inf`; every state or none. |
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
| `chapter_list` | yes | Either `{"inline": [{"number", "title", "slug", ...}]}` or `{"path", "items_key", "fields": {"number", "title", "slug", "skill"}, "slug_mode": "value" or "path_stem", "equations": {"field", "tex", "asset", "number", "alt"}}`. In `equations`, `number` (default key `number`) and `alt` (default key `alt`) are optional fields of each equation entry: the equation's printed number and a spoken form for its alt text. Every listed chapter appears on the index; unbuilt ones say "In preparation" and are not linked. The optional `skill` field (default key `skill`, renamed through `fields.skill`) names the chapter's skill for `ask_skill`. |
| `canonical_text` | no | How to find the chapter text: `manifest` (`path`, `base`, `list_key`, `id_key`, `id_format`, `path_key`), and/or `paths` (`{"6": "..."}`, with `base`), and/or `field` (`field_base`) from the chapter list; `forbidden` substrings that must never be used; `required` (default false: a missing file skips the heading check with a note). |
| `links` | no | `index`, `notebook`, `skill`, `guide`: `{"href": pattern, "label": text, "require_target": true}`. Patterns use `{slug}`, `{number}`, `{number02}` and any string field of the chapter list entry. A link whose target file does not exist is omitted with a note, so a project without notebooks or skills still builds. |
| `math.mathjax_script` | no | Relative path to a local MathJax `tex-svg.js`. Since engine 1.3.0 it is loaded only when an equation could not be typeset at build time (A6) and is shown in its text form; MathJax, if the file is reachable, then replaces that text with typeset math. Readers never depend on it. |
| `budgets` | no | `demos_per_chapter` 4, `max_states_per_demo` 12, `min_values_per_control` 2, `max_values_per_control` 4, `max_reader_bytes` 4000000, `max_total_bytes` 55000000, `min_font_points` 9.5, `min_prediction_options` 2, `max_prediction_options` 4, `min_steps` 2, `max_steps` 8, `max_step_chars` 240, `min_scope_phrase_words` 4, `min_rendered_text_px` 9 and `min_equation_scale` 0.6 (both engine 1.3.0, A1.1). (Before engine 1.2.0 the defaults were 8 states, 2500000 and 45000000 bytes.) |
| `text_rules` | no | `provenance_must_include`, `forbidden_terms`, `empirical_phrases`. |
| `style` | no | `colors` (cycle) and `rcparams` overrides. |
| `theme_css` | no | Path to the project's theme stylesheet, relative to this configuration file (engine 1.4.0, A1.2). Inlined after the base style on every chapter page and the index page. Must exist; no `@import`, no non-`data:` `url(...)`, no network address, no `</style`. Omit it for the neutral base look. |
| `pager` | no | `true` or `false` (default `false`; engine 1.4.0, A1.2). When true, each chapter page ends with previous and next chapter links in chapter list order. |

## A6. Equations

Each string in a demo's `equations` must match, after normalization, either an equation in the canonical chapter text or an equation recorded in the chapter list. Normalization removes whitespace, braces, `\tag{...}`, the spacing commands `\, \; \: \! \quad \qquad`, and trailing `.`, `,` or `;`. Equations searched in the chapter text: display `\[...\]` and `$$...$$`, inline `\(...\)`, `$...$`, and backtick spans. Anything else is rejected, so you cannot paraphrase or invent a formula. Copy the TeX from the chapter, drop the `\tag`, and keep the rest.

Rendering: if the chapter list records an SVG asset for the equation, the SVG is embedded (works with no script at all). Its `alt` is readable text: `Equation (16.3): <alt>` when the chapter list entry has an `alt` (spoken form, checked by the text rules), otherwise `Equation (16.3), written in LaTeX: <TeX>` with `\tag`, spacing commands and `\left`/`\right`/`\big` sizing removed. The number comes from the entry's `number` field and is left out when it is not a plain number such as `16.3`. The exact TeX is kept in the image's `data-tex` attribute, which is what equation tests should read. The image is sized by width (the SVG's `ex` width x 0.55 em) with `max-width:100%` and `height:auto`, so a wide equation shrinks to fit its column, down to `min_equation_scale` of its width, and then scrolls sideways inside its container (A1.1).

An equation with no asset (inline math from the chapter text, for example `1/(\mu-f\lambda)`) is typeset by the builder (engine 1.3.0): Matplotlib's math renderer draws it as an SVG whose glyphs are paths (Computer Modern shapes, ink `#14202b`, transparent background, so it needs no font, no script and no network), sized by width in em like an asset. Before typesetting, `\tag{...}`, `\left`, `\right`, `\big` sizing and `\!` are dropped, and `\le`, `\ge`, `\ne`, `\dfrac`, `\tfrac`, `\text{...}` and `\operatorname*` are mapped to forms the renderer knows. Its alt text is the same LaTeX form as above, and its exact TeX is in the image's `data-typeset-tex` attribute (not `data-tex`, which stays reserved for chapter-list assets, so a chapter test that checks every `data-tex` against the chapter list is unaffected). If the renderer cannot parse the TeX (for example `\begin{cases}`), the equation is shown as a clean text form, `<p class="equation text" data-typeset-tex="...">`, with Greek letters and common relations as characters, `\frac{a}{b}` as `(a)/(b)`, multi-character exponents as `^(...)`, and no backslashes or braces; only then is the configured MathJax file loaded, as an optional upgrade. A reader never shows raw TeX with delimiters. Before engine 1.3.0 such equations were emitted as `\[...\]` for MathJax and appeared as raw TeX whenever the MathJax file was not reachable from the page (for example in any build written to another folder with the builder's out option).

## A7. Commands

```
python engine/build_readers.py --config reader.config.json --chapters N --check   # validate, render in memory, write nothing
python engine/build_readers.py --config reader.config.json --chapters N           # build reader N and refresh the index
python engine/build_readers.py --config reader.config.json --chapters all         # every authored module
python engine/build_readers.py --config reader.config.json --chapters N --out DIR # build elsewhere
```

`--check` exits 1 and lists every problem with its demonstration and state. The builder needs numpy, matplotlib and jinja2 and stops with a clear message if one is missing. Output is byte-reproducible: fixed SVG hash salt, no dates, no creator metadata, sorted JSON.

## A8. Engine tests

`node engine/dom_harness.js READER.html` parses the page, checks the no-script view (default figure, alt text that starts `Figure: <demo title>.` and describes the figure, metrics, labelled and disabled selects, noscript note, skip link, heading order, `aria-live`), then runs the page's own script and drives every select through every state, comparing image, alt text, metrics, interpretation and selected values, and checks the reset button. It is a controlled harness, not a browser.

For the optional features it also checks: the ask-skill callout (heading, labelling, skill name, prompt); prediction radios (legend, labels, index values, disabled before the script, enabled after, the exact `Correct.`/`Not quite.` feedback for every option in an `aria-live` line that starts empty); worked steps (default steps in the HTML, steps for every state or none, the list replaced on every state change); the stepper (hidden native buttons and status before the script; after it, Back to the first value and Next to the last with the figure, steps and status checked at each step, no wrap at either end, disabled ends, reset to the default); and non-empty misconception and scope-note panels. Its report counts `ask_skill`, `predictions_checked`, `steps_checked`, `stepper_moves` and `panels_checked`.

Engine 1.3.0 adds: the figure image carries `style="min-width:Npx"` equal to the state's `min_width` before the script and after every state change; each figure has a "Scroll sideways" hint (`p.scroll-hint.figure-hint`) and sits in a focusable `.figure-frame`; every equation is an image with alt text and `data-tex` or `data-typeset-tex` and a `width`/`min-width` (or `height`) style, or the text form with no backslash or brace. The report counts `equations_checked`. Engine 1.4.0 adds: when a page has `nav.chapter-pager`, it must carry `aria-label="Previous and next chapter"` and one or two links, each `.prev` or `.next`, pointing at `../SLUG/reader.html`, with a `span` naming "Chapter N" and a non-empty `b` title; the report counts `pager_links`. The theme is not checked. Layout itself (whether the hint shows, whether anything overflows) needs a browser: B8 describes the 360 px Chrome check.


# Part B. This book's choices (*The Mathematics of AI Agents*)

## B1. Files and names

- Your module: `tools/readers/chapters/chNN.py`, for example `ch14.py`.
- Output: `readers/NN-slug/reader.html`, where `NN-slug` is the notebook stem in `chapter-map.json` (`06-expected-utility`, `14-transition-model-bound`). You never type it; the configuration derives it.
- Demonstration ids: `C14-D01` to `C14-D04`.
- Your test: `tests/test_readers_chNN.py`, modelled on `tests/test_readers_ch06.py`.
- Do not edit the engine, `reader.config.json`, `theme/reader-theme.css`, other chapters, the notebooks, `chapter-map.json`, the guide, README files, manifests or manuscript files. If the engine blocks something legitimate, report it instead of working around it.

## B2. The chapter text

Use only the canonical chapter. The configuration resolves it from `Build/holistic-review-manuscript.manifest.json` (key `chapter-NN`):

- Chapters 1 to 5: `Manuscript/revisions/part-i-v2/01...05-*.md`.
- Chapters 6 to 27: `Manuscript/part-ii` to `Manuscript/part-vi`.
- `Manuscript/chapters/` holds superseded drafts. Never read or cite them; the builder rejects that path.

`source_section` must be the exact text of a `#`, `##` or `###` heading in that file (for example `The cost of declining, measured`), and `source_anchor` its slug (`the-cost-of-declining-measured`).

## B3. Equations for this book

`chapter-map.json` records each chapter's display equations with pre-rendered SVGs in `assets/math`; use those when you can, because they render with no script. Some chapters have only one or two display equations (Chapter 15 has one, Chapter 20 has two). Then use the chapter's inline math (`$...$` or backtick TeX in the chapter file), which the validator also accepts and which the engine typesets at build time (A6); the laboratory's local MathJax copy is only a fallback for TeX the typesetter cannot parse, and no current chapter needs it. Two demonstrations may show the same equation. Never write an equation that is not in the chapter.

The `chapter-map.json` equation entries carry a `number` (for example `16.3`) but no `alt` field, so equation images in this book use the fallback alt text `Equation (16.3), written in LaTeX: ...`. Chapter tests read the exact TeX from the image's `data-tex` attribute.

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

Then look at the reader at phone width. Headless Chrome's window has a minimum width, so wrap the page in a 360 px iframe (a small local HTML file containing `<iframe src="/absolute/path/reader.html" width="360" height="900">`) and screenshot the wrapper:

```
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --hide-scrollbars \
  --allow-file-access-from-files --virtual-time-budget=6000 --window-size=360,900 \
  --screenshot=/tmp/ch14-360.png file:///tmp/wrap-360.html
```

Expect: no sideways scroll of the page itself; figures at a legible size inside their frame with the "Scroll sideways for the whole figure" line above them; wide equations scrolling with their own hint; the navigation pills wrapping onto two rows. A script in the wrapper can scroll the iframe to a demonstration (`scrollIntoView({behavior: 'instant'})`, since the page uses smooth scrolling) or set a figure frame's `scrollLeft` to see its right panel.

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
| `N control combinations; at most 12` | Remove a value or a control. |
| `unknown field '...'` | Check the spelling against A2 and A2.1. |
| `scope_note source_section ... is neither a heading nor a phrase` | Copy a heading, or at least four consecutive words, from the canonical chapter text. |
| `N of M states return steps` | Return `steps` from every state of the demonstration, or from none. |
| `no hand-sized calculation` | Add an ASCII sum such as `0.8 x 10 = 8.0` with the state's numbers to the interpretation. |
| `labels overlap` / `extends outside the plotting area` | Move or shorten the label, change `ha`, split into two lines, or widen limits. Test every state: labels move with the data. |
| `text ... is 8.0 pt` | Do not shrink text below 9.5 points; shorten it instead. |
| `metric value is NaN` / `contains NaN or inf` | Detect the undefined case and return `undefined (reason)`. |
| `mentions the software dependency` | Remove words like Python or numpy from reader text. |
| `contains em dash` / `double hyphen` | Rewrite with a comma, colon or parentheses; check f-strings and figure titles too. |
| `provenance must say 'constructed'` | Start provenance with "Constructed example:". |
| Harness: `every state shows the same figure` | A control that changes nothing visible must be removed or must change the figure. |
| Fresh-build test fails | Rebuild your chapter after the last edit; never hand-edit `readers/`. |

## B10a. This book's look

`reader.config.json` sets `"theme_css": "../../theme/reader-theme.css"` (that is `Companion/theme/reader-theme.css`) and `"pager": true`. The theme gives the readers the card layout of the reference companion: paper background, serif headings, teal and gold accents, pill navigation, a four-column demonstration grid, one card per demonstration, and a dark palette under `prefers-color-scheme: dark`. It extends the same style to the engine features (stepper buttons, worked steps, prediction choices and feedback, misconception and scope panels, the ask-skill card in the header, scroll hints, white equation plates in dark mode, the pager, and one-column navigation at phone width). Change the look only there; never put look rules in the engine.

## B11. Size budgets for this book

`reader.config.json` sets `max_reader_bytes` to 4000000 and `max_total_bytes` to 55000000 (engine 1.2.0; previously 2500000 and 45000000). Measured on 2026-10-02 from the 27 built readers (engine 1.1.0, at most 8 states per demonstration): 30.7 MB in all, largest reader 2.34 MB (Chapter 11). Projecting every demonstration to 12 states at its own measured average bytes per state gives a largest reader of 3.38 MB (Chapter 21; Chapters 11, 26 and 19 also exceed 2.5 MB) and 48.0 MB for the set. A 12-state demonstration cannot fit in those chapters under 2.5 MB, so the per-reader budget is 4 MB (about 18 percent headroom over 3.38 MB) and the set budget 55 MB (about 15 percent over 48.0 MB). If a chapter still exceeds 4 MB, simplify its heaviest figures (fewer plotted points, fewer panels) rather than raising the budget again.


# Part C. Adopting the engine in a new book

1. Copy `engine/` unchanged into the new project (for example `tools/readers/engine/`).
2. Write `reader.config.json`: branding, `chapter_modules`, `output_dir`, a `chapter_list` (inline is simplest), and optionally `canonical_text`, `links`, `math`, `python_paths`, `budgets`, `theme_css` (the book's look, A1.2) and `pager`. Omit `links` entries the project does not have; the reader simply has fewer links.
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
- [ ] Each control has 2 to 4 values; each demonstration has at most 12 states; every control visibly changes the figure.
- [ ] Optional fields (A2.1), where used, come from the chapter: a `scope_note` from its own "what this does not settle" material, a `misconception` the chapter names, `steps` split from the state's own calculation.
- [ ] Every state's interpretation has a hand calculation with that state's numbers.
- [ ] Undefined cases and ties are shown and named, not hidden or replaced.
- [ ] All examples are labelled constructed; no empirical claim is made.
- [ ] No em dashes, en dashes, double hyphens or dependency names anywhere, including figure text.
- [ ] `--check` is clean; the chapter is built; the reader is under 4 MB (B11).
- [ ] Every state's figure was looked at: labels legible, no overlaps, nothing clipped, including at a 360 px page width (the figure scrolls sideways at a legible size; A1.1).
- [ ] `node tools/readers/engine/dom_harness.js readers/NN-slug/reader.html` passes.
- [ ] `tests/test_readers_chNN.py` recomputes the displayed numbers independently and passes.
- [ ] `PYTHONPATH=src python3 -m unittest discover -s tests` is green.
