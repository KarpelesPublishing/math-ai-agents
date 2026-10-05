"""Illustrated reader engine tests against a synthetic two-chapter project.

The fixture in tests/reader_fixture is a tiny invented book ("A Small Book of
Lines"), so these tests show the engine works without any part of this
laboratory. Rendering needs numpy, matplotlib and jinja2: the tests use the
current interpreter when it has them, otherwise the laboratory's .venv, and
skip with a reason when neither is available. The DOM checks need Node.
"""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import types
import unittest

HERE = Path(__file__).resolve().parent
LAB = HERE.parent
ENGINE = LAB / "tools" / "readers" / "engine"
FIXTURE = HERE / "reader_fixture"
HARNESS = ENGINE / "dom_harness.js"


def builder_python():
    """An interpreter with numpy, matplotlib and jinja2, or None."""
    if all(importlib.util.find_spec(m) for m in ("numpy", "matplotlib", "jinja2")):
        return sys.executable
    for candidate in (LAB / ".venv/bin/python", LAB / ".venv/Scripts/python.exe"):
        if candidate.exists():
            probe = subprocess.run([str(candidate), "-c", "import numpy, matplotlib, jinja2"], capture_output=True)
            if probe.returncode == 0:
                return str(candidate)
    return None


def run_builder(python, *args):
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    return subprocess.run([python, str(ENGINE / "build_readers.py"), *args], capture_output=True, text=True, env=env, timeout=600)


def load_engine():
    spec = importlib.util.spec_from_file_location("reader_engine_for_tests", ENGINE / "build_readers.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class EnginePureFunctionTests(unittest.TestCase):
    """Standard-library parts of the engine: no rendering dependencies needed."""

    @classmethod
    def setUpClass(cls):
        cls.engine = load_engine()

    def test_tex_normalization_ignores_whitespace_braces_tags_and_spacing(self):
        n = self.engine.normalize_tex
        self.assertEqual(n(r"\operatorname{EU}(a)=\sum_{y}p(y\mid a)\,u(y)." + "\n" + r"\tag{6.2}"), n(r"\operatorname EU(a) = \sum_y p(y\mid a) u(y)"))
        self.assertNotEqual(n("y = a x + b"), n("y = m x + c"))

    def test_equations_found_in_display_inline_and_backtick_math(self):
        text = (FIXTURE / "text/ch01.md").read_text()
        found = {self.engine.normalize_tex(t) for t in self.engine.text_equations(text)}
        for tex in ("y=ax+b", "a_1 x + b_1 = a_2 x + b_2", "a"):
            self.assertIn(self.engine.normalize_tex(tex), found)

    def test_headings_and_slugs(self):
        heads = self.engine.text_headings("# One\n\n## The cost of declining, measured\n<h3>Inner <em>x</em></h3>")
        self.assertIn("The cost of declining, measured", heads)
        self.assertIn("Inner x", heads)
        self.assertEqual(self.engine.slugify("The cost of declining, measured"), "the-cost-of-declining-measured")

    def test_dash_detection(self):
        self.assertEqual(self.engine.dash_problems("a \u2014 b \u2013 c " + "-" * 2 + " d"), ["em dash", "en dash", "double hyphen"])
        self.assertEqual(self.engine.dash_problems("well-formed - text"), [])

    def test_hand_calculation_pattern(self):
        pattern = self.engine.HAND_CALC
        self.assertTrue(pattern.search("0.85 x 100 + 0.15 x (-400) - 0 = 25.0"))
        self.assertTrue(pattern.search("t = (0 - (-4)) / (1 - (-4)) = 4 / 5 = 0.80"))
        self.assertFalse(pattern.search("The value goes up."))

    def test_svg_cleaning_rounds_coordinates_but_not_text(self):
        raw = '<?xml version="1.0"?><!-- made by a tool --><svg><metadata>x</metadata><path d="M 1.23456 2.5"/><text>0.100</text></svg>'
        clean = self.engine.clean_svg(raw)
        self.assertIn('d="M 1.23 2.5"', clean)
        self.assertIn("<text>0.100</text>", clean)
        self.assertNotIn("metadata", clean)
        self.assertNotIn("<!--", clean)

    def test_forbidden_canonical_path_is_rejected(self):
        project = self.engine.Project(FIXTURE / "reader.config.json")
        project.cfg["canonical_text"]["paths"]["2"] = "text/old/ch02.md"
        with self.assertRaises(self.engine.ContractError):
            project.canonical_text(2)

    def test_engine_contains_nothing_book_specific(self):
        banned = re.compile(r"Mathematics of AI Agents|Karpeles|maa-\d|math_ai_agents|chapter-map|Manuscript|Companion", re.I)
        for path in ENGINE.rglob("*"):
            if path.is_file() and path.suffix in {".py", ".js", ".css", ".j2"}:
                with self.subTest(file=path.name):
                    self.assertIsNone(banned.search(path.read_text(encoding="utf-8")))

    def test_missing_dependency_message_is_clear(self):
        if all(importlib.util.find_spec(m) for m in ("numpy", "matplotlib", "jinja2")):
            self.skipTest("this interpreter has every rendering dependency, so the missing-dependency path cannot be shown here")
        run = subprocess.run([sys.executable, str(ENGINE / "build_readers.py"), "--config", str(FIXTURE / "reader.config.json"), "--check"],
                             capture_output=True, text=True, timeout=60)
        self.assertNotEqual(run.returncode, 0)
        self.assertIn("needs the Python packages numpy, matplotlib and jinja2", run.stdout + run.stderr)


class AltTextAndEquationLayoutTests(unittest.TestCase):
    """Engine 1.1.0: optional per-state figure alt, readable equation alt, equations that fit the column."""

    @classmethod
    def setUpClass(cls):
        cls.engine = load_engine()
        cls.tmp = Path(tempfile.mkdtemp(prefix="reader-alt-"))
        cls.asset = cls.tmp / "eq.svg"
        cls.asset.write_text('<svg xmlns="http://www.w3.org/2000/svg" width="40ex" height="2.5ex" viewBox="0 0 400 25">'
                             '<text x="0" y="20">A</text></svg>', encoding="utf-8")
        config = json.loads((FIXTURE / "reader.config.json").read_text())
        config["project"]["root"] = str(FIXTURE)
        config["theme_css"] = str(FIXTURE / config["theme_css"])
        config["chapter_list"]["inline"][1]["equations"] = [
            {"tex": "A = s^{2}", "asset": str(cls.asset), "number": "2.1", "alt": "A equals s squared"},
            {"tex": r"P = 4\,s \tag{2.2}", "asset": str(cls.asset), "number": "2.2"},
            {"tex": "d = s", "asset": str(cls.asset), "number": "un-numbered display 3"},
        ]
        config["chapter_list"]["equations"] = {"field": "equations", "tex": "tex", "asset": "asset"}
        cls.config = cls.tmp / "reader.config.json"
        cls.config.write_text(json.dumps(config), encoding="utf-8")
        cls.project = cls.engine.Project(cls.config)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def demo(self, *equations):
        return {"id": "C02-D01", "title": "Square", "equations": list(equations)}

    def test_state_alt_falls_back_to_the_interpretation(self):
        self.assertEqual(self.engine.state_alt(self.demo(), " A = 2 x 2 = 4. "), "Figure: Square. A = 2 x 2 = 4.")
        self.assertEqual(self.engine.state_alt(self.demo(), "A = 4.", "   "), "Figure: Square. A = 4.")

    def test_state_alt_uses_the_module_alt_when_given(self):
        alt = self.engine.state_alt(self.demo(), "A = 2 x 2 = 4.", "A square of side 2 shaded inside a 4 by 4 grid.")
        self.assertEqual(alt, "Figure: Square. A square of side 2 shaded inside a 4 by 4 grid.")

    def test_chapter_list_equation_number_and_alt_are_loaded(self):
        eqs = self.project.chapters[2]["equations"]
        self.assertEqual([e["number"] for e in eqs], ["2.1", "2.2", "un-numbered display 3"])
        self.assertEqual([e["alt"] for e in eqs], ["A equals s squared", None, None])

    def test_equation_alt_is_readable_and_the_tex_is_kept(self):
        blocks = self.engine.equation_blocks(self.project, 2, self.demo("A = s^{2}", r"P = 4\,s", "d = s"))
        self.assertEqual([b["kind"] for b in blocks], ["svg", "svg", "svg"])
        self.assertEqual([b["typeset"] for b in blocks], [False, False, False])
        self.assertEqual(blocks[0]["alt"], "Equation (2.1): A equals s squared")
        self.assertEqual(blocks[1]["alt"], "Equation (2.2), written in LaTeX: P = 4 s")
        self.assertEqual(blocks[2]["alt"], "Equation, written in LaTeX: d = s")
        self.assertEqual([b["tex"] for b in blocks], ["A = s^{2}", r"P = 4\,s", "d = s"])
        self.assertEqual((blocks[0]["width"], blocks[0]["height"], blocks[0]["min_width"]), (22.0, 1.38, 13.2))

    def test_equation_alt_cleaning(self):
        alt = self.engine.equation_alt(r"\mathrm{E}\!\left[\frac{m}{k}\right] \;=\; p \tag{9.1}", "9.1")
        self.assertEqual(alt, r"Equation (9.1), written in LaTeX: \mathrm{E}[\frac{m}{k}] = p")

    def test_equation_alt_obeys_the_text_rules(self):
        self.project.chapters[2]["equations"][0]["alt"] = "A " + "-" * 2 + " s squared"
        try:
            module = types.ModuleType("alt_rule_module")
            module.CHAPTER = {"number": 2, "title": "Squares", "subtitle": "x", "summary": "x", "demos": [{}]}
            errors, _ = self.engine.validate_chapter_static(self.project, 2, module)
        finally:
            self.project.chapters[2]["equations"][0]["alt"] = "A equals s squared"
        self.assertTrue(any("equation 1 alt" in e and "double hyphen" in e for e in errors), errors)

    def test_equation_css_lets_images_shrink_to_the_column(self):
        css = (ENGINE / "static" / "reader.css").read_text(encoding="utf-8")
        self.assertRegex(css, r"\.equation\{[^}]*max-width:100%;overflow-x:auto;overflow-y:hidden[^}]*\}")
        self.assertIn(".equation img{display:block;max-width:100%;height:auto;margin:0 auto}", css)
        self.assertIn(".equation mjx-container svg{max-width:100%;height:auto}", css)
        template = (ENGINE / "templates" / "chapter.html.j2").read_text(encoding="utf-8")
        self.assertIn('alt="{{ eq.alt }}" {% if eq.typeset %}data-typeset-tex{% else %}data-tex{% endif %}="{{ eq.tex }}"', template)

    def test_page_carries_equation_alt_tex_and_width(self):
        if importlib.util.find_spec("jinja2") is None:
            self.skipTest(f"jinja2 not installed in {sys.executable}; reader templates cannot be rendered")
        demo = {"id": "C02-D01", "title": "Square", "question": "How big?", "explanation": "Square the side.",
                "equations": ["A = s^{2}", r"P = 4\,s"], "symbols": "s is the side.", "prediction": "Guess.",
                "application": "Scale.", "assumptions": "Constructed.", "check": "Area of side 3?", "answer": "9.",
                "provenance": "Constructed example.", "source_section": "The area of a square",
                "controls": [{"key": "side", "label": "Side", "values": [1, 2], "default": 1}]}
        state = {"image": self.engine.svg_data_uri("<svg></svg>"), "alt": self.engine.state_alt(demo, "A = 1 x 1 = 1."),
                 "metrics": [["Area", "1"]], "interpretation": "A = 1 x 1 = 1.", "selected": "Side: 1"}
        view = [{"key": "side", "label": "Side", "options": [{"index": 0, "text": "1", "selected": True},
                                                              {"index": 1, "text": "2", "selected": False}]}]
        demos = [{**demo, "states": {"0": state}, "default_key": "0", "controls_view": view, "default_state": state,
                  "equation_blocks": self.engine.equation_blocks(self.project, 2, demo)}]
        page = self.engine.render_page(self.project, 2, {"number": 2, "title": "Squares", "subtitle": "x", "summary": "x"}, demos, [])
        self.assertIn('alt="Equation (2.1): A equals s squared" data-tex="A = s^{2}" style="width:22.0em;min-width:13.2em"', page)
        self.assertIn('alt="Equation (2.2), written in LaTeX: P = 4 s" data-tex="P = 4\\,s"', page)
        self.assertNotIn("max-width:none", page)
        self.assertIn('alt="Figure: Square. A = 1 x 1 = 1."', page)

    def test_render_demo_accepts_an_optional_fourth_alt_value(self):
        if not all(importlib.util.find_spec(m) for m in ("numpy", "matplotlib")):
            self.skipTest(f"numpy or matplotlib not installed in {sys.executable}; figures cannot be drawn")
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        def picture(side=1, alt="given"):
            fig, ax = plt.subplots(figsize=(4, 3))
            ax.plot([0, side], [0, side * side])
            ax.set_xlabel("side")
            ax.set_ylabel("area")
            interpretation = f"A = {side} x {side} = {side * side}."
            if alt == "none":
                return fig, {"Area": side * side}, interpretation
            if alt == "empty":
                return fig, {"Area": side * side}, interpretation, " "
            if alt == "dash":
                return fig, {"Area": side * side}, interpretation, "A rising line — steep."
            return fig, {"Area": side * side}, interpretation, f"A line rising from 0 to {side * side}."

        module = types.ModuleType("alt_render_module")
        module.picture = picture
        base = {"id": "C02-D01", "title": "Square", "function": "picture"}
        cases = {
            "given": ("Figure: Square. A line rising from 0 to 4.", None),
            "none": ("Figure: Square. A = 2 x 2 = 4.", None),
            "empty": (None, "fourth return value (alt text) must be a non-empty str"),
            "dash": (None, "alt: contains em dash"),
        }
        for mode, (expected_alt, expected_error) in cases.items():
            with self.subTest(mode=mode):
                demo = {**base, "controls": [{"key": "side", "label": "Side", "values": [2], "default": 2},
                                             {"key": "alt", "label": "Alt", "values": [mode], "default": mode}]}
                errors = []
                states = self.engine.render_demo(self.project, module, demo, errors)
                if expected_error:
                    self.assertTrue(any(expected_error in e for e in errors), errors)
                else:
                    self.assertEqual(errors, [])
                    self.assertEqual(states["0,0"]["alt"], expected_alt)


def stairs_module(engine, project):
    """Fixture chapter 4 (every optional field), loaded fresh; it imports numpy only when drawing."""
    module = engine.load_module(project, 4)
    module.CHAPTER = copy.deepcopy(module.CHAPTER)
    return module


class NarrowScreenAndEquationTests(unittest.TestCase):
    """Engine 1.3.0: legible figures at phone width, and every equation typeset with no script or network."""

    @classmethod
    def setUpClass(cls):
        cls.engine = load_engine()
        cls.project = cls.engine.Project(FIXTURE / "reader.config.json")

    def test_default_budgets_for_legibility(self):
        b = self.project.budgets
        self.assertEqual((b["min_rendered_text_px"], b["min_equation_scale"]), (9, 0.6))

    def test_figure_min_width_keeps_body_text_legible(self):
        svg = ('<svg width="760.08pt" height="320pt" viewBox="0 0 760.08 320"><text style="font: 10.5px \'DejaVu Sans\'">a</text>'
               '<text style="font: 7.35px \'DejaVu Sans\'">b</text><text style="font: 11.5px \'DejaVu Sans\'">c</text></svg>')
        # Body text is 10.5 (7.35 is a subscript below min_font_points 9.5): 760.08 x 9 / 10.5 = 651.5 px.
        self.assertEqual(self.engine.figure_min_width(svg, self.project), 652)
        # Never wider than the natural size (viewBox x 4/3 px), even when the smallest body text is the floor.
        tiny = svg.replace("10.5px", "9.5px").replace("11.5px", "9.5px")
        self.assertEqual(self.engine.figure_min_width(tiny, self.project), 721)
        self.assertEqual(self.engine.figure_min_width('<svg viewBox="0 0 300 100"><path d="M0 0"/></svg>', self.project), 285)
        self.assertIsNone(self.engine.figure_min_width("<svg></svg>", self.project))

    def test_plain_text_form_of_tex(self):
        plain = self.engine.tex_plain
        self.assertEqual(plain(r"1/(\mu-f\lambda)"), "1/(\u03bc-f\u03bb)")
        self.assertEqual(plain(r"A - B e^{-k/\tau}"), "A - B e^(-k/\u03c4)")
        self.assertEqual(plain(r"\frac{a}{b} \le \operatorname{cost}(u) \tag{3}"), "(a)/(b) \u2264 cost(u)")
        for text in (plain(r"\begin{cases}x, & y\\z\end{cases}"), plain(r"\hat h(u)\le c")):
            self.assertNotRegex(text, r"[\\{}]")
            self.assertEqual(self.engine.dash_problems(text), [])

    def test_templates_and_styles_for_narrow_screens(self):
        css = (ENGINE / "static" / "reader.css").read_text(encoding="utf-8")
        template = (ENGINE / "templates" / "chapter.html.j2").read_text(encoding="utf-8")
        script = (ENGINE / "static" / "reader.js").read_text(encoding="utf-8")
        self.assertNotIn("min-width:520px", css)
        self.assertIn(".js .scroll-hint.is-needed{display:block}", css)
        self.assertIn('style="min-width:{{ demo.default_state.min_width }}px"', template)
        self.assertIn('<p class="scroll-hint figure-hint">Scroll sideways for the whole figure', template)
        self.assertIn('<p class="scroll-hint equation-hint">Scroll sideways for the whole equation', template)
        self.assertIn('width:{{ eq.width }}em;min-width:{{ eq.min_width }}em', template)
        self.assertNotIn("\\[{{ eq.tex }}\\]", template)
        self.assertIn("image.setAttribute('style', 'min-width:' + state.min_width + 'px')", script)


class EquationTypesettingTests(unittest.TestCase):
    """Equations without a chapter asset are typeset at build time (needs matplotlib)."""

    @classmethod
    def setUpClass(cls):
        if importlib.util.find_spec("matplotlib") is None:
            raise unittest.SkipTest(f"matplotlib not installed in {sys.executable}; equations cannot be typeset")
        import matplotlib
        matplotlib.use("Agg")
        cls.engine = load_engine()
        cls.project = cls.engine.Project(FIXTURE / "reader.config.json")

    def test_unmatched_equation_becomes_a_path_svg(self):
        svg, width, height = self.engine.tex_svg(r"1/(\mu-f\lambda)")
        self.assertIn("<path", svg)
        self.assertNotIn("<text", svg)
        # Glyph scale factors survive exactly; rounding scale(0.015625) to 0.02 made letters overlap.
        self.assertIn("scale(0.015625)", svg)
        self.assertNotIn("scale(0.02)", svg)
        self.assertTrue(3 < width < 8 and 0.8 < height < 2.5, (width, height))
        self.assertEqual(self.engine.tex_svg(r"1/(\mu-f\lambda)")[0], svg)
        for tex in (r"\hat h(u) \le \operatorname{cost}(u,v)+\hat h(v)", r"A - B e^{-k/\tau} \tag{26.9}", r"(1+\gamma_{\mathrm{cap}})r"):
            self.assertIsNotNone(self.engine.tex_svg(tex), tex)

    def test_blocks_typeset_or_fall_back_to_text(self):
        demo = {"equations": ["y = a x + b", r"1/(\mu-f\lambda)", r"\begin{cases}a, & b\\c\end{cases}"]}
        blocks = self.engine.equation_blocks(self.project, 1, demo)
        self.assertEqual([b["kind"] for b in blocks], ["svg", "svg", "text"])
        self.assertTrue(blocks[1]["src"].startswith("data:image/svg+xml;base64,"))
        self.assertEqual(blocks[1]["alt"], r"Equation, written in LaTeX: 1/(\mu-f\lambda)")
        self.assertEqual(blocks[1]["min_width"], round(blocks[1]["width"] * 0.6, 2))
        self.assertEqual([b.get("typeset") for b in blocks], [True, True, None])
        self.assertEqual(blocks[2]["tex"], demo["equations"][2])
        self.assertNotRegex(blocks[2]["text"], r"[\\{}]")


class OptionalFieldStaticTests(unittest.TestCase):
    """Engine 1.2.0 optional fields: validation needs no rendering dependency."""

    @classmethod
    def setUpClass(cls):
        cls.engine = load_engine()
        cls.project = cls.engine.Project(FIXTURE / "reader.config.json")

    def errors_for(self, mutate, number=4):
        module = stairs_module(self.engine, self.project)
        mutate(module.CHAPTER)
        errors, _ = self.engine.validate_chapter_static(self.project, number, module)
        return "\n".join(errors)

    def test_default_budgets_allow_twelve_states(self):
        b = self.engine.Project(FIXTURE / "reader.config.json").budgets
        self.assertEqual((b["max_states_per_demo"], b["max_values_per_control"], b["max_reader_bytes"], b["max_total_bytes"]),
                         (12, 4, 4_000_000, 55_000_000))

    def test_fixture_chapter_with_every_optional_field_passes(self):
        module = stairs_module(self.engine, self.project)
        errors, _ = self.engine.validate_chapter_static(self.project, 4, module)
        self.assertEqual(errors, [])
        demo = module.CHAPTER["demos"][0]
        self.assertEqual(len(demo["controls"][0]["values"]) * len(demo["controls"][1]["values"]), 12)
        self.assertEqual(self.project.chapters[4]["skill"], "stairs-skill")
        self.assertIsNone(self.project.chapters[2]["skill"])

    def test_state_cap_is_twelve(self):
        def thirteen_plus(c):
            c["demos"][0]["controls"][1]["values"] = [10, 15, 20, 25]
        self.assertIn("16 control combinations; at most 12", self.errors_for(thirteen_plus))

    def test_optional_field_rules_are_reported(self):
        def demo(c):
            return c["demos"][0]
        cases = [
            (lambda c: c.update(ask_skill={"prompt": "Explain.", "extra": "x"}), 'ask_skill must be {"prompt"'),
            (lambda c: c.update(ask_skill={"prompt": "  "}), 'ask_skill must be {"prompt"'),
            (lambda c: c.update(ask_skill={"prompt": "Explain — why."}), "ask_skill.prompt: contains em dash"),
            (lambda c: c.update(ask_skill={"prompt": "Run it in numpy."}), "software dependency 'numpy'"),
            (lambda c: c.update(asked_skill={"prompt": "Explain."}), "CHAPTER has an unknown field 'asked_skill'"),
            (lambda c: demo(c).update(misconceptions={"title": "x", "text": "y"}), "unknown field 'misconceptions'"),
            (lambda c: demo(c).update(misconception={"title": "Once"}), "misconception must be"),
            (lambda c: demo(c).update(misconception={"title": "Once", "text": "Add it " + "-" * 2 + " once."}), "misconception.text: contains double hyphen"),
            (lambda c: demo(c).update(scope_note={"text": "Uneven steps."}), "scope_note must be"),
            (lambda c: demo(c).update(scope_note={"text": "Uneven steps.", "source_section": "Spiral staircases are not covered here"}),
             "is neither a heading nor a phrase"),
            (lambda c: demo(c).update(scope_note={"text": "Uneven steps.", "source_section": "same rise"}), "at least 4 words"),
            (lambda c: demo(c).update(scope_note={"text": "Studies show steps vary.", "source_section": "What this chapter does not settle"}),
             "suggests an empirical claim"),
            (lambda c: demo(c).pop("prediction_feedback"), "go together; missing prediction_feedback"),
            (lambda c: demo(c).update(prediction_options=["Only one"]), "2 to 4 non-empty strings"),
            (lambda c: demo(c).update(prediction_options=["a", "b", "c", "d", "e"]), "2 to 4 non-empty strings"),
            (lambda c: demo(c).update(prediction_options=["a", "a"]), "repeat an option"),
            (lambda c: demo(c).update(prediction_answer=3), "prediction_answer must be the index (0 to 2)"),
            (lambda c: demo(c).update(prediction_answer=True), "prediction_answer must be the index"),
            (lambda c: demo(c).update(prediction_feedback={"correct": "Yes."}), "prediction_feedback must be"),
            (lambda c: demo(c).update(prediction_feedback={"correct": "Yes.", "incorrect": "No – one rise."}), "prediction_feedback.incorrect: contains en dash"),
            (lambda c: demo(c).update(prediction_options=["15 cm", "Python says 30"]), "software dependency 'python'"),
            (lambda c: demo(c).update(stepper="height"), "stepper must name one of the demonstration's control keys"),
        ]
        for i, (mutate, expected) in enumerate(cases):
            with self.subTest(case=i, expected=expected):
                self.assertIn(expected, self.errors_for(mutate))

    def test_scope_note_accepts_a_heading_or_a_long_enough_phrase(self):
        def phrase(c):
            c["demos"][0]["scope_note"]["source_section"] = "every step has the  same rise"
        self.assertEqual(self.errors_for(phrase), "")
        self.assertEqual(self.errors_for(lambda c: None), "")

    def test_scope_note_needs_canonical_text(self):
        project = self.engine.Project(FIXTURE / "reader.config.json")
        project.cfg["canonical_text"]["paths"].pop("4")
        module = stairs_module(self.engine, project)
        errors, _ = self.engine.validate_chapter_static(project, 4, module)
        self.assertTrue(any("scope_note needs the canonical chapter text" in e for e in errors), errors)

    def test_ask_skill_needs_a_skill_name_in_the_chapter_list(self):
        module = types.ModuleType("ask_without_skill")
        module.CHAPTER = {"number": 2, "title": "Squares", "subtitle": "x", "summary": "x", "demos": [{}],
                          "ask_skill": {"prompt": "Explain the area."}}
        errors, _ = self.engine.validate_chapter_static(self.project, 2, module)
        self.assertTrue(any("ask_skill needs the chapter's skill name" in e for e in errors), errors)

    def test_steps_rules(self):
        check = self.engine.check_steps
        cases = [
            (["only one"], "2 to 8 non-empty strings"),
            ([f"step {i}" for i in range(9)], "2 to 8 non-empty strings"),
            (["fine", " "], "2 to 8 non-empty strings"),
            ("not a list", "2 to 8 non-empty strings"),
            (["fine", "x" * 241], "step 2 has 241 characters"),
            (["fine", "h = 2 — 30"], "step 2: contains em dash"),
            (["fine", "h = nan"], "contains NaN or inf"),
        ]
        for steps, expected in cases:
            with self.subTest(expected=expected):
                errors = []
                check(self.project, "C04-D01 [x]", steps, errors)
                self.assertTrue(any(expected in e for e in errors), errors)
        errors = []
        self.assertEqual(check(self.project, "w", [" a = 1 ", "b = 2"], errors), ["a = 1", "b = 2"])
        self.assertEqual(errors, [])

    def test_stepper_status_text_matches_the_script(self):
        control = {"key": "steps", "label": "Number of steps", "values": [1, 2, 3, 4], "default": 2}
        self.assertEqual(self.engine.stepper_status(control, 1), "Step 2 of 4: Number of steps: 2")
        script = (ENGINE / "static" / "reader.js").read_text(encoding="utf-8")
        self.assertIn("'Step ' + (index + 1) + ' of ' + (last + 1) + ': ' + control.label + ': ' + control.values[index]", script)
        view = self.engine.stepper_view({"stepper": "steps", "controls": [control]})
        self.assertEqual(view, {"key": "steps", "label": "Number of steps", "status": "Step 2 of 4: Number of steps: 2",
                                "at_start": False, "at_end": False})
        self.assertIsNone(self.engine.stepper_view({"controls": [control]}))

    def test_payload_adds_keys_only_for_features_in_use(self):
        control = {"key": "steps", "label": "Steps", "values": [1, 2], "default": 1}
        plain = {"id": "C04-D03", "title": "Plain", "controls": [control], "states": {}}
        self.assertEqual(sorted(self.engine.demo_payload(plain)), ["controls", "id", "states", "title"])
        reported = {**plain, "evidence_kind": "source-reported measurements with constructed controls"}
        self.assertEqual(self.engine.demo_payload(reported)["evidence_kind"], reported["evidence_kind"])
        rich = {**plain, "stepper": "steps", "prediction_options": ["a", "b"], "prediction_answer": 1,
                "prediction_feedback": {"correct": " Yes. ", "incorrect": "No."}}
        entry = self.engine.demo_payload(rich)
        self.assertEqual(entry["stepper"], "steps")
        self.assertEqual(entry["predict"], {"answer": 1, "correct": "Yes.", "incorrect": "No."})


class OptionalFieldRenderTests(unittest.TestCase):
    """Per-state worked steps returned by figure functions (needs numpy and matplotlib)."""

    @classmethod
    def setUpClass(cls):
        if not all(importlib.util.find_spec(m) for m in ("numpy", "matplotlib")):
            raise unittest.SkipTest(f"numpy or matplotlib not installed in {sys.executable}; figures cannot be drawn")
        import matplotlib
        matplotlib.use("Agg")
        cls.engine = load_engine()
        cls.project = cls.engine.Project(FIXTURE / "reader.config.json")

    def run_mode(self, mode):
        import matplotlib.pyplot as plt

        def picture(side=1, mode="steps"):
            fig, ax = plt.subplots(figsize=(4, 3))
            ax.plot([0, side], [0, side * side])
            ax.set_xlabel("side")
            ax.set_ylabel("area")
            text = f"A = {side} x {side} = {side * side}."
            steps = [f"s = {side}.", text]
            if mode == "partial" and side == 2:
                return fig, {"Area": side * side}, text
            extras = {"steps": {"steps": steps}, "partial": {"steps": steps}, "both": {"alt": "A rising line.", "steps": steps},
                      "unknown": {"steps": steps, "hint": "x"}, "empty": {}, "badalt": {"alt": " ", "steps": steps},
                      "short": {"steps": steps[:1]}}
            return fig, {"Area": side * side}, text, extras[mode]

        module = types.ModuleType("steps_render_module")
        module.picture = picture
        demo = {"id": "C04-D01", "title": "Square", "function": "picture",
                "controls": [{"key": "side", "label": "Side", "values": [1, 2], "default": 1},
                             {"key": "mode", "label": "Mode", "values": [mode], "default": mode}]}
        errors = []
        states = self.engine.render_demo(self.project, module, demo, errors)
        return states, errors

    def test_steps_are_stored_per_state(self):
        states, errors = self.run_mode("steps")
        self.assertEqual(errors, [])
        self.assertEqual(states["1,0"]["steps"], ["s = 2.", "A = 2 x 2 = 4."])
        self.assertEqual(states["1,0"]["alt"], "Figure: Square. A = 2 x 2 = 4.")
        states, errors = self.run_mode("both")
        self.assertEqual(errors, [])
        self.assertEqual(states["0,0"]["alt"], "Figure: Square. A rising line.")

    def test_step_errors_are_reported(self):
        for mode, expected in (("partial", "1 of 2 states return steps"), ("unknown", "takes only 'alt' and 'steps' (got hint)"),
                               ("empty", "got nothing"), ("badalt", "'alt' must be a non-empty str"),
                               ("short", "2 to 8 non-empty strings")):
            with self.subTest(mode=mode):
                _, errors = self.run_mode(mode)
                self.assertTrue(any(expected in e for e in errors), errors)


class ThemeAndPagerTests(unittest.TestCase):
    """Engine 1.4.0: a neutral base look, an optional project theme (theme_css) and an optional chapter pager."""

    @classmethod
    def setUpClass(cls):
        cls.engine = load_engine()

    def test_base_style_and_templates_are_neutral(self):
        css = (ENGINE / "static" / "reader.css").read_text(encoding="utf-8")
        template = (ENGINE / "templates" / "chapter.html.j2").read_text(encoding="utf-8")
        for marker in (".hero", "gradient", "pill-num", "backdrop-filter", "box-shadow"):
            with self.subTest(marker=marker):
                self.assertNotIn(marker, css)
        for marker in ('class="hero"', 'class="bar"', 'pill-num', 'ch-num'):
            with self.subTest(marker=marker):
                self.assertNotIn(marker, template)
        # Structural rules stay in the base: dark-mode white plate behind equation images, scroll hints, pager layout.
        self.assertIn('.equation{background:#fff;color:#14202b', css)
        self.assertIn(".chapter-pager{", css)
        self.assertIn('<style id="book-theme">{{ theme_css|safe }}</style>', template)
        self.assertIn('<nav class="chapter-pager" aria-label="Previous and next chapter">', template)

    def test_theme_problems(self):
        problems = self.engine.theme_problems
        self.assertEqual(problems(":root{--ink:#123}.demo{border:1px solid}"), [])
        self.assertEqual(problems("select{background:url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg'%3E%3C/svg%3E\")}"), [])
        self.assertEqual(problems("/* see https://example.org for the palette */ a{color:red}"), [])
        for bad, expected in (("@import 'other.css';", "@import"), ("@IMPORT url(x.css);", "@import"),
                              ("body{background:url(https://example.org/a.png)}", "only data: URIs"),
                              ("body{background:url('//cdn.example.org/a.png')}", "only data: URIs"),
                              ("body{background:url(paper.png)}", "only data: URIs"),
                              ("a:after{content:'https://example.org'}", "network address"),
                              ("a{color:red}</style><script>", "</style")):
            with self.subTest(css=bad):
                found = problems(bad)
                self.assertTrue(any(expected in p for p in found), found)

    def config_with(self, **extra):
        tmp = Path(tempfile.mkdtemp(prefix="reader-theme-"))
        self.addCleanup(shutil.rmtree, tmp, True)
        config = json.loads((FIXTURE / "reader.config.json").read_text())
        config["project"]["root"] = str(FIXTURE)
        config["theme_css"] = str(FIXTURE / config["theme_css"])
        config.update(extra)
        path = tmp / "reader.config.json"
        path.write_text(json.dumps(config))
        return tmp, path

    def test_theme_path_is_relative_to_the_configuration_and_must_exist(self):
        project = self.engine.Project(FIXTURE / "reader.config.json")
        self.assertEqual(project.theme_path, (FIXTURE / "theme" / "fixture-theme.css").resolve())
        self.assertIn("Fixture theme", project.theme_css)
        tmp, path = self.config_with(theme_css="missing.css")
        with self.assertRaises(SystemExit) as caught:
            self.engine.Project(path)
        self.assertIn("Theme stylesheet not found", str(caught.exception))
        (tmp / "net.css").write_text("@import url(https://example.org/x.css);")
        _, path2 = self.config_with(theme_css=str(tmp / "net.css"))
        with self.assertRaises(SystemExit) as caught:
            self.engine.Project(path2)
        self.assertIn("cannot be used", str(caught.exception))
        _, path3 = self.config_with(theme_css=None)
        self.assertIsNone(self.engine.Project(path3).theme_css)

    def test_pager_must_be_boolean(self):
        _, path = self.config_with(pager="yes")
        with self.assertRaises(SystemExit) as caught:
            self.engine.Project(path)
        self.assertIn("pager must be true or false", str(caught.exception))

    def test_pager_links_follow_authored_chapters_in_list_order(self):
        project = self.engine.Project(FIXTURE / "reader.config.json")
        one, two, four = project.pager_links(1), project.pager_links(2), project.pager_links(4)
        self.assertIsNone(one["prev"])
        self.assertEqual(one["next"], {"number": 2, "title": "Squares", "href": "../02-squares/reader.html"})
        self.assertEqual((two["prev"]["number"], two["next"]["number"]), (1, 4))  # chapter 3 has no module yet
        self.assertEqual((four["prev"]["href"], four["next"]), ("../02-squares/reader.html", None))
        self.assertIsNone(project.pager_links(3))
        _, path = self.config_with(pager=False)
        self.assertIsNone(self.engine.Project(path).pager_links(2))


class EngineBuildTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.python = builder_python()
        if cls.python is None:
            raise unittest.SkipTest("no interpreter with numpy, matplotlib and jinja2 (laboratory .venv absent)")
        cls.tmp = Path(tempfile.mkdtemp(prefix="reader-engine-"))
        cls.runs = []
        for name in ("first", "second"):
            run = run_builder(cls.python, "--config", str(FIXTURE / "reader.config.json"), "--chapters", "all", "--out", str(cls.tmp / name))
            cls.runs.append(run)

    @classmethod
    def tearDownClass(cls):
        if getattr(cls, "tmp", None):
            shutil.rmtree(cls.tmp, ignore_errors=True)

    def test_build_succeeds_for_both_fixture_chapters(self):
        for run in self.runs:
            self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        for slug in ("01-lines", "02-squares"):
            self.assertTrue((self.tmp / "first" / slug / "reader.html").is_file())
        self.assertFalse((self.tmp / "first" / "03-circles").exists())

    def test_rebuild_is_byte_identical(self):
        for rel in ("index.html", "01-lines/reader.html", "02-squares/reader.html", "04-stairs/reader.html"):
            a = hashlib.sha256((self.tmp / "first" / rel).read_bytes()).hexdigest()
            b = hashlib.sha256((self.tmp / "second" / rel).read_bytes()).hexdigest()
            self.assertEqual(a, b, rel)

    def test_index_links_built_chapters_and_marks_the_rest_in_preparation(self):
        index = (self.tmp / "first" / "index.html").read_text()
        self.assertIn('href="01-lines/reader.html"', index)
        self.assertIn('href="02-squares/reader.html"', index)
        self.assertNotIn("03-circles", index)
        self.assertIn("Circles", index)
        self.assertEqual(index.count("In preparation"), 1)
        self.assertIn("A Small Book of Lines", index)

    def test_optional_links_present_only_when_target_exists(self):
        one = (self.tmp / "first/01-lines/reader.html").read_text()
        two = (self.tmp / "first/02-squares/reader.html").read_text()
        self.assertIn('href="../../notebooks/01-lines.ipynb"', one)
        self.assertNotIn(".ipynb", two)

    def test_branding_comes_from_configuration_only(self):
        page = (self.tmp / "first/01-lines/reader.html").read_text()
        self.assertIn("A Small Book of Lines, practice reader", page)
        self.assertNotIn("Agents", page)

    def test_built_pages_have_no_raw_tex_and_legible_figure_widths(self):
        for slug in ("01-lines", "02-squares", "04-stairs"):
            page = (self.tmp / "first" / slug / "reader.html").read_text()
            with self.subTest(slug=slug):
                self.assertNotIn('class="equation tex"', page)
                self.assertNotRegex(page, r'<p class="equation[^"]*">\\\[')
                self.assertRegex(page, r'<div class="figure-frame"[^>]*><img src="data:image/svg\+xml;base64,[^"]+" alt="[^"]+" style="min-width:\d+px"></div>')
                self.assertNotIn("<script defer src=", page)
        one = (self.tmp / "first" / "01-lines" / "reader.html").read_text()
        self.assertRegex(one, r'<p class="equation"><img src="data:image/svg\+xml;base64,[^"]+" alt="Equation, written in LaTeX: y = a x \+ b" data-typeset-tex="y = a x \+ b" style="width:[\d.]+em;min-width:[\d.]+em"></p>')

    def test_theme_is_inlined_after_the_base_style_on_every_page(self):
        theme = (FIXTURE / "theme" / "fixture-theme.css").read_text(encoding="utf-8")
        for rel in ("index.html", "01-lines/reader.html", "02-squares/reader.html", "04-stairs/reader.html"):
            page = (self.tmp / "first" / rel).read_text()
            with self.subTest(page=rel):
                self.assertEqual(page.count('<style id="book-theme">'), 1)
                self.assertIn('<style id="book-theme">' + theme + "</style>", page)
                self.assertLess(page.index("<style>"), page.index('<style id="book-theme">'))
                self.assertLess(page.index('<style id="book-theme">'), page.index("</head>"))

    def test_pager_links_previous_and_next_authored_chapters(self):
        one = (self.tmp / "first/01-lines/reader.html").read_text()
        two = (self.tmp / "first/02-squares/reader.html").read_text()
        four = (self.tmp / "first/04-stairs/reader.html").read_text()
        self.assertIn('<nav class="chapter-pager" aria-label="Previous and next chapter"><a class="next" href="../02-squares/reader.html">'
                      '<span>Chapter 2 &#8594;</span><b>Squares</b></a></nav>\n</main>', one)
        self.assertIn('<a class="prev" href="../01-lines/reader.html"><span>&#8592; Chapter 1</span><b>Straight Lines</b></a>'
                      '<a class="next" href="../04-stairs/reader.html"><span>Chapter 4 &#8594;</span><b>Stairs</b></a>', two)
        self.assertNotIn('class="next"', four.split('class="chapter-pager"')[1])
        self.assertNotIn("chapter-pager", (self.tmp / "first/index.html").read_text().split("</style>")[-1])

    def test_build_without_theme_or_pager_has_neither(self):
        config = json.loads((FIXTURE / "reader.config.json").read_text())
        config["project"]["root"] = str(FIXTURE)
        del config["theme_css"], config["pager"]
        path = self.tmp / "plain.config.json"
        path.write_text(json.dumps(config))
        run = run_builder(self.python, "--config", str(path), "--chapters", "2", "--out", str(self.tmp / "plain"))
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        page = (self.tmp / "plain/02-squares/reader.html").read_text()
        self.assertNotIn("book-theme", page)
        self.assertNotIn("chapter-pager", page.split("</style>", 1)[1])

    def test_missing_theme_stops_the_build(self):
        config = json.loads((FIXTURE / "reader.config.json").read_text())
        config["project"]["root"] = str(FIXTURE)
        config["theme_css"] = "no-such-theme.css"
        path = self.tmp / "notheme.config.json"
        path.write_text(json.dumps(config))
        run = run_builder(self.python, "--config", str(path), "--check")
        self.assertNotEqual(run.returncode, 0)
        self.assertIn("Theme stylesheet not found", run.stdout + run.stderr)

    def test_dom_harness_checks_the_pager(self):
        if shutil.which("node") is None:
            self.skipTest("Node is not installed; the DOM harness needs it")
        good = self.tmp / "first/02-squares/reader.html"
        ok = subprocess.run(["node", str(HARNESS), str(good)], capture_output=True, text=True, timeout=60)
        self.assertEqual(ok.returncode, 0, ok.stderr)
        self.assertEqual(json.loads(ok.stdout)["reports"][0]["pager_links"], 2)
        page = good.read_text()
        broken = [page.replace('aria-label="Previous and next chapter"', 'aria-label="Pages"', 1),
                  page.replace('<b>Straight Lines</b>', '<b></b>', 1),
                  page.replace('<a class="next" href="../04-stairs/reader.html">', '<a class="next" href="https://example.org/">', 1)]
        for i, text in enumerate(broken):
            with self.subTest(case=i):
                self.assertNotEqual(text, page)
                path = self.tmp / f"broken-pager-{i}.html"
                path.write_text(text)
                run = subprocess.run(["node", str(HARNESS), str(path)], capture_output=True, text=True, timeout=60)
                self.assertNotEqual(run.returncode, 0)

    def test_undefined_value_is_stated_not_replaced(self):
        page = (self.tmp / "first/01-lines/reader.html").read_text()
        self.assertIn("undefined (parallel lines)", page)

    def test_dom_harness_drives_every_state(self):
        if shutil.which("node") is None:
            self.skipTest("Node is not installed; the DOM harness needs it")
        files = [str(self.tmp / "first" / s / "reader.html") for s in ("01-lines", "02-squares")]
        run = subprocess.run(["node", str(HARNESS), *files], capture_output=True, text=True, timeout=120)
        self.assertEqual(run.returncode, 0, run.stderr)
        reports = json.loads(run.stdout)["reports"]
        self.assertEqual([r["states_checked"] for r in reports], [20, 16])
        self.assertTrue(all(r["equations_checked"] > 0 for r in reports), reports)
        self.assertEqual([r["resets_checked"] for r in reports], [4, 4])

    def test_dom_harness_rejects_a_broken_page(self):
        if shutil.which("node") is None:
            self.skipTest("Node is not installed; the DOM harness needs it")
        page = (self.tmp / "first/02-squares/reader.html").read_text()
        broken = [
            page.replace('<label for="C02-D01-side">', '<label for="other">', 1),
            page.replace("aria-live=\"polite\"", "", 1),
            page.replace("select.disabled = false;", "", 1),
            page.replace('class="interpretation" aria-live="polite" aria-atomic="true">A = 2 x 2', 'class="interpretation" aria-live="polite" aria-atomic="true">A = 3 x 2', 1),
            page.replace("image.setAttribute('style', 'min-width:' + state.min_width + 'px');", "image.setAttribute('style', 'min-width:520px');", 1),
            page.replace('<p class="scroll-hint figure-hint">', '<p class="figure-note">', 1),
            re.sub(r'<p class="equation"><img [^>]*></p>', r'<p class="equation">\\[s^{2}\\]</p>', page, count=1),
        ]
        for i, text in enumerate(broken):
            with self.subTest(case=i):
                self.assertNotEqual(text, page)
                path = self.tmp / f"broken-{i}.html"
                path.write_text(text)
                run = subprocess.run(["node", str(HARNESS), str(path)], capture_output=True, text=True, timeout=60)
                self.assertNotEqual(run.returncode, 0)

    def test_optional_features_render_in_the_fixture_reader(self):
        page = (self.tmp / "first/04-stairs/reader.html").read_text()
        self.assertIn('<aside class="ask-skill" aria-labelledby="ask-skill-title"><h2 id="ask-skill-title">Ask the chapter skill</h2>', page)
        self.assertIn('<a href="../../skills/stairs-skill.md">stairs-skill</a>', page)
        self.assertIn('<p class="ask-prompt">Explain why a staircase of n equal steps of rise r climbs n x r.</p>', page)
        self.assertIn('<input type="radio" name="C04-D01-prediction" value="0" autocomplete="off" disabled> 15 cm higher</label>', page)
        self.assertIn('<p class="prediction-feedback" aria-live="polite" aria-atomic="true"></p>', page)
        self.assertIn('<span class="step-status" aria-live="polite" aria-atomic="true" hidden>Step 2 of 4: Number of steps: 2</span>', page)
        self.assertIn('<li>Height h = 2 x 15 = 30 cm.</li>', page)
        self.assertIn('<summary>Common wrong turn: Adding the rise only once</summary>', page)
        self.assertIn('<summary>What this does not settle</summary>', page)
        self.assertIn('Chapter 4 source: "What this chapter does not settle".', page)
        self.assertEqual(page.count('class="predict-options"'), 2)
        self.assertEqual(page.count('class="stepper"'), 1)
        self.assertEqual(page.count('class="steps-panel"'), 2)

    def test_pages_without_optional_fields_carry_no_optional_markup(self):
        for slug in ("01-lines", "02-squares"):
            page = (self.tmp / "first" / slug / "reader.html").read_text()
            for marker in ('class="ask-skill"', 'class="predict-options"', 'class="stepper"', 'class="steps-panel"',
                           'class="misconception"', 'class="scope-note"', '"predict":', '"stepper":', '"steps":'):
                with self.subTest(slug=slug, marker=marker):
                    self.assertNotIn(marker, page)

    def test_dom_harness_drives_every_optional_feature(self):
        if shutil.which("node") is None:
            self.skipTest("Node is not installed; the DOM harness needs it")
        run = subprocess.run(["node", str(HARNESS), str(self.tmp / "first/04-stairs/reader.html")], capture_output=True, text=True, timeout=120)
        self.assertEqual(run.returncode, 0, run.stderr)
        report = json.loads(run.stdout)["reports"][0]
        self.assertEqual((report["states_checked"], report["ask_skill"], report["predictions_checked"], report["steps_checked"],
                          report["stepper_moves"], report["panels_checked"]), (24, 1, 6, 26, 4, 2))

    def test_dom_harness_rejects_broken_optional_features(self):
        if shutil.which("node") is None:
            self.skipTest("Node is not installed; the DOM harness needs it")
        page = (self.tmp / "first/04-stairs/reader.html").read_text()
        broken = [
            page.replace("radio.disabled = false;", "", 1),
            page.replace('<p class="prediction-feedback" aria-live="polite"', '<p class="prediction-feedback"', 1),
            page.replace("'Correct. ' + demo.predict.correct", "'Correct.'", 1),
            page.replace("next.disabled = index >= last;", "next.disabled = false;", 1),
            page.replace("if (index < 0 || index > control.values.length - 1) { return; }",
                         "index = (index + control.values.length) % control.values.length;", 1),
            page.replace("back.hidden = false;", "", 1),
            page.replace("renderSteps(section, state);", "", 1),
            page.replace("<li>Height h = 2 x 15 = 30 cm.</li>", "<li>Height h = 30 cm.</li>", 1),
            page.replace('<h2 id="ask-skill-title">Ask the chapter skill</h2>', '<h2 id="ask-skill-title">Ask</h2>', 1),
            page.replace('<span class="step-status" aria-live="polite"', '<span class="step-status"', 1),
        ]
        for i, text in enumerate(broken):
            with self.subTest(case=i):
                self.assertNotEqual(text, page)
                path = self.tmp / f"broken-opt-{i}.html"
                path.write_text(text)
                run = subprocess.run(["node", str(HARNESS), str(path)], capture_output=True, text=True, timeout=60)
                self.assertNotEqual(run.returncode, 0)

    def test_check_reports_contract_violations(self):
        run = run_builder(self.python, "--config", str(FIXTURE / "reader.bad.config.json"), "--check", "--chapters", "1")
        self.assertEqual(run.returncode, 1)
        for expected in ("contains em dash", "equation not found", "is not a heading", "has 5 values",
                         "is not among its values", "double hyphen", "software dependency 'numpy'", "provenance must say 'constructed'"):
            self.assertIn(expected, run.stdout)

    def test_check_reports_rendering_violations(self):
        run = run_builder(self.python, "--config", str(FIXTURE / "reader.badrender.config.json"), "--check", "--chapters", "1")
        self.assertEqual(run.returncode, 1)
        for expected in ("no y-axis label", "NaN or infinite", "raised ZeroDivisionError", "labels overlap",
                         "minimum is 9.5 pt", "no hand-sized calculation"):
            self.assertIn(expected, run.stdout)

    def test_check_writes_nothing(self):
        out = self.tmp / "check-only"
        run = run_builder(self.python, "--config", str(FIXTURE / "reader.config.json"), "--check", "--out", str(out))
        self.assertEqual(run.returncode, 0, run.stdout)
        self.assertFalse(out.exists())

    def test_state_budget_is_enforced(self):
        config = json.loads((FIXTURE / "reader.config.json").read_text())
        config["budgets"] = {"max_states_per_demo": 4}
        config["project"]["root"] = str(FIXTURE)
        config["theme_css"] = str(FIXTURE / config["theme_css"])
        path = self.tmp / "budget.config.json"
        path.write_text(json.dumps(config))
        run = run_builder(self.python, "--config", str(path), "--check", "--chapters", "1")
        self.assertEqual(run.returncode, 1)
        self.assertIn("6 control combinations; at most 4", run.stdout)

    def test_size_budget_is_enforced(self):
        config = json.loads((FIXTURE / "reader.config.json").read_text())
        config["budgets"] = {"max_reader_bytes": 1000}
        config["project"]["root"] = str(FIXTURE)
        config["theme_css"] = str(FIXTURE / config["theme_css"])
        path = self.tmp / "size.config.json"
        path.write_text(json.dumps(config))
        run = run_builder(self.python, "--config", str(path), "--check", "--chapters", "2")
        self.assertEqual(run.returncode, 1)
        self.assertIn("budget is 1000", run.stdout)


if __name__ == "__main__":
    unittest.main()
