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
