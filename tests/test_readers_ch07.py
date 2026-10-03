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
        self.assertEqual([len(d["states"]) for d in self.data["demos"]], [12, 12, 12, 12])
        self.assertLess(self.reader.stat().st_size, 4_000_000)

    def test_optional_fields_present(self):
        text = html.unescape(self.page)
        self.assertIn("Ask the chapter skill", text)
        self.assertGreaterEqual(text.count("What this does not settle"), 4)
        self.assertEqual(text.count("Common wrong turn"), 4)
        for d in self.data["demos"]:
            for s in d["states"].values():
                self.assertTrue(s.get("steps"))
        self.assertEqual(len(re.findall(r'type="radio"', text)), 12)

    def test_d01_discount_weights(self):
        def small(x):
            if x >= 1: return f"{x:.1f}"
            if x >= 0.01: return f"{x:.2f}"
            if x >= 0.0001: return f"{x:.4f}"
            mant, ex = f"{x:.1e}".split("e")
            return f"less than 0.0001 (about {mant} x 10^{int(ex)})"
        seen = {}
        for (gamma, k), m, state in self.states("C07-D01"):
            worth = 100 * gamma ** k
            scale = 1 / (1 - gamma)
            self.assertEqual(m["Worth now"], small(worth))
            self.assertEqual(m["Planning scale 1/(1 - gamma)"], f"{scale:.0f} steps")
            self.assertEqual(m["Worth at that scale"], f"{100 * gamma ** scale:.1f}")
            total = sum(gamma ** j for j in range(20000))
            self.assertAlmostEqual(total, scale, places=6)
            seen[(gamma, k)] = m["Worth now"]
        # the chapter's own numbers: 0.99 gives 90, 61, 37; 0.95 gives 60, 8, under 1; 0.9 gives 35, under 1
        self.assertEqual(seen[(0.99, 10)], "90.4")
        self.assertEqual(seen[(0.99, 50)], "60.5")
        self.assertEqual(seen[(0.99, 100)], "36.6")
        self.assertEqual(seen[(0.95, 10)], "59.9")
        self.assertEqual(seen[(0.95, 50)], "7.7")
        self.assertEqual(seen[(0.95, 100)], "0.59")
        self.assertEqual(seen[(0.9, 10)], "34.9")
        self.assertEqual(seen[(0.9, 50)], "0.52")
        self.assertEqual(seen[(0.5, 10)], "0.10")   # about one thousandth of 100 x 1 (0.5^10 = 0.000977)

    def test_d02_three_states(self):
        sc = {"book": (85, 97, 5, 1.0), "tie": (85, 97, 12, 1.0), "wb1": (80, 95, 6, 0.9), "wb3": (80, 95, 6, 0.75)}
        names = ["book", "tie", "wb1", "wb3"]
        def nice(x):
            t = f"{x:.2f}"
            return t[:-1] if t.endswith("0") else t
        for (name, stage), m, st in self.states("C07-D02"):
            name = names[0] if isinstance(name, float) else name
        by = {}
        demo = self.demos["C07-D02"]
        for key, st in demo["states"].items():
            si, gi = [int(i) for i in key.split(",")]
            by[(names[si], gi)] = (dict(st["metrics"]), st)
        for (name, stage), (m, st) in by.items():
            rel, ver, c, g = sc[name]
            verify = -c + g * ver
            self.assertEqual(m["Value of the terminal state"], "0.0")
            if stage >= 1:
                self.assertEqual(m["Value of the verified state"], nice(ver))
            else:
                self.assertEqual(m["Value of the verified state"], "not computed yet")
            if stage == 2:
                self.assertEqual(m["Start value, release at once"], nice(rel))
                self.assertEqual(m["Start value, verify then release"], nice(verify))
                exp = "tie" if abs(verify - rel) < 1e-9 else ("verify" if verify > rel else "release")
                self.assertEqual(m["Chosen at the start"], exp)
                self.assertEqual(len(st["steps"]), 6)
            else:
                self.assertEqual(m["Chosen at the start"], "not computed yet")
        # chapter: 92 against 85, a gain of 7; break-even at cost 12 is a tie
        self.assertEqual(by[("book", 2)][0]["Start value, verify then release"], "92.0")
        self.assertEqual(by[("book", 2)][0]["Gain from verifying"], "7.0")
        self.assertEqual(by[("tie", 2)][0]["Chosen at the start"], "tie")
        # workbench II.1: 80 against -6 + 0.9 x 95 = 79.5; tie discount 86/95
        self.assertEqual(by[("wb1", 2)][0]["Start value, verify then release"], "79.5")
        self.assertIn(f"{86 / 95:.4f}", by[("wb1", 2)][1]["interpretation"])
        # workbench II.3: -6 + 0.75 x 95 = 65.25, release wins by 14.75
        self.assertEqual(by[("wb3", 2)][0]["Start value, verify then release"], "65.25")
        self.assertIn("14.75 more", by[("wb3", 2)][1]["interpretation"])

    def test_d03_horizon_model(self):
        models = ["prep", "wait"]
        par = {"prep": (2.0, -1.0, 6.0), "wait": (1.0, 0.0, 4.0)}
        names = {"prep": ("cash", "prepare"), "wait": ("now", "later")}
        hs, gs = [1, 2, 3], [1.0, 0.5]
        demo = self.demos["C07-D03"]
        by = {}
        for key, st in demo["states"].items():
            mi, hi, gi = [int(i) for i in key.split(",")]
            by[(models[mi], hs[hi], gs[gi])] = (dict(st["metrics"]), st)
        # brute force over every plan: take the immediate action, or invest then collect if a decision is left
        for (model, h, g), (m, st) in by.items():
            a, c, big = par[model]
            plans = {"imm": a, "inv": c + (g * big if h >= 2 else 0.0)}
            self.assertEqual(m["Value of the immediate action"], f"{plans['imm']:.2f}")
            inv = plans["inv"]
            self.assertEqual(m["Value of the investing action"], f"(-{-inv:.2f})" if inv < 0 else f"{inv:.2f}")
            self.assertEqual(m["Start value (the larger)"], f"{max(plans.values()):.2f}")
            if abs(plans["imm"] - inv) < 1e-9:
                exp = "tie"
            else:
                exp = names[model][0] if plans["imm"] > inv else names[model][1]
            self.assertEqual(m["Chosen"], exp)
        self.assertEqual(by[("prep", 2, 1.0)][0]["Chosen"], "prepare")
        self.assertEqual(by[("prep", 1, 1.0)][0]["Chosen"], "cash")      # changed case
        self.assertEqual(by[("prep", 3, 1.0)][0]["Start value (the larger)"], "5.00")  # horizon 3 adds nothing
        self.assertEqual(by[("prep", 2, 0.5)][0]["Chosen"], "tie")
        self.assertEqual(by[("wait", 2, 0.5)][0]["Chosen"], "later")     # transfer case: 0 + 0.5 x 4 = 2 against 1
        self.assertEqual(by[("wait", 2, 0.5)][0]["Start value (the larger)"], "2.00")
        self.assertEqual(by[("wait", 1, 0.5)][0]["Chosen"], "now")
        self.assertTrue(by[("prep", 1, 1.0)][0]["Break-even discount"].startswith("undefined"))
        self.assertEqual(by[("wait", 2, 1.0)][0]["Break-even discount"], "0.25")

    def test_d04_residual_bound(self):
        gs = [0.9, 0.95, 0.99, 1.0]
        demo = self.demos["C07-D04"]
        def T(v, g):
            return (max(85 + g * v[2], -5 + g * v[1]), 97 + g * v[2], g * v[2])
        for key, st in demo["states"].items():
            gi, stage = [int(i) for i in key.split(",")]
            g = gs[gi]
            m = dict(st["metrics"])
            v = (0.0, 0.0, 0.0)
            for _ in range(stage):
                v = T(v, g)
            star = T(T((0.0, 0.0, 0.0), g), g)
            tv = T(v, g)
            residual = max(abs(a - b) for a, b in zip(tv, v))
            error = max(abs(a - b) for a, b in zip(v, star))
            self.assertEqual(m["Residual ||TV - V||"], f"{residual:.2f}")
            self.assertEqual(m["Actual error ||V - V*||"], f"{error:.2f}")
            if g < 1:
                self.assertEqual(m["Bound from Equation (7.5)"], f"{residual / (1 - g):.1f}")
                self.assertLessEqual(error, residual / (1 - g) + 1e-9)
            else:
                self.assertTrue(m["Bound from Equation (7.5)"].startswith("undefined"))
        by = {tuple(int(i) for i in k.split(",")): dict(s["metrics"]) for k, s in demo["states"].items()}
        self.assertEqual(by[(1, 0)]["Bound from Equation (7.5)"], "1940.0")      # 97 / 0.05
        self.assertEqual(by[(2, 0)]["Bound from Equation (7.5)"], "9700.0")      # 97 / 0.01
        self.assertEqual(by[(0, 0)]["Bound from Equation (7.5)"], "970.0")       # the chapter-style check
        self.assertEqual(by[(0, 1)]["Actual error ||V - V*||"], "0.00")          # at 0.9 releasing is already optimal
        self.assertEqual(by[(1, 1)]["Residual ||TV - V||"], "2.15")             # -5 + 0.95 x 97 - 85
        self.assertEqual(by[(1, 2)]["Bound from Equation (7.5)"], "0.0")

    def svg(self, state):
        return base64.b64decode(state["image"].split(",", 1)[1]).decode("utf-8")

    def test_d04_figure_title_matches_bound(self):
        # at discount 1 no bound exists, so the title may not say the error never exceeds it.
        for key, state in self.demos["C07-D04"]["states"].items():
            gi, stage = [int(i) for i in key.split(",")]
            g = [0.9, 0.95, 0.99, 1.0][gi]
            svg = self.svg(state)
            if g < 1:
                self.assertIn(f"Discount {g:.2f}: error never exceeds the bound", svg)
                self.assertNotIn("no bound exists", svg)
            else:
                self.assertIn("Discount 1.00: no bound exists", svg)
                self.assertNotIn("never exceeds", svg)
                self.assertIn("this finite-horizon model (its terminal state loops with reward 0)", state["interpretation"])
            self.assertIn("largest gap, V to V*", svg)
            self.assertIn("largest gap, TV to V", svg)
            self.assertNotIn("||V - V*||", svg)

    def test_d04_ratio_for_loose_bound(self):
        by = {k: st for k, st in self.demos["C07-D04"]["states"].items()}
        self.assertIn("(here 100.0 times the error)", by["2,0"]["interpretation"])
        self.assertNotIn("times the error", by["0,1"]["interpretation"])
        self.assertIn("changed nothing here", by["0,2"]["interpretation"])

    def test_wording(self):
        text = html.unescape(self.page)
        self.assertIn("How many decisions are left can change the answer", text)
        self.assertIn("Workbench II.1", text)

    def test_d01_figure_names_the_other_curves(self):
        for key, state in self.demos["C07-D01"]["states"].items():
            gi, _ = [int(i) for i in key.split(",")]
            g = [0.5, 0.9, 0.95, 0.99][gi]
            others = [x for x in (0.5, 0.9, 0.95, 0.99) if x != g]
            self.assertIn("steepest first: " + ", ".join(f"{x:.2f}" for x in others), self.svg(state))

    def test_equations_come_from_chapter(self):
        chapter = next(c for c in json.loads((LAB / "chapter-map.json").read_text()) if c["chapter"] == 7)
        def norm(t):
            t = re.sub(r"\\tag\{[^}]*\}", "", t)
            t = re.sub(r"\\[,;:!]", "", t)
            return re.sub(r"[\s{}]", "", t).rstrip(".")
        allowed = {norm(e["tex"]) for e in chapter["equations"]}
        alts = re.findall(r'data-tex="([^"]+)"', self.page)
        self.assertEqual(len(alts), 6)
        for tex in alts:
            self.assertIn(norm(html.unescape(tex)), allowed)

    def test_patch2_small_gamma_and_notation(self):
        # g3-03: the rule of a third is only approximate at gamma 0.5 (25.0 is a quarter)
        demo = self.demos["C07-D01"]
        st = demo["states"]["0,0"]
        self.assertIn("a quarter", st["interpretation"])
        self.assertIn("only approximate for small gamma", st["interpretation"])
        self.assertNotIn("about a third of 100", " ".join(st["steps"]))
        st = demo["states"]["2,0"]
        self.assertIn("roughly a third", st["interpretation"])
        # g3-04: no raw scientific notation for tiny values
        for key in ("0,1", "0,2"):
            st = demo["states"][key]
            blob = st["interpretation"] + " " + " ".join(f"{k} {v}" for k, v in st["metrics"]) + " " + " ".join(st["steps"])
            self.assertNotRegex(blob, r"\de-\d")
            self.assertIn("x 10^-", blob)
            self.assertIn("less than 0.0001", blob)

    def test_patch2_negative_break_even_explained(self):
        # g3-05: at discount 0.75 even a free verification loses (0.75 x 95 = 71.25 < 80)
        st = self.demos["C07-D02"]["states"]["3,2"]
        text = st["interpretation"]
        self.assertIn("Even a free verification would lose", text)
        self.assertIn("0.75 x 95.0 = 71.25", text)
        self.assertIn("no cost can rescue verification", text)
        self.assertNotIn("this verification costs more than the later support it buys", text)
        # the book controller keeps the cost-based wording
        self.assertNotIn("Even a free verification", self.demos["C07-D02"]["states"]["0,2"]["interpretation"])

    def test_patch2_provenance_prediction_alt(self):
        # g3-06, g3-07, g3-08
        text = html.unescape(self.page)
        self.assertIn("derived from it as 97 - 85 and 90/97", text)
        self.assertNotIn("Release at once (85)", text)
        self.assertNotIn("Verify, then release (92)", text)
        self.assertEqual(self.demos["C07-D02"]["controls"][1]["default"], 0)
        alt = self.demos["C07-D03"]["states"]["0,0,0"]["alt"]
        self.assertIn("with 1 decision left", alt)
        self.assertNotIn("1 decisions", alt)

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
