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
D1_REQUEST = [0.2, 0.4, 0.6]
D1_REJECTION = ["stop", "blind"]
D1_CALLS = [2, 1]
D2_SYSTEM = ["default", "changed", "transfer"]
D2_STEPS = [1, 2, 3, 30]
D3_ACCURACY = [0.5, 0.75, 0.9, 1.0]
D3_PATH = ["stops", "dropped", "reaches"]
D4_CASE = [0.95, 0.99, 0.999, "transfer"]
D4_HANDLING = ["none", "retry", "shared"]

CHOOSER = {"default": [[0.8, 0.2], [0.3, 0.7]], "changed": [[0.8, 0.2], [0.3, 0.7]], "transfer": [[1, 0], [0, 1]]}
TOOL = {"default": [[0.9, 0.1], [0.2, 0.8]], "changed": [[0.6, 0.4], [0.1, 0.9]], "transfer": [[0.7, 0.3], [0.4, 0.6]]}
START = {"default": 1.0, "changed": 1.0, "transfer": 0.5}


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

    def state(self, demo_id, *idx):
        return self.demos[demo_id]["states"][",".join(str(i) for i in idx)]

    # Structure

    def test_four_demonstrations_with_state_budget(self):
        self.assertEqual(list(self.demos), ["C05-D01", "C05-D02", "C05-D03", "C05-D04"])
        self.assertEqual([len(d["states"]) for d in self.data["demos"]], [12, 12, 12, 12])
        self.assertEqual([[len(c["values"]) for c in d["controls"]] for d in self.data["demos"]],
                         [[3, 2, 2], [3, 4], [4, 3], [4, 3]])

    def test_size_budget(self):
        self.assertLess(self.reader.stat().st_size, 4_000_000)

    def test_optional_features(self):
        text = html.unescape(self.page)
        self.assertIn("Ask the chapter skill", text)
        self.assertEqual(text.count("Common wrong turn:"), 4)
        self.assertGreaterEqual(text.count("What this does not settle"), 4)
        for d in self.data["demos"]:
            for s in d["states"].values():
                self.assertTrue(2 <= len(s["steps"]) <= 8)
                self.assertTrue(all(len(x) <= 240 for x in s["steps"]))

    # Demonstration 1: six assemblies, outcome parts, budget

    def test_d01_parts_by_hand(self):
        keys = ["Model only", "Memory, no reader", "Tool, no recurrence", "Recurrence, blind",
                "Connected, granted", "Connected, denied"]
        for i, r in enumerate(D1_REQUEST):
            for j, policy in enumerate(D1_REJECTION):
                for k, calls in enumerate(D1_CALLS):
                    m = metrics(self.state("C05-D01", i, j, k))
                    blind = (1 - r) / 2                      # answer0 and answer1 each (1 - r) / 2; either is right half the time
                    informed = 0.9 * 0.85 + 0.1 * 0.10       # 0.775
                    if calls == 2:
                        row4 = blind + r * blind
                        row5 = blind + r * informed
                        row6 = blind if policy == "stop" else row4
                        expected = [blind, blind, blind, row4, row5, row6]
                        wrong = blind + r * (0.9 * 0.10 + 0.1 * 0.85)
                        self.assertEqual(m["Row 5 wrong answer"], f3(wrong))
                        self.assertEqual(m["Row 5 stops with no answer"], f3(r * 0.05))
                        self.assertAlmostEqual(row5 + wrong + r * 0.05, 1.0, places=12)
                        self.assertEqual(m["Row 5 minus row 1"], f3(row5 - blind))
                    else:
                        expected = [blind] * 6        # a request on the last call ends the run: no second call in any row
                        self.assertEqual(m["Row 5 wrong answer"], f3(blind))
                        self.assertEqual(m["Row 5 stops with no answer"], f3(r))
                        self.assertEqual(m["Row 5 minus row 1"], "0.000")
                    self.assertEqual(m["Calls allowed"], str(calls))
                    for key, value in zip(keys, expected):
                        self.assertEqual(m[key], f3(value), (r, policy, calls, key))

    def test_d01_the_books_table_5_1_values(self):
        m = metrics(self.state("C05-D01", 1, 0, 0))       # request 0.40, denial stops, two calls
        self.assertEqual([m[k] for k in ("Model only", "Memory, no reader", "Tool, no recurrence", "Recurrence, blind",
                                        "Connected, granted", "Connected, denied")],
                         ["0.300", "0.300", "0.300", "0.420", "0.610", "0.300"])
        self.assertEqual((m["Row 5 wrong answer"], m["Row 5 stops with no answer"]), ("0.370", "0.020"))
        self.assertEqual(metrics(self.state("C05-D01", 1, 1, 0))["Connected, denied"], "0.420")
        self.assertIn("0.90 x 0.85 + 0.10 x 0.10 = 0.775", self.page)
        # One call allowed: every row is the blind rate and the interpretation says why.
        one = self.state("C05-D01", 1, 0, 1)
        self.assertIn("no budget for a second call", one["interpretation"])
        self.assertEqual(metrics(one)["Connected, granted"], "0.300")

    # Demonstration 2: composite kernel, with the transfer case

    @staticmethod
    def kernel(system):
        c, t = CHOOSER[system], TOOL[system]
        return [[sum(c[i][a] * t[a][j] for a in range(2)) for j in range(2)] for i in range(2)]

    def test_d02_kernel_and_occupancy_by_hand(self):
        for i, system in enumerate(D2_SYSTEM):
            k = self.kernel(system)
            pi0 = k[1][0] / (k[0][1] + k[1][0])
            lam = k[0][0] - k[1][0]
            for j, n in enumerate(D2_STEPS):
                m = metrics(self.state("C05-D02", i, j))
                self.assertEqual(m["Composite row 0"], f"[{k[0][0]:.2f}, {k[0][1]:.2f}]")
                self.assertEqual(m["Composite row 1"], f"[{k[1][0]:.2f}, {k[1][1]:.2f}]")
                # Closed form for a two-state chain: pi0 + (mu0 - pi0) lam^n for a start with probability mu0 in state 0.
                after = pi0 + (START[system] - pi0) * lam ** n
                label = f"State 0 after {n} transition" + ("" if n == 1 else "s")
                # (the transfer case at 3 transitions is exactly 0.5695, a rounding tie, so compare numerically)
                self.assertLessEqual(abs(float(m[label]) - after), 0.0005 + 1e-9, (system, n))
                self.assertEqual(m["Long-run state 0"], f3(pi0))
                self.assertAlmostEqual(sum(k[0]), 1.0)
                self.assertAlmostEqual(sum(k[1]), 1.0)

    def test_d02_the_books_numbers_and_transfer(self):
        m = metrics(self.state("C05-D02", 0, 1))      # default tool, two transitions
        self.assertEqual(m["Composite row 0"], "[0.76, 0.24]")
        self.assertEqual(m["State 0 after 2 transitions"], "0.676")
        changed = metrics(self.state("C05-D02", 1, 1))
        self.assertEqual(changed["Composite row 0"], "[0.50, 0.50]")
        self.assertEqual(changed["State 0 after 2 transitions"], "0.375")
        self.assertIn("0.76 x 0.76 + 0.24 x 0.41 = 0.676", self.page)
        # Transfer: identity chooser, so K equals the tool; start half in each state: 0.5 x 0.7 + 0.5 x 0.4 = 0.55, then 0.565.
        t = self.state("C05-D02", 2, 1)
        self.assertEqual(metrics(t)["Composite row 0"], "[0.70, 0.30]")
        self.assertEqual(metrics(t)["State 0 after 2 transitions"], "0.565")
        self.assertIn("0.5 x 0.70 + 0.5 x 0.40 = 0.550", t["interpretation"])
        data = json.loads((LAB / "data" / "examples" / "ch05.json").read_text())
        self.assertEqual(data["chooser"], [[1, 0], [0, 1]])
        self.assertEqual(data["tool"], [[0.7, 0.3], [0.4, 0.6]])
        self.assertEqual(data["initial"], [0.5, 0.5])

    def test_d02_laboratory_function_agrees_with_matrix_product(self):
        for system in D2_SYSTEM:
            out = evaluate({"step_success": 0.99, "steps": 2, "conditional_success": [0.99, 0.99], "chooser": CHOOSER[system],
                            "tool": TOOL[system], "initial": [START[system], 1 - START[system]]})
            k = self.kernel(system)
            for i in range(2):
                for j in range(2):
                    self.assertAlmostEqual(out["metrics"]["composite_kernel"][i][j], k[i][j], places=12)

    # Demonstration 3: observation worth and a memory that drops it

    def test_d03_information_and_success_by_hand(self):
        for i, a in enumerate(D3_ACCURACY):
            h = 0.0 if a in (0.0, 1.0) else -(a * math.log2(a) + (1 - a) * math.log2(1 - a))
            info = 1 - h
            for j, path in enumerate(D3_PATH):
                m = metrics(self.state("C05-D03", i, j))
                self.assertEqual(m["Uncertainty after, H(Y | O)"], f"{h:.3f} bits")
                self.assertEqual(m["Information, I(Y;O)"], f"{info:.3f} bits")
                informed = a * 0.85 + (1 - a) * 0.10
                success = {"stops": 0.30, "dropped": 0.30 + 0.40 * 0.30, "reaches": 0.30 + 0.40 * informed}[path]
                self.assertEqual(m["Success with this assembly"], f3(success))
                self.assertEqual(m["Success gain over model only"], f3(success - 0.30))

    def test_d03_the_books_numbers_and_boundaries(self):
        book = metrics(self.state("C05-D03", 2, 0))   # accuracy 0.90, run stops (row 3)
        self.assertEqual(book["Uncertainty after, H(Y | O)"], "0.469 bits")
        self.assertEqual(book["Information, I(Y;O)"], "0.531 bits")
        self.assertEqual(book["Success gain over model only"], "0.000")
        self.assertEqual(metrics(self.state("C05-D03", 2, 2))["Success with this assembly"], "0.610")
        self.assertEqual(metrics(self.state("C05-D03", 0, 2))["Information, I(Y;O)"], "0.000 bits")
        perfect = metrics(self.state("C05-D03", 3, 0))
        self.assertEqual((perfect["Uncertainty after, H(Y | O)"], perfect["Information, I(Y;O)"]), ("0.000 bits", "1.000 bits"))
        self.assertIn("0 bits, yet success still rises", self.state("C05-D03", 0, 2)["interpretation"])
        self.assertEqual(f"{0.25 * 2 + 0.75 * -math.log2(0.75):.3f}", "0.811")
        self.assertEqual(metrics(self.state("C05-D03", 1, 0))["Information, I(Y;O)"], "0.189 bits")

    def test_d03_dropped_report_fails_the_merge_condition(self):
        # Equation (5.3): the states 'report says 0' and 'report says 1' send 0.85 and 0.10 into the class 'answer 0'.
        text = self.state("C05-D03", 2, 1)["interpretation"]
        self.assertIn("the chance of the class 'answer 0' would be 0.85 from one state and 0.10 from the other if the two states were kept apart", text)
        self.assertNotIn("answer 0' is 0.85 from one state", text)
        self.assertIn("success = 0.30 + 0.40 x 0.30 = 0.420", text)
        # Dropping the report gives the same success at every accuracy, equal to row 4 of the six assemblies.
        values = {metrics(self.state("C05-D03", i, 1))["Success with this assembly"] for i in range(4)}
        self.assertEqual(values, {"0.420"})
        # The chapter's rows: blind second call 0.30 + 0.40 x 0.30 = 0.42.
        self.assertAlmostEqual(0.30 + 0.40 * 0.30, 0.42)

    # Demonstration 4: recurrence, shared cause, transfer

    def test_d04_products_by_hand(self):
        for i, p in enumerate(D4_CASE[:3]):
            for j, handling in enumerate(D4_HANDLING):
                m = metrics(self.state("C05-D04", i, j))
                if handling == "shared":
                    self.assertEqual(m["Conditional success per step used"], f"{p:.3f} marginal")
                    for n in (10, 40, 100):
                        self.assertEqual(m[f"After {n} steps"], f3(p))
                    self.assertEqual(m["Steps until success falls below 0.5"], f"does not fall: stays at {p:.3f}")
                    continue
                q = p if handling == "none" else 1 - (1 - p) ** 2
                self.assertEqual(m["Conditional success per step used"], f"{q:.6f}" if q > 0.99995 else f"{q:.4f}")
                for n in (10, 40, 100):
                    value = 1.0
                    for _ in range(n):
                        value *= q                      # repeated multiplication, not a power
                    self.assertEqual(m[f"After {n} steps"], f3(value), (p, handling, n))
                half = math.log(0.5) / math.log(q)
                beyond = " (beyond the plotted 100)" if half > 100 else ""
                self.assertEqual(m["Steps until success falls below 0.5"], f"{half:.{0 if half >= 100 else 1}f} steps{beyond}")

    def test_d04_chapter_horizons(self):
        # The chapter: about 14 steps at 0.95, about 69 at 0.99, about 693 at 0.999.
        self.assertEqual(metrics(self.state("C05-D04", 0, 0))["Steps until success falls below 0.5"], "13.5 steps")
        self.assertEqual(metrics(self.state("C05-D04", 1, 0))["Steps until success falls below 0.5"], "69.0 steps")
        self.assertEqual(metrics(self.state("C05-D04", 2, 0))["Steps until success falls below 0.5"], "693 steps (beyond the plotted 100)")
        self.assertEqual(round(math.log(0.5) / math.log(0.95)), 14)
        self.assertEqual(round(math.log(0.5) / math.log(0.999)), 693)
        self.assertEqual(metrics(self.state("C05-D04", 1, 0))["After 40 steps"], "0.669")
        self.assertEqual(metrics(self.state("C05-D04", 0, 0))["After 40 steps"], "0.129")
        self.assertEqual(metrics(self.state("C05-D04", 1, 0))["After 100 steps"], "0.366")

    def test_d04_shared_cause_and_independence_have_equal_marginals(self):
        text = self.state("C05-D04", 1, 2)["interpretation"]
        self.assertIn("all-step success stays 0.990 at 10, 40 and 100 steps", text)
        self.assertIn("(40 factors) = 0.669", text)
        # Independent: 0.99^100 = 0.366; shared: 0.99. Same marginal per step.
        self.assertAlmostEqual(0.99 ** 100, 0.366, places=3)

    def test_d04_transfer_case(self):
        data = json.loads((LAB / "data" / "examples" / "ch05.json").read_text())
        self.assertEqual(data["conditional_success"], [0.9, 0.8, 0.7])
        m = metrics(self.state("C05-D04", 3, 0))
        self.assertEqual(m["Chain rule with rates 0.9, 0.8, 0.7"], "0.504")          # 0.9 x 0.8 x 0.7
        self.assertEqual(m["A different system: three independent steps each at 0.9"], "0.729")             # 0.9^3
        self.assertEqual(m["Shared cause, marginal 0.9"], "0.900")
        retry = 0.99 * 0.96 * 0.91
        self.assertEqual(m["One retry per step on the rates"], f"{retry:.4f}")
        self.assertEqual(metrics(self.state("C05-D04", 3, 1))["After 3 steps with this handling"], f"{retry:.4f}")
        self.assertEqual(metrics(self.state("C05-D04", 3, 2))["After 3 steps with this handling"], "0.900")
        self.assertEqual(metrics(self.state("C05-D04", 3, 0))["After 3 steps with this handling"], "0.504")
        self.assertIn("0.9 x 0.8 x 0.7 = 0.504", self.state("C05-D04", 3, 0)["interpretation"])
        self.assertIn("1 - 0.1 x 0.1 = 0.99, 1 - 0.2 x 0.2 = 0.96 and 1 - 0.3 x 0.3 = 0.91", self.state("C05-D04", 3, 1)["interpretation"])

    def test_d04_laboratory_chain_rule_agrees(self):
        out = evaluate({"step_success": 0.99, "steps": 100, "conditional_success": [0.99] * 100,
                        "chooser": [[1, 0], [0, 1]], "tool": [[1, 0], [0, 1]], "initial": [1, 0]})
        self.assertAlmostEqual(out["metrics"]["chain_rule_all_success"], 0.99 ** 100, places=12)
        self.assertAlmostEqual(out["metrics"]["shared_condition_all_success"], 0.99, places=12)
        out = evaluate({"step_success": 0.9, "steps": 3, "conditional_success": [0.9, 0.8, 0.7], "chooser": [[1, 0], [0, 1]],
                        "tool": [[0.7, 0.3], [0.4, 0.6]], "initial": [0.5, 0.5]})
        self.assertAlmostEqual(out["metrics"]["chain_rule_all_success"], 0.504, places=12)

    def test_g2_11_retry_arithmetic_keeps_the_digits(self):
        text = self.state("C05-D04", 2, 1)["interpretation"]       # per-step 0.999 with one retry
        self.assertIn("q = 1 - 0.001 x 0.001 = 0.999999", text)
        self.assertIn("two steps give 0.999999 x 0.999999 = 0.999998", text)
        self.assertIn("(40 factors) = 0.99996", text)
        self.assertEqual(f"{0.999999 ** 40:.5f}", "0.99996")
        self.assertEqual(metrics(self.state("C05-D04", 2, 1))["Conditional success per step used"], "0.999999")

    def test_zero_information_is_not_called_real(self):
        stops = self.state("C05-D03", 0, 0)["interpretation"]
        self.assertIn("The report carries no information, so its decision value is zero as well.", stops)
        self.assertNotIn("information is real", stops)
        real = self.state("C05-D03", 2, 0)["interpretation"]
        self.assertIn("The information is real and its decision value here is zero.", real)

    def test_no_claim_about_real_models(self):
        page = html.unescape(self.page)
        self.assertNotIn("a real model would learn", page)
        self.assertIn("the declared law still responds to it, because the law is held fixed by construction", page)
        m = metrics(self.state("C05-D03", 0, 2))
        self.assertEqual((m["Information, I(Y;O)"], m["Success with this assembly"], m["Success gain over model only"]),
                         ("0.000 bits", "0.490", "0.190"))

    # Page-level checks

    def test_displayed_equations_are_chapter_equations(self):
        chapter = next(c for c in json.loads((LAB / "chapter-map.json").read_text()) if c["chapter"] == 5)

        def norm(t):
            t = re.sub(r"\\tag\{[^}]*\}", "", t)
            t = re.sub(r"\\[,;:!]", "", t)
            return re.sub(r"[\s{}]", "", t).rstrip(".")
        allowed = {norm(e["tex"]) for e in chapter["equations"]}
        text = (LAB.parent / chapter["source_path"]).read_text(encoding="utf-8")
        inline = {norm(m) for m in re.findall(r"\$([^$\n]+)\$", text)}
        alts = {norm(html.unescape(t)) for t in re.findall(r'data-tex="([^"]+)"', self.page)}
        for tex in alts:
            self.assertTrue(tex in allowed or tex in inline, tex)
        numbered = {e["number"]: norm(e["tex"]) for e in chapter["equations"]}
        for number in ("5.1", "5.2", "5.3", "5.4", "5.5"):
            self.assertIn(numbered[number], alts, number)

    def test_source_sections_are_chapter_headings(self):
        text = (LAB.parent / "Manuscript/revisions/part-i-v2/05-what-the-model-becomes-inside-an-agent.md").read_text()
        headings = set(re.findall(r"^#{1,3} (.+)$", text, re.M))
        sections = ["The fair experiment", "The law the model does not contain", "What an observation is worth", "Recurrence multiplies"]
        self.assertEqual([d["source_section"] for d in CHAPTER_DEMOS()], sections)
        for s in sections:
            self.assertIn(s, headings)

    # Group 2 patch 2: corrected text, and the old wrong text is gone.

    def test_d01_scope_note_cites_the_section_that_holds_its_sentences(self):
        text = (LAB.parent / "Manuscript/revisions/part-i-v2/05-what-the-model-becomes-inside-an-agent.md").read_text()
        section = text.split("### Reading the table honestly", 1)[1].split("\n## ", 1)[0]
        self.assertIn("the size of the jump", section)
        self.assertIn("chosen large because the argument is easier to see at full strength", section)
        note = CHAPTER_DEMOS()[0]["scope_note"]
        self.assertIn("The size of the jump", note["text"])
        self.assertEqual(note["source_section"], "Reading the table honestly")
        self.assertNotEqual(note["source_section"], "What this does not settle")

    def test_d04_transfer_independent_row_is_named_a_different_system(self):
        for handling in range(3):
            st = self.state("C05-D04", 3, handling)
            self.assertNotIn("Independent, equal marginals", json.dumps(st))
            self.assertIn("A different system, three independent steps each at 0.9: 0.9 x 0.9 x 0.9 = 0.729.", st["steps"])
            self.assertIn("A different system, three independent steps that each succeed with probability 0.9", st["interpretation"])

    def test_links_and_offline(self):
        for href in (f"../../notebooks/{SLUG}.ipynb", "../../skills/maa-05-composite-kernel/SKILL.md",
                     f"../../guide/chapters/{SLUG}.html"):
            self.assertIn(f'href="{href}"', self.page)
        self.assertRegex(self.page, r'href="(\.\./)+index\.html"')   # the link to the readers index (its depth depends on the output folder)
        self.assertIsNone(re.search(r'(src|href)="(https?:)?//', self.page))

    def test_page_text_has_no_dashes_or_dependency_names(self):
        text = re.sub(r"<script\b.*?</script>|<style\b.*?</style>", " ", self.page, flags=re.S)
        text = html.unescape(re.sub(r"<[^>]+>", " ", text))
        for state in (s for d in self.data["demos"] for s in d["states"].values()):
            text += " " + state["interpretation"] + " " + " ".join(" ".join(p) for p in state["metrics"]) + " " + " ".join(state["steps"])
        for bad in ("\u2014", "\u2013", "\u2212", "--"):
            self.assertNotIn(bad, text)
        for term in ("matplotlib", "numpy", "python", "jupyter"):
            self.assertNotIn(term, text.lower())
        self.assertIn("constructed", text.lower())

    def test_accessibility_basics(self):
        self.assertIn('<a class="skip" href="#main">', self.page)
        self.assertIn('<html lang="en" class="no-js">', self.page)
        self.assertIn("<noscript>", self.page)
        self.assertGreaterEqual(self.page.count('aria-live="polite"'), 4)
        for d in self.data["demos"]:
            for c in d["controls"]:
                self.assertIn(f'<label for="{d["id"]}-{c["key"]}">', self.page)

    def test_every_control_combination_renders(self):
        for demo in self.data["demos"]:
            n = 1
            for c in demo["controls"]:
                n *= len(c["values"])
            self.assertEqual(len(demo["states"]), n)
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
        self.assertEqual((report["states_checked"], report["resets_checked"], report["labelled_controls"]), (48, 4, 9))
        self.assertEqual(report["ask_skill"], 1)
        self.assertEqual(report["panels_checked"], 8)

    def test_build_is_reproducible(self):
        with tempfile.TemporaryDirectory() as out:
            run = subprocess.run([self.python, str(WRAPPER), "--chapters", "5", "--out", out], capture_output=True, text=True,
                                 timeout=600, env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
            self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
            fresh = Path(out) / SLUG / "reader.html"
            self.assertEqual(hashlib.sha256(fresh.read_bytes()).hexdigest(), hashlib.sha256(self.reader.read_bytes()).hexdigest())


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
