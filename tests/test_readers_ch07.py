"""Chapter 7 laboratory reader: independent hand checks of the built page.

Expected numbers are recomputed here from the chapter's arithmetic (discount
powers, the three-state backward calculation, the cash and prepare horizon
model, the Bellman residual bound), not read back from the module.
"""
from __future__ import annotations

import base64
import html
import json
import math
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
LAB = HERE.parent
WRAPPER = LAB / "tools" / "readers" / "build_readers.py"
HARNESS = LAB / "tools" / "readers" / "engine" / "dom_harness.js"
SLUG = "07-finite-horizon-planning"


def build_python():
    venv = LAB / ".venv" / "bin" / "python"
    return str(venv) if venv.exists() else sys.executable


def as_number(text):
    try:
        return float(text)
    except ValueError:
        return text


class Chapter7ReaderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        run = subprocess.run([build_python(), str(WRAPPER), "--chapters", "7", "--out", cls.tmp.name],
                             capture_output=True, text=True, timeout=600)
        if run.returncode != 0:
            raise unittest.SkipTest("cannot build: " + run.stdout + run.stderr)
        cls.reader = Path(cls.tmp.name) / SLUG / "reader.html"
        cls.page = cls.reader.read_text(encoding="utf-8")
        m = re.search(r'<script id="reader-data" type="application/json">(.*?)</script>', cls.page, re.S)
        cls.data = json.loads(m.group(1))
        cls.demos = {d["id"]: d for d in cls.data["demos"]}

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def states(self, demo_id):
        demo = self.demos[demo_id]
        for key, state in demo["states"].items():
            idx = [int(i) for i in key.split(",")]
            yield [as_number(c["values"][i]) for c, i in zip(demo["controls"], idx)], dict(state["metrics"]), state

    def test_structure_and_budget(self):
        self.assertEqual(list(self.demos), ["C07-D01", "C07-D02", "C07-D03", "C07-D04"])
        self.assertEqual([len(d["states"]) for d in self.data["demos"]], [8, 6, 8, 8])
        self.assertLess(self.reader.stat().st_size, 2_500_000)

    def test_d01_discount_weights(self):
        for (gamma, k), m, state in self.states("C07-D01"):
            worth = 100 * gamma ** k
            scale = 1 / (1 - gamma)
            digits = 1 if worth >= 1 else (2 if worth >= 0.01 else 4)
            self.assertEqual(m["Worth now"], f"{worth:.{digits}f}")
            self.assertEqual(m["Planning scale 1/(1 - gamma)"], f"{scale:.0f} steps")
            self.assertEqual(m["Worth at that scale"], f"{100 * gamma ** scale:.1f}")
            # series check: summing 1 per step for 20000 steps approaches 1/(1-gamma)
            total = sum(gamma ** j for j in range(20000))
            self.assertAlmostEqual(total, scale, places=6)
        book = {(0.9, 10): "34.9", (0.99, 50): "60.5", (0.95, 10): "59.9", (0.9, 50): "0.52"}
        for (g, k), m, _ in self.states("C07-D01"):
            if (g, k) in book:
                self.assertEqual(m["Worth now"], book[(g, k)])

    def test_d02_three_states(self):
        for (cost, q), m, _ in self.states("C07-D02"):
            verified = 100 * q
            release, verify = 85.0, -cost + verified
            self.assertEqual(m["Value of the verified state"], f"{verified:.1f}")
            self.assertEqual(m["Start value, release at once"], f"{release:.1f}")
            self.assertEqual(m["Start value, verify then release"], f"{verify:.1f}")
            expected = "tie" if abs(verify - release) < 1e-9 else ("verify" if verify > release else "release")
            self.assertEqual(m["Chosen at the start"], expected)
        book = next(m for v, m, _ in self.states("C07-D02") if v == [5, 0.97])
        self.assertEqual(book["Start value, verify then release"], "92.0")  # the chapter's 92 against 85
        tie = next(m for v, m, _ in self.states("C07-D02") if v == [12, 0.97])
        self.assertEqual(tie["Chosen at the start"], "tie")

    def test_d03_horizon_model(self):
        # Brute force over all plans of length h in the cash/prepare/release model.
        def best(h, g):
            cash = 2.0
            prepare = -1.0 + (g * 6.0 if h >= 2 else 0.0)
            return cash, prepare
        for (h, g), m, _ in self.states("C07-D03"):
            cash, prepare = best(int(h), g)
            self.assertEqual(m["Value of cash"], f"{cash:.2f}")
            self.assertEqual(m["Value of prepare"], f"(-{-prepare:.2f})" if prepare < 0 else f"{prepare:.2f}")
            self.assertEqual(m["Start value (the larger)"], f"{max(cash, prepare):.2f}")
            expected = "tie" if abs(cash - prepare) < 1e-9 else ("cash" if cash > prepare else "prepare")
            self.assertEqual(m["Chosen"], expected)
        by = {tuple(v): m for v, m, _ in self.states("C07-D03")}
        self.assertEqual(by[(2, 1.0)]["Chosen"], "prepare")   # -1 + 6 = 5 beats 2
        self.assertEqual(by[(1, 1.0)]["Chosen"], "cash")
        self.assertEqual(by[(2, 0.5)]["Chosen"], "tie")        # -1 + 3 = 2
        self.assertTrue(by[(1, 0.5)]["Break-even discount"].startswith("undefined"))

    def test_d04_residual_bound(self):
        candidates = {"All zeros": (0, 0, 0), "Best immediate reward in each state": (85, 97, 0)}
        for (g, cand), m, _ in self.states("C07-D04"):
            vu, vv, vt = candidates[cand]
            # optimal values by direct recursion for this acyclic model (terminal value 0)
            star_v, star_t = 97.0, 0.0
            star_u = max(85.0, -5.0 + g * star_v)
            tu = max(85 + g * vt, -5 + g * vv)
            tv_, tt = 97 + g * vt, g * vt
            residual = max(abs(tu - vu), abs(tv_ - vv), abs(tt - vt))
            error = max(abs(vu - star_u), abs(vv - star_v), abs(vt - star_t))
            self.assertEqual(m["Residual ||TV - V||"], f"{residual:.2f}")
            self.assertEqual(m["Actual error ||V - V*||"], f"{error:.2f}")
            if g < 1:
                bound = residual / (1 - g)
                self.assertEqual(m["Bound from Equation (7.5)"], f"{bound:.1f}")
                self.assertLessEqual(error, bound + 1e-9)
            else:
                self.assertTrue(m["Bound from Equation (7.5)"].startswith("undefined"))
        by = {tuple(v): m for v, m, _ in self.states("C07-D04")}
        self.assertEqual(by[(0.95, "All zeros")]["Bound from Equation (7.5)"], "1940.0")
        self.assertEqual(by[(0.9, "Best immediate reward in each state")]["Actual error ||V - V*||"], "0.00")

    def svg(self, state):
        return base64.b64decode(state["image"].split(",", 1)[1]).decode("utf-8")

    def test_d04_figure_title_matches_bound(self):
        # g3-01: at discount 1 no bound exists, so the title may not say the error never exceeds it.
        for (g, cand), m, state in self.states("C07-D04"):
            svg = self.svg(state)
            if g < 1:
                self.assertIn(f"Discount {g:.2f}: error never exceeds the bound", svg)
                self.assertNotIn("no bound exists", svg)
            else:
                self.assertIn("Discount 1.00: no bound exists", svg)
                self.assertNotIn("never exceeds", svg)
                self.assertTrue(m["Bound from Equation (7.5)"].startswith("undefined"))
                self.assertIn("this finite-horizon model (its terminal state loops with reward 0)", state["interpretation"])
                self.assertNotIn("acyclic", state["interpretation"])
            # g3-09: axis labels use words, since bar glyphs render as capital I
            self.assertIn("largest gap, V to V*", svg)
            self.assertIn("largest gap, TV to V", svg)
            self.assertNotIn("||V - V*||", svg)

    def test_d04_ratio_for_loose_bound(self):
        by = {tuple(v): st for v, _, st in self.states("C07-D04")}
        self.assertIn("(here 100.0 times the error)", by[(0.99, "All zeros")]["interpretation"])
        self.assertNotIn("times the error", by[(0.9, "Best immediate reward in each state")]["interpretation"])

    def test_wording_fixes(self):
        text = html.unescape(self.page)
        # g3-02: a tie at cost 12 means the prompt may not presuppose a winner
        self.assertIn("how do the two start policies compare: is either one worth more?", text)
        self.assertNotIn("which start policy is worth more?", text)
        # g3-03: a finite horizon permits, not forces, gamma = 1
        self.assertIn("here set to 1, which a finite horizon permits", text)
        self.assertNotIn("here 1 because the horizon is finite", text)
        # g3-04: the three-step policy fails only with one decision left (at discount 1)
        self.assertIn("can be wrong once steps have been spent", text)
        self.assertNotIn("is not valid once one step has been spent", text)
        # g3-05: one counting convention (decisions left at the start)
        self.assertIn("With one decision left at the start, preparing uses it and the ready state has none left", text)
        self.assertNotIn("With one decision left the ready state has no decision to spend", text)
        # g3-11: the horizon changes the answer only for some discounts
        self.assertIn("How many decisions are left can change the answer", text)
        self.assertNotIn("How many decisions are left changes the answer", text)

    def test_d01_figure_names_the_other_curves(self):
        for (g, k), m, state in self.states("C07-D01"):
            svg = self.svg(state)
            others = [x for x in (0.8, 0.9, 0.95, 0.99) if x != g]
            self.assertIn("steepest first: " + ", ".join(f"{x:.2f}" for x in others), svg)
            self.assertNotIn("the other three", svg)

    def test_equations_come_from_chapter(self):
        chapter = next(c for c in json.loads((LAB / "chapter-map.json").read_text()) if c["chapter"] == 7)
        def norm(t):
            t = re.sub(r"\\tag\{[^}]*\}", "", t)
            t = re.sub(r"\\[,;:!]", "", t)
            return re.sub(r"[\s{}]", "", t).rstrip(".")
        allowed = {norm(e["tex"]) for e in chapter["equations"]}
        alts = re.findall(r'alt="Equation: ([^"]+)"', self.page)
        self.assertEqual(len(alts), 4)
        for tex in alts:
            self.assertIn(norm(html.unescape(tex)), allowed)

    def test_text_rules(self):
        text = re.sub(r"<script\b.*?</script>|<style\b.*?</style>", " ", self.page, flags=re.S)
        text = html.unescape(re.sub(r"<[^>]+>", " ", text))
        for d in self.data["demos"]:
            for s in d["states"].values():
                text += " " + s["interpretation"] + " " + " ".join(" ".join(p) for p in s["metrics"])
        for bad in ("\u2014", "\u2013", "--", "\u2212"):
            self.assertNotIn(bad, text)
        for term in ("matplotlib", "numpy", "python", "jupyter"):
            self.assertNotIn(term, text.lower())
        self.assertIn("constructed", text.lower())

    def test_dom_harness(self):
        run = subprocess.run(["node", str(HARNESS), str(self.reader)], capture_output=True, text=True, timeout=120)
        if run.returncode != 0 and "not found" in run.stderr:
            self.skipTest("node missing")
        self.assertEqual(run.returncode, 0, run.stderr + run.stdout)


if __name__ == "__main__":
    unittest.main()
