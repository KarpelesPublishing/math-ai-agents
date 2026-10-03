"""Chapter 1 laboratory reader: independent hand checks of the built page.

Expected numbers are recomputed here from the chapter's own arithmetic
(Table 1.1, the 0.45/0.35/0.20 distribution, the threshold example), not read
back from the module. The reader is built into a temporary directory.
"""
from __future__ import annotations

import hashlib
import html
import json
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
PYTHON = LAB / ".venv" / "bin" / "python"


PRED = {"Scale 5": 2, "About 9 times": 2, "No, all five must be fixed": 1}


def payload(text):
    return json.loads(re.search(r'<script id="reader-data" type="application/json">(.*?)</script>', text, re.S).group(1))


def build(out):
    run = subprocess.run([str(PYTHON), str(WRAPPER), "--chapters", "1", "--out", str(out)], capture_output=True, text=True, timeout=600)
    if run.returncode != 0:
        raise AssertionError(run.stdout + run.stderr)
    return Path(out) / "01-score-threshold" / "reader.html"


@unittest.skipUnless(PYTHON.is_file(), "laboratory .venv absent")
class Chapter1ReaderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.reader = build(cls.tmp.name)
        cls.page = cls.reader.read_text(encoding="utf-8")
        cls.data = payload(cls.page)
        cls.demos = {d["id"]: d for d in cls.data["demos"]}

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def states(self, demo_id):
        """Yield (tuple of control indices, state); callers map indices to the declared values below."""
        for key, state in self.demos[demo_id]["states"].items():
            yield tuple(int(i) for i in key.split(",")), state

    def state_text(self, demo_id, key):
        return self.demos[demo_id]["states"][key]["interpretation"]

    @staticmethod
    def m(state):
        return dict(state["metrics"])

    def test_structure_and_budget(self):
        self.assertEqual(list(self.demos), ["C01-D01", "C01-D02", "C01-D03", "C01-D04"])
        self.assertEqual([len(d["states"]) for d in self.data["demos"]], [8, 12, 12, 8])
        self.assertLess(self.reader.stat().st_size, 4_000_000)

    def test_d01_flags_crossings_and_slopes(self):
        sets = [([1, 2, 3, 4, 5], [0.42, 0.46, 0.49, 0.52, 0.56]), ([10, 20, 40, 80], [0.1, 0.3, 0.6, 0.8])]
        cutoffs = [0.5, 0.55, 0.6, 0.7]
        for (si, ci), state in self.states("C01-D01"):
            cutoff = cutoffs[ci]
            xs, ys = sets[si]
            flags = [1 if y >= cutoff else 0 for y in ys]
            m = self.m(state)
            self.assertEqual(m["Verdicts"], "".join(map(str, flags)))
            self.assertEqual(m["Checkpoints passing"], f"{sum(flags)} of {len(ys)}")
            self.assertEqual(m["Verdict changes between checkpoints"], str(sum(a != b for a, b in zip(flags, flags[1:]))))
            slope = max((ys[i] - ys[i - 1]) / (xs[i] - xs[i - 1]) for i in range(1, len(ys)))
            self.assertEqual(m["Largest rise per scale unit"], f"{slope:.3f} per scale unit")
            if 1 in flags:
                self.assertEqual(m["First passing scale"], str(xs[flags.index(1)]))
            else:
                self.assertTrue(m["First passing scale"].startswith("undefined"))
            self.assertEqual(len(state["steps"]), 6)
        g = lambda k: self.m(self.demos["C01-D01"]["states"][k])
        self.assertEqual((g("0,0")["Verdicts"], g("0,1")["Verdicts"]), ("00011", "00001"))  # skill use case: 0.5 then 0.55
        self.assertTrue(g("0,2")["First passing scale"].startswith("undefined"))
        self.assertEqual(g("1,3")["Verdicts"], "0001")  # transfer: cutoff 0.7 passes only the last checkpoint
        self.assertEqual(g("1,3")["Largest rise per scale unit"], "0.020 per scale unit")
        self.assertEqual(g("1,2")["Verdicts"], "0011")  # 0.6 equals the score at scale 40 and passes

    def test_d01_prediction_and_panels(self):
        d = self.demos["C01-D01"]
        self.assertEqual(d["predict"]["answer"], PRED["Scale 5"])
        self.assertIn("Scale 5", self.page)
        self.assertIn("moved by 0.03, against 0.04", self.state_text("C01-D01", "0,0"))
        self.assertIn("moved by 0.04, the largest rise", self.state_text("C01-D01", "0,1"))
        self.assertIn("0.50 gives scale 4, 0.55 gives scale 5, 0.60 gives no pass, 0.70 gives no pass", self.state_text("C01-D01", "0,0"))
        self.assertIn("0.50 gives scale 40, 0.55 gives scale 40, 0.60 gives scale 40, 0.70 gives scale 80", self.state_text("C01-D01", "1,0"))
        self.assertIn("What this does not settle", self.page)
        self.assertIn("A score that crosses a pass line is a new internal state", self.page)

    def test_d02_scores(self):
        laws = [(0.45, 0.35, 0.20), (0.30, 0.30, 0.40)]
        accepted = [{0}, {2}]
        for (di, ei, li), state in self.states("C01-D02"):
            law = laws[li]
            acc = accepted[ei]
            p_acc = sum(law[i] for i in acc)
            if di == 0:
                best = max(range(3), key=lambda i: law[i])
                expected = 1.0 if best in acc else 0.0
            elif di == 1:
                expected = p_acc
            else:
                expected = 1 - (1 - p_acc) ** 20
            m = self.m(state)
            key = "Expected score" if di == 1 else "Score"
            self.assertEqual(m[key], f"{expected:.2f}", (di, ei, li))
            self.assertEqual(m["Model law (A, B, evidence)"], ", ".join(f"{p:.2f}" for p in law))
            self.assertEqual(len(state["steps"]), 4)
        self.assertIn("0.45 x 1 + 0.35 x 0 + 0.20 x 0 = 0.45", self.page)
        self.assertIn("1.00 x 1 + 0.00 x 0 + 0.00 x 0 = 1.00", self.page)
        # The chapter's twenty attempts at probability 0.20: about ninety-nine times in a hundred.
        text = self.state_text("C01-D02", "2,1,0")
        self.assertIn("1 - (1 - 0.20)^20 = 1 - 0.0115 = 0.9885", text)
        # The check question: flat law 0.30, 0.30, 0.40, evidence rewarded: greedy 1, one draw 0.40.
        self.assertEqual(self.m(self.demos["C01-D02"]["states"]["0,1,1"])["Score"], "1.00")
        self.assertEqual(self.m(self.demos["C01-D02"]["states"]["1,1,1"])["Expected score"], "0.40")
        self.assertIn("0.30 x 0 + 0.30 x 0 + 0.40 x 1 = 0.40", self.state_text("C01-D02", "1,1,1"))
        self.assertIn("Equation (1.1)", self.page)

    def test_d03_table_1_1_and_first_order_rule(self):
        table = {(0.90, 5): 0.590, (0.95, 5): 0.774, (0.99, 5): 0.951, (0.90, 20): 0.122, (0.95, 20): 0.358,
                 (0.99, 20): 0.818, (0.90, 40): 0.015, (0.95, 40): 0.129, (0.99, 40): 0.669, (0.90, 100): 0.000,
                 (0.95, 100): 0.006, (0.99, 100): 0.366}
        lengths = [5, 20, 40, 100]
        steps = [(0.90, 0.95), (0.95, 0.99), (0.90, 0.99)]
        for (li, si), state in self.states("C01-D03"):
            n = lengths[li]
            q0, q1 = steps[si]
            m = self.m(state)
            u0, u1 = q0 ** n, q1 ** n
            self.assertAlmostEqual(float(m[f"Score at q = {q0:.2f}"]), u0, delta=0.5e-4 if u0 >= 1e-3 else 5e-7)
            self.assertAlmostEqual(float(m[f"Score at q = {q1:.2f}"]), u1, delta=0.5e-4 if u1 >= 1e-3 else 5e-7)
            self.assertEqual(m["Gain in task score"], f"a factor of {u1 / u0:.1f}")
            rise = round(q1 / q0 - 1, 4)
            self.assertEqual(m["First-order multiple (1 + n x rise)"], f"{1 + n * rise:.2f}")
            self.assertEqual(m["Absolute slope at start"], f"{n * q0 ** (n - 1):.3f}")
            self.assertEqual(len(state["steps"]), 7)
            for q, u in ((q0, u0), (q1, u1)):
                self.assertAlmostEqual(table[(q, n)], u, delta=0.0006)
        g = lambda k: self.m(self.demos["C01-D03"]["states"][k])
        self.assertEqual(g("2,0")["Gain in task score"], "a factor of 8.7")  # book: 8.7
        self.assertEqual(g("3,0")["Score at q = 0.90"], "0.000027")  # book: 0.000027
        self.assertEqual(g("1,2")["Gain in task score"], "a factor of 6.7")  # coding assistant, 20 lines
        d = self.demos["C01-D03"]
        self.assertEqual(d["predict"]["answer"], PRED["About 9 times"])
        self.assertIn("About 9 times", self.page)

    def test_d03_trial_sentence_follows_the_expected_passes(self):
        near_zero = self.state_text("C01-D03", "3,0")
        self.assertIn("Over 100 trials the expected passes are 0.0 then 0.6, both under one", near_zero)
        self.assertIn("not proof that nothing improved", near_zero)
        for key, passes in (("2,0", "1.5 then 12.9"), ("0,0", "59.0 then 77.4"), ("3,1", "0.6 then 36.6")):
            text = self.state_text("C01-D03", key)
            self.assertIn(f"Over 100 trials the expected passes are {passes}", text, key)
            self.assertNotIn("not proof that nothing improved", text, key)
        for key, state in self.demos["C01-D03"]["states"].items():
            self.assertIn("A short target amplifies a gain less than a long target does.", state["interpretation"], key)

    def test_d03_first_order_wording_states_its_criterion(self):
        # n = 5, 0.90 to 0.95: rule 1.28 against exact 1.31, within 10 percent.
        self.assertIn("within 10 percent of the exact 1.31", self.state_text("C01-D03", "0,0"))
        # n = 40, 0.90 to 0.95: rule 3.22 against exact 8.70.
        far = self.state_text("C01-D03", "2,0")
        self.assertIn("1 + 40 x 0.0556 = 3.22, more than 10 percent away from the exact 8.69", far)
        self.assertIn("n x q^(n - 1) = 40 x 0.90^39 = 0.657, below one", far)

    def test_d04_declarations_and_audit(self):
        unfixed = ["none", "scale axis", "metric and baseline", "predictor class"]
        for (ui, ci), state in self.states("C01-D04"):
            m = self.m(state)
            k = 0 if ui == 0 else 1
            self.assertEqual(m["Declarations fixed (assumed)"], f"{5 - k} of 5")
            self.assertEqual(m["Open declaration"], unfixed[ui])
            self.assertEqual(m["Checkable in principle"], "yes" if k == 0 else "no")
            self.assertEqual(m["Audit rows answered"], "6 of 6" if ci == 0 else "3 of 6")
            self.assertEqual(m["Audit verdict"], "assigned to the readout" if ci == 0 else "no verdict")
            self.assertIn(f"Declarations fixed = 5 - {k} = {5 - k} of 5", state["interpretation"])
        self.assertIn("Audit rows the chapter answers for this claim = 6 - 3 = 3 of 6", self.state_text("C01-D04", "0,1"))
        self.assertIn("the cliff softened", self.state_text("C01-D04", "2,0"))
        self.assertIn("the cliff relocated", self.state_text("C01-D04", "1,0"))
        d = self.demos["C01-D04"]
        self.assertEqual(d["predict"]["answer"], PRED["No, all five must be fixed"])
        self.assertIn("No, all five must be fixed", self.page)

    def test_d04_all_five_fixed_is_a_supposition_not_a_fact(self):
        # g1-01: the chapter never says a particular claim has all five declarations fixed, and the benchmark
        # case is one the chapter says cannot be settled.
        for key in ("0,0", "0,1"):
            text = self.state_text("C01-D04", key)
            self.assertIn("here all five are supposed fixed, so it would be checkable in principle", text)
            self.assertNotIn("and they are", text)
            state = self.demos["C01-D04"]["states"][key]
            self.assertNotIn("Claim checkable", dict(state["metrics"]))
            self.assertTrue(any("supposed fixed, so it would be" in step for step in state["steps"]))
            self.assertNotIn("It is.", " ".join(state["steps"]))
        bench = self.state_text("C01-D04", "0,1")
        self.assertIn("Being checkable in principle does not produce a verdict here", bench)
        self.assertIn("The audit returns no verdict", bench)
        self.assertNotIn("Being checkable in principle", self.state_text("C01-D04", "0,0"))
        self.assertIn("None (suppose all five fixed)", self.page)
        self.assertNotIn("Checkable: all five fixed.", self.page)

    def test_d01_closing_sentence_is_not_a_blanket_claim(self):
        # g1-02, g1-03: 0.50, 0.55 and 0.60 all give scale 40 on the steep set.
        for key in ("1,0", "1,1", "1,2"):
            text = self.state_text("C01-D01", key)
            self.assertNotIn("the date of arrival followed the line", text)
            self.assertIn("while the line stays inside a gap between scores, the date stays put", text)
            self.assertIn("The largest rise per scale unit is", text)
            self.assertNotIn("steepest graded step", text.lower())
        self.assertIn("the largest rise in score between neighbouring checkpoints", self.state_text("C01-D01", "1,0"))

    def test_d03_budget_and_slope_wording(self):
        # g1-04: the 100 trial budget is the reader's number; g1-05: the 0.657 slope is the slope at the starting q.
        d = self.demos["C01-D03"]
        self.assertIn("The budget of 100 trials behind the expected-passes readout is a value defined for the reader", self.page)
        self.assertIn("a budget of 100 trials, a number defined for the reader", self.page)
        self.assertNotIn("The chapter says a flat observed region need not mean nothing was happening: at n = 100", self.page)
        far = self.state_text("C01-D03", "2,0")
        self.assertIn("so at the starting q a one-point gain in q buys less than one point of score", far)
        slope1 = 40 * 0.95 ** 39
        avg = (0.95 ** 40 - 0.90 ** 40) / 0.05
        self.assertIn(f"The slope at q = 0.95 is {slope1:.3f}, and over the whole step the average slope is {avg:.3f}.", far)

    def test_optional_panels_present(self):
        self.assertIn("Ask the chapter skill", self.page)
        self.assertIn("maa-01-score-threshold", self.page)
        self.assertGreaterEqual(self.page.count("Chapter 1 source:"), 3)
        self.assertGreaterEqual(self.page.count("Common wrong turn"), 4)

    def test_equations_are_chapter_equations(self):
        chapter = next(c for c in json.loads((LAB / "chapter-map.json").read_text()) if c["chapter"] == 1)

        def norm(t):
            t = re.sub(r"\\tag\{[^}]*\}", "", t)
            t = re.sub(r"\\(qquad|quad)|\\[,;:!]", "", t)
            return re.sub(r"[\s{}]", "", t).rstrip(".")
        allowed = {norm(e["tex"]) for e in chapter["equations"]}
        alts = [norm(html.unescape(t)) for t in re.findall(r'data-tex="([^"]+)"', self.page)]
        self.assertGreaterEqual(len(alts), 4)
        for a in alts:
            self.assertIn(a, allowed)
        manuscript = (LAB.parent / "Manuscript/revisions/part-i-v2/01-when-a-score-becomes-a-skill.md").read_text()
        self.assertIn("$nq^{n-1}$", manuscript)

    def test_text_rules_and_links(self):
        text = re.sub(r"<script\b.*?</script>|<style\b.*?</style>", " ", self.page, flags=re.S)
        text = html.unescape(re.sub(r"<[^>]+>", " ", text))
        for state in (s for d in self.data["demos"] for s in d["states"].values()):
            text += " " + state["interpretation"] + " " + " ".join(" ".join(p) for p in state["metrics"])
        for bad in ("\u2014", "\u2013", "\u2212", "--"):
            self.assertNotIn(bad, text)
        for term in ("matplotlib", "numpy", "python", "jupyter"):
            self.assertNotIn(term, text.lower())
        self.assertIn("constructed", text.lower())
        self.assertIsNone(re.search(r'(src|href)="(https?:)?//', self.page))
        self.assertIn('<a class="skip" href="#main">', self.page)

    def test_dom_harness(self):
        if shutil.which("node") is None:
            self.skipTest("Node is not installed")
        run = subprocess.run(["node", str(HARNESS), str(self.reader)], capture_output=True, text=True, timeout=120)
        self.assertEqual(run.returncode, 0, run.stderr)
        report = json.loads(run.stdout)["reports"][0]
        self.assertEqual((report["states_checked"], report["resets_checked"], report["labelled_controls"]), (40, 4, 9))

    def test_build_is_reproducible(self):
        with tempfile.TemporaryDirectory() as out:
            again = build(out)
            self.assertEqual(hashlib.sha256(again.read_bytes()).hexdigest(), hashlib.sha256(self.reader.read_bytes()).hexdigest())


if __name__ == "__main__":
    unittest.main()
