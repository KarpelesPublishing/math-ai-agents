"""Chapter 5 laboratory reader: independent hand checks of the built page.

Every expected number is recomputed here from the chapter's own arithmetic
(the six-assembly experiment, the two-state composite kernel, the binary
entropy of the tool's report, the product of per-step probabilities), not
read back from the module that produced the page. The test builds the page
into a temporary directory, so it never touches the shared readers folder;
if a committed reader exists it also checks that it is current.
"""
from __future__ import annotations

import hashlib
import html
import importlib.util
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest

from math_ai_agents.chapters.ch05 import evaluate

HERE = Path(__file__).resolve().parent
LAB = HERE.parent
SLUG = "05-composite-kernel"
COMMITTED = LAB / "readers" / SLUG / "reader.html"
WRAPPER = LAB / "tools" / "readers" / "build_readers.py"
HARNESS = LAB / "tools" / "readers" / "engine" / "dom_harness.js"


def _engine_helpers():
    spec = importlib.util.spec_from_file_location("reader_engine_tests", HERE / "test_readers_engine.py")
    helpers = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helpers)
    return helpers


def payload(text):
    match = re.search(r'<script id="reader-data" type="application/json">(.*?)</script>', text, re.S)
    return json.loads(match.group(1))


def metrics(state):
    return dict(state["metrics"])


def f3(x):
    return f"{x:.3f}"


# Control values in the order the chapter module declares them (the page stores display labels).
D1_REQUEST = [0.2, 0.4, 0.6, 0.8]
D1_REJECTION = ["stop", "blind"]
D2_TOOL = ["default", "changed"]
D2_STEPS = [1, 2, 3, 30]
D3_ACCURACY = [0.5, 0.75, 0.9, 1.0]
D3_REACHES = ["stops", "reaches"]
D4_P = [0.9, 0.95, 0.99, 0.999]
D4_HANDLING = ["none", "retry"]

CHOOSER = [[0.8, 0.2], [0.3, 0.7]]
TOOL = {"default": [[0.9, 0.1], [0.2, 0.8]], "changed": [[0.6, 0.4], [0.1, 0.9]]}


class Chapter5ReaderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.helpers = _engine_helpers()
        cls.python = cls.helpers.builder_python()
        if cls.python is None:
            raise unittest.SkipTest("no interpreter with numpy, matplotlib and jinja2 (laboratory .venv absent)")
        cls.tmp = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.tmp.cleanup)
        run = subprocess.run([cls.python, str(WRAPPER), "--chapters", "5", "--out", cls.tmp.name], capture_output=True,
                             text=True, timeout=600, env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
        assert run.returncode == 0, run.stdout + run.stderr
        cls.reader = Path(cls.tmp.name) / SLUG / "reader.html"
        cls.page = cls.reader.read_text(encoding="utf-8")
        cls.data = payload(cls.page)
        cls.demos = {d["id"]: d for d in cls.data["demos"]}

    def key_for(self, *idx):
        return ",".join(str(i) for i in idx)

    def state(self, demo_id, *idx):
        return self.demos[demo_id]["states"][self.key_for(*idx)]

    # Structure

    def test_four_demonstrations_with_state_budget(self):
        self.assertEqual(list(self.demos), ["C05-D01", "C05-D02", "C05-D03", "C05-D04"])
        self.assertEqual([len(d["states"]) for d in self.data["demos"]], [8, 8, 8, 8])
        for d in self.data["demos"]:
            self.assertLessEqual(len(d["states"]), 8)
        self.assertEqual([[len(c["values"]) for c in d["controls"]] for d in self.data["demos"]],
                         [[4, 2], [2, 4], [4, 2], [4, 2]])

    def test_size_budget(self):
        self.assertLess(self.reader.stat().st_size, 2_500_000)

    # Demonstration 1: six assemblies

    def test_d01_six_assemblies_by_hand(self):
        keys = ["Model only", "Memory, no reader", "Tool, no recurrence", "Recurrence, blind",
                "Connected, granted", "Connected, denied"]
        for i, r in enumerate(D1_REQUEST):
            for j, policy in enumerate(D1_REJECTION):
                m = metrics(self.state("C05-D01", i, j))
                blind = (1 - r) / 2                      # answer0 and answer1 each (1 - r) / 2; either is right half the time
                row4 = blind + r * blind                 # second blind call rescues the requests
                informed = 0.9 * 0.85 + 0.1 * 0.10       # 0.775
                row5 = blind + r * informed
                row6 = blind if policy == "stop" else row4
                expected = [blind, blind, blind, row4, row5, row6]
                for key, value in zip(keys, expected):
                    self.assertEqual(m[key], f3(value), (r, policy, key))
                wrong = blind + r * (0.9 * 0.10 + 0.1 * 0.85)
                self.assertEqual(m["Row 5 wrong answer"], f3(wrong))
                self.assertEqual(m["Row 5 stops with no answer"], f3(r * 0.05))
                self.assertAlmostEqual(row5 + wrong + r * 0.05, 1.0, places=12)  # three outcomes sum to one
                self.assertEqual(m["Row 5 minus row 1"], f3(row5 - blind))

    def test_d01_the_books_table_5_1_values(self):
        m = metrics(self.state("C05-D01", 1, 0))       # request 0.40, denial stops
        self.assertEqual([m[k] for k in ("Model only", "Memory, no reader", "Tool, no recurrence", "Recurrence, blind",
                                        "Connected, granted", "Connected, denied")],
                         ["0.300", "0.300", "0.300", "0.420", "0.610", "0.300"])
        self.assertEqual((m["Row 5 wrong answer"], m["Row 5 stops with no answer"]), ("0.370", "0.020"))
        # The chapter notes a second blind call after denial would score 0.42.
        self.assertEqual(metrics(self.state("C05-D01", 1, 1))["Connected, denied"], "0.420")
        self.assertIn("0.90 x 0.85 + 0.10 x 0.10 = 0.775", self.page)

    # Demonstration 2: composite kernel

    @staticmethod
    def kernel(tool):
        c, t = CHOOSER, TOOL[tool]
        return [[sum(c[i][a] * t[a][j] for a in range(2)) for j in range(2)] for i in range(2)]

    def test_d02_kernel_and_occupancy_by_hand(self):
        for i, tool in enumerate(D2_TOOL):
            k = self.kernel(tool)
            # Closed form for a two-state chain started in state 0: pi0 + (1 - pi0) lam^n.
            pi0 = k[1][0] / (k[0][1] + k[1][0])
            lam = k[0][0] - k[1][0]
            for j, n in enumerate(D2_STEPS):
                m = metrics(self.state("C05-D02", i, j))
                self.assertEqual(m["Composite row 0"], f"[{k[0][0]:.2f}, {k[0][1]:.2f}]")
                self.assertEqual(m["Composite row 1"], f"[{k[1][0]:.2f}, {k[1][1]:.2f}]")
                after = pi0 + (1 - pi0) * lam ** n
                label = f"State 0 after {n} transition" + ("" if n == 1 else "s")
                self.assertEqual(m[label], f3(after), (tool, n))
                self.assertEqual(m["Long-run state 0"], f3(pi0))
                # Row sums of a kernel built from stochastic factors are one.
                self.assertAlmostEqual(sum(k[0]), 1.0)
                self.assertAlmostEqual(sum(k[1]), 1.0)

    def test_d02_the_books_numbers(self):
        m = metrics(self.state("C05-D02", 0, 1))      # default tool, two transitions
        self.assertEqual(m["Composite row 0"], "[0.76, 0.24]")   # 0.8 x 0.9 + 0.2 x 0.2 and 0.8 x 0.1 + 0.2 x 0.8
        self.assertEqual(m["State 0 after 2 transitions"], "0.676")  # 0.76 x 0.76 + 0.24 x 0.41
        changed = metrics(self.state("C05-D02", 1, 1))
        self.assertEqual(changed["Composite row 0"], "[0.50, 0.50]")  # the changed first row named in the lab
        self.assertEqual(changed["State 0 after 2 transitions"], "0.375")  # 0.5 x 0.5 + 0.5 x 0.25
        self.assertIn("0.76 x 0.76 + 0.24 x 0.41 = 0.676", self.page)

    def test_d02_laboratory_function_agrees_with_matrix_product(self):
        for tool in D2_TOOL:
            out = evaluate({"step_success": 0.99, "steps": 2, "conditional_success": [0.99, 0.99], "chooser": CHOOSER,
                            "tool": TOOL[tool], "initial": [1, 0]})
            k = self.kernel(tool)
            for i in range(2):
                for j in range(2):
                    self.assertAlmostEqual(out["metrics"]["composite_kernel"][i][j], k[i][j], places=12)

    # Demonstration 3: observation worth

    def test_d03_information_and_success_by_hand(self):
        for i, a in enumerate(D3_ACCURACY):
            h = 0.0 if a in (0.0, 1.0) else -(a * math.log2(a) + (1 - a) * math.log2(1 - a))
            info = 1 - h
            for j, reaches in enumerate(D3_REACHES):
                m = metrics(self.state("C05-D03", i, j))
                self.assertEqual(m["Uncertainty after, H(Y | O)"], f"{h:.3f} bits")
                self.assertEqual(m["Information, I(Y;O)"], f"{info:.3f} bits")
                informed = a * 0.85 + (1 - a) * 0.10
                success = 0.30 + 0.40 * informed if reaches == "reaches" else 0.30
                self.assertEqual(m["Success with this assembly"], f3(success))
                self.assertEqual(m["Success gain over model only"], f3(success - 0.30))

    def test_d03_the_books_numbers_and_boundaries(self):
        book = metrics(self.state("C05-D03", 2, 0))   # accuracy 0.90, run stops (row 3)
        self.assertEqual(book["Uncertainty after, H(Y | O)"], "0.469 bits")
        self.assertEqual(book["Information, I(Y;O)"], "0.531 bits")
        self.assertEqual(book["Success gain over model only"], "0.000")   # information with no decision value
        self.assertEqual(metrics(self.state("C05-D03", 2, 1))["Success with this assembly"], "0.610")
        useless = metrics(self.state("C05-D03", 0, 1))
        self.assertEqual(useless["Information, I(Y;O)"], "0.000 bits")
        perfect = metrics(self.state("C05-D03", 3, 0))
        self.assertEqual((perfect["Uncertainty after, H(Y | O)"], perfect["Information, I(Y;O)"]), ("0.000 bits", "1.000 bits"))
        # The coin-flip tool still scores above 0.30 once connected; the page must say that this is not information.
        self.assertIn("0 bits, yet success still rises", self.state("C05-D03", 0, 1)["interpretation"])
        # The check question (accuracy 0.75): 0.25 x 2.000 + 0.75 x 0.415 = 0.811 bits, so 0.189 bits delivered.
        self.assertEqual((f"{-math.log2(0.25):.3f}", f"{-math.log2(0.75):.3f}"), ("2.000", "0.415"))
        self.assertEqual(f"{0.25 * 2 + 0.75 * -math.log2(0.75):.3f}", "0.811")
        self.assertIn("0.25 x 2.000 + 0.75 x 0.415 = 0.500 + 0.311 = 0.811", CHAPTER_DEMOS()[2]["answer"])
        self.assertEqual(metrics(self.state("C05-D03", 1, 0))["Information, I(Y;O)"], "0.189 bits")

    # Demonstration 4: recurrence

    def test_d04_products_by_hand(self):
        for i, p in enumerate(D4_P):
            for j, handling in enumerate(D4_HANDLING):
                q = p if handling == "none" else 1 - (1 - p) ** 2
                m = metrics(self.state("C05-D04", i, j))
                self.assertEqual(m["Conditional success per step used"], f"{q:.6f}" if q > 0.99995 else f"{q:.4f}")
                for n in (10, 40, 100):
                    value = 1.0
                    for _ in range(n):
                        value *= q                      # repeated multiplication, not a power
                    self.assertEqual(m[f"After {n} steps"], f3(value), (p, handling, n))
                half = math.log(0.5) / math.log(q)
                beyond = " (beyond the plotted 100)" if half > 100 else ""
                self.assertEqual(m["Steps until success falls below 0.5"], f"{half:.{0 if half >= 100 else 1}f} steps{beyond}")

    def test_g2_08_zero_information_is_not_called_real(self):
        stops = self.state("C05-D03", 0, 0)["interpretation"]       # accuracy 0.50, run stops
        self.assertEqual(metrics(self.state("C05-D03", 0, 0))["Information, I(Y;O)"], "0.000 bits")
        self.assertIn("The report carries no information, so its decision value is zero as well.", stops)
        self.assertNotIn("Information is real", stops)
        self.assertNotIn("information is real", stops)
        real = self.state("C05-D03", 2, 0)["interpretation"]        # accuracy 0.90, run stops
        self.assertIn("The information is real and its decision value here is zero.", real)

    def test_g2_09_no_claim_about_real_models(self):
        page = html.unescape(self.page)
        self.assertNotIn("a real model would learn", page)
        self.assertNotIn("learn to ignore", page)
        self.assertIn("the declared law still responds to it, because the law is held fixed by construction", page)
        # The page itself shows that response: at accuracy 0.50 with the report reaching a later call, success rises with 0 bits.
        m = metrics(self.state("C05-D03", 0, 1))
        self.assertEqual((m["Information, I(Y;O)"], m["Success with this assembly"], m["Success gain over model only"]),
                         ("0.000 bits", "0.490", "0.190"))

    def test_g2_10_demo_three_does_not_depend_on_row_numbers(self):
        demo = self.demos["C05-D03"]
        self.assertEqual(demo["controls"][1]["values"],
                         ["No, the run stops (tool, no recurrence)", "Yes, it enters the next context (connected, granted)"])
        blob = json.dumps(demo)
        self.assertNotIn("row 1", blob)
        self.assertNotIn("(row 3)", blob)
        self.assertNotIn("(row 5)", blob)
        self.assertIn("Success gain over model only", blob)

    def test_g2_11_retry_arithmetic_keeps_the_digits(self):
        text = self.state("C05-D04", 3, 1)["interpretation"]       # per-step 0.999 with one retry
        self.assertAlmostEqual(1 - 0.001 * 0.001, 0.999999)
        self.assertIn("q = 1 - 0.001 x 0.001 = 0.999999", text)
        self.assertIn("two steps give 0.999999 x 0.999999 = 0.999998", text)
        self.assertIn("(40 factors) = 0.99996", text)
        self.assertNotIn("1 x 1", text)
        self.assertEqual(f"{0.999999 ** 40:.5f}", "0.99996")
        self.assertEqual(metrics(self.state("C05-D04", 3, 1))["Conditional success per step used"], "0.999999")

    def test_g2_12_horizon_beyond_the_plot_is_flagged(self):
        expect = {(1, 1): "277 steps (beyond the plotted 100)", (2, 1): "6931 steps (beyond the plotted 100)",
                  (3, 1): "693147 steps (beyond the plotted 100)", (2, 0): "69.0 steps"}
        for (i, j), text in expect.items():
            self.assertEqual(metrics(self.state("C05-D04", i, j))["Steps until success falls below 0.5"], text)

    def test_d04_the_books_compounding_values(self):
        self.assertEqual(metrics(self.state("C05-D04", 2, 0))["After 40 steps"], "0.669")   # 0.99 over forty steps
        self.assertEqual(metrics(self.state("C05-D04", 1, 0))["After 40 steps"], "0.129")   # 0.95 over forty steps
        self.assertEqual(metrics(self.state("C05-D04", 2, 0))["After 100 steps"], "0.366")  # lab: about 0.366
        self.assertEqual(metrics(self.state("C05-D04", 0, 1))["Conditional success per step used"], "0.9900")  # 1 - 0.1 x 0.1
        self.assertAlmostEqual(0.99 * 0.99, 0.9801)   # the check question's answer

    def test_d04_laboratory_chain_rule_agrees(self):
        out = evaluate({"step_success": 0.99, "steps": 100, "conditional_success": [0.99] * 100,
                        "chooser": [[1, 0], [0, 1]], "tool": [[1, 0], [0, 1]], "initial": [1, 0]})
        self.assertAlmostEqual(out["metrics"]["chain_rule_all_success"], 0.99 ** 100, places=12)
        self.assertAlmostEqual(out["metrics"]["independent_all_success"], 0.99 ** 100, places=12)

    # Page-level checks

    def test_displayed_equations_are_chapter_equations(self):
        chapter = next(c for c in json.loads((LAB / "chapter-map.json").read_text()) if c["chapter"] == 5)

        def norm(t):
            t = re.sub(r"\\tag\{[^}]*\}", "", t)
            t = re.sub(r"\\[,;:!]", "", t)
            return re.sub(r"[\s{}]", "", t).rstrip(".")
        allowed = {norm(e["tex"]) for e in chapter["equations"]}
        alts = re.findall(r'data-tex="([^"]+)"', self.page)
        self.assertEqual(len(alts), 4)
        for tex in alts:
            self.assertIn(norm(html.unescape(tex)), allowed)

    def test_source_sections_are_chapter_headings(self):
        text = (LAB.parent / "Manuscript/revisions/part-i-v2/05-what-the-model-becomes-inside-an-agent.md").read_text()
        headings = set(re.findall(r"^#{1,3} (.+)$", text, re.M))
        sections = [
            "The fair experiment", "The law the model does not contain", "What an observation is worth", "Recurrence multiplies",
        ]
        self.assertEqual([d["source_section"] for d in CHAPTER_DEMOS()], sections)
        for s in sections:
            self.assertIn(s, headings)

    def test_links_and_offline(self):
        for href in (f"../../notebooks/{SLUG}.ipynb", "../../skills/maa-05-composite-kernel/SKILL.md",
                     f"../../guide/chapters/{SLUG}.html", "../index.html"):
            self.assertIn(f'href="{href}"', self.page)
            self.assertTrue((LAB / "readers" / SLUG / href).resolve().exists(), href)
        self.assertIsNone(re.search(r'(src|href)="(https?:)?//', self.page))

    def test_page_text_has_no_dashes_or_dependency_names(self):
        text = re.sub(r"<script\b.*?</script>|<style\b.*?</style>", " ", self.page, flags=re.S)
        text = html.unescape(re.sub(r"<[^>]+>", " ", text))
        for state in (s for d in self.data["demos"] for s in d["states"].values()):
            text += " " + state["interpretation"] + " " + " ".join(" ".join(p) for p in state["metrics"])
        for bad in ("\u2014", "\u2013", "\u2212", "--"):
            self.assertNotIn(bad, text)
        for term in ("matplotlib", "numpy", "python", "jupyter"):
            self.assertNotIn(term, text.lower())
        self.assertIn("constructed", text.lower())

    def test_accessibility_basics(self):
        self.assertIn('<a class="skip" href="#main">', self.page)
        self.assertIn('<html lang="en" class="no-js">', self.page)
        self.assertIn("<noscript>", self.page)
        self.assertEqual(self.page.count('aria-live="polite"'), 4)
        for d in self.data["demos"]:
            for c in d["controls"]:
                self.assertIn(f'<label for="{d["id"]}-{c["key"]}">', self.page)

    def test_every_control_combination_renders(self):
        for demo in self.data["demos"]:
            sizes = [len(c["values"]) for c in demo["controls"]]
            self.assertEqual(len(demo["states"]), sizes[0] * sizes[1])
            for state in demo["states"].values():
                self.assertTrue(state["metrics"])
                self.assertTrue(state["interpretation"])
                self.assertTrue(state["image"].startswith("data:image/svg+xml"))

    def test_dom_harness(self):
        if shutil.which("node") is None:
            self.skipTest("Node is not installed; the DOM harness needs it")
        run = subprocess.run(["node", str(HARNESS), str(self.reader)], capture_output=True, text=True, timeout=120)
        self.assertEqual(run.returncode, 0, run.stderr)
        report = json.loads(run.stdout)["reports"][0]
        self.assertEqual((report["states_checked"], report["resets_checked"], report["labelled_controls"]), (32, 4, 8))

    def test_committed_reader_is_current_if_present(self):
        if not COMMITTED.is_file():
            self.skipTest("Chapter 5 reader not yet built into the shared readers folder")
        self.assertEqual(hashlib.sha256(COMMITTED.read_bytes()).hexdigest(), hashlib.sha256(self.reader.read_bytes()).hexdigest(),
                         "reader.html is stale or the build is not reproducible")


def CHAPTER_DEMOS():
    spec = importlib.util.spec_from_file_location("ch05_reader_module", LAB / "tools/readers/chapters/ch05.py")
    import sys
    engine = str(LAB / "tools/readers/engine")
    if engine not in sys.path:
        sys.path.insert(0, engine)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.CHAPTER["demos"]


if __name__ == "__main__":
    unittest.main()
