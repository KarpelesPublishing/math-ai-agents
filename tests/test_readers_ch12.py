"""Chapter 12 laboratory reader: independent hand checks of the built page.

Every expected number is recomputed here from the chapter's own arithmetic
(the four-step trajectory, the eight episodes, the weights of Equation (12.4),
the first search's TD error), not read back from the module that produced the
page. The page is built into a temporary directory, so the test does not
depend on the committed readers folder.
"""
from __future__ import annotations

import html
import itertools
import json
import math
import os
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
    return json.loads(re.search(r'<script id="reader-data" type="application/json">(.*?)</script>', text, re.S).group(1))


def as_number(text):
    try:
        return float(text)
    except ValueError:
        return text


@unittest.skipUnless(VENV_PYTHON.is_file(), "laboratory .venv absent")
class Chapter12ReaderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        run = subprocess.run([str(VENV_PYTHON), str(WRAPPER), "--chapters", "12", "--out", cls.tmp.name],
                             capture_output=True, text=True, timeout=600, env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
        assert run.returncode == 0, run.stdout + run.stderr
        cls.reader = Path(cls.tmp.name) / "12-trajectory-credit" / "reader.html"
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
        self.assertEqual(list(self.demos), ["C12-D01", "C12-D02", "C12-D03", "C12-D04"])
        self.assertEqual([len(d["states"]) for d in self.data["demos"]], [6, 6, 8, 8])
        self.assertLess(self.reader.stat().st_size, 2_500_000)

    def test_d01_one_trajectory_by_hand(self):
        for (alpha, reward), state in self.states("C12-D01"):
            reward = float(str(reward).split()[0])  # the control shows a label such as '1 (the run succeeds)'
            m = dict(state["metrics"])
            outcome = 0.5 + alpha * (reward - 0.5)             # Equation (12.1), same target for all four states
            delta4 = reward + 0 - 0.5                          # Equation (12.2) at state 4
            state4 = 0.5 + alpha * delta4                      # Equation (12.3)
            self.assertEqual(m["Outcome rule, each of the 4 states"], f"{outcome:.3f}")
            self.assertEqual(m["One-step rule, state 4"], f"{state4:.3f}")
            self.assertEqual(m["One-step rule, states 1 to 3"], "0.500")  # errors 0 + 0.5 - 0.5 = 0
            self.assertEqual(m["States moved (outcome / one-step)"], "4 / 1")
        book = dict(self.demos["C12-D01"]["states"]["0,0"]["metrics"])  # the book's alpha = 0.1, reward 1
        self.assertEqual((book["Outcome rule, each of the 4 states"], book["One-step rule, state 4"]), ("0.550", "0.550"))
        self.assertIn("0.5 + 0.1 x (1 - 0.5) = 0.550", self.page)

    def test_d02_eight_episodes_by_hand(self):
        for (ones, a_final), state in self.states("C12-D02"):
            # Independent batch run of both rules on the eight episodes.
            b_rewards = [a_final] + [1] * int(ones) + [0] * (7 - int(ones))
            va = vb = 0.0
            for _ in range(20000):
                da = vb - va
                db = sum(r - vb for r in b_rewards) / 8
                va, vb = va + 0.05 * da, vb + 0.05 * db
            m = dict(state["metrics"])
            self.assertAlmostEqual(float(m["Value of B (both rules)"]), vb, places=3)
            self.assertAlmostEqual(float(m["Value of A, one-step rule"]), va, places=3)
            self.assertEqual(m["Value of A, outcome rule"], f"{float(a_final):.3f}")  # the one return A saw
            self.assertEqual(m["Value of B (both rules)"], f"{(ones + a_final) / 8:.3f}")
            self.assertEqual(m["Disagreement about A"], f"{abs((ones + a_final) / 8 - a_final):.3f}")
        book = dict(self.demos["C12-D02"]["states"]["1,0"]["metrics"])  # six ones, A episode ends at 0
        self.assertEqual((book["Value of B (both rules)"], book["Value of A, outcome rule"], book["Value of A, one-step rule"]),
                         ("0.750", "0.000", "0.750"))
        agree = dict(self.demos["C12-D02"]["states"]["2,1"]["metrics"])  # seven ones, A episode ends at 1: rules agree
        self.assertEqual(agree["Disagreement about A"], "0.000")
        self.assertIn("agree", self.demos["C12-D02"]["states"]["2,1"]["interpretation"])

    def test_d03_lambda_weights_by_hand(self):
        for (lam, n), state in self.states("C12-D03"):
            n = int(n)
            weights = [(1 - lam) * lam ** (k - 1) for k in range(1, n)] + [lam ** (n - 1)]
            self.assertAlmostEqual(sum(weights), 1.0, places=12)
            m = dict(state["metrics"])
            self.assertEqual(m["Weight on the one-step target"], f"{weights[0]:.4f}")
            self.assertEqual(m["Weight on the full return"], f"{weights[-1]:.4f}")
            self.assertEqual(m["Weights add to"], "1.0000")
        # Figure 12.4: eight transitions, lambda 0.9, terminal weight 0.4783 and first weight 0.1.
        fig = dict(self.demos["C12-D03"]["states"]["2,1"]["metrics"])
        self.assertEqual((fig["Weight on the full return"], fig["Weight on the one-step target"]), ("0.4783", "0.1000"))
        self.assertAlmostEqual(0.9 ** 7, 0.4782969, places=6)
        # Ends of the dial: lambda 0 is all one-step, lambda 1 is all complete return.
        zero = dict(self.demos["C12-D03"]["states"]["0,1"]["metrics"])
        one = dict(self.demos["C12-D03"]["states"]["3,1"]["metrics"])
        self.assertEqual((zero["Weight on the one-step target"], zero["Weight on the full return"]), ("1.0000", "0.0000"))
        self.assertEqual((one["Weight on the one-step target"], one["Weight on the full return"]), ("0.0000", "1.0000"))

    def test_d04_td_error_by_hand(self):
        for (prior, successor), state in self.states("C12-D04"):
            delta = -0.02 + successor - prior   # Equation (12.2), discount 1
            m = dict(state["metrics"])
            self.assertEqual(m["TD error delta"], f"{delta:.2f}")
            self.assertEqual(m["Successor estimate that gives zero"], f"{prior + 0.02:.2f}")
            expected = "zero" if abs(delta) < 1e-12 else ("positive" if delta > 0 else "negative")
            self.assertEqual(m["Sign"], expected)
        # The book's two numbers: 0.28 and -0.12 (prior 0.20).
        self.assertEqual(dict(self.demos["C12-D04"]["states"]["0,2"]["metrics"])["TD error delta"], "0.28")
        self.assertEqual(dict(self.demos["C12-D04"]["states"]["0,0"]["metrics"])["TD error delta"], "-0.12")
        self.assertIn("-0.02 + 0.50 - 0.20 = 0.28", html.unescape(self.page).replace("(-0.02)", "-0.02"))

    def prose(self):
        """Visible page text with whitespace collapsed (prompts, explanations, answers)."""
        text = re.sub(r"<script\b.*?</script>|<style\b.*?</style>", " ", self.page, flags=re.S)
        return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", text)))

    def test_check_questions_answers(self):
        # D01 check: step 0.3 (a preset value), final reward 1.
        self.assertAlmostEqual(0.5 + 0.3 * (1 - 0.5), 0.65)
        # D02 check: three ones (a preset value), A ends 0 -> B = 3/8.
        self.assertAlmostEqual(3 / 8, 0.375)
        # D03 check: four transitions, lambda 0.3 (a preset value).
        w = [(1 - 0.3) * 0.3 ** (k - 1) for k in (1, 2, 3)] + [0.3 ** 3]
        self.assertAlmostEqual(w[0], 0.7)
        self.assertAlmostEqual(w[1], 0.21)
        self.assertAlmostEqual(w[2], 0.063)
        self.assertAlmostEqual(w[3], 0.027)
        self.assertAlmostEqual(sum(w), 1.0)
        # D04 check: prior 0.6, successor 0.5.
        self.assertAlmostEqual(-0.02 + 0.5 - 0.6, -0.12)

    def test_patch_g4_ch12_checks_use_preset_values(self):
        """g4-29: every check question can be reproduced with the page controls."""
        text = self.prose()
        for needle in ("With step size 0.3 and a final reward of 1", "Suppose three of the seven B-only episodes pay 1",
                       "With 4 transitions remaining and lambda = 0.3, what weight does the complete return get", "= 0.65 for every state",
                       "B = (3 + 0) / 8 = 0.375", "0.3^3 = 0.027"):
            self.assertIn(needle, text)
        for old in ("With step size 0.2", "Suppose five of the seven", "lambda = 0.5, what weight", "B = (5 + 0) / 8"):
            self.assertNotIn(old, text)
        controls = {d["id"]: {c["key"]: c["values"] for c in d["controls"]} for d in self.data["demos"]}
        self.assertIn(0.3, [as_number(v) for v in controls["C12-D01"]["alpha"]])
        self.assertIn(3, [as_number(v) for v in controls["C12-D02"]["ones_in_b_only"]])
        self.assertIn(0.3, [as_number(v) for v in controls["C12-D03"]["lam"]])
        self.assertIn(4, [as_number(v) for v in controls["C12-D03"]["remaining"]])

    def test_patch_g4_ch12_td_error_wording(self):
        """g4-26, g4-27, g4-28: the verdict follows the state and does not assert the search was useless."""
        for (prior, successor), state in self.states("C12-D04"):
            text = state["interpretation"]
            delta = -0.02 + successor - prior
            self.assertNotIn("found nothing useful", text)
            self.assertNotIn("too low to justify the old forecast", text)
            if delta > 1e-12:
                self.assertIn("Suppose the search itself was unhelpful", text)
                self.assertIn("higher than the estimate before it by more than the cost of 0.02", text)
            elif delta < -1e-12 and successor >= prior - 1e-12:   # 0.2 / 0.2
                self.assertIn("did not rise enough to cover the cost of 0.02", text)
                self.assertNotIn("lower than the estimate before it", text)
            elif delta < -1e-12:
                self.assertIn("lower than the estimate before it", text)
        text = self.prose()
        self.assertIn("which of these successor estimates give a positive error", text)
        self.assertNotIn("which successor estimate gives a positive error", text)
        # The prompt really has two answers (0.50 and 0.80), so the plural wording is required.
        positives = [s for s in (0.1, 0.2, 0.5, 0.8) if -0.02 + s - 0.2 > 0]
        self.assertEqual(positives, [0.5, 0.8])

    def test_patch_g4_ch12_symbols_and_terms(self):
        """g4-30, g4-31, g4-32, g4-34."""
        text = self.prose()
        self.assertIn("gamma is the discount factor (1 here, so nothing is discounted), x_t is the state visited at step t", text)
        self.assertIn("so n = N - t is the number of transitions left", text)
        self.assertIn("temporal-difference (TD) error", text)
        self.assertIn("temporal-difference (TD) learning with a lambda setting", text)
        self.assertLess(text.index("temporal-difference (TD)"), text.index("TD error delta"))
        import base64
        for state in self.demos["C12-D02"]["states"].values():
            svg = base64.b64decode(state["image"].split(",", 1)[1]).decode("utf-8")
            self.assertIn("Value each rule settles on", svg)
            self.assertNotIn("Value both rules converge to", svg)
        self.assertIn("For a fixed policy and a prediction target, it changes the estimator, not the objective", text)

    def test_patch_g4_ch12_lambda_figure_labels_full_return_bar(self):
        """g4-33: the full-return bar is labelled in every state, with 3-decimal labels elsewhere."""
        import base64
        for (lam, n), state in self.states("C12-D03"):
            n = int(n)
            svg = base64.b64decode(state["image"].split(",", 1)[1]).decode("utf-8")
            weights = [(1 - lam) * lam ** (k - 1) for k in range(1, n)] + [lam ** (n - 1)]
            full = weights[-1]
            expected = "0" if full == 0 else ("&lt;0.001" if full < 0.0005 else f"{full:.3f}")
            self.assertIn(f">{expected}<", svg, (lam, n))
            if lam not in (0, 1):
                self.assertIn(f">{weights[0]:.3f}<", svg, (lam, n))

    def test_displayed_equations_are_chapter_equations(self):
        chapter = next(c for c in json.loads((LAB / "chapter-map.json").read_text()) if c["chapter"] == 12)

        def norm(t):
            t = re.sub(r"\\tag\{[^}]*\}", "", t)
            t = re.sub(r"\\[,;:!]", "", t)
            return re.sub(r"[\s{}]", "", t).rstrip(".")
        allowed = {norm(e["tex"]) for e in chapter["equations"]}
        alts = re.findall(r'alt="Equation: ([^"]+)"', self.page)
        self.assertGreaterEqual(len(alts), 4)
        for tex in alts:
            self.assertIn(norm(html.unescape(tex)), allowed)

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

    def test_every_control_combination_renders(self):
        code = (
            "import sys, itertools; sys.path[:0]=['src','tools/readers/engine','tools/readers/chapters'];"
            "import matplotlib; matplotlib.use('Agg'); import ch12;"
            "n=0\n"
            "for d in ch12.CHAPTER['demos']:\n"
            "    f=getattr(ch12,d['function'])\n"
            "    for combo in itertools.product(*[c['values'] for c in d['controls']]):\n"
            "        fig,m,i=f(**{c['key']:v for c,v in zip(d['controls'],combo)}); n+=1\n"
            "print(n)"
        )
        run = subprocess.run([str(VENV_PYTHON), "-c", code], cwd=LAB, capture_output=True, text=True, timeout=600)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertEqual(run.stdout.strip(), "28")

    def test_dom_harness(self):
        if shutil.which("node") is None:
            self.skipTest("Node is not installed")
        run = subprocess.run(["node", str(HARNESS), str(self.reader)], capture_output=True, text=True, timeout=120)
        self.assertEqual(run.returncode, 0, run.stderr)
        report = json.loads(run.stdout)["reports"][0]
        self.assertEqual((report["states_checked"], report["resets_checked"], report["labelled_controls"]), (28, 4, 8))


if __name__ == "__main__":
    unittest.main()
