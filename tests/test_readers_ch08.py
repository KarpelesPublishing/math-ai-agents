"""Chapter 8 laboratory reader: independent hand checks of the built page.

Expected numbers are recomputed here with exact fractions and closed forms (belief updates,
Bayes posteriors, plan dot products, value of one report), not read back from the module.
"""
from __future__ import annotations

from fractions import Fraction as F
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
SLUG = "08-belief-information"


def build_python():
    venv = LAB / ".venv" / "bin" / "python"
    return str(venv) if venv.exists() else sys.executable


def as_number(text):
    try:
        return float(text)
    except ValueError:
        return text


class Chapter8ReaderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        run = subprocess.run([build_python(), str(WRAPPER), "--chapters", "8", "--out", cls.tmp.name],
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

    def by_index(self, demo_id):
        out = {}
        for key, st in self.demos[demo_id]["states"].items():
            out[tuple(int(i) for i in key.split(","))] = (dict(st["metrics"]), st)
        return out

    def test_structure_and_optional_fields(self):
        self.assertEqual(list(self.demos), ["C08-D01", "C08-D02", "C08-D03", "C08-D04"])
        self.assertEqual([len(d["states"]) for d in self.data["demos"]], [12, 12, 12, 12])
        self.assertLess(self.reader.stat().st_size, 4_000_000)
        text = html.unescape(self.page)
        self.assertIn("Ask the chapter skill", text)
        self.assertEqual(text.count("Common wrong turn"), 4)
        self.assertGreaterEqual(text.count("What this does not settle"), 4)
        self.assertEqual(len(re.findall(r'type="radio"', text)), 12)
        for d in self.data["demos"]:
            for s in d["states"].values():
                self.assertTrue(s.get("steps"))

    def update(self, belief, T, O):
        k = len(belief)
        pred = [sum(belief[i] * T[i][j] for i in range(k)) for j in range(k)]
        mass = sum(pred[j] * O[j] for j in range(k))
        return pred, mass, [pred[j] * O[j] / mass for j in range(k)]

    def f3(self, x):
        return f"{float(x):.3f}"

    def test_d01_update_stages(self):
        s = F(1, 10)
        T = [[s, 1 - s, 0, 0], [s, 0, 1 - s, 0], [0, s, 0, 1 - s], [0, 0, s, 1 - s]]
        Og = [F(1), F(1), F(0), F(1)]
        b0 = [F(1, 3), F(1, 3), F(0), F(1, 3)]
        p1, m1, b1 = self.update(b0, T, Og)
        p2, m2, b2 = self.update(b1, T, Og)
        # the paper's reported sequence
        self.assertEqual(b1, [F(1, 10), F(9, 20), F(0), F(9, 20)])
        self.assertEqual(p1, [F(1, 15), F(3, 10), F(1, 3), F(3, 10)])
        self.assertEqual(b2, [F(1, 10), F(9, 55), F(0), F(81, 110)])
        self.assertEqual(m2, F(11, 20))
        I = [[1, 0], [0, 1]]
        tr = [[F(7, 10), F(3, 10)], [F(1, 5), F(4, 5)]]
        cases = {
            0: (b0, T, Og, p1, m1, b1),
            1: (b1, T, Og, p2, m2, b2),
            2: ([F(1, 2), F(1, 2)], I, [F(9, 10), F(1, 10)], None, None, None),
            3: ([F(4, 5), F(1, 5)], tr, [F(1, 5), F(7, 10)], None, None, None),
        }
        got = self.by_index("C08-D01")
        for ci, (b, Tm, Om, p, m, post) in cases.items():
            p, m, post = self.update(b, Tm, Om)
            for stage in range(3):
                met, st = got[(ci, stage)]
                self.assertEqual(met["Prior belief"], ", ".join(self.f3(x) for x in b))
                if stage >= 1:
                    self.assertEqual(met["Predicted belief"], ", ".join(self.f3(x) for x in p))
                else:
                    self.assertEqual(met["Predicted belief"], "not computed yet")
                if stage == 2:
                    self.assertEqual(met["Belief after the report"], ", ".join(self.f3(x) for x in post))
                    self.assertEqual(met["Weight the report keeps"], self.f3(m))
                else:
                    self.assertEqual(met["Belief after the report"], "not computed yet")
        # notebook cases: default posterior (0.9, 0.1); transfer predictive (0.6, 0.4), posterior (0.3, 0.7)
        self.assertEqual(got[(2, 2)][0]["Belief after the report"], "0.900, 0.100")
        self.assertEqual(got[(3, 1)][0]["Predicted belief"], "0.600, 0.400")
        self.assertEqual(got[(3, 2)][0]["Belief after the report"], "0.300, 0.700")
        self.assertEqual(got[(3, 2)][0]["Weight the report keeps"], "0.400")

    def test_d02_instrument_posteriors(self):
        kernels = [(1.0, 0.03, 0.8), (1.0, 0.30, 0.8), (0.9, 0.1, 0.5), (0.5, 0.5, 0.5)]
        priors = [0.2, 0.5, 0.8]
        got = self.by_index("C08-D02")
        for (ki, pi), (met, st) in got.items():
            tp, fp, thr = kernels[ki]
            p = priors[pi]
            post = p * tp / (p * tp + (1 - p) * fp)
            self.assertEqual(met["Posterior, first state"], f"{post:.4f}")
            self.assertEqual(met["Chance of this report"], f"{p * tp + (1 - p) * fp:.4f}")
            exp = "exactly on the threshold" if abs(post - thr) < 1e-9 else ("above the threshold" if post > thr else "below the threshold")
            if ki == 3:   # aliased sensor: the report left the prior where it was (g3-17)
                exp += " (unchanged: the report left the prior where it was)"
            self.assertEqual(met["Compared with the threshold"], exp)
        self.assertEqual(got[(0, 1)][0]["Posterior, first state"], "0.9709")   # 1 / 1.03
        self.assertEqual(got[(1, 1)][0]["Posterior, first state"], "0.7692")   # 1 / 1.30
        self.assertEqual(got[(2, 1)][0]["Posterior, first state"], "0.9000")   # notebook default posterior
        self.assertEqual(got[(3, 1)][0]["Change from the prior"], "0.0000")    # aliasing: no information
        self.assertEqual(got[(3, 0)][0]["Change from the prior"], "0.0000")
        # the false-positive that puts the posterior exactly at 0.80 is 0.25
        self.assertAlmostEqual(0.5 / (0.5 + 0.5 * 0.25), 0.8)

    def test_d03_plans_and_memories(self):
        settings = [
            ((4.0, 1.0), (0.0, 3.0), [0.25, 0.5, 0.75], ["plan 1", "plan 2"]),
            ((4.0, -12.0), (0.0, 0.0), [1.0, 0.0, 0.5], ["release", "hold"]),
            ((4.0, -12.0), (0.0, 0.0), [0.5, 0.5, 0.5], ["release", "hold"]),
            ((100.0, 0.0), (97.0, 97.0), [0.45, 0.98, 0.97], ["commit now", "detour first"]),
        ]
        got = self.by_index("C08-D03")
        for (si, ci), (met, st) in got.items():
            a1, a2, bs, names = settings[si]
            b = bs[ci]
            v1 = a1[0] * b + a1[1] * (1 - b)
            v2 = a2[0] * b + a2[1] * (1 - b)
            def sg(x):
                return f"(-{-x:.2f})" if x < -1e-12 else f"{abs(x) if abs(x) < 1e-12 else x:.2f}".replace("-", "")
            self.assertEqual(met[f"Value of {names[0]}"], sg(v1))
            self.assertEqual(met[f"Value of {names[1]}"], sg(v2))
            self.assertEqual(met["Belief value V(b) (the larger)"], sg(max(v1, v2)))
            exp = "tie" if abs(v1 - v2) < 1e-9 else (names[0] if v1 > v2 else names[1])
            self.assertEqual(met["Chosen"], exp)
        # chapter: 1.75 and 2.25 at belief (0.25, 0.75); the second plan is selected
        m = got[(0, 0)][0]
        self.assertEqual((m["Value of plan 1"], m["Value of plan 2"], m["Chosen"]), ("1.75", "2.25", "plan 2"))
        self.assertEqual(m["Crossing belief"], "0.333")
        # detour: commit 45 against 97 (detour wins by 52); belief 0.98 gives 98 against 97; 0.97 ties
        self.assertEqual(got[(3, 0)][0]["Chosen"], "detour first")
        self.assertIn("wins by 52", got[(3, 0)][1]["interpretation"])
        self.assertEqual(got[(3, 1)][0]["Chosen"], "commit now")
        self.assertEqual(got[(3, 2)][0]["Chosen"], "tie")
        # one-bit memories: authorization yes releases (4.00), no holds; formatting leaves belief 0.5 and release (-4.00)
        self.assertEqual(got[(1, 0)][0]["Chosen"], "release")
        self.assertEqual(got[(1, 1)][0]["Chosen"], "hold")
        self.assertEqual(got[(2, 0)][0]["Value of release"], "(-4.00)")
        self.assertIn("(4 + 4 + 0 + 0) / 4 = 2.0", got[(1, 0)][1]["interpretation"])
        self.assertIn("(0 + 0 + 0 + 0) / 4 = 0.0", got[(2, 0)][1]["interpretation"])

    def voi(self, pred, O, R):
        k = len(pred)
        now = max(sum(pred[j] * r[j] for j in range(k)) for r in R)
        after = 0.0
        for o in range(len(O[0])):
            after += max(sum(pred[j] * O[j][o] * r[j] for j in range(k)) for r in R)
        return after - now

    def test_d04_value_of_looking(self):
        cases = [
            ([0.6, 0.4], [[0.9, 0.1], [0.15, 0.85]], [[10, -40], [0, 0]], 1.0),
            ([0.5, 0.5], [[0.9, 0.1], [0.1, 0.9]], [[10, -10], [-10, 10]], 1.0),
            ([0.5, 0.5], [[0.5, 0.5], [0.5, 0.5]], [[10, -10], [-10, 10]], 1.0),
            ([0.6, 0.4], [[0.8, 0.2], [0.3, 0.7]], [[5, -4], [0, 2]], 0.2),   # predictive belief of the transfer case
        ]
        got = self.by_index("C08-D04")
        for (ci, pi), (met, st) in got.items():
            pred, O, R, case_price = cases[ci]
            gross = self.voi(pred, O, R)
            gross = 0.0 if abs(gross) < 1e-12 else gross
            cost = [0.0, case_price, gross][pi]
            self.assertEqual(met["Value of looking (gross)"], f"{gross:.2f}")
            self.assertEqual(met["Price of looking"], f"{cost:.2f}")
            self.assertEqual(met["Net value of looking"], f"{abs(gross - cost) if abs(gross - cost) < 1e-9 else gross - cost:.2f}".replace("-0.00", "0.00"))
        # chapter: 3.0 at prior 0.6; notebook default 8 gross, 7 net at price 1, break-even price 8
        self.assertEqual(got[(0, 0)][0]["Value of looking (gross)"], "3.00")
        self.assertEqual(got[(1, 1)][0]["Net value of looking"], "7.00")
        self.assertEqual(got[(1, 2)][0]["Price of looking"], "8.00")
        # notebook changed: identical rows give 0 and net (-1); transfer: gross computed by hand above
        self.assertEqual(got[(2, 0)][0]["Value of looking (gross)"], "0.00")
        self.assertEqual(got[(2, 1)][0]["Net value of looking"], "-1.00")
        self.assertEqual(got[(2, 1)][0]["Decision"], "do not look (value 0)")
        self.assertEqual(got[(3, 0)][0]["Value of looking (gross)"], f"{self.voi(*cases[3][:3]):.2f}")
        self.assertEqual(got[(0, 2)][0]["Decision"], "tie (break-even)")
        # chapter's zero regions: beliefs 0.2 and 0.99 give exactly 0, 0.8 is the peak 6.0
        tool = cases[0]
        for p, exp in ((0.2, 0.0), (0.99, 0.0), (0.8, 6.0)):
            self.assertAlmostEqual(self.voi([p, 1 - p], tool[1], tool[2]), exp, places=9)

    def test_equations_come_from_chapter(self):
        chapter = next(c for c in json.loads((LAB / "chapter-map.json").read_text()) if c["chapter"] == 8)
        def norm(t):
            t = re.sub(r"\\tag\{[^}]*\}", "", t)
            t = re.sub(r"\\[,;:!]", "", t)
            return re.sub(r"[\s{}]", "", t).rstrip(".")
        allowed = {norm(e["tex"]) for e in chapter["equations"]}
        alts = re.findall(r'data-tex="([^"]+)"', self.page)
        self.assertEqual(len(alts), 7)
        for tex in alts:
            self.assertIn(norm(html.unescape(tex)), allowed)

    def test_patch2_labels_and_text(self):
        text = html.unescape(self.page)
        # g3-18: the detour value is stipulated, not derived from a certain route
        self.assertIn("stipulates 97 for the detour", text)
        self.assertNotIn("three-move cost 3 followed by a routed value of 100", text)
        # g3-19: formatting cases are letters, no unexplained loss label, and the two memories are compared
        self.assertNotIn("(loss 12)", text)
        self.assertNotIn("no message, prior", text)
        st = self.demos["C08-D03"]["states"]["2,0"]
        self.assertEqual(dict(st["metrics"])["Mean utility over four histories: authorization memory against formatting memory"], "2.0 against 0.0")
        # g3-23: the default case needs one control change to reach the prediction's belief
        self.assertEqual(self.demos["C08-D03"]["controls"][1]["default"], 1)
        # g3-14: stage 1 no longer restates a trivial sum over the first two coordinates
        st = self.demos["C08-D01"]["states"]["2,0"]
        self.assertNotIn("first two coordinates hold", st["interpretation"])
        self.assertIn("will later weight", st["interpretation"])
        # g3-17: aliased sensor adds no information, so the threshold comparison is flagged as unchanged
        st = self.demos["C08-D02"]["states"]["3,2"]
        self.assertIn("decision is whatever the prior already implied", st["interpretation"])
        self.assertIn("unchanged", dict(st["metrics"])["Compared with the threshold"])
        # g3-22: exact band edges are stated (chapter: 0.4 and 34/35 for the tool; 9/29 and 21/26 for the transfer case)
        tool = self.demos["C08-D04"]["states"]["0,0"]["interpretation"]
        self.assertIn("between 0.4000 and 0.9714", tool)
        transfer = self.demos["C08-D04"]["states"]["3,0"]["interpretation"]
        self.assertIn("between 0.3103 and 0.8077", transfer)

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
