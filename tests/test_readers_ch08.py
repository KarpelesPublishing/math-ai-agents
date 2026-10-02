"""Chapter 8 laboratory reader: independent hand checks of the built page.

Expected numbers are recomputed here with exact fractions and closed forms
(the corridor update, the runner posterior, the one-bit memory table and the
verification-tool value), not read back from the module that produced the page.
"""
from __future__ import annotations

from fractions import Fraction as F
import html
import json
import math
from pathlib import Path
import re
import shutil
import subprocess
import sys
import unittest

HERE = Path(__file__).resolve().parent
LAB = HERE.parent
sys.path.insert(0, str(LAB / "tools" / "readers" / "engine"))
sys.path.insert(0, str(LAB / "tools" / "readers" / "chapters"))
import os
_CANDIDATES = [Path(os.environ["READER_CH08"])] if os.environ.get("READER_CH08") else []
_CANDIDATES += [LAB / "readers" / "08-belief-information" / "reader.html",
                Path("/private/tmp/readers-ch08/08-belief-information/reader.html")]
READER = next((p for p in _CANDIDATES if p.is_file()), _CANDIDATES[0])
HARNESS = LAB / "tools" / "readers" / "engine" / "dom_harness.js"


def payload(text):
    return json.loads(re.search(r'<script id="reader-data" type="application/json">(.*?)</script>', text, re.S).group(1))


def num(x):
    try:
        return float(x)
    except ValueError:
        return x


def corridor(moves, slip):
    """Exact corridor filter with fractions: predict through T_E, drop the goal, rescale."""
    s = F(str(slip))
    T = [[s, 1 - s, 0, 0], [s, 0, 1 - s, 0], [0, s, 0, 1 - s], [0, 0, s, 1 - s]]
    b = [F(1, 3), F(1, 3), F(0), F(1, 3)]
    for _ in range(moves):
        before = b
        pred = [sum(before[i] * T[i][j] for i in range(4)) for j in range(4)]
        mass = 1 - pred[2]
        b = [pred[j] / mass if j != 2 else F(0) for j in range(4)]
    return before, pred, b, mass


def vo(p):
    """Value of one verification report by the closed form with joint weights."""
    now = max(10 * p - 40 * (1 - p), 0)
    ps = max(0.9 * p * 10 - 0.15 * (1 - p) * 40, 0)
    fl = max(0.1 * p * 10 - 0.85 * (1 - p) * 40, 0)
    return ps + fl - now, now


@unittest.skipUnless(READER.is_file(), "Chapter 8 reader not built")
class Chapter8ReaderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.page = READER.read_text(encoding="utf-8")
        cls.data = payload(cls.page)
        cls.demos = {d["id"]: d for d in cls.data["demos"]}

    def states(self, demo_id):
        demo = self.demos[demo_id]
        for key, state in demo["states"].items():
            idx = [int(i) for i in key.split(",")]
            yield [num(c["values"][i]) for c, i in zip(demo["controls"], idx)], dict(state["metrics"]), state

    def test_shape_and_budget(self):
        self.assertEqual(list(self.demos), ["C08-D01", "C08-D02", "C08-D03", "C08-D04"])
        self.assertEqual([len(d["states"]) for d in self.data["demos"]], [6, 8, 6, 8])
        self.assertLess(READER.stat().st_size, 2_500_000)

    def test_d01_corridor_matches_exact_fractions(self):
        f3 = lambda v: f"{float(v):.3f}"
        for (moves, slip), m, _ in self.states("C08-D01"):
            before, pred, after, mass = corridor(int(moves), slip)
            self.assertEqual(m["Predicted after EAST"], ", ".join(map(f3, pred)))
            self.assertEqual(m["Belief after the report"], ", ".join(map(f3, after)))
            self.assertEqual(m["Weight the report keeps"], f3(mass))
            self.assertEqual(m["West end after the report"], f3(after[0]))
            self.assertEqual(after[2], 0)
            self.assertGreater(after[0], 0)
        # The book's own numbers: (1/15, 3/10, 1/3, 3/10), then (0.10, 0.45, 0, 0.45), then (0.100, 9/55, 0, 81/110).
        _, pred, after, mass = corridor(1, "0.1")
        self.assertEqual(pred, [F(1, 15), F(3, 10), F(1, 3), F(3, 10)])
        self.assertEqual((after, mass), ([F(1, 10), F(9, 20), 0, F(9, 20)], F(2, 3)))
        _, pred, after, mass = corridor(2, "0.1")
        self.assertEqual(pred, [F(55, 1000), F(9, 100), F(9, 20), F(405, 1000)])
        self.assertEqual((after[0], after[1], after[3], mass), (F(1, 10), F(9, 55), F(81, 110), F(11, 20)))
        page_default = dict(self.demos["C08-D01"]["states"]["0,0"]["metrics"])
        self.assertEqual(page_default["Belief after the report"], "0.100, 0.450, 0.000, 0.450")

    def test_d01_transfer_answer(self):
        _, pred, after, mass = corridor(1, "0.2")
        self.assertEqual((pred[0], mass, after[0]), (F(2, 15), F(2, 3), F(1, 5)))
        self.assertEqual(pred[2], F(1, 3))

    def test_d02_runner_posterior_closed_form(self):
        for (fp, prior), m, state in self.states("C08-D02"):
            post = prior / (prior + (1 - prior) * fp)
            self.assertEqual(m["Posterior, tests pass"], f"{post:.4f}")
            self.assertEqual(m["Chance of a pass report"], f"{prior + (1 - prior) * fp:.4f}")
            self.assertEqual(m["Compared with 0.80"], "above 0.80" if post > 0.8 + 1e-9 else "below 0.80")
        book = self.demos["C08-D02"]["states"]
        self.assertEqual(dict(book["0,0"]["metrics"])["Posterior, tests pass"], "0.9709")  # 1/1.03
        self.assertEqual(dict(book["2,0"]["metrics"])["Posterior, tests pass"], "0.7692")  # 1/1.30
        # Uninformative boundary: false-positive 1 returns the prior.
        self.assertEqual(dict(book["3,0"]["metrics"])["Posterior, tests pass"], "0.5000")
        self.assertEqual(dict(book["3,1"]["metrics"])["Posterior, tests pass"], "0.2000")
        # Check-question answer: f = 0.25 puts the posterior exactly at 0.8.
        self.assertAlmostEqual(0.5 / (0.5 + 0.5 * 0.25), 0.8)

    def test_d03_one_bit_memories(self):
        for (memory, loss), m, state in self.states("C08-D03"):
            mean = (4 + 4 + 0 + 0) / 4 if memory == "Authorization" else 0.0
            self.assertEqual(m["Mean utility, four histories"], f"{mean:.1f}")
            if memory == "Formatting letter":
                self.assertEqual(m["Release value at that belief"], f"{0.5 * 4 + 0.5 * loss:.1f}")
                self.assertIn("hold", m["Action taken"])
            else:
                self.assertIn("release on yes", m["Action taken"])
        # Chapter numbers: release at belief 0.5 with loss 12 is (4 - 12) / 2 = -4.
        fmt_state = self.demos["C08-D03"]["states"]["1,0"]
        self.assertEqual(dict(fmt_state["metrics"])["Release value at that belief"], "-4.0")
        # Tie at loss 4: unconstrained release equals hold.
        self.assertIn("tie at 0.0", self.demos["C08-D03"]["states"]["1,1"]["interpretation"])
        self.assertAlmostEqual(20 / 24, 0.8333, places=3)

    def test_d04_value_of_looking(self):
        for (p, cost), m, _ in self.states("C08-D04"):
            gross, now = vo(p)
            self.assertEqual(m["Value of looking (gross)"], f"{gross:.2f}")
            cost = {"Free": 0.0, "3.0 utility points": 3.0}[cost]
            net = gross - cost
            self.assertEqual(m["Net value of looking"], f"{abs(net):.2f}" if abs(net) < 1e-9 else f"{net:.2f}")
        # The book's numbers: 3.0 at 0.6, exactly 0 at 0.2 and 0.99, peak 6.0 at 0.8, band edges 0.4 and 34/35.
        self.assertAlmostEqual(vo(0.6)[0], 3.0)
        self.assertAlmostEqual(vo(0.2)[0], 0, places=12)
        self.assertAlmostEqual(vo(0.99)[0], 0, places=12)
        self.assertAlmostEqual(vo(0.8)[0], 6.0)
        self.assertAlmostEqual(vo(0.4)[0], 0, places=12)
        self.assertGreater(vo(0.41)[0], 0)
        self.assertAlmostEqual(vo(34 / 35 + 1e-6)[0], 0, places=12)
        self.assertGreater(vo(34 / 35 - 1e-3)[0], 0)
        self.assertAlmostEqual(vo(0.5)[0], 1.5)  # check-question answer
        be = self.demos["C08-D04"]["states"]["1,1"]  # prior 0.6 at cost 3: break-even tie
        self.assertEqual(dict(be["metrics"])["Decision"], "tie (break-even)")
        self.assertEqual(dict(self.demos["C08-D04"]["states"]["0,1"]["metrics"])["Decision"], "do not look (value 0)")
        self.assertIn("tie at 0.0", self.demos["C08-D04"]["states"]["2,0"]["interpretation"])

    def test_g3_wording_and_tie_fixes(self):
        import ch08
        # g3-15: a tie at prior 0.8 is shown as a tie, not as decline
        _, metrics, text = ch08.look_picture(0.8, 0)
        self.assertEqual(metrics["Best action without looking"], "tie (0.0)")
        self.assertNotIn("decline (0.0)", metrics["Best action without looking"])
        _, metrics, _ = ch08.look_picture(0.2, 0)
        self.assertEqual(metrics["Best action without looking"], "decline (0.0)")
        # g3-16: the sums are labelled as joint weights and the 0.15 is explained; 3.00 = 0.60 x 5.00
        _, _, text = ch08.look_picture(0.6, 0)
        self.assertIn("0.90 x 0.60 x 10 - 0.15 x 0.40 x 40 = 5.40 - 2.40 = 3.00", text)
        self.assertIn("After a pass (chance 0.60)", text)
        self.assertIn("0.15 = 1 - 0.85 is the chance that an unsupported claim still passes", text)
        self.assertIn("weighted best release at 3.00 (0.60 x 5.00:", text)
        self.assertNotIn("best release at 3.00.", text)
        self.assertAlmostEqual(0.9 * 0.6 + 0.15 * 0.4, 0.60)
        self.assertAlmostEqual((0.9 * 0.6 * 10 - 0.15 * 0.4 * 40) / 0.60, 5.0)
        # g3-14: the prior is held fixed when only the instrument changes; the conclusion flips with the prior too
        self.assertAlmostEqual(0.5 / (0.5 + 0.5 * 0.1), 0.9091, places=4)
        self.assertAlmostEqual(0.2 / (0.2 + 0.8 * 0.1), 0.7143, places=4)
        d2 = next(d for d in ch08.CHAPTER["demos"] if d["id"] == "C08-D02")
        self.assertIn("Holding the prior fixed, only the assumed instrument changes", d2["explanation"])
        self.assertNotIn("Only the assumed instrument changes", d2["explanation"])
        _, _, text = ch08.runner_picture(0.1, 0.5)
        self.assertIn("Holding the prior fixed, the only thing that changes", text)
        self.assertNotIn("The only thing that changed between states is the assumed instrument", text)
        # g3-12: the west end is not conserved beyond the two worked moves
        for slip, third in (("0.1", 0.0338), ("0.3", 0.2829)):
            _, _, after, _ = corridor(3, slip)
            self.assertAlmostEqual(float(after[0]), third, places=4)
        d1 = next(d for d in ch08.CHAPTER["demos"] if d["id"] == "C08-D01")
        self.assertIn("true of those two moves only, and a third move lowers it", d1["explanation"])
        # g3-13: the symbols paragraph defines a, P(x' | x, a), Obs with its action, x'' and the sums
        for piece in ("a is the action taken", "P(x' | x, a) is the chance that action a moves place x to place x'",
                      "Obs(o | x', a)", "x'' is a stand-in place", "each sum runs over the four places"):
            self.assertIn(piece, d1["symbols"])

    def test_default_hand_sums_present(self):
        self.assertIn("0.90 x 0.60 x 10 - 0.15 x 0.40 x 40 = 5.40 - 2.40 = 3.00", self.page)
        self.assertIn("0.50 x 1 / (0.50 x 1 + 0.50 x 0.03) = 0.50 / 0.5150 = 0.9709", self.page)

    def test_equations_are_chapter_equations(self):
        chapter = next(c for c in json.loads((LAB / "chapter-map.json").read_text()) if c["chapter"] == 8)
        norm = lambda t: re.sub(r"[\s{}]", "", re.sub(r"\\[,;:!]", "", re.sub(r"\\tag\{[^}]*\}", "", t))).rstrip(".")
        allowed = {norm(e["tex"]) for e in chapter["equations"]}
        alts = re.findall(r'data-tex="([^"]+)"', self.page)
        self.assertTrue(alts)
        for tex in alts:
            self.assertIn(norm(html.unescape(tex)), allowed)

    def test_page_text_rules(self):
        text = re.sub(r"<script\b.*?</script>|<style\b.*?</style>", " ", self.page, flags=re.S)
        text = html.unescape(re.sub(r"<[^>]+>", " ", text))
        for state in (s for d in self.data["demos"] for s in d["states"].values()):
            text += " " + state["interpretation"] + " " + " ".join(" ".join(p) for p in state["metrics"])
        for bad in ("\u2014", "\u2013", "--", "\u2212"):
            self.assertNotIn(bad, text)
        for term in ("matplotlib", "numpy", "python", "jupyter"):
            self.assertNotIn(term, text.lower())
        self.assertIn("constructed", text.lower())

    def test_dom_harness(self):
        if shutil.which("node") is None:
            self.skipTest("Node is not installed")
        run = subprocess.run(["node", str(HARNESS), str(READER)], capture_output=True, text=True, timeout=120)
        self.assertEqual(run.returncode, 0, run.stderr)
        report = json.loads(run.stdout)["reports"][0]
        self.assertEqual((report["states_checked"], report["labelled_controls"]), (28, 8))

    def test_every_control_combination_renders(self):
        import itertools
        try:
            import matplotlib
            import numpy  # noqa: F401
        except ImportError:
            self.skipTest('plotting libraries unavailable')
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import ch08
        for demo in ch08.CHAPTER["demos"]:
            fn = getattr(ch08, demo["function"])
            for combo in itertools.product(*[c["values"] for c in demo["controls"]]):
                fig, metrics, text = fn(**{c["key"]: v for c, v in zip(demo["controls"], combo)})
                self.assertTrue(metrics and text)
                plt.close(fig)


if __name__ == "__main__":
    unittest.main()
