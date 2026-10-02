"""Chapter 14 laboratory reader: independent hand checks of the built page.

Every expected number is recomputed here from the chapter's own arithmetic
(Equations 14.1 to 14.4, the Figure 14.2 case and the priced twenty-step
plan), not read back from the module that produced the page. The reader is
built into a temporary directory, so the test never touches the committed
readers folder.
"""
from __future__ import annotations

import html
import json
from fractions import Fraction
import math
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
LAB = HERE.parent
WRAPPER = LAB / "tools" / "readers" / "build_readers.py"
HARNESS = LAB / "tools" / "readers" / "engine" / "dom_harness.js"
VENV_PYTHON = LAB / ".venv" / "bin" / "python"


def payload(text):
    match = re.search(r'<script id="reader-data" type="application/json">(.*?)</script>', text, re.S)
    return json.loads(match.group(1))


def metrics(state):
    return dict(state["metrics"])


def as_number(text):
    try:
        return float(text)
    except ValueError:
        return text


def tv(p, q):
    return 0.5 * sum(abs(a - b) for a, b in zip(p, q))


@unittest.skipUnless(VENV_PYTHON.is_file(), "laboratory .venv absent; cannot build the reader")
class Chapter14ReaderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        run = subprocess.run([str(VENV_PYTHON), str(WRAPPER), "--chapters", "14", "--out", cls.tmp.name],
                             capture_output=True, text=True, timeout=600)
        if run.returncode != 0:
            raise RuntimeError(run.stdout + run.stderr)
        cls.reader = Path(cls.tmp.name) / "14-transition-model-bound" / "reader.html"
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
            yield values, state

    def test_four_demonstrations_with_state_budget(self):
        self.assertEqual(list(self.demos), ["C14-D01", "C14-D02", "C14-D03", "C14-D04"])
        self.assertEqual([len(d["states"]) for d in self.data["demos"]], [6, 8, 6, 6])
        self.assertLess(self.reader.stat().st_size, 2_500_000)

    def test_d01_epsilon_is_the_largest_row_error(self):
        true_rows = [[0.9, 0.1], [0.2, 0.8]]
        for (d0, d1), state in self.states("C14-D01"):
            model_rows = [[0.9 - d0, 0.1 + d0], [0.2 + d1, 0.8 - d1]]
            row_errors = [tv(p, q) for p, q in zip(true_rows, model_rows)]
            m = metrics(state)
            self.assertEqual(m["Epsilon (largest row error)"], f"{max(row_errors):.2f}")
            self.assertEqual(m["Average row error"], f"{sum(row_errors) / 2:.2f}")
            self.assertEqual(m["Error in state 1"], f"{row_errors[0]:.2f}")
            self.assertEqual(m["Error in state 2"], f"{row_errors[1]:.2f}")
        worst = metrics(self.demos["C14-D01"]["states"]["0,2"])  # 0.02 and 0.30
        self.assertEqual((worst["Epsilon (largest row error)"], worst["Average row error"]), ("0.30", "0.16"))
        # The chapter's transfer row: (0.5, 0.3, 0.2) against (0.4, 0.4, 0.2) is off by 0.10.
        self.assertAlmostEqual(tv([0.5, 0.3, 0.2], [0.4, 0.4, 0.2]), 0.10)

    def test_d02_bound_and_value_scale(self):
        for (gamma, eps), state in self.states("C14-D02"):
            bound = gamma * eps * 1 / (1 - gamma) ** 2
            scale = 1 / (1 - gamma)
            m = metrics(state)
            self.assertEqual(m["Bound gamma x error x R / (1-gamma)^2"], f"{bound:.2f}")
            self.assertEqual(m["Largest possible value R/(1-gamma)"], f"{scale:.1f}")
            self.assertEqual(m["Effective horizon 1/(1-gamma)"], f"{scale:.1f}")
            self.assertEqual(m["Bound as a share of that value"], f"{bound / scale:.3f}")
        book = metrics(self.demos["C14-D02"]["states"]["3,0"])  # gamma 0.99, eps 0.01: the chapter's "about a hundred"
        self.assertEqual(book["Bound gamma x error x R / (1-gamma)^2"], "99.00")
        # Twice the error at 0.99 exceeds the largest possible value of 100: the bound says nothing.
        vacuous = self.demos["C14-D02"]["states"]["3,1"]
        self.assertEqual(metrics(vacuous)["Bound gamma x error x R / (1-gamma)^2"], "198.00")
        self.assertIn("says nothing", vacuous["interpretation"])
        # Raising gamma from 0.9 to 0.99 at error 0.01 multiplies the bound by 110.
        low = float(metrics(self.demos["C14-D02"]["states"]["1,0"])["Bound gamma x error x R / (1-gamma)^2"])
        self.assertAlmostEqual(99.0 / low, 110.0, places=6)

    def test_d02_explanation_quotes_the_right_bound(self):
        # Reviewer finding g5-09: at gamma 0.9 and error 0.01 the bound is 0.9, not 0.09.
        page = html.unescape(self.page)
        self.assertIn("(0.9 to 99 at an error of 0.01)", page)
        self.assertNotIn("0.09 to 99", page)
        state = self.demos["C14-D02"]["states"]["1,0"]
        self.assertEqual(metrics(state)["Bound gamma x error x R / (1-gamma)^2"], "0.90")
        self.assertEqual(metrics(state)["Bound as a share of that value"], "0.090")  # 0.09 is the share, not the bound
        self.assertAlmostEqual(99.0 / 0.9, 110.0)
        # g5-10: the assumptions follow the chapter (worst case, tight for adversarial models, often loose).
        self.assertIn("tight for adversarial models", page)
        self.assertNotIn("Reward-model error would add a term", page)

    def test_d04_prediction_asks_about_the_scaling(self):
        # g5-11: the old prompt's literal answer (doubles) hid the lesson.
        page = html.unescape(self.page)
        self.assertNotIn("Does the certified horizon double, or grow by less?", page)
        self.assertIn("cut the error by 8 times, from 0.08 to 0.01. Does the certified horizon grow by 8 times, or by far less?", page)
        by_state = {tuple(v): int(metrics(s)["Certified horizon H*"]) for v, s in self.states("C14-D04")}
        high, low = by_state[("R = 10, gap 2 (priced plan)", 0.08)], by_state[("R = 10, gap 2 (priced plan)", 0.01)]
        self.assertEqual((high, low), (2, 4))  # an 8 times smaller error buys 2 times the horizon, not 8

    def test_d04_figure_says_what_it_leaves_out(self):
        # g5-12: omitted points and the dashed line are named in the figure itself.
        import base64
        for (scenario, eps), state in self.states("C14-D04"):
            svg = base64.b64decode(state["image"].split(",", 1)[1]).decode()
            reward, gap = (1, 0.5) if scenario.startswith("R = 1,") else (10, 2)
            values = [reward * eps * h * (h - 1) for h in range(1, 10)]
            first_fail = next(v for v in values if v >= gap)
            top = max(3.2 * gap, 1.5 * first_fail)
            hidden = [h for h, v in zip(range(1, 10), values) if v > 0.70 * top]
            self.assertIn("circle: certified; cross: not certified", svg)
            self.assertIn("dashed line: after the last certified horizon", svg)
            self.assertEqual("not drawn, above the plot" in svg, bool(hidden), (scenario, eps))
            # The first failing horizon is always drawn, so the reader sees where the certificate stops.
            self.assertNotIn(values.index(first_fail) + 1, hidden)

    def test_d03_symbols_define_the_best_action_and_delta(self):
        page = html.unescape(self.page)
        self.assertIn("a* is a best action", page)
        self.assertIn("the chapter's delta", page)
        self.assertIn("2 delta < Delta", page)

    def test_d03_model_choice_and_certificate(self):
        true = [0.9, 0.6, 0.2]
        names = ["Plan A", "Plan B", "Plan C"]
        for (delta, pattern), state in self.states("C14-D03"):
            if pattern.startswith("Shared"):
                model = [v + delta for v in true]
            else:
                model = [true[0] - delta, true[1] + delta, true[2]]
            gap = true[0] - true[1]
            top = max(model)
            winners = [n for n, v in zip(names, model) if abs(v - top) < 1e-9]
            m = metrics(state)
            self.assertEqual(m["True gap (Equation 14.3)"], f"{gap:.2f}")
            self.assertEqual(m["Twice the error"], f"{2 * delta:.2f}")
            self.assertEqual(m["Guarantee 2 x error < gap holds"], "yes" if Fraction(str(delta)) * 2 < Fraction("0.3") else "no")
            self.assertEqual(m["Model's own gap"], f"{model[0] - model[1]:.2f}")
            self.assertEqual(m["Model's choice"], " and ".join(winners) + (" (tie)" if len(winners) > 1 else ""))
            # The certificate is sound: whenever it holds, the model keeps the true best action.
            if m["Guarantee 2 x error < gap holds"] == "yes":
                self.assertEqual(winners, ["Plan A"])
        # Exact tie at error 0.15, adversarial: 0.9 - 0.15 = 0.6 + 0.15, and the strict test fails at equality.
        tie = metrics(self.demos["C14-D03"]["states"]["1,1"])
        self.assertEqual(tie["Model's choice"], "Plan A and Plan B (tie)")
        self.assertEqual(tie["Guarantee 2 x error < gap holds"], "no")
        # The same size of error as a shared offset reorders nothing, even though the guarantee is not claimed.
        shared = metrics(self.demos["C14-D03"]["states"]["2,0"])
        self.assertEqual((shared["Model's choice"], shared["Guarantee 2 x error < gap holds"]), ("Plan A", "no"))

    def test_d04_certified_horizon_by_brute_force(self):
        scenarios = {"R = 1, gap 0.5 (Figure 14.2)": (Fraction(1), Fraction("0.5")),
                     "R = 10, gap 2 (priced plan)": (Fraction(10), Fraction(2))}
        for (scenario, eps), state in self.states("C14-D04"):
            reward, gap = scenarios[scenario]
            e = Fraction(str(eps))
            certified = [h for h in range(1, 10) if reward * e * h * (h - 1) < gap]
            h_star = max(certified)
            m = metrics(state)
            self.assertEqual(m["Certified horizon H*"], str(h_star))
            self.assertEqual(m["First horizon that fails"], str(h_star + 1) if h_star < 9 else "none up to the cap")
            self.assertEqual(m[f"R x epsilon x H(H-1) at H* = {h_star}"], f"{float(reward * e * h_star * (h_star - 1)):.2f}")
            # Certified horizons are a prefix: nothing above H* passes.
            self.assertEqual(certified, list(range(1, h_star + 1)))
        by_state = {tuple(v): metrics(s)["Certified horizon H*"] for v, s in self.states("C14-D04")}
        # The chapter's numbers: Figure 14.2 (5 rewards); priced plan 2 rewards at 0.08 and 4 at 0.01.
        self.assertEqual(by_state[("R = 1, gap 0.5 (Figure 14.2)", 0.02)], "5")
        self.assertEqual(by_state[("R = 10, gap 2 (priced plan)", 0.08)], "2")
        self.assertEqual(by_state[("R = 10, gap 2 (priced plan)", 0.01)], "4")

    def test_d04_failure_by_equality_is_named(self):
        state = next(s for v, s in self.states("C14-D04") if v == ["R = 10, gap 2 (priced plan)", 0.01])
        self.assertIn("10 x 0.01 x 5 x 4 = 2.00", state["interpretation"])
        self.assertIn("fails by equality", state["interpretation"])
        self.assertIn("inconclusive", state["interpretation"])

    def test_hand_calculations_use_the_states_numbers(self):
        d1 = self.demos["C14-D01"]["states"]["0,0"]["interpretation"]
        self.assertIn("1/2 x (|0.88 - 0.90| + |0.12 - 0.10|) = 1/2 x (0.02 + 0.02) = 0.02", d1)
        d2 = self.demos["C14-D02"]["states"]["1,0"]["interpretation"]
        self.assertIn("0.90 x 0.01 x 1 / (1 - 0.90)^2", d2)
        d3 = self.demos["C14-D03"]["states"]["0,0"]["interpretation"]
        self.assertIn("Gap = 0.90 - 0.60 = 0.30", d3)

    def test_displayed_equations_are_chapter_equations(self):
        chapter = next(c for c in json.loads((LAB / "chapter-map.json").read_text()) if c["chapter"] == 14)

        def norm(t):
            t = re.sub(r"\\tag\{[^}]*\}", "", t)
            t = re.sub(r"\\[,;:!]", "", t)
            return re.sub(r"[\s{}]", "", t).rstrip(".")
        allowed = {norm(e["tex"]) for e in chapter["equations"]}
        alts = re.findall(r'data-tex="([^"]+)"', self.page)
        self.assertEqual(len(alts), 4)
        for tex in alts:
            self.assertIn(norm(html.unescape(tex)), allowed)

    def test_links_and_offline(self):
        for href in ("../../notebooks/14-transition-model-bound.ipynb", "../../skills/maa-14-transition-model-bound/SKILL.md",
                     "../index.html"):
            self.assertIn(f'href="{href}"', self.page)
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
        self.assertEqual((report["states_checked"], report["resets_checked"], report["labelled_controls"]), (26, 4, 8))

    def test_build_is_reproducible(self):
        with tempfile.TemporaryDirectory() as out:
            run = subprocess.run([str(VENV_PYTHON), str(WRAPPER), "--chapters", "14", "--out", out],
                                 capture_output=True, text=True, timeout=600)
            self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
            fresh = Path(out) / "14-transition-model-bound" / "reader.html"
            self.assertEqual(fresh.read_bytes(), self.reader.read_bytes())


if __name__ == "__main__":
    unittest.main()
