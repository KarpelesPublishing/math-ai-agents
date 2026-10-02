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
        demo = self.demos[demo_id]
        for key, state in demo["states"].items():
            idx = [int(i) for i in key.split(",")]
            yield [c["values"][i] for c, i in zip(demo["controls"], idx)], state

    @staticmethod
    def m(state):
        return dict(state["metrics"])

    def test_structure_and_budget(self):
        self.assertEqual(list(self.demos), ["C01-D01", "C01-D02", "C01-D03", "C01-D04"])
        self.assertEqual([len(d["states"]) for d in self.data["demos"]], [8, 6, 8, 8])
        self.assertLess(self.reader.stat().st_size, 2_500_000)

    def test_d01_flags_crossings_and_slopes(self):
        sets = {"gradual": ([1, 2, 3, 4, 5], [0.42, 0.46, 0.49, 0.52, 0.56]),
                "steep": ([10, 20, 40, 80], [0.1, 0.3, 0.6, 0.8])}
        for (name, cutoff), state in self.states("C01-D01"):
            name = "gradual" if name.startswith("Gradual") else "steep"
            cutoff = float(cutoff)
            xs, ys = sets[name]
            flags = [1 if y >= cutoff else 0 for y in ys]
            m = self.m(state)
            self.assertEqual(m["Verdicts"], "".join(map(str, flags)))
            self.assertEqual(m["Checkpoints passing"], f"{sum(flags)} of {len(ys)}")
            self.assertEqual(m["Verdict changes between checkpoints"], str(sum(a != b for a, b in zip(flags, flags[1:]))))
            slope = max((ys[i] - ys[i - 1]) / (xs[i] - xs[i - 1]) for i in range(1, len(ys)))
            self.assertEqual(m["Steepest graded step"], f"{slope:.3f} per scale unit")
            if 1 in flags:
                self.assertEqual(m["First passing scale"], str(xs[flags.index(1)]))
            else:
                self.assertTrue(m["First passing scale"].startswith("undefined"))
        # Book values: cutoff 0.50 puts the first pass at checkpoint 4, 0.55 moves it to 5.
        g = lambda k: self.m(self.demos["C01-D01"]["states"][k])
        self.assertEqual((g("0,1")["Verdicts"], g("0,2")["Verdicts"]), ("00011", "00001"))
        self.assertEqual(g("0,1")["Steepest graded step"], "0.040 per scale unit")
        self.assertTrue(g("0,3")["First passing scale"].startswith("undefined"))  # cutoff above every score

    def test_d02_expected_scores(self):
        law = {"A": 0.45, "B": 0.35, "E": 0.20}
        accepted = {"Accepts only A": {"A"}, "Rewards asking for evidence": {"E"}, "Accepts A or B": {"A", "B"}}
        for (decoder, evaluator), state in self.states("C01-D02"):
            if decoder.startswith("Greedy"):
                best = max(law, key=law.get)
                expected = 1.0 if best in accepted[evaluator] else 0.0
            else:
                expected = sum(p for k, p in law.items() if k in accepted[evaluator])
            self.assertEqual(self.m(state)["Expected score"], f"{expected:.2f}", (decoder, evaluator))
            self.assertEqual(self.m(state)["Model law (A, B, evidence)"], "0.45, 0.35, 0.20")
        text = self.page
        self.assertIn("0.45 x 1 + 0.35 x 0 + 0.20 x 0 = 0.45", text)
        self.assertIn("1.00 x 1 + 0.00 x 0 + 0.00 x 0 = 1.00", text)

    def test_d03_table_1_1(self):
        table = {(0.90, 5): 0.590, (0.95, 5): 0.774, (0.99, 5): 0.951, (0.90, 20): 0.122, (0.95, 20): 0.358,
                 (0.99, 20): 0.818, (0.90, 40): 0.015, (0.95, 40): 0.129, (0.99, 40): 0.669, (0.90, 100): 0.000,
                 (0.95, 100): 0.006, (0.99, 100): 0.366}
        for (n, step), state in self.states("C01-D03"):
            n = int(n)
            q0, q1 = (0.90, 0.95) if "0.90" in step else (0.95, 0.99)
            m = self.m(state)
            u0, u1 = q0 ** n, q1 ** n
            self.assertAlmostEqual(float(m[f"Score at q = {q0:.2f}"]), u0, delta=0.5e-4 if u0 >= 1e-3 else 5e-7)
            self.assertAlmostEqual(float(m[f"Score at q = {q1:.2f}"]), u1, delta=0.5e-4 if u1 >= 1e-3 else 5e-7)
            self.assertEqual(m["Gain in task score"], f"a factor of {u1 / u0:.1f}")
            for q, u in ((q0, u0), (q1, u1)):
                self.assertAlmostEqual(table[(q, n)], u, delta=0.0006)
        self.assertEqual(self.m(self.demos["C01-D03"]["states"]["2,0"])["Gain in task score"], "a factor of 8.7")  # book: 8.7
        self.assertEqual(self.m(self.demos["C01-D03"]["states"]["3,0"])["Score at q = 0.90"], "0.000027")  # book: 0.000027

    def test_d04_elasticity(self):
        for (n, rise), state in self.states("C01-D04"):
            n = int(n)
            r = 0.01 if rise.startswith("1%") else 0.05
            q0, q1 = 0.9, 0.9 * (1 + r)
            exact = (q1 / q0) ** n - 1
            m = self.m(state)
            self.assertEqual(m["First-order gain (n x rise)"], f"{n * r * 100:.0f}%")
            self.assertEqual(m["Exact gain"], f"{exact * 100:.0f}%")
            self.assertEqual(m["Absolute slope at start"], f"{n * q0 ** (n - 1):.3f}")
        # The chapter's remark: the absolute slope can be below one while the elasticity is n.
        self.assertTrue(float(self.m(self.demos["C01-D04"]["states"]["2,0"])["Absolute slope at start"]) < 1)
        self.assertEqual(self.m(self.demos["C01-D04"]["states"]["3,1"])["Exact gain"], "13050%")  # first-order rule fails here

    # Reader patch (group 1): state-aware wording and regression checks for the old, wrong text.

    def state_text(self, demo_id, key):
        return self.demos[demo_id]["states"][key]["interpretation"]

    def test_d01_jump_size_is_reported_against_the_largest_rise(self):
        # Gradual set, cutoff 0.45 (key 0,0) and 0.55 (0,2): the jump sits on the largest rise (0.04).
        for key in ("0,0", "0,2"):
            text = self.state_text("C01-D01", key)
            self.assertIn("moved by 0.04, the largest rise between neighbouring checkpoints in this set", text, key)
        # Cutoff 0.50 (0,1): the jump of 0.03 is smaller than the largest rise 0.04.
        self.assertIn("moved by 0.03, against 0.04 for the largest rise between neighbouring checkpoints in this set",
                      self.state_text("C01-D01", "0,1"))
        # Steeper set (second option): the jump 0.6 - 0.3 = 0.30 is the largest rise.
        self.assertIn("moved by 0.30, the largest rise between neighbouring checkpoints in this set",
                      self.state_text("C01-D01", "1,0"))
        for key, state in self.demos["C01-D01"]["states"].items():
            self.assertNotIn("moved by only", state["interpretation"], key)

    def test_d01_closing_sentence_depends_on_the_state(self):
        for key in ("0,0", "0,1", "0,2"):
            self.assertIn("Move the cutoff and the place where the skill seems to arrive moves with it", self.state_text("C01-D01", key))
        for key in ("1,0", "1,1", "1,2", "1,3"):
            text = self.state_text("C01-D01", key)
            self.assertNotIn("Move the cutoff and the place", text, key)
            self.assertIn("Every cutoff offered here (0.45 to 0.60) gives the same first pass, scale 40", text, key)
            self.assertIn("a cutoff of 0.70 would move the first pass to scale 80", text, key)

    def test_d01_labels_define_the_terms(self):
        self.assertNotIn("Steeper rise", self.page)
        self.assertIn("Larger rise, four checkpoints (scales double)", self.page)
        self.assertNotIn("Crossings in the verdict", self.page)
        self.assertIn("A verdict change is a pair of neighbouring checkpoints", self.page)
        self.assertIn("z-hat_i is the output generated for prompt i", self.page)

    def test_d02_names_stages_not_arrows_and_greedy_is_a_score(self):
        self.assertNotIn("three arrows", self.page)
        self.assertIn("joins three stages by two arrows", self.page)
        for (decoder, evaluator), state in self.states("C01-D02"):
            text = state["interpretation"]
            if decoder.startswith("Greedy"):
                self.assertIn(". Score = ", text)
                self.assertNotIn("Expected score = ", text)
            else:
                self.assertIn("Expected score = ", text)

    def test_d03_trial_sentence_follows_the_expected_passes(self):
        old = "a score near zero produces about the same observed count"
        for key, state in self.demos["C01-D03"]["states"].items():
            self.assertNotIn(old, state["interpretation"], key)
            self.assertNotIn("hides the effect", state["interpretation"], key)
            self.assertIn("A short target amplifies a gain less than a long target does.", state["interpretation"], key)
        # n = 100, q 0.90 to 0.95 (key 3,0): expected passes 0.0027 then 0.59, both under one.
        near_zero = self.state_text("C01-D03", "3,0")
        self.assertIn("Over 100 trials the expected passes are 0.0 then 0.6, both under one", near_zero)
        self.assertIn("not proof that nothing improved", near_zero)
        # n = 40 default (2,0): 1.5 then 12.9; n = 5 (0,0): 59.0 then 77.4; n = 100 q 0.95 to 0.99 (3,1): 0.6 then 36.6.
        for key, passes in (("2,0", "1.5 then 12.9"), ("0,0", "59.0 then 77.4"), ("3,1", "0.6 then 36.6")):
            text = self.state_text("C01-D03", key)
            self.assertIn(f"Over 100 trials the expected passes are {passes}", text, key)
            self.assertIn("not hidden by low scores", text, key)
            self.assertNotIn("not proof that nothing improved", text, key)
        self.assertIn("computed from the unrounded values", self.state_text("C01-D03", "3,0"))

    def test_d04_first_order_wording_states_its_criterion(self):
        # Default n = 40, rise 1% (2,0): 40% against 49%, a gap of 18 percent of the exact gain.
        far = self.state_text("C01-D04", "2,0")
        self.assertIn("more than 10 percent below the exact gain (40% against 49%)", far)
        self.assertNotIn("misses badly", far)
        # n = 20, rise 1% (1,0): 20% against 22%, within 10 percent.
        close = self.state_text("C01-D04", "1,0")
        self.assertIn("within 10 percent of the exact gain (20% against 22%)", close)
        self.assertIn("n x rise = 0.20", close)
        self.assertNotIn("small relative to the length", close)
        for key, state in self.demos["C01-D04"]["states"].items():
            self.assertNotIn("small relative to the length", state["interpretation"], key)
            self.assertNotIn("misses badly", state["interpretation"], key)
        self.assertIn("the derivative dU/dq", self.page)

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
        self.assertEqual((report["states_checked"], report["resets_checked"], report["labelled_controls"]), (30, 4, 8))

    def test_build_is_reproducible(self):
        with tempfile.TemporaryDirectory() as out:
            again = build(out)
            self.assertEqual(hashlib.sha256(again.read_bytes()).hexdigest(), hashlib.sha256(self.reader.read_bytes()).hexdigest())


if __name__ == "__main__":
    unittest.main()
