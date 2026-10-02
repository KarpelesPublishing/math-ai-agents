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


SINGLES = {
    "p only 0.30, i only 0.25 (Table 2.1)": (F(30, 100), F(25, 100)),
    "p only 0.55, i only 0.50 (second example)": (F(55, 100), F(50, 100)),
}
TABLE = "p only 0.30, i only 0.25 (Table 2.1)"
SECOND = "p only 0.55, i only 0.50 (second example)"
FOUR = "Four cells, Equation (2.1)"
THREE = "Three cells (neither score left out)"


def gamma(neither, p, i, both):
    return both - p - i + neither


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
        demo = self.demos[demo_id]
        for key, state in demo["states"].items():
            idx = [int(i) for i in key.split(",")]
            values = [as_number(c["values"][i]) for c, i in zip(demo["controls"], idx)]
            yield values, dict(state["metrics"]), state

    def test_four_demonstrations_all_states_rendered(self):
        self.assertEqual(list(self.demos), ["C02-D01", "C02-D02", "C02-D03", "C02-D04"])
        self.assertEqual([len(d["states"]) for d in self.data["demos"]], [8, 6, 4, 8])
        self.assertLessEqual(self.reader.stat().st_size, 2_500_000)
        for demo in self.data["demos"]:
            for state in demo["states"].values():
                self.assertTrue(state["image"].startswith("data:image/svg+xml"))

    def test_d01_contrast_for_every_state(self):
        singles = SINGLES
        seen = {}
        for (both, kind), m, _ in self.states("C02-D01"):
            p, i = singles[kind]
            both_f = F(str(both))
            g = gamma(F(20, 100), p, i, both_f)
            additive = p + i - F(20, 100)
            self.assertEqual(m["Interaction contrast Gamma"], two(g), (both, kind))
            self.assertEqual(m["Additive prediction"], two(additive))
            self.assertEqual(m["Joint gain (both minus neither)"], two(both_f - F(20, 100)))
            sign = "zero" if g == 0 else ("positive" if g > 0 else "negative")
            self.assertEqual(m["Sign of Gamma"], sign)
            seen[(both, kind)] = g
        # Table 2.1: 0.80 - 0.30 - 0.25 + 0.20 = 0.45; the book's negative example: -0.15; an exact zero.
        self.assertEqual(seen[(0.8, TABLE)], F(45, 100))
        self.assertEqual(seen[(0.7, SECOND)], F(-15, 100))
        self.assertEqual(seen[(0.35, TABLE)], 0)
        self.assertIn("0.80 - 0.30 - 0.25 + 0.20 = 0.45", self.page)
        self.assertIn("0.70 - 0.55 - 0.50 + 0.20 = -0.15", self.page)

    def test_d01_identity_split_holds_in_every_state(self):
        # Equation (2.2): joint gain = gain from p + gain from i + Gamma.
        singles = SINGLES
        for (both, kind), m, _ in self.states("C02-D01"):
            p, i = singles[kind]
            joint = F(str(both)) - F(20, 100)
            self.assertEqual(joint, (p - F(20, 100)) + (i - F(20, 100)) + gamma(F(20, 100), p, i, F(str(both))))
            self.assertEqual(m["Joint gain (both minus neither)"], two(joint))

    def test_d02_baseline_and_three_cell_drift(self):
        for (baseline, method), m, _ in self.states("C02-D02"):
            b = F(str(baseline))
            a_cells = (F(20, 100), F(30, 100), F(25, 100), F(80, 100))
            b_cells = (b, b + F(2, 100), b + F(1, 100), F(80, 100))
            four_a, four_b = gamma(*a_cells), gamma(*b_cells)
            self.assertEqual(four_a, F(45, 100))
            self.assertEqual(four_b, F(77, 100) - b)           # 0.80 - (b + 0.02) - (b + 0.01) + b
            three_a = a_cells[3] - a_cells[1] - a_cells[2]
            three_b = b_cells[3] - b_cells[1] - b_cells[2]
            self.assertEqual(three_a, four_a - a_cells[0])      # the baseline was removed twice
            self.assertEqual(three_b, four_b - b)
            self.assertEqual(m["System A, four-cell Gamma"], two(four_a))
            self.assertEqual(m["System B, four-cell Gamma"], two(four_b))
            self.assertEqual(m["System A, three cells"], two(three_a))
            self.assertEqual(m["System B, three cells"], two(three_b))
            self.assertEqual(m["System B baseline"], two(b))
        book = next(m for v, m, _ in self.states("C02-D02") if v == [0.7, FOUR])
        self.assertEqual((book["System A, four-cell Gamma"], book["System B, four-cell Gamma"]), ("0.45", "0.07"))
        negative = next(m for v, m, _ in self.states("C02-D02") if v == [0.7, THREE])
        self.assertEqual(negative["System B, three cells"], "-0.63")
        self.assertIn("0.80 - 0.72 - 0.71 + 0.70 = 0.07", self.page)

    def test_d03_share_domain_and_undefined_ratio(self):
        cells = {
            "Table 2.1 (ratio 0.75)": (F(20, 100), F(30, 100), F(25, 100), F(80, 100)),
            "Small gain (amount 0.02)": (F(50, 100), F(50, 100), F(50, 100), F(52, 100)),
            "Negative example (ratio -0.30)": (F(20, 100), F(55, 100), F(50, 100), F(70, 100)),
            "Zero joint gain (ratio undefined)": (F(50, 100), F(60, 100), F(50, 100), F(50, 100)),
        }
        for (key,), m, state in self.states("C02-D03"):
            u = cells[key]
            g = gamma(*u)
            joint = u[3] - u[0]
            valid = joint > 0 and u[1] - u[0] >= 0 and u[2] - u[0] >= 0 and g >= 0
            self.assertEqual(m["Interaction contrast (amount)"], two(g))
            self.assertEqual(m["Joint gain"], two(joint))
            if joint == 0:
                self.assertTrue(m["Ratio Gamma / joint gain"].startswith("undefined"))
                self.assertIn("undefined", state["interpretation"])
            else:
                self.assertEqual(m["Ratio Gamma / joint gain"], two(g / joint))
            self.assertEqual(m["Valid as a fraction"].startswith("yes"), valid, key)
            if valid:
                self.assertTrue(0 <= g / joint <= 1)
        by_key = {k: m for (k,), m, _ in self.states("C02-D03")}
        self.assertEqual(by_key["Table 2.1 (ratio 0.75)"]["Ratio Gamma / joint gain"], "0.75")
        negative = by_key["Negative example (ratio -0.30)"]
        self.assertEqual(negative["Ratio Gamma / joint gain"], "-0.30")
        self.assertTrue(negative["Valid as a fraction"].startswith("no"))
        self.assertEqual(by_key["Small gain (amount 0.02)"]["Ratio Gamma / joint gain"], "1.00")

    def test_d04_standard_errors_and_intervals(self):
        for (n, true_g), m, _ in self.states("C02-D04"):
            n = int(n)
            sigma = F(4, 10)
            # Variance of the four-cell sum of independent cells: 4 sigma^2 / n.
            var_cell = sigma ** 2 / n
            se_cell = math.sqrt(var_cell)
            se_gamma = math.sqrt(4 * var_cell)
            se_diff = math.sqrt(2 * var_cell)
            self.assertAlmostEqual(se_gamma, 2 * se_cell, places=12)
            half = 1.96 * se_gamma
            lo, hi = true_g - half, true_g + half
            self.assertEqual(m["Standard error of one cell"], three(se_cell))
            self.assertEqual(m["Standard error of Gamma"], three(se_gamma))
            self.assertEqual(m["Standard error of a difference of two intact scores"], three(se_diff))
            self.assertEqual(m["Interval for Gamma"], f"{three(lo)} to {three(hi)}")
            self.assertEqual(m["Smallest Gamma that clears zero"], three(half))
            self.assertEqual(m["Interval excludes zero"], "yes" if lo > 0 else "no")
        by_state = {tuple(v): m for v, m, _ in self.states("C02-D04")}
        self.assertEqual(by_state[(1600, 0.05)]["Smallest Gamma that clears zero"], "0.039")  # 1.96 x 0.020
        self.assertEqual(by_state[(1600, 0.05)]["Interval excludes zero"], "yes")
        self.assertEqual(by_state[(400, 0.05)]["Interval excludes zero"], "no")
        self.assertEqual(by_state[(100, 0.15)]["Interval excludes zero"], "no")      # lower end 0.15 - 0.157
        self.assertEqual(by_state[(400, 0.15)]["Interval excludes zero"], "yes")

    # Reader patch (group 1): corrected sentences and regression checks for the old, wrong text.

    def test_d01_check_answer_compares_gain_with_gain(self):
        # Adding the isolated gains: 0.35 + 0.30 = 0.65; the additive score is 0.20 + 0.65 = 0.85.
        self.assertEqual(F(35, 100) + F(30, 100), F(65, 100))
        self.assertEqual(F(20, 100) + F(65, 100), F(85, 100))
        text = html.unescape(self.page)
        self.assertIn("its gain is 0.50 against 0.65 predicted by adding the isolated gains", text)
        self.assertIn("scores 0.70 rather than the additive 0.85", text)
        self.assertNotIn("0.50 against 0.85", text)

    def test_d02_contrast_comparison_follows_the_state(self):
        # Four-cell states of System B: baseline 0.30 -> 0.47 (larger than A's 0.45), 0.50 -> 0.27, 0.70 -> 0.07.
        expected = {0.3: ("larger than", "0.47", "0.50"), 0.5: ("smaller than", "0.27", "0.30"), 0.7: ("smaller than", "0.07", "0.10")}
        for (baseline, method), m, state in self.states("C02-D02"):
            text = state["interpretation"]
            self.assertNotIn("and its contrast is smaller", text)
            self.assertNotIn("adds only", text)
            if method != FOUR:
                continue
            word, g, joint = expected[baseline]
            self.assertIn(f"B's contrast {g} is {word} A's 0.45", text, baseline)
            self.assertIn(f"{joint} of improvement against 0.60 for A", text, baseline)
        # Exact check of the three baselines with fractions.
        for b, (word, g, _) in expected.items():
            gb = gamma(F(str(b)), F(str(b)) + F(2, 100), F(str(b)) + F(1, 100), F(80, 100))
            self.assertEqual(f"{float(gb):.2f}", g)
            self.assertEqual(gb > F(45, 100), word == "larger than")

    def test_d04_wording_claims_only_what_is_computed(self):
        self.assertIn("Is the contrast clearly different from zero?", self.page)
        self.assertNotIn("survive a rerun", self.page)
        self.assertNotIn("second run", self.page)
        self.assertNotIn("borderline", self.page)
        self.assertNotIn("even though a same-size difference of intact scores (lower end -", self.page)
        by = {tuple(v): s["interpretation"] for v, _, s in self.states("C02-D04")}
        # 100 trials, true 0.15: Gamma interval -0.007 to 0.307, intact difference lower end 0.039 (resolved).
        self.assertIn("is not clear of zero here, even though a same-size difference of intact scores (lower end 0.039) is resolved.",
                      by[(100, 0.15)])
        # 100 trials, true 0.05: both unresolved.
        self.assertIn("is not clear of zero here, and a same-size difference of intact scores (lower end -0.061) is also unresolved.",
                      by[(100, 0.05)])
        self.assertIn("the interval for Gamma excludes zero at this size", by[(400, 0.15)])
        self.assertIn("compare the two intervals at 100 trials and a true amount of 0.15", self.page)

    def test_symbols_define_theta_and_intact_score(self):
        text = html.unescape(self.page)
        self.assertGreaterEqual(text.count("is the frozen model"), 4)  # one definition in each demonstration
        self.assertEqual(text.count("An intact score is the score with both operations on"), 2)

    def test_more_trials_never_widen_the_interval(self):
        for true_g in (0.05, 0.15):
            widths = [float(m["Smallest Gamma that clears zero"]) for (n, g), m, _ in self.states("C02-D04")
                      if g == true_g]
            self.assertEqual(widths, sorted(widths, reverse=True))

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
        self.assertEqual(combos, 26)
        self.assertEqual(len(set(itertools.chain.from_iterable(
            [s["image"] for s in d["states"].values()] for d in self.data["demos"]))), 26)

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
        self.assertEqual(self.page.count('aria-live="polite"'), 4)
        for d in self.data["demos"]:
            for c in d["controls"]:
                self.assertIn(f'<label for="{d["id"]}-{c["key"]}">', self.page)

    def test_dom_harness(self):
        if shutil.which("node") is None:
            self.skipTest("Node is not installed; the DOM harness needs it")
        run = subprocess.run(["node", str(HARNESS), str(self.reader)], capture_output=True, text=True, timeout=120)
        self.assertEqual(run.returncode, 0, run.stderr)
        report = json.loads(run.stdout)["reports"][0]
        self.assertEqual((report["states_checked"], report["resets_checked"], report["labelled_controls"]), (26, 4, 7))


if __name__ == "__main__":
    unittest.main()
