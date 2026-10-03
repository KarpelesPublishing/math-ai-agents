"""Chapter 2 laboratory reader: independent hand checks of the built page.

Every expected number below is recomputed here from the chapter's own
arithmetic (Table 2.1, the negative example, Figure 2.3, the variance remark),
with exact fractions, not read back from the module that produced the page.
The reader is built into a private temporary directory so that the test does
not depend on, or touch, the committed readers folder.
"""
from __future__ import annotations

import html
import itertools
import json
import math
from fractions import Fraction as F
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
LAB = HERE.parent
WRAPPER = LAB / "tools" / "readers" / "build_readers.py"
HARNESS = LAB / "tools" / "readers" / "engine" / "dom_harness.js"
VENV_PYTHON = LAB / ".venv" / "bin" / "python"
SLUG = "02-four-cell-interaction"


def payload(text):
    match = re.search(r'<script id="reader-data" type="application/json">(.*?)</script>', text, re.S)
    return json.loads(match.group(1))


def as_number(text):
    try:
        return float(text)
    except ValueError:
        return text


def two(x):
    return f"{float(x):.2f}"


def three(x):
    return f"{float(x):.3f}"


def two_dp(x):
    return f"{float(x):.2f}"


CASES = [(F(20, 100), F(30, 100), F(25, 100), F(80, 100)), (F(20, 100), F(30, 100), F(25, 100), F(35, 100)),
         (F(20, 100), F(55, 100), F(50, 100), F(70, 100)), (F(40, 100), F(52, 100), F(49, 100), F(58, 100))]
RUNS = ["matched", "doubled", "cubed"]


def g_of(c):
    n, p, i, b = c
    return b - p - i + n


@unittest.skipUnless(VENV_PYTHON.is_file(), "laboratory .venv absent; cannot build the reader")
class Chapter2ReaderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        run = subprocess.run([str(VENV_PYTHON), str(WRAPPER), "--chapters", "2", "--out", cls.tmp.name],
                             capture_output=True, text=True, timeout=600)
        if run.returncode != 0:
            raise RuntimeError(run.stdout + run.stderr)
        cls.reader = Path(cls.tmp.name) / SLUG / "reader.html"
        cls.page = cls.reader.read_text(encoding="utf-8")
        cls.data = payload(cls.page)
        cls.demos = {d["id"]: d for d in cls.data["demos"]}

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def states(self, demo_id):
        """Yield (control indices, metrics, state)."""
        for key, state in self.demos[demo_id]["states"].items():
            yield tuple(int(i) for i in key.split(",")), dict(state["metrics"]), state

    def text(self, demo_id, key):
        return self.demos[demo_id]["states"][key]["interpretation"]

    def test_structure_and_budget(self):
        self.assertEqual(list(self.demos), ["C02-D01", "C02-D02", "C02-D03", "C02-D04"])
        self.assertEqual([len(d["states"]) for d in self.data["demos"]], [12, 6, 12, 12])
        self.assertLessEqual(self.reader.stat().st_size, 4_000_000)
        for demo in self.data["demos"]:
            for state in demo["states"].values():
                self.assertTrue(state["image"].startswith("data:image/svg+xml"))
                self.assertGreaterEqual(len(state["steps"]), 2)

    def test_d01_every_state_by_exact_fractions(self):
        for (ci, ri), m, state in self.states("C02-D01"):
            cells = CASES[ci]
            if ci == 3 and ri == 1:
                cells = (cells[0], cells[1], cells[2], F(73, 100))
            if ri == 2:
                cells = tuple(x ** 3 for x in cells)
            n, p, i, b = cells
            g, joint = g_of(cells), b - n
            d = 3 if ri == 2 else 2
            self.assertEqual(m["Interaction contrast Gamma"], f"{float(g):.{d}f}".replace("-0.000", "0.000"), (ci, ri))
            self.assertEqual(m["Joint gain (both minus neither)"], f"{float(joint):.{d}f}")
            self.assertEqual(m["Additive prediction"], f"{float(n + (p - n) + (i - n)):.{d}f}")
            self.assertEqual(m["Sign of Gamma"], "zero" if g == 0 else ("positive" if g > 0 else "negative"))
            self.assertEqual(m["Budgets matched"].startswith("yes"), ri != 1)
            valid = joint > 0 and p - n >= 0 and i - n >= 0 and g >= 0
            self.assertEqual(m["Valid as a fraction"] == "yes", valid, (ci, ri))
            self.assertEqual(m["Ratio Gamma / joint gain"], f"{float(g / joint):.2f}")
            # Equation (2.2) identity appears in the worked steps.
            self.assertEqual((p - n) + (i - n) + g, joint)

    def test_d01_book_values(self):
        m = lambda k: dict(self.demos["C02-D01"]["states"][k]["metrics"])
        self.assertEqual(m("0,0")["Interaction contrast Gamma"], "0.45")      # Table 2.1
        self.assertEqual(m("0,0")["Ratio Gamma / joint gain"], "0.75")
        self.assertEqual(m("0,0")["Valid as a fraction"], "yes")
        self.assertEqual(m("1,0")["Sign of Gamma"], "zero")                    # additive prediction 0.35
        self.assertEqual(m("2,0")["Interaction contrast Gamma"], "-0.15")      # second example
        self.assertEqual(m("2,0")["Ratio Gamma / joint gain"], "-0.30")
        self.assertTrue(m("2,0")["Valid as a fraction"].startswith("no"))
        # Workbench: I.3 matched rerun, Gamma = -0.03, share -1/6; I.1 doubled run, Gamma = 0.12, share 4/11.
        self.assertEqual(m("3,0")["Interaction contrast Gamma"], "-0.03")
        self.assertEqual(m("3,0")["Ratio Gamma / joint gain"], "-0.17")
        self.assertEqual(m("3,1")["Interaction contrast Gamma"], "0.12")
        self.assertEqual(m("3,1")["Ratio Gamma / joint gain"], "0.36")
        self.assertTrue(m("3,1")["Budgets matched"].startswith("no"))
        # Cubing the second example flips the sign: 0.343 - 0.166375 - 0.125 + 0.008 = 0.059625.
        self.assertEqual(m("2,2")["Interaction contrast Gamma"], "0.060")
        self.assertEqual(m("2,2")["Sign of Gamma"], "positive")
        self.assertIn("A matched rerun", self.text("C02-D01", "3,1"))
        d = self.demos["C02-D01"]
        self.assertEqual(d["predict"]["answer"], 1)
        self.assertIn("Additive", self.page)

    def test_d02_baseline_and_three_cell_drift(self):
        for (bi, mi), m, state in self.states("C02-D02"):
            base = [F(30, 100), F(50, 100), F(70, 100)][bi]
            a = g_of((F(20, 100), F(30, 100), F(25, 100), F(80, 100)))
            b4 = g_of((base, base + F(2, 100), base + F(1, 100), F(80, 100)))
            self.assertEqual(m["System A, four-cell Gamma"], two_dp(a))
            self.assertEqual(m["System B, four-cell Gamma"], two_dp(b4))
            self.assertEqual(m["System B, three cells"], two_dp(b4 - base))
            self.assertEqual(m["System A, three cells"], two_dp(a - F(20, 100)))
            self.assertEqual(len(state["steps"]), 4)
        self.assertIn("0.80 - 0.72 - 0.71 + 0.70 = 0.07", self.text("C02-D02", "2,0"))
        self.assertEqual(self.demos["C02-D02"]["predict"]["answer"], 1)

    def test_d03_route_and_leaking_control(self):
        order = ["neither", "p only", "i only", "both"]
        base = {"neither": F(20, 100), "p only": F(30, 100), "i only": F(25, 100), "both": F(80, 100)}
        leaks = [F(0), F(1, 2), F(1)]
        for (ci, li), m, state in self.states("C02-D03"):
            lk = leaks[li]
            cells = {
                "neither": base["neither"] + lk * (base["p only"] - base["neither"]),
                "p only": base["p only"],
                "i only": base["i only"] + lk * (base["both"] - base["i only"]),
                "both": base["both"],
            }
            g = cells["both"] - cells["p only"] - cells["i only"] + cells["neither"]
            self.assertEqual(g, F(45, 100) * (1 - lk))
            self.assertEqual(m["Selected cell"], order[ci])
            self.assertEqual(m["Score of the selected cell"], f"{float(cells[order[ci]]):.3f}")
            self.assertEqual(m["Measured Gamma"], f"{float(g):.3f}")
            self.assertEqual(m["Neither / p only / i only / both"], ", ".join(f"{float(cells[k]):.3f}" for k in order))
            self.assertEqual(m["Clean-control Gamma"], "0.45")
        self.assertIn("i only = 0.25 + 0.50 x (0.80 - 0.25) = 0.525", self.text("C02-D03", "2,1"))
        self.assertIn("Gamma = 0.80 - 0.30 - 0.525 + 0.250 = 0.225", self.text("C02-D03", "0,1"))
        self.assertIn("Equation (2.2) still balances", self.text("C02-D03", "3,2"))
        d = self.demos["C02-D03"]
        self.assertEqual(d["predict"]["answer"], 2)
        self.assertIn("Back", self.page)

    def test_d04_standard_errors_intervals_and_pair_search(self):
        trials = [100, 400, 1600]
        contrasts = [0.05, 0.15]
        pairs = [1, 384 * 383 // 2]
        self.assertEqual(pairs[1], 73536)
        for (ti, ci, pi), m, state in self.states("C02-D04"):
            n, g = trials[ti], contrasts[ci]
            se_cell = 0.4 / math.sqrt(n)
            se_g = 2 * se_cell
            half = 1.96 * se_g
            self.assertEqual(m["Standard error of one cell"], f"{se_cell:.3f}")
            self.assertEqual(m["Standard error of Gamma"], f"{se_g:.3f}")
            self.assertEqual(m["Standard error of a difference of two intact scores"], f"{math.sqrt(2) * se_cell:.3f}")
            self.assertEqual(m["Interval for Gamma"], f"{g - half:.3f} to {g + half:.3f}")
            self.assertEqual(m["Interval excludes zero"], "yes" if g - half > 0 else "no")
            self.assertEqual(m["Pairs searched"], f"{pairs[pi]:,}")
        self.assertEqual(self.demos["C02-D04"]["states"]["2,1,1"]["metrics"][-1][1], "about 3,677 of 73,536")
        self.assertIn("73,536 x 0.05 = 3,676.8", self.text("C02-D04", "0,0,1"))
        # Check question: 1600 trials, smallest clearing contrast 0.039.
        self.assertEqual(dict(self.demos["C02-D04"]["states"]["2,0,0"]["metrics"])["Smallest Gamma that clears zero"], "0.039")
        self.assertEqual(self.demos["C02-D04"]["predict"]["answer"], 1)

    def test_patch2_wording_fixes(self):
        # g1-08: doubled run on a case with no doubled-run score only flips the budget flag, and says so.
        table = self.text("C02-D01", "0,1")
        self.assertIn("This case has no doubled-run score, so only the budget flag changes", table)
        self.assertNotIn("This case has no doubled-run score", self.text("C02-D01", "3,1"))
        self.assertIn("A matched rerun (the other run in this control) gives the joint score 0.58 instead of 0.73", self.text("C02-D01", "3,1"))
        # g1-09: direction and proportionality belong to the leak model defined for the reader.
        self.assertIn("In the leak model defined here, the p-off cells then score too high", self.page)
        self.assertIn("taken as the clean-control values", self.page)
        self.assertNotIn("Table 2.1's four scores are the clean-control values", self.page)
        # g1-10: the stepper opens at step 1, the neither cell.
        self.assertEqual(next(c for c in self.demos["C02-D03"]["controls"] if c["key"] == "cell")["default"], 0)
        # g1-11: the feedback covers both questions of the prediction (0.80 - 0.72 - 0.71 = -0.63).
        self.assertIn("(-0.63)", self.page)
        self.assertEqual(round(0.80 - 0.72 - 0.71, 2), -0.63)
        # g1-13: the search caption is conditional, not a claim about the selected true contrast.
        self.assertNotIn("pairs, none real", self.page)
        # g1-14: the chapter's resolved-difference case is pointed to.
        self.assertIn("a true amount of 0.15 at 100 trials shows it", self.page)

    def test_optional_panels_present(self):
        self.assertIn("Ask the chapter skill", self.page)
        self.assertIn("maa-02-four-cell-interaction", self.page)
        self.assertGreaterEqual(self.page.count("Chapter 2 source:"), 4)
        self.assertGreaterEqual(self.page.count("Common wrong turn"), 4)

    def test_laboratory_function_agrees_with_table_2_1(self):
        sys.path.insert(0, str(LAB / "src"))
        try:
            from math_ai_agents.chapters.ch02 import evaluate
        finally:
            sys.path.pop(0)
        out = evaluate({"scores": [0.2, 0.3, 0.25, 0.8], "budgets": [10, 10, 10, 10]})["metrics"]
        self.assertAlmostEqual(out["interaction"], 0.45)
        self.assertAlmostEqual(out["fraction_share"], 0.75)

    def test_every_control_combination_renders_with_a_hand_calculation(self):
        combos = 0
        for demo in self.data["demos"]:
            expected = 1
            for control in demo["controls"]:
                expected *= len(control["values"])
            self.assertEqual(len(demo["states"]), expected)
            combos += expected
            for state in demo["states"].values():
                self.assertTrue(state["interpretation"].strip())
                self.assertTrue(state["metrics"])
                self.assertRegex(state["interpretation"], r"\d\s*[-+x/]\s*\(?\d.*=\s*\(?-?\d")
        self.assertEqual(combos, 42)

    def test_displayed_equations_are_chapter_equations(self):
        chapters = json.loads((LAB / "chapter-map.json").read_text())
        chapter = next(c for c in chapters if c["chapter"] == 2)

        def norm(t):
            t = re.sub(r"\\tag\{[^}]*\}", "", t)
            t = re.sub(r"\\[,;:!]", "", t)
            return re.sub(r"[\s{}]", "", t).rstrip(".")
        allowed = {norm(e["tex"]) for e in chapter["equations"]}
        alts = re.findall(r'data-tex="([^"]+)"', self.page)
        self.assertGreaterEqual(len(alts), 4)
        for tex in alts:
            self.assertIn(norm(html.unescape(tex)), allowed)

    def test_page_text_has_no_dashes_or_dependency_names(self):
        text = re.sub(r"<script\b.*?</script>|<style\b.*?</style>", " ", self.page, flags=re.S)
        text = html.unescape(re.sub(r"<[^>]+>", " ", text))
        for state in (s for d in self.data["demos"] for s in d["states"].values()):
            text += " " + state["interpretation"] + " " + " ".join(" ".join(p) for p in state["metrics"])
        for bad in ("\u2014", "\u2013", "--", "\u2212"):
            self.assertNotIn(bad, text)
        for term in ("matplotlib", "numpy", "python", "jupyter"):
            self.assertNotIn(term, text.lower())
        self.assertIn("constructed", text.lower())

    def test_links_offline_and_accessibility(self):
        self.assertIsNone(re.search(r'(src|href)="(https?:)?//', self.page))
        self.assertIn("../../notebooks/02-four-cell-interaction.ipynb", self.page)
        self.assertIn('<a class="skip" href="#main">', self.page)
        self.assertIn("<noscript>", self.page)
        for d in self.data["demos"]:
            for c in d["controls"]:
                self.assertIn(f'<label for="{d["id"]}-{c["key"]}">', self.page)

    def test_dom_harness(self):
        if shutil.which("node") is None:
            self.skipTest("Node is not installed; the DOM harness needs it")
        run = subprocess.run(["node", str(HARNESS), str(self.reader)], capture_output=True, text=True, timeout=120)
        self.assertEqual(run.returncode, 0, run.stderr)
        report = json.loads(run.stdout)["reports"][0]
        self.assertEqual((report["states_checked"], report["resets_checked"], report["labelled_controls"]), (42, 4, 9))


if __name__ == "__main__":
    unittest.main()
