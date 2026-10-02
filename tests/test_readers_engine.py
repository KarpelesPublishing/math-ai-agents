"""Illustrated reader engine tests against a synthetic two-chapter project.

The fixture in tests/reader_fixture is a tiny invented book ("A Small Book of
Lines"), so these tests show the engine works without any part of this
laboratory. Rendering needs numpy, matplotlib and jinja2: the tests use the
current interpreter when it has them, otherwise the laboratory's .venv, and
skip with a reason when neither is available. The DOM checks need Node.
"""
from __future__ import annotations

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
        self.assertEqual(blocks[0]["alt"], "Equation (2.1): A equals s squared")
        self.assertEqual(blocks[1]["alt"], "Equation (2.2), written in LaTeX: P = 4 s")
        self.assertEqual(blocks[2]["alt"], "Equation, written in LaTeX: d = s")
        self.assertEqual([b["tex"] for b in blocks], ["A = s^{2}", r"P = 4\,s", "d = s"])
        self.assertEqual((blocks[0]["width"], blocks[0]["height"]), (22.0, 1.38))

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
        self.assertIn(".equation{margin:6px 0 10px;max-width:100%;overflow-x:auto;overflow-y:hidden}", css)
        self.assertIn(".equation img{display:block;max-width:100%;height:auto;margin:0 auto}", css)
        self.assertIn(".equation mjx-container svg{max-width:100%;height:auto}", css)
        template = (ENGINE / "templates" / "chapter.html.j2").read_text(encoding="utf-8")
        self.assertIn('alt="{{ eq.alt }}" data-tex="{{ eq.tex }}"', template)

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
        self.assertIn('alt="Equation (2.1): A equals s squared" data-tex="A = s^{2}" style="width:22.0em"', page)
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
        for rel in ("index.html", "01-lines/reader.html", "02-squares/reader.html"):
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
        ]
        for i, text in enumerate(broken):
            with self.subTest(case=i):
                self.assertNotEqual(text, page)
                path = self.tmp / f"broken-{i}.html"
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
        path = self.tmp / "budget.config.json"
        path.write_text(json.dumps(config))
        run = run_builder(self.python, "--config", str(path), "--check", "--chapters", "1")
        self.assertEqual(run.returncode, 1)
        self.assertIn("6 control combinations; at most 4", run.stdout)

    def test_size_budget_is_enforced(self):
        config = json.loads((FIXTURE / "reader.config.json").read_text())
        config["budgets"] = {"max_reader_bytes": 1000}
        config["project"]["root"] = str(FIXTURE)
        path = self.tmp / "size.config.json"
        path.write_text(json.dumps(config))
        run = run_builder(self.python, "--config", str(path), "--check", "--chapters", "2")
        self.assertEqual(run.returncode, 1)
        self.assertIn("budget is 1000", run.stdout)


if __name__ == "__main__":
    unittest.main()
