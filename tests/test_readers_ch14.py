"""Chapter 14 laboratory reader: independent hand checks of the built page.

Every expected number is recomputed here from the chapter's own arithmetic
(the temperature table, Equations 14.1 to 14.4, the Figure 14.2 case, the
twelve-tool landscape and the priced twenty-step plan) by code that does not
import the chapter module: value recurrences are written out directly, the
horizon search is a brute-force loop over exact fractions. The reader is built
into a temporary directory, so the test never touches the committed readers
folder.
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
CHAPTER_TEXT = LAB.parent / "Manuscript" / "part-iv" / "14-building-a-world-inside.md"


def payload(text):
    match = re.search(r'<script id="reader-data" type="application/json">(.*?)</script>', text, re.S)
    return json.loads(match.group(1))


def metrics(state):
    return dict(state["metrics"])


def tv(p, q):
    return 0.5 * sum(abs(a - b) for a, b in zip(p, q))


TABLE = [(0.10, 2086, 193), (0.50, 2060, 196), (1.00, 1145, 868), (1.15, 918, 1092), (1.30, 732, 753)]
TEMPS = [0.10, 1.00, 1.15, 1.30]
JUDGES = ["dream", "real"]
CASES = ["default", "changed", "transfer", "percent"]
GAMMAS = [0.5, 0.9, 0.99]
PATTERNS = ["shared", "favorable", "adversarial"]
ERRORS3 = [0.05, 0.15, 0.3, 0.9]
SCENARIOS = [(Fraction(1), Fraction("0.5")), (Fraction(1), Fraction("0.2")), (Fraction(10), Fraction(2))]
ERRORS4 = [0.01, 0.02, 0.04, 0.08]
TRUE12 = [0.20, 0.30, 0.40, 0.50, 0.60, 0.90, 0.55, 0.45, 0.35, 0.25, 0.15, 0.10]


def case_kernels(case):
    if case == "transfer":
        ident = [[1.0, 0.0], [0.0, 1.0]]
        return ident, ident, [1.0, 2.0], 4
    s = {"default": 0.02, "changed": 0.02, "percent": 0.01}[case]
    horizon = {"default": 5, "changed": 20, "percent": 20}[case]
    true = [[0.9, 0.1], [0.2, 0.8]]
    model = [[0.9 - s, 0.1 + s], [0.2 + s, 0.8 - s]]
    return true, model, [0.0, 1.0], horizon


def recurrence_error(true, model, rewards, gamma, horizon):
    """max over states of |V_H - W_H| by H applications of V <- r + gamma P V (no library calls)."""
    v = [0.0, 0.0]
    w = [0.0, 0.0]
    for _ in range(horizon):
        v = [rewards[i] + gamma * sum(true[i][j] * v[j] for j in range(2)) for i in range(2)]
        w = [rewards[i] + gamma * sum(model[i][j] * w[j] for j in range(2)) for i in range(2)]
    return max(abs(a - b) for a, b in zip(v, w))


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

    def states(self, demo_id, axes):
        demo = self.demos[demo_id]
        for key, state in demo["states"].items():
            idx = [int(i) for i in key.split(",")]
            yield [axis[i] for axis, i in zip(axes, idx)], state

    def test_four_demonstrations_with_state_budget(self):
        self.assertEqual(list(self.demos), ["C14-D01", "C14-D02", "C14-D03", "C14-D04"])
        self.assertEqual([len(d["states"]) for d in self.data["demos"]], [8, 12, 12, 12])
        self.assertLess(self.reader.stat().st_size, 4_000_000)

    def test_d01_temperature_table_matches_the_chapter_and_the_judging_rule(self):
        text = CHAPTER_TEXT.read_text()
        for t, dream, real in TABLE:
            self.assertIn(f"| {t:.2f} | {dream} | {real} |", text)
        self.assertIn("| random policy | not applicable | 210 |", text)
        self.assertIn("| best leaderboard entry | not applicable | 820 |", text)
        rows = {t: (d, r) for t, d, r in TABLE}
        for (t, judge), state in self.states("C14-D01", [TEMPS, JUDGES]):
            m = metrics(state)
            dream, real = rows[t]
            self.assertEqual(m["Score inside the model"], str(dream))
            self.assertEqual(m["Score in the actual environment"], str(real))
            self.assertEqual(m["Model minus actual"], str(dream - real))
            self.assertEqual(m["Actual minus random policy (210)"], str(real - 210))
            key = (lambda r: r[1]) if judge == "dream" else (lambda r: r[2])
            winner = max(TABLE, key=key)
            self.assertEqual(m[f"Picked by the {judge} column"], f"{winner[0]:.2f}")
            self.assertEqual(m["Picked: score in the actual environment"], str(winner[2]))
            self.assertEqual(m["Picked: actual minus random policy (210)"], str(winner[2] - 210))
            self.assertIn(f"model {dream} - actual {real} = {dream - real}", state["interpretation"])
        # Judged by the model column the pick is below the random policy; by the actual column it beats the leaderboard.
        by = {tuple(v): metrics(s) for v, s in self.states("C14-D01", [TEMPS, JUDGES])}
        self.assertEqual(by[(0.10, "dream")]["Picked: actual minus random policy (210)"], "-17")
        self.assertEqual(by[(1.15, "real")]["Picked: score in the actual environment"], "1092")
        self.assertIn("1092 - 193 = 899", self.demos["C14-D01"]["states"]["0,0"]["interpretation"])
        self.assertEqual(by[(1.30, "dream")]["Model minus actual"], "-21")

    def test_d02_bounds_and_actual_error_by_direct_recurrence(self):
        for (case, gamma), state in self.states("C14-D02", [CASES, GAMMAS]):
            true, model, rewards, horizon = case_kernels(case)
            eps = max(tv(p, q) for p, q in zip(true, model))
            R = max(rewards)
            finite = R * eps * horizon * (horizon - 1) / 2
            discounted = gamma * eps * R / (1 - gamma) ** 2
            actual = recurrence_error(true, model, rewards, gamma, horizon)
            m = metrics(state)
            self.assertEqual(m["Epsilon (Equation 14.1)"], f"{eps:.3f}")
            self.assertEqual(m[f"Actual error after H = {horizon}"], f"{actual:.4f}", (case, gamma))
            self.assertEqual(m[f"Finite bound at H = {horizon}"], f"{finite:.3f}")
            self.assertEqual(m["Discounted bound (Equation 14.2)"], f"{discounted:.3f}", (case, gamma))
            self.assertEqual(m["Tightest valid bound"], f"{min(finite, discounted):.3f}")
            self.assertEqual(m["Largest possible value R/(1-gamma)"], f"{R / (1 - gamma):.1f}")
            self.assertLessEqual(actual, min(finite, discounted) + 1e-12)  # both bounds hold
        by = {tuple(v): metrics(s) for v, s in self.states("C14-D02", [CASES, GAMMAS])}
        # The notebook's numbers: epsilon 0.02, discounted bound 1.8, finite bound 0.2 at 5 and 3.8 at 20.
        self.assertEqual(by[("default", 0.9)]["Discounted bound (Equation 14.2)"], "1.800")
        self.assertEqual(by[("default", 0.9)]["Finite bound at H = 5"], "0.200")
        self.assertEqual(by[("changed", 0.9)]["Finite bound at H = 20"], "3.800")
        self.assertEqual(by[("changed", 0.9)]["Tightest valid bound"], "1.800")
        # The chapter's illustration: gamma 0.99, error 0.01, rewards of order one give a bound of about 99.
        self.assertEqual(by[("percent", 0.99)]["Discounted bound (Equation 14.2)"], "99.000")
        # The transfer case: identical kernels give zero everywhere.
        for g in GAMMAS:
            self.assertEqual(by[("transfer", g)]["Tightest valid bound"], "0.000")
            self.assertEqual(by[("transfer", g)]["Actual error after H = 4"], "0.0000")

    def test_d02_hand_check_after_two_rewards_in_the_interpretation(self):
        state = self.demos["C14-D02"]["states"]["0,1"]  # default case, gamma 0.9
        text = state["interpretation"]
        self.assertIn("1/2 x (|0.88 - 0.90| + |0.12 - 0.10|) = 1/2 x (0.02 + 0.02) = 0.02", text)
        self.assertIn("0.90 x 0.02 x 1 / (1 - 0.90)^2 = 1.800", text)
        # State 2 after two rewards: true 1 + 0.9 x (0.2 x 0 + 0.8 x 1) = 1.72, model 1 + 0.9 x 0.78 = 1.702.
        self.assertAlmostEqual(1 + 0.9 * 0.8, 1.72)
        self.assertAlmostEqual(1 + 0.9 * 0.78, 1.702)
        self.assertIn("|1.720 - 1.702| = 0.018", text)

    def test_d03_closing_sentence_matches_the_error_pattern(self):
        """g5-01: 'accurate on eleven tools' is true only for the favorable pattern (tool 12 the one wrong tool)."""
        old = "The model was accurate on eleven tools and the search found the twelfth."
        new = "The model is exact on ten tools and wrong on the two the decision turns on"
        for (pattern, e), state in self.states("C14-D03", [PATTERNS, ERRORS3]):
            text = state["interpretation"]
            model = list(TRUE12)
            if pattern == "adversarial":
                model[5] -= e
                model[4] += e
                wrong = sum(1 for a, b in zip(model, TRUE12) if abs(a - b) > 1e-9)
                self.assertEqual(wrong, 2)
                if "The optimizer now picks" in text:
                    self.assertIn(new, text)
                    self.assertNotIn(old, text)
                else:
                    self.assertNotIn(old, text)
            elif pattern == "favorable" and e >= 0.9:
                self.assertIn(old, text)
                self.assertNotIn(new, text)
            else:
                self.assertNotIn(new, text)
        self.assertIn(new, self.demos["C14-D03"]["states"]["2,2"]["interpretation"])
        self.assertNotIn(old, self.demos["C14-D03"]["states"]["2,2"]["interpretation"])
        self.assertNotIn(old, self.demos["C14-D03"]["states"]["2,3"]["interpretation"])

    def test_d02_bounds_are_not_ranked_as_a_statement_to_quote(self):
        """g5-14 and g5-17: each bound holds under its own assumptions; remedy wording follows the chapter."""
        d = self.demos["C14-D02"]
        for key, state in d["states"].items():
            self.assertNotIn("statement to quote", state["interpretation"])
            if not key.startswith("2,"):  # the transfer case has identical kernels and every bound is 0
                self.assertIn("holds under its own assumptions", state["interpretation"])
                self.assertIn("percent of the smaller one", state["interpretation"])
                self.assertIn("The two recurrences give", state["interpretation"])
                self.assertNotIn("far from the envelope", state["interpretation"])
        page = html.unescape(self.page)
        self.assertNotIn("statement to quote", page)
        self.assertNotIn("sooner rather than to polish", page)
        self.assertIn("If the model cannot be improved, consult the world more often.", page)

    def test_d03_landscape_pick_and_certificate_by_enumeration(self):
        for (pattern, e), state in self.states("C14-D03", [PATTERNS, ERRORS3]):
            model = list(TRUE12)
            if pattern == "shared":
                model = [v + e for v in model]
            elif pattern == "favorable":
                model[11] += e
            else:
                model[5] -= e
                model[4] += e
            errs = [abs(a - b) for a, b in zip(model, TRUE12)]
            best = max(model)
            picks = [i for i, v in enumerate(model) if abs(v - best) < 1e-9]
            m = metrics(state)
            self.assertEqual(m["True gap (Equation 14.3)"], "0.30")
            self.assertEqual(m["Largest error"], f"{max(errs):.3f}")
            self.assertEqual(m["Average error over 12 tools"], f"{sum(errs) / 12:.3f}")
            holds = Fraction(str(e)) * 2 < Fraction("0.3")
            self.assertEqual(m["Guarantee 2 x error < gap holds"], "yes" if holds else "no", (pattern, e))
            if len(picks) == 1:
                self.assertEqual(m["Model's pick"], f"tool {picks[0] + 1}")
                self.assertEqual(m["True value of the pick"], f"{TRUE12[picks[0]]:.2f}")
            else:
                self.assertIn("tie", m["Model's pick"])
        by = {tuple(v): metrics(s) for v, s in self.states("C14-D03", [PATTERNS, ERRORS3])}
        self.assertEqual(by[("adversarial", 0.15)]["Model's pick"], "tools 5 and 6 (tie)")  # 0.90 - 0.15 = 0.60 + 0.15
        self.assertEqual(by[("adversarial", 0.3)]["Model's pick"], "tool 5")
        self.assertEqual(by[("favorable", 0.9)]["Model's pick"], "tool 12")  # 0.10 + 0.90 = 1.00 beats 0.90
        self.assertEqual(by[("favorable", 0.3)]["Model's pick"], "tool 6")   # the model is wrong about tool 12 yet decides correctly
        self.assertEqual(by[("favorable", 0.3)]["Guarantee 2 x error < gap holds"], "no")
        for e in ERRORS3:
            self.assertEqual(by[("shared", e)]["Model's pick"], "tool 6")    # a shared offset never reorders
        # Best and runner-up of the constructed landscape.
        ordered = sorted(TRUE12, reverse=True)
        self.assertAlmostEqual(ordered[0] - ordered[1], 0.30)

    def test_d03_average_is_not_the_maximum(self):
        m = metrics(self.demos["C14-D03"]["states"]["1,3"])  # one favorable error 0.9
        self.assertEqual((m["Largest error"], m["Average error over 12 tools"]), ("0.900", "0.075"))

    def test_d04_certified_horizon_by_brute_force(self):
        for (scenario, eps), state in self.states("C14-D04", [SCENARIOS, ERRORS4]):
            reward, gap = scenario
            e = Fraction(str(eps))
            certified = [h for h in range(1, 10) if reward * e * h * (h - 1) < gap]
            h_star = max(certified)
            m = metrics(state)
            self.assertEqual(m["Certified horizon H*"], str(h_star))
            self.assertEqual(m["First horizon that fails"], str(h_star + 1) if h_star < 9 else "none up to the cap")
            self.assertEqual(m[f"R x epsilon x H(H-1) at H* = {h_star}"], f"{float(reward * e * h_star * (h_star - 1)):.2f}")
            self.assertEqual(m["Same quantity at a twenty-step plan"], f"{float(reward * e * 20 * 19):.1f}")
            self.assertEqual(certified, list(range(1, h_star + 1)))  # certified horizons are a prefix
            self.assertGreater(reward * e * 20 * 19, gap)           # a twenty-step plan never passes here
        by = {(v[0][0], v[0][1], v[1]): metrics(s)["Certified horizon H*"] for v, s in self.states("C14-D04", [SCENARIOS, ERRORS4])}
        # The chapter's numbers: Figure 14.2 (3 and 5 rewards); priced plan 2 rewards at 0.08 and 4 at 0.01.
        self.assertEqual(by[(Fraction(1), Fraction("0.5"), 0.02)], "5")
        self.assertEqual(by[(Fraction(1), Fraction("0.2"), 0.02)], "3")
        self.assertEqual(by[(Fraction(10), Fraction(2), 0.08)], "2")
        self.assertEqual(by[(Fraction(10), Fraction(2), 0.01)], "4")

    def test_d04_failure_by_equality_is_named(self):
        state = self.demos["C14-D04"]["states"]["2,0"]  # R = 10, gap 2, error 0.01
        self.assertIn("10 x 0.01 x 5 x 4 = 2.00", state["interpretation"])
        self.assertIn("fails by equality", state["interpretation"])
        self.assertIn("inconclusive", state["interpretation"])
        self.assertIn("10 x 0.01 x 20 x 19 = 38.0", state["interpretation"])

    def test_optional_fields_come_from_the_chapter(self):
        page = html.unescape(self.page)
        self.assertIn("Ask the chapter skill", page)
        self.assertEqual(page.count("Common wrong turn"), 4)
        self.assertGreaterEqual(page.count("What this does not settle"), 4)
        self.assertEqual(self.demos["C14-D02"]["stepper"], "discount")
        for demo in self.data["demos"]:
            self.assertTrue(demo["predict"]["correct"] and demo["predict"]["incorrect"])
            for state in demo["states"].values():
                self.assertTrue(2 <= len(state["steps"]) <= 8)
                self.assertTrue(state["alt"])
        flat = re.sub(r"\s+", " ", CHAPTER_TEXT.read_text()).lower()
        for phrase in ("been confidently wrong", "often loose, and a model with a large error may perform far better",
                       "the useful question is never how accurate the model is", "inconclusive, not evidence",
                       "the preprint reporting on its authors' own systems".replace("the preprint", "the anchor is a preprint"),
                       "this schematic explains the selection mechanism rather than supplying a measured error landscape"):
            self.assertIn(phrase, flat)

    def test_displayed_equations_are_chapter_equations(self):
        chapter = next(c for c in json.loads((LAB / "chapter-map.json").read_text()) if c["chapter"] == 14)

        def norm(t):
            t = re.sub(r"\\tag\{[^}]*\}", "", t)
            t = re.sub(r"\\[,;:!]", "", t)
            return re.sub(r"[\s{}]", "", t).rstrip(".")
        allowed = {norm(e["tex"]) for e in chapter["equations"]}
        alts = re.findall(r'data-tex="([^"]+)"', self.page)
        self.assertEqual(len(alts), 5)  # 14.1 in D01 and D02, 14.2 in D02, 14.3 in D03, 14.4 in D04
        for tex in alts:
            self.assertIn(norm(html.unescape(tex)), allowed)

    def test_links_and_offline(self):
        for href in ("../../notebooks/14-transition-model-bound.ipynb", "../../skills/maa-14-transition-model-bound/SKILL.md"):
            self.assertIn(f'href="{href}"', self.page)
        # The index link target is set by the shared configuration (it was changed to ../../index.html during this work).
        self.assertRegex(self.page, r'href="(\.\./)+index\.html"')
        self.assertIsNone(re.search(r'(src|href)="(https?:)?//', self.page))

    def test_page_text_has_no_dashes_or_dependency_names(self):
        text = re.sub(r"<script\b.*?</script>|<style\b.*?</style>", " ", self.page, flags=re.S)
        text = html.unescape(re.sub(r"<[^>]+>", " ", text))
        for state in (s for d in self.data["demos"] for s in d["states"].values()):
            text += " " + state["interpretation"] + " " + " ".join(" ".join(p) for p in state["metrics"]) + " " + " ".join(state["steps"]) + " " + state["alt"]
        for bad in ("\u2014", "\u2013", "\u2212", "--"):
            self.assertNotIn(bad, text)
        for term in ("matplotlib", "numpy", "python", "jupyter"):
            self.assertNotIn(term, text.lower())
        self.assertIn("constructed", text.lower())

    def test_accessibility_basics(self):
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
        self.assertEqual((report["states_checked"], report["resets_checked"]), (44, 4))
        self.assertGreaterEqual(report["predictions_checked"], 4)
        self.assertGreater(report["stepper_moves"], 0)

    def test_build_is_reproducible(self):
        with tempfile.TemporaryDirectory() as out:
            run = subprocess.run([str(VENV_PYTHON), str(WRAPPER), "--chapters", "14", "--out", out],
                                 capture_output=True, text=True, timeout=600)
            self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
            fresh = Path(out) / "14-transition-model-bound" / "reader.html"
            self.assertEqual(fresh.read_bytes(), self.reader.read_bytes())


if __name__ == "__main__":
    unittest.main()
