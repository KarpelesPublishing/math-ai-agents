"""Chapter 22 laboratory reader: independent hand checks of the built page.

Every expected number is recomputed here from the chapter's own arithmetic
(the two-policy table, Workbench VI.1, the laboratory transfer case, the
one-update bound and margin, the tail measure of the constructed lottery, the
risk budget, the four-action authority example), not read back from the
module that produced the page. The reader is built fresh into a
temporary directory, so nothing under readers/ is touched.
"""
from __future__ import annotations

import html
import importlib.util
import json
import math
import os
from fractions import Fraction
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

    def grid(self, demo_id):
        """Every state keyed by the tuple of numeric (or string) control values."""
        demo = self.demos[demo_id]
        raw = authored_demos(22)[demo_id]["controls"]  # the page shows labels; the module holds the raw values
        out = {}
        for key, state in demo["states"].items():
            idx = [int(i) for i in key.split(",")]
            values = tuple(c["values"][i] for c, i in zip(raw, idx))
            out[values] = (dict(state["metrics"]), state["interpretation"], state)
        return out

    def states(self, demo_id):
        demo = self.demos[demo_id]
        for key, state in demo["states"].items():
            idx = [int(i) for i in key.split(",")]
            values = [as_number(c["values"][i]) for c, i in zip(demo["controls"], idx)]
            yield values, dict(state["metrics"]), state

    def test_four_demonstrations_all_states_render(self):
        self.assertEqual(list(self.demos), ["C22-D01", "C22-D02", "C22-D03", "C22-D04"])
        self.assertEqual([len(d["states"]) for d in self.data["demos"]], [12, 12, 12, 12])
        for demo in self.data["demos"]:
            combos = math.prod(len(c["values"]) for c in demo["controls"])
            self.assertEqual(len(demo["states"]), combos)
            for state in demo["states"].values():
                self.assertTrue(state["image"].startswith("data:image/svg+xml"))
                self.assertTrue(state["interpretation"])
                self.assertTrue(state["alt"])
                self.assertGreaterEqual(len(state["steps"]), 2)

    def test_size_budget(self):
        self.assertLess(self.reader.stat().st_size, 4_000_000)

    # Demonstration 1: three policy sets on one plane

    SETS = {
        "table": ({"Careful": (8, "1/2"), "Aggressive": (12, "3/2")}, 1),
        "workbench": ({"Careful": (7, "1/2"), "Aggressive": (11, 2)}, 1),
        "transfer": ({"act": (20, "1/100"), "wait": (-1, 0)}, 0),
    }

    def d01_expected(self, case, lam):
        pol, limit = self.SETS[case]
        pol = {n: (Fraction(r), Fraction(c)) for n, (r, c) in pol.items()}
        scores = {n: r - lam * c for n, (r, c) in pol.items()}
        top = max(scores.values())
        picks = [n for n in pol if scores[n] == top]
        eligible = {n: r for n, (r, c) in pol.items() if c <= limit}
        con = max(eligible, key=eligible.get) if eligible else None
        return pol, scores, picks, con

    def test_d01_every_state_by_hand(self):
        for (case, lam), (m, _, _) in self.grid("C22-D01").items():
            lam = Fraction(str(lam))
            pol, scores, picks, con = self.d01_expected(case, lam)
            names = list(pol)
            for n in names:
                self.assertEqual(m[f"{n} score"], f"{float(scores[n]):.2f}")
            if len(picks) > 1:
                self.assertTrue(m["Penalty rule picks"].startswith("tie"))
            else:
                self.assertEqual(m["Penalty rule picks"], picks[0])
            self.assertEqual(m["Constraint rule picks"], con)
            low = min(pol, key=lambda n: pol[n][1])
            high = max(pol, key=lambda n: pol[n][1])
            flip = (pol[high][0] - pol[low][0]) / (pol[high][1] - pol[low][1])
            expect_flip = f"{float(flip):.2f}".rstrip("0").rstrip(".")
            self.assertEqual(m["Multiplier at which the penalty rule flips"], expect_flip)

    def test_d01_book_workbench_and_transfer_numbers(self):
        by = {k: (v[0], v[1]) for k, v in self.grid("C22-D01").items()}
        m, text = by[("table", 2)]  # chapter: 8 - 2(0.5) = 7 and 12 - 2(1.5) = 9
        self.assertEqual((m["Careful score"], m["Aggressive score"]), ("7.00", "9.00"))
        self.assertEqual((m["Penalty rule picks"], m["Constraint rule picks"]), ("Aggressive", "Careful"))
        self.assertIn("8 - 2 x 0.5 = 7.00", text)
        self.assertIn("12 - 2 x 1.5 = 9.00", text)
        self.assertEqual(by[("table", 4)][0]["Careful score"], "6.00")  # exact tie, 6 = 6
        self.assertTrue(by[("table", 4)][0]["Penalty rule picks"].startswith("tie"))
        self.assertEqual(by[("table", 6)][0]["Penalty rule picks"], "Careful")
        # Table with randomising: 0.5 + 1.0 p <= 1 gives p = 1/2 and reward 8 + 4 x 1/2 = 10.
        self.assertIn("probability 1/2 of Aggressive, reward 10.00", by[("table", 2)][0]["Best randomised mix"])
        # Workbench VI.1: 7 - 2(0.5) = 6 and 11 - 2(2) = 7; penalty picks Aggressive (cost 2 > 1); mix 1/3 gives 25/3.
        m, _ = by[("workbench", 2)]
        self.assertEqual((m["Careful score"], m["Aggressive score"]), ("6.00", "7.00"))
        self.assertEqual((m["Penalty rule picks"], m["Constraint rule picks"]), ("Aggressive", "Careful"))
        self.assertIn("probability 1/3 of Aggressive, reward 8.33", m["Best randomised mix"])
        self.assertEqual(m["Multiplier at which the penalty rule flips"], "2.67")
        # Transfer: 20 - 100(0.01) = 19; the penalty still picks act at 100; only wait meets the limit 0.
        m, _ = by[("transfer", 100)]
        self.assertEqual((m["act score"], m["wait score"]), ("19.00", "-1.00"))
        self.assertEqual((m["Penalty rule picks"], m["Constraint rule picks"]), ("act", "wait"))
        self.assertEqual(m["Multiplier at which the penalty rule flips"], "2100")
        self.assertIn("probability 0 of act", m["Best randomised mix"])
        self.assertNotIn("0/1", m["Best randomised mix"])
        self.assertIn("outside the policy family", m["Best randomised mix"])

    def test_patch2_marker_label_and_mix_scope_and_gate_label(self):
        # g8-04: the right-panel marker is the step, and the allowance is a separate number.
        st = self.demos["C22-D02"]["states"]["0,0,0"]
        self.assertIn("step 0.005 with allowance 0.020", st["alt"])
        self.assertNotIn("this step at", st["alt"])
        # g8-05: the randomised mix is labelled as the workbench reading off the chapter table.
        by = self.grid("C22-D01")
        self.assertTrue(by[("table", 2)][0]["Best randomised mix"].startswith("workbench reading, outside the policy family"))
        self.assertFalse(by[("workbench", 2)][0]["Best randomised mix"].startswith("workbench reading"))

    def test_d01_transfer_agrees_with_the_laboratory_function(self):
        for lam in (2, 4, 6, 100):
            out = evaluate({"risk_limit": 0, "risk_penalty": lam, "actions": [
                {"name": "act", "reward": 20, "risk": 0.01, "authorized": True},
                {"name": "wait", "reward": -1, "risk": 0, "authorized": True}]})
            self.assertEqual(out["metrics"]["unconstrained_penalty_choice"], "act")
            self.assertEqual(out["metrics"]["constrained_choice"], "wait")

    # Demonstration 2: d = 10, epsilon = 0.1

    def test_d02_allowance_margin_and_largest_step_by_hand(self):
        for (delta, gamma, margin), (m, _, _) in self.grid("C22-D02").items():
            allowance = math.sqrt(2 * delta) * gamma * 0.1 / (1 - gamma) ** 2
            self.assertEqual(m["Allowance above the aimed level"], f"{allowance:.3f}")
            self.assertEqual(m["Worst case when aiming at the limit"], f"{10 + allowance:.3f}")
            self.assertEqual(m["Ceiling d minus margin"], f"{10 - margin:.1f}")
            self.assertEqual(m["Worst case when aiming at the ceiling"], f"{10 - margin + allowance:.3f}")
            self.assertEqual(m["Margin covers the allowance"], "yes" if allowance < margin else "no")
            # Largest step: solve the allowance formula for delta by bisection, independently of the closed form.
            lo, hi = 0.0, 1000.0
            for _ in range(200):
                mid = (lo + hi) / 2
                if math.sqrt(2 * mid) * gamma * 0.1 / (1 - gamma) ** 2 < margin:
                    lo = mid
                else:
                    hi = mid
            self.assertEqual(m["Largest step the margin covers"], f"{lo:.4f}")

    def test_d02_book_values_and_scaling(self):
        by = {k: v[0] for k, v in self.grid("C22-D02").items()}
        self.assertEqual(by[(0.005, 0.85, 0.5)]["Allowance above the aimed level"], "0.378")  # 0.1 x 0.85 x 0.1 / 0.0225
        self.assertEqual(by[(0.02, 0.85, 0.5)]["Allowance above the aimed level"], "0.756")
        self.assertEqual(by[(0.005, 0.9, 0.5)]["Allowance above the aimed level"], "0.900")  # check question: 0.009 / 0.01
        self.assertEqual(by[(0.005, 0.9, 0.5)]["Margin covers the allowance"], "no")
        self.assertEqual(by[(0.005, 0.9, 1.0)]["Margin covers the allowance"], "yes")
        self.assertEqual(by[(0.02, 0.9, 1.0)]["Margin covers the allowance"], "no")  # 1.8 > 1.0
        for g in (0.5, 0.85, 0.9):
            a1 = float(by[(0.005, g, 0.5)]["Allowance above the aimed level"])
            a2 = float(by[(0.02, g, 0.5)]["Allowance above the aimed level"])
            self.assertAlmostEqual(a2 / a1, 2.0, places=1)  # four times the step, twice the allowance
        # The plus sign: aiming at the limit always may exceed it.
        for m in by.values():
            self.assertGreater(float(m["Worst case when aiming at the limit"]), 10.0)

    def test_d02_ceiling_row_is_labelled_as_a_replaced_limit(self):
        for _, _, state in self.states("C22-D02"):
            self.assertIn("the bound is applied with the ceiling in place of d", state["interpretation"])

    # Demonstration 3: C = 100 with probability 0.01, else 0; budget ledger

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

    @staticmethod
    def budget_by_hand(budget):
        left = Fraction(str(budget))
        accepted = []
        for charge in (Fraction("0.04"), Fraction("0.05"), Fraction("0.03"), Fraction("0.05")):
            if charge <= left:
                left -= charge
                accepted.append(True)
            else:
                accepted.append(False)
        return accepted, left

    def test_d03_cvar_two_independent_ways_and_budget_by_hand(self):
        for (alpha, budget), (m, _, _) in self.grid("C22-D03").items():
            expected = self.cvar_by_tail_average(alpha, 0.01)
            self.assertAlmostEqual(expected, self.cvar_by_search(alpha, 0.01), places=6)
            self.assertEqual(m["Tail average (CVaR)"], f1(expected))
            self.assertEqual(m["Mean cost"], "1.0")
            accepted, left = self.budget_by_hand(budget)
            self.assertEqual(m["Charges accepted"], f"{sum(accepted)} of 4")
            self.assertEqual(m["Budget left at the end"], f"{float(left):.2f}")
            self.assertEqual(m["Budget B"], f"{budget:.2f}")

    def test_d03_book_lottery_and_budget_cases(self):
        by = {k: (v[0], v[1]) for k, v in self.grid("C22-D03").items()}
        book = by[(0.99, 0.1)][0]  # expected loss 1, CVaR_.99 = 100
        self.assertEqual((book["Mean cost"], book["Tail average (CVaR)"]), ("1.0", "100.0"))
        self.assertEqual(by[(0.9, 0.1)][0]["Tail average (CVaR)"], "10.0")  # zeros dilute a wide tail: 1.0 / 0.1
        self.assertEqual(by[(0.95, 0.1)][0]["Tail average (CVaR)"], "20.0")
        self.assertEqual(by[(0.995, 0.1)][0]["Tail average (CVaR)"], "100.0")
        # Budget 0.10: 0.04 charged (0.06 left), 0.05 charged (0.01 left), 0.03 and 0.05 refused.
        m, text = by[(0.99, 0.1)]
        self.assertEqual((m["Charges accepted"], m["Budget left at the end"]), ("2 of 4", "0.01"))
        self.assertIn("0.10 - 0.04 = 0.06", text)
        self.assertIn("0.06 - 0.05 = 0.01", text)
        self.assertIn("0.03 > 0.01, refused", text)
        # Budget 0.20 charges all four and leaves 0.03; budget 0.05 charges only the first.
        self.assertEqual((by[(0.99, 0.2)][0]["Charges accepted"], by[(0.99, 0.2)][0]["Budget left at the end"]), ("4 of 4", "0.03"))
        self.assertEqual((by[(0.99, 0.05)][0]["Charges accepted"], by[(0.99, 0.05)][0]["Budget left at the end"]), ("1 of 4", "0.01"))
        # The check question: budget 0.08 gives charged, refused, charged, refused with 0.01 left.
        accepted, left = self.budget_by_hand("0.08")
        self.assertEqual((accepted, left), ([True, False, True, False], Fraction("0.01")))

    def test_d03_flat_minimum_is_stated(self):
        text = self.grid("C22-D03")[(0.99, 0.1)][1]  # alpha 0.99, B 0.10
        self.assertIn("flat", text)
        self.assertIn("0 + 1.0 / 0.01 = 100.0", text)

    def test_d03_cut_off_sentence_only_when_the_curve_exceeds_the_axis(self):
        for (alpha, _), (_, text, _) in self.grid("C22-D03").items():
            top = max(z + (0.01 * max(100 - z, 0) + 0.99 * max(0 - z, 0)) / (1 - alpha) for z in (k / 2 - 10 for k in range(241)))
            if top > 230:
                self.assertIn("rises above the top of the left plot", text)
            else:
                self.assertIn("fits inside the left plot", text)

    # Demonstration 4: the laboratory's four actions, with a bypass

    ACTIONS = [("fast-release", 10, 0.3, False), ("reviewed-release", 5, 0.05, True),
               ("risky-authorized", 8, 0.2, True), ("abstain", 0, 0.0, True)]

    def test_d04_choices_by_hand(self):
        for (limit, penalty, route), (m, _, _) in self.grid("C22-D04").items():
            values = {n: r - penalty * k for n, r, k, _ in self.ACTIONS}
            best = max(values.values())
            tops = [n for n in values if abs(values[n] - best) < 1e-9]
            authorized = {n: values[n] for n, _, _, a in self.ACTIONS if a}
            eligible = {n: r for n, r, k, a in self.ACTIONS if a and k <= limit}
            gate = max(eligible, key=eligible.get)
            self.assertEqual(m["Penalty pick over all rows"], tops[0] if len(tops) == 1 else f"tie ({' and '.join(tops)})")
            self.assertEqual(m["Penalty pick among authorized rows"], max(authorized, key=authorized.get))
            self.assertEqual(m["Gate pick (authority, then limit, then reward)"], gate)
            self.assertEqual(m["Eligible actions"], f"{len(eligible)} of 4")
            self.assertEqual(m["Row that executes"], tops[0] if route == "bypass" else gate)
            self.assertNotIn("fast-release", m["Gate pick (authority, then limit, then reward)"])

    def test_d04_chapter_numbers_and_bypass(self):
        by = {k: (v[0], v[1]) for k, v in self.grid("C22-D04").items()}
        g = "Gate pick (authority, then limit, then reward)"
        default = by[(0.1, 5, "checked")][0]
        self.assertEqual(default["Penalty pick over all rows"], "fast-release")      # 10 - 5 x 0.3 = 8.5
        self.assertEqual(default["Penalty pick among authorized rows"], "risky-authorized")  # 8 - 5 x 0.2 = 7
        self.assertEqual(default[g], "reviewed-release")
        self.assertEqual(by[(0.25, 5, "checked")][0][g], "risky-authorized")
        self.assertEqual(by[(0.25, 5, "checked")][0]["Removed by authority"], "fast-release")
        self.assertEqual(by[(0, 5, "checked")][0][g], "abstain")
        self.assertEqual(by[(0, 5, "checked")][0]["Eligible actions"], "1 of 4")
        self.assertEqual(by[(0.1, 25, "checked")][0]["Penalty pick over all rows"], by[(0.1, 25, "checked")][0][g])
        self.assertNotEqual(by[(0.25, 25, "checked")][0]["Penalty pick over all rows"], by[(0.25, 25, "checked")][0][g])
        self.assertIn("10 - 5 x 0.3 = 8.50", by[(0.1, 5, "checked")][1])
        self.assertIn("8 - 5 x 0.2 = 7.00", by[(0.1, 5, "checked")][1])
        # Bypass at penalty 5: the unauthorized row executes; at penalty 25 the bypass goes unnoticed.
        self.assertEqual(by[(0.1, 5, "bypass")][0]["Row that executes"], "fast-release")
        self.assertIn("executes what the gate would have refused", by[(0.1, 5, "bypass")][1])
        self.assertEqual(by[(0.1, 25, "bypass")][0]["Row that executes"], "reviewed-release")
        self.assertIn("looks safe even though the check was skipped", by[(0.1, 25, "bypass")][1])

    def test_d04_laboratory_function_boundaries(self):
        rows = [{"name": n, "reward": r, "risk": k, "authorized": a} for n, r, k, a in self.ACTIONS]
        out = evaluate({"risk_limit": 0.2, "risk_penalty": 5, "actions": rows})
        self.assertEqual(out["metrics"]["constrained_choice"], "risky-authorized")  # 0.2 <= 0.2

    # Optional fields

    def test_optional_fields_are_present_and_sourced(self):
        text = (LAB.parent / "Manuscript" / "part-vi" / "22-safe-enough-to-act.md").read_text(encoding="utf-8")
        authored = authored_demos(22)
        for demo_id, demo in authored.items():
            self.assertIn("by hand", demo["check"])
        self.assertIn("What this does not settle", text)
        for demo_id in ("C22-D02", "C22-D03", "C22-D04"):
            self.assertEqual(authored[demo_id]["scope_note"]["source_section"], "What this does not settle")
        for demo_id in ("C22-D01", "C22-D02", "C22-D03", "C22-D04"):
            self.assertIn("misconception", authored[demo_id])
            self.assertEqual(len(authored[demo_id]["prediction_options"]), 3)
        self.assertIn("Ask the chapter skill", self.page)
        self.assertEqual(self.page.count("Common wrong turn"), 4)
        self.assertGreaterEqual(self.page.count("What this does not settle"), 3)

    # Page-level checks

    def test_displayed_equations_are_chapter_equations(self):
        chapter = next(c for c in json.loads((LAB / "chapter-map.json").read_text()) if c["chapter"] == 22)

        def norm(t):
            t = re.sub(r"\\tag\{[^}]*\}", "", t)
            t = re.sub(r"\\[,;:!]", "", t)
            return re.sub(r"[\s{}]", "", t).rstrip(".")
        allowed = {norm(e["tex"]) for e in chapter["equations"]}
        alts = re.findall(r'data-tex="([^"]+)"', self.page)
        self.assertEqual(len(alts), 8)  # 2 + 2 + 2 + 2 equations
        shown = set()
        for tex in alts:
            self.assertIn(norm(html.unescape(tex)), allowed)
            shown.add(norm(html.unescape(tex)))
        self.assertEqual(len(shown), 6)  # all six chapter equations are covered, including (22.6)

    def test_source_sections_exist_in_the_canonical_chapter(self):
        text = (LAB.parent / "Manuscript" / "part-vi" / "22-safe-enough-to-act.md").read_text(encoding="utf-8")
        headings = {line.lstrip("#").strip() for line in text.splitlines() if line.startswith("#")}
        expected = ["Fixed penalties make a hidden exchange rate", "A constraint is not a promise",
                    "Other risk contracts", "Authority is an operating envelope", "What this does not settle"]
        for title in expected:
            self.assertIn(title, headings)
            self.assertIn(html.escape(title), self.page)

    def test_links_and_offline(self):
        config = json.loads((LAB / "tools" / "readers" / "reader.config.json").read_text(encoding="utf-8"))
        index_href = config["links"]["index"]["href"]  # read from the configuration, which another owner may change
        for href in (f"../../notebooks/{SLUG}.ipynb", "../../skills/maa-22-risk-authority-contract/SKILL.md", index_href):
            self.assertIn(f'href="{href}"', self.page)
        self.assertIsNone(re.search(r'(src|href)="(https?:)?//', self.page))

    def test_page_text_has_no_dashes_or_dependency_names(self):
        text = re.sub(r"<script\b.*?</script>|<style\b.*?</style>", " ", self.page, flags=re.S)
        text = html.unescape(re.sub(r"<[^>]+>", " ", text))
        for demo in self.data["demos"]:
            for state in demo["states"].values():
                text += " " + state["interpretation"] + " " + " ".join(" ".join(p) for p in state["metrics"]) + " " + " ".join(state["steps"]) + " " + state["alt"]
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
        self.assertEqual((report["states_checked"], report["resets_checked"], report["labelled_controls"]), (48, 4, 10))
        self.assertEqual((report["ask_skill"], report["predictions_checked"], report["panels_checked"]), (1, 12, 7))


if __name__ == "__main__":
    unittest.main()
