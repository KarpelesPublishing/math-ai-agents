"""Chapter 22 laboratory reader: independent hand checks of the built page.

Every expected number is recomputed here from the chapter's own arithmetic
(the two-policy table, the one-update bound, the tail measure of the
constructed lottery, the four-action authority example), not read back from
the module that produced the page. The reader is built fresh into a
temporary directory, so nothing under readers/ is touched.
"""
from __future__ import annotations

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

from math_ai_agents.chapters.ch22 import evaluate

HERE = Path(__file__).resolve().parent
LAB = HERE.parent
WRAPPER = LAB / "tools" / "readers" / "build_readers.py"
HARNESS = LAB / "tools" / "readers" / "engine" / "dom_harness.js"
SLUG = "22-risk-authority-contract"


def _builder_python():
    spec = importlib.util.spec_from_file_location("reader_engine_tests", HERE / "test_readers_engine.py")
    helpers = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helpers)
    return helpers.builder_python()


def authored_demos(number):
    """The authored CHAPTER dictionary of the module under test, keyed by demonstration id (for wording checks)."""
    import sys
    for p in (str(LAB / "tools" / "readers" / "engine"), str(LAB / "src")):
        if p not in sys.path:
            sys.path.insert(0, p)
    spec = importlib.util.spec_from_file_location(f"reader_ch{number}_wording", LAB / "tools" / "readers" / "chapters" / f"ch{number}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return {d["id"]: d for d in mod.CHAPTER["demos"]}


def payload(text):
    match = re.search(r'<script id="reader-data" type="application/json">(.*?)</script>', text, re.S)
    return json.loads(match.group(1))


def as_number(text):
    try:
        return float(text)
    except ValueError:
        return text


def f1(x):
    return f"{x:.1f}"


class Chapter22ReaderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        python = _builder_python()
        if python is None:
            raise unittest.SkipTest("no interpreter with numpy, matplotlib and jinja2 (laboratory .venv absent)")
        cls._tmp = tempfile.TemporaryDirectory()
        run = subprocess.run([python, str(WRAPPER), "--chapters", "22", "--out", cls._tmp.name], capture_output=True, text=True,
                             timeout=600, env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
        if run.returncode != 0:
            raise AssertionError(run.stdout + run.stderr)
        cls.reader = Path(cls._tmp.name) / SLUG / "reader.html"
        cls.page = cls.reader.read_text(encoding="utf-8")
        cls.data = payload(cls.page)
        cls.demos = {d["id"]: d for d in cls.data["demos"]}

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def states(self, demo_id):
        demo = self.demos[demo_id]
        for key, state in demo["states"].items():
            idx = [int(i) for i in key.split(",")]
            values = [as_number(c["values"][i]) for c, i in zip(demo["controls"], idx)]
            yield values, dict(state["metrics"]), state

    def test_four_demonstrations_all_states_render(self):
        self.assertEqual(list(self.demos), ["C22-D01", "C22-D02", "C22-D03", "C22-D04"])
        self.assertEqual([len(d["states"]) for d in self.data["demos"]], [6, 6, 8, 6])
        for demo in self.data["demos"]:
            combos = math.prod(len(c["values"]) for c in demo["controls"])
            self.assertEqual(len(demo["states"]), combos)
            for state in demo["states"].values():
                self.assertTrue(state["image"].startswith("data:image/svg+xml"))
                self.assertTrue(state["interpretation"])

    def test_size_budget(self):
        self.assertLess(self.reader.stat().st_size, 2_500_000)

    # Demonstration 1: Careful (8, 0.5) and Aggressive (12, 1.5)

    def test_d01_penalty_and_constraint_by_hand(self):
        for (lam, limit), m, _ in self.states("C22-D01"):
            careful, aggressive = 8 - lam * 0.5, 12 - lam * 1.5
            self.assertEqual(m["Careful score"], f1(careful))
            self.assertEqual(m["Aggressive score"], f1(aggressive))
            if abs(careful - aggressive) < 1e-9:
                self.assertTrue(m["Penalty rule picks"].startswith("tie"))
            else:
                self.assertEqual(m["Penalty rule picks"], "Careful" if careful > aggressive else "Aggressive")
            # Constraint rule: cost at most the limit, then larger reward.
            policies = {"Careful": (8, 0.5), "Aggressive": (12, 1.5)}
            eligible = {n: r for n, (r, c) in policies.items() if c <= limit}
            self.assertEqual(m["Constraint rule picks"], max(eligible, key=eligible.get))
            self.assertEqual(m["Penalty at which the penalty rule flips"], "4.0")

    def test_d01_book_numbers_and_tie(self):
        by = {tuple(v): m for v, m, _ in self.states("C22-D01")}
        # The chapter: multiplier 2 gives 7 and 9, the penalty rule picks Aggressive, the constraint rule Careful.
        m = by[(2, 1)]
        self.assertEqual((m["Careful score"], m["Aggressive score"]), ("7.0", "9.0"))
        self.assertEqual((m["Penalty rule picks"], m["Constraint rule picks"]), ("Aggressive", "Careful"))
        # Multiplier exactly 4 is a tie (6 = 6) and is reported as one.
        self.assertEqual((by[(4, 1)]["Careful score"], by[(4, 1)]["Aggressive score"]), ("6.0", "6.0"))
        self.assertTrue(by[(4, 1)]["Penalty rule picks"].startswith("tie"))
        # Above 4 the penalty ranking reverses; the constraint rule at limit 1 never moves.
        self.assertEqual(by[(6, 1)]["Penalty rule picks"], "Careful")
        self.assertEqual({by[(lam, 1)]["Constraint rule picks"] for lam in (2, 4, 6)}, {"Careful"})
        # A limit of 2 admits both policies, so the higher reward wins.
        self.assertEqual(by[(6, 2)]["Constraint rule picks"], "Aggressive")
        self.assertEqual(by[(6, 2)]["Policies within the limit"], "Careful and Aggressive")

    def test_d01_default_interpretation_shows_the_hand_sum(self):
        self.assertIn("8 - 2 x 0.5 = 7.0", self.page)
        self.assertIn("12 - 2 x 1.5 = 9.0", self.page)

    # Demonstration 2: d = 10, epsilon = 0.1, margin 0.5

    def test_d02_allowance_by_hand(self):
        for (delta, gamma), m, _ in self.states("C22-D02"):
            allowance = math.sqrt(2 * delta) * gamma * 0.1 / (1 - gamma) ** 2
            self.assertEqual(m["Allowance above the aimed level"], f"{allowance:.3f}")
            self.assertEqual(m["Worst case when aiming at the limit"], f"{10 + allowance:.3f}")
            self.assertEqual(m["Worst case when aiming at the ceiling"], f"{9.5 + allowance:.3f}")
            self.assertEqual(m["Margin covers the allowance"], "yes" if allowance < 0.5 else "no")
        by = {tuple(v): m for v, m, _ in self.states("C22-D02")}
        # Hand values: 0.1 x 0.85 x 0.1 / 0.0225 = 0.3778 and 0.2 x 0.85 x 0.1 / 0.0225 = 0.7556.
        self.assertEqual(by[(0.005, 0.85)]["Allowance above the aimed level"], "0.378")
        self.assertEqual(by[(0.02, 0.85)]["Allowance above the aimed level"], "0.756")
        self.assertEqual(by[(0.005, 0.5)]["Allowance above the aimed level"], "0.020")  # 0.1 x 0.5 x 0.1 / 0.25
        # The plus sign matters: the bound never sits below the limit, so a start at the limit always may exceed it.
        for m in by.values():
            self.assertGreater(float(m["Worst case when aiming at the limit"]), 10.0)

    def test_d02_larger_step_and_discount_enlarge_the_allowance(self):
        by = {tuple(v): float(m["Allowance above the aimed level"]) for v, m, _ in self.states("C22-D02")}
        for gamma in (0.5, 0.8, 0.85):
            self.assertAlmostEqual(by[(0.02, gamma)], by[(0.005, gamma)] * 2, places=2)  # sqrt(4x) = 2 sqrt(x)
        for delta in (0.005, 0.02):
            self.assertLess(by[(delta, 0.5)], by[(delta, 0.8)])
            self.assertLess(by[(delta, 0.8)], by[(delta, 0.85)])

    def test_d02_ceiling_row_is_labelled_as_a_replaced_limit(self):
        # Finding g8-05: the lower row replaces d by d minus the margin; it is not only a different start.
        for _, _, state in self.states("C22-D02"):
            text = state["interpretation"]
            self.assertIn("the bound is applied with the ceiling in place of d", text)
            self.assertIn("9.5 +", text)
            self.assertNotIn("From the ceiling", text)
            self.assertNotIn("Start at the ceiling", text)
        for key in ("Worst case from a start at the ceiling", "Allowance above the start"):
            for _, m, _ in self.states("C22-D02"):
                self.assertNotIn(key, m)

    def test_d02_symbols_and_explanation_wording(self):
        # Findings g8-04 and g8-06: square-root scaling, absolute expected advantage, named margin symbol.
        demo = authored_demos(22)["C22-D02"]
        self.assertIn("proportion to the square root of the step", demo["explanation"])
        self.assertNotIn("scales it up directly", demo["explanation"])
        self.assertIn("largest absolute expected constraint advantage", demo["symbols"])
        self.assertIn("epsilon_safe", demo["symbols"])
        by = {tuple(v): float(m["Allowance above the aimed level"]) for v, m, _ in self.states("C22-D02")}
        # Four times the step gives only twice the allowance (0.378 then 0.756 at gamma 0.85).
        self.assertAlmostEqual(by[(0.02, 0.85)] / by[(0.005, 0.85)], 2.0, places=2)

    # Demonstration 3: C = 100 with probability p, else 0

    @staticmethod
    def cvar_by_tail_average(alpha, p):
        """Average cost over the worst (1 - alpha) share of probability, by sorting the two outcomes."""
        outcomes = [(100.0, p), (0.0, 1 - p)]  # worst first
        remaining = 1 - alpha
        total = 0.0
        for cost, prob in outcomes:
            take = min(prob, remaining)
            total += cost * take
            remaining -= take
        return total / (1 - alpha)

    @staticmethod
    def cvar_by_search(alpha, p):
        """Equation (22.5) by brute force over a fine grid of cutoffs z."""
        best = None
        for k in range(-1000, 11001):
            z = k / 100
            value = z + (p * max(100 - z, 0) + (1 - p) * max(0 - z, 0)) / (1 - alpha)
            best = value if best is None or value < best else best
        return best

    def test_d03_cvar_two_independent_ways(self):
        for (alpha, p), m, _ in self.states("C22-D03"):
            expected = self.cvar_by_tail_average(alpha, p)
            self.assertAlmostEqual(expected, self.cvar_by_search(alpha, p), places=6)
            self.assertEqual(m["Tail average (CVaR)"], f1(expected))
            self.assertEqual(m["Mean cost"], f1(100 * p))

    def test_d03_book_lottery(self):
        by = {tuple(v): m for v, m, _ in self.states("C22-D03")}
        book = by[(0.99, 0.01)]  # expected loss 1, CVaR_.99 = 100
        self.assertEqual((book["Mean cost"], book["Tail average (CVaR)"]), ("1.0", "100.0"))
        self.assertEqual(by[(0.9, 0.01)]["Tail average (CVaR)"], "10.0")  # zeros dilute a wide tail
        self.assertEqual(by[(0.95, 0.05)]["Tail average (CVaR)"], "100.0")  # boundary: tail share equals p
        self.assertEqual(by[(0.9, 0.05)]["Tail average (CVaR)"], "50.0")
        # CVaR can never exceed the worst outcome.
        for m in by.values():
            self.assertLessEqual(float(m["Tail average (CVaR)"]), 100.0)

    def test_d03_flat_minimum_is_stated(self):
        _, _, state = next(s for s in self.states("C22-D03") if s[0] == [0.99, 0.01])
        self.assertIn("flat", state["interpretation"])
        self.assertIn("0 + 1.0 / 0.01 = 100.0", state["interpretation"])

    def test_d03_cut_off_sentence_only_when_the_curve_exceeds_the_axis(self):
        # Finding g8-01: the curve is plotted for z in [-10, 110] against a y limit of 230.
        for (alpha, p), _, state in self.states("C22-D03"):
            top = max(z + (p * max(100 - z, 0) + (1 - p) * max(0 - z, 0)) / (1 - alpha) for z in (k / 2 - 10 for k in range(241)))
            text = state["interpretation"]
            if top > 230:
                self.assertIn("rises above the top of the left plot", text)
            else:
                self.assertIn("fits inside the left plot", text)
            self.assertNotIn("The curve is cut off at the top of the left plot", text)
        by = {tuple(v): s["interpretation"] for v, _, s in self.states("C22-D03")}
        for key in ((0.9, 0.01), (0.9, 0.05), (0.95, 0.01)):  # maxima 110, 140, 210: nothing is cut off
            self.assertIn("fits inside the left plot", by[key])
        self.assertIn("rises above the top of the left plot", by[(0.99, 0.01)])

    def test_d03_prediction_and_check_wording(self):
        demo = authored_demos(22)["C22-D03"]
        # Both 0.99 and 0.995 give 100 at p = 0.01, so the question asks for the offered levels, plural.
        self.assertIn("which of the offered tail levels give a tail average of 100", demo["prediction"])
        by = {tuple(v): m["Tail average (CVaR)"] for v, m, _ in self.states("C22-D03")}
        self.assertEqual((by[(0.99, 0.01)], by[(0.995, 0.01)], by[(0.9, 0.01)]), ("100.0", "100.0", "10.0"))

    # Demonstration 4: the laboratory's four actions

    ACTIONS = [("fast-release", 10, 0.3, False), ("reviewed-release", 5, 0.05, True),
               ("risky-authorized", 8, 0.2, True), ("abstain", 0, 0.0, True)]

    def test_d04_choices_by_hand(self):
        for (limit, penalty), m, _ in self.states("C22-D04"):
            values = {n: r - penalty * k for n, r, k, _ in self.ACTIONS}
            top = max(values, key=values.get)
            authorized = {n: values[n] for n, _, _, a in self.ACTIONS if a}
            eligible = {n: r for n, r, k, a in self.ACTIONS if a and k <= limit}
            self.assertEqual(m["Penalty pick over all rows"], top)
            self.assertEqual(m["Penalty pick among authorized rows"], max(authorized, key=authorized.get))
            self.assertEqual(m["Constraint pick"], max(eligible, key=eligible.get))
            self.assertEqual(m["Eligible actions"], f"{len(eligible)} of 4")
            self.assertNotIn("fast-release", m["Constraint pick"])

    def test_d04_chapter_numbers(self):
        by = {tuple(v): m for v, m, _ in self.states("C22-D04")}
        default = by[(0.1, 5)]
        self.assertEqual(default["Penalty pick over all rows"], "fast-release")      # 10 - 5 x 0.3 = 8.5
        self.assertEqual(default["Penalty pick among authorized rows"], "risky-authorized")  # 8 - 5 x 0.2 = 7
        self.assertEqual(default["Constraint pick"], "reviewed-release")
        self.assertEqual(by[(0.25, 5)]["Constraint pick"], "risky-authorized")
        self.assertEqual(by[(0.25, 5)]["Removed by authority"], "fast-release")
        # Boundary: a limit of zero leaves only the explicit abstain row.
        self.assertEqual(by[(0, 5)]["Constraint pick"], "abstain")
        self.assertEqual(by[(0, 5)]["Eligible actions"], "1 of 4")
        # A large penalty can make the penalty rule agree with the gate in one state and not in the next.
        self.assertEqual(by[(0.1, 25)]["Penalty pick over all rows"], by[(0.1, 25)]["Constraint pick"])
        self.assertNotEqual(by[(0.25, 25)]["Penalty pick over all rows"], by[(0.25, 25)]["Constraint pick"])
        self.assertIn("10 - 5 x 0.3 = 8.50", self.page)
        self.assertIn("8 - 5 x 0.2 = 7.00", self.page)

    def test_check_questions_are_marked_as_hand_work_when_not_on_a_control(self):
        # Finding g8-03: the check values 3, 0.9, 0.02/0.97 and 0.2 are not selectable, so the page says so.
        for demo_id in ("C22-D01", "C22-D02", "C22-D03", "C22-D04"):
            self.assertIn("by hand", authored_demos(22)[demo_id]["check"])
        self.assertIn("between which two", authored_demos(22)["C22-D01"]["prediction"].lower())

    def test_d04_constraint_pick_is_named_on_the_left_panel_and_symbols_are_mapped(self):
        demo = authored_demos(22)["C22-D04"]
        self.assertIn("Ret is the reward, Cost is the risk, d_i is the risk limit and lambda_safe is the penalty", demo["symbols"])
        self.assertIn("provided abstain is authorized", demo["application"])
        self.assertIn("not taken from the chapter", demo["provenance"])

    def test_d04_laboratory_function_boundaries(self):
        rows = [{"name": n, "reward": r, "risk": k, "authorized": a} for n, r, k, a in self.ACTIONS]
        # Limit exactly equal to a risk meets the contract (0.2 <= 0.2); fast-release stays forbidden.
        out = evaluate({"risk_limit": 0.2, "risk_penalty": 5, "actions": rows})
        self.assertEqual(out["metrics"]["constrained_choice"], "risky-authorized")
        # The laboratory's transfer case: limit 0, penalty 100, only wait is feasible.
        out = evaluate({"risk_limit": 0, "risk_penalty": 100, "actions": [
            {"name": "act", "reward": 20, "risk": 0.01, "authorized": True},
            {"name": "wait", "reward": -1, "risk": 0, "authorized": True}]})
        self.assertEqual(out["metrics"]["constrained_choice"], "wait")
        self.assertEqual(out["metrics"]["unconstrained_penalty_choice"], "act")  # 20 - 100 x 0.01 = 19 > -1

    # Page-level checks

    def test_displayed_equations_are_chapter_equations(self):
        chapter = next(c for c in json.loads((LAB / "chapter-map.json").read_text()) if c["chapter"] == 22)

        def norm(t):
            t = re.sub(r"\\tag\{[^}]*\}", "", t)
            t = re.sub(r"\\[,;:!]", "", t)
            return re.sub(r"[\s{}]", "", t).rstrip(".")
        allowed = {norm(e["tex"]) for e in chapter["equations"]}
        alts = re.findall(r'alt="Equation: ([^"]+)"', self.page)
        self.assertEqual(len(alts), 7)  # 2 + 2 + 1 + 2 equations
        for tex in alts:
            self.assertIn(norm(html.unescape(tex)), allowed)

    def test_source_sections_exist_in_the_canonical_chapter(self):
        text = (LAB.parent / "Manuscript" / "part-vi" / "22-safe-enough-to-act.md").read_text(encoding="utf-8")
        headings = {line.lstrip("#").strip() for line in text.splitlines() if line.startswith("#")}
        expected = ["Fixed penalties make a hidden exchange rate", "A constraint is not a promise",
                    "Other risk contracts", "Authority is an operating envelope"]
        for title in expected:
            self.assertIn(title, headings)
            self.assertIn(html.escape(title), self.page)

    def test_links_and_offline(self):
        for href in (f"../../notebooks/{SLUG}.ipynb", "../../skills/maa-22-risk-authority-contract/SKILL.md", "../index.html"):
            self.assertIn(f'href="{href}"', self.page)
        self.assertIsNone(re.search(r'(src|href)="(https?:)?//', self.page))

    def test_page_text_has_no_dashes_or_dependency_names(self):
        text = re.sub(r"<script\b.*?</script>|<style\b.*?</style>", " ", self.page, flags=re.S)
        text = html.unescape(re.sub(r"<[^>]+>", " ", text))
        for state in (s for d in self.data["demos"] for s in d["states"].values()):
            text += " " + state["interpretation"] + " " + " ".join(" ".join(p) for p in state["metrics"])
        for bad in ("\u2014", "\u2013", "--"):
            self.assertNotIn(bad, text)
        for term in ("matplotlib", "numpy", "python", "jupyter"):
            self.assertNotIn(term, text.lower())
        self.assertIn("constructed", text.lower())

    def test_dom_harness(self):
        if shutil.which("node") is None:
            self.skipTest("Node is not installed; the DOM harness needs it")
        run = subprocess.run(["node", str(HARNESS), str(self.reader)], capture_output=True, text=True, timeout=120)
        self.assertEqual(run.returncode, 0, run.stderr)
        report = json.loads(run.stdout)["reports"][0]
        self.assertEqual((report["states_checked"], report["resets_checked"], report["labelled_controls"]), (26, 4, 8))


if __name__ == "__main__":
    unittest.main()
