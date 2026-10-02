"""Chapter 17 laboratory reader: independent hand checks of the built page.

The reader is built into a private temporary directory (never into readers/),
then every headline number is recomputed here from the chapter's own
arithmetic with exact fractions, not read back from the module that made it.
"""
from __future__ import annotations

import hashlib
import html
import importlib.util
import json
import os
from fractions import Fraction as F
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
SLUG = "17-effect-and-retry"


def builder_python():
    spec = importlib.util.spec_from_file_location("reader_engine_tests", HERE / "test_readers_engine.py")
    helpers = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helpers)
    return helpers.builder_python()


def build(out):
    python = builder_python()
    if python is None:
        return None
    run = subprocess.run([python, str(WRAPPER), "--chapters", "17", "--out", out], capture_output=True, text=True,
                         timeout=600, env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
    assert run.returncode == 0, run.stdout + run.stderr
    return Path(out) / SLUG / "reader.html"


def payload(text):
    return json.loads(re.search(r'<script id="reader-data" type="application/json">(.*?)</script>', text, re.S).group(1))


def num(text):
    try:
        return float(text)
    except ValueError:
        return text


class Chapter17ReaderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        cls.reader = build(cls._tmp.name)
        if cls.reader is None:
            raise unittest.SkipTest("no interpreter with numpy, matplotlib and jinja2 (laboratory .venv absent)")
        cls.page = cls.reader.read_text(encoding="utf-8")
        cls.data = payload(cls.page)
        cls.demos = {d["id"]: d for d in cls.data["demos"]}

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    VALUES = {
        "C17-D01": [["put", "delete", "charge", "charge_key"], [2, 3]],
        "C17-D02": [[0.5, 0.99], [0.1, 0.5, 0.9]],
        "C17-D03": [[0, 10, 90], [0.5, 0.99]],
        "C17-D04": [["none", "idempotent", "absent", "restored"], ["yes", "no"]],
    }

    def states(self, demo_id):
        """Yield (control values as written in the reader's definition, state); the page stores labels, so map by index."""
        for key, state in self.demos[demo_id]["states"].items():
            idx = [int(i) for i in key.split(",")]
            yield [vals[i] for vals, i in zip(self.VALUES[demo_id], idx)], state

    def test_structure_and_budgets(self):
        self.assertEqual(list(self.demos), ["C17-D01", "C17-D02", "C17-D03", "C17-D04"])
        self.assertEqual([len(d["states"]) for d in self.data["demos"]], [8, 6, 6, 8])
        self.assertLess(self.reader.stat().st_size, 2_500_000)

    def test_d01_repeat_by_hand(self):
        seen = 0
        for (op, n), state in self.states("C17-D01"):
            n = int(n)
            m = dict(state["metrics"])
            one = {"put": 150, "delete": None, "charge": 100 + 50, "charge_key": 150}[op]
            many = {"put": 150, "delete": None, "charge": 100 + 50 * n, "charge_key": 100 + 50}[op]
            if op == "delete":
                self.assertEqual(m["Record after one request"], "absent")
                self.assertEqual(m["Equation (17.1)"], "holds")
            else:
                self.assertEqual(m["Record after one request"], f"{one}")
                self.assertEqual(m[f"Record after {n} requests"], f"{many}")
                self.assertEqual(m["Equation (17.1)"], "holds" if one == many else "fails")
            self.assertEqual(m["Log lines written"], str(n))
            seen += 1
        self.assertEqual(seen, 8)
        # the book's point: a charge with no key repeated 3 times ends at 250
        charge3 = next(s for v, s in self.states("C17-D01") if v == ["charge", 3])
        self.assertEqual(dict(charge3["metrics"])["Record after 3 requests"], "250")
        self.assertIn("100 + 3 x 50 = 250", charge3["interpretation"])
        # the service's logging and replies are declared as constructed behaviour
        self.assertIn("The service is also constructed to log every request and to reply as shown.", self.page)

    def test_d02_posterior_by_hand(self):
        for (prior, la), state in self.states("C17-D02"):
            p, a, b = F(str(prior)), F(str(la)), F(1, 2)
            post = a * p / (a * p + b * (1 - p))
            m = dict(state["metrics"])
            self.assertEqual(m["Belief after silence"], f"{float(post):.3f}")
            self.assertEqual(m["Belief before (prior)"], f"{float(p):.3f}")
        # equal likelihoods leave the prior unchanged (the chapter's baseline)
        base = next(s for v, s in self.states("C17-D02") if v == [0.99, 0.5])
        self.assertEqual(dict(base["metrics"])["Belief after silence"], "0.990")
        self.assertIn("cancel", base["interpretation"])
        # the change is printed as a plain signed number, not a parenthesised negative
        for (prior, la), state in self.states("C17-D02"):
            p, a = F(str(prior)), F(str(la))
            change = a * p / (a * p + F(1, 2) * (1 - p)) - p
            self.assertEqual(dict(state["metrics"])["Change"], f"{float(change):.3f}")
        down = next(s for v, s in self.states("C17-D02") if v == [0.5, 0.1])
        self.assertEqual(dict(down["metrics"])["Change"], "-0.333")
        self.assertNotIn("(-0.333)", " ".join(" ".join(p) for p in down["metrics"]))
        # the prediction names the control that exists and the symbols explain the empty set
        self.assertIn("set the chance of silence if the effect landed to 0.9, against a fixed 0.5", self.page)
        self.assertNotIn("Then try 0.9 against 0.5", self.page)
        self.assertIn("the empty-set symbol stands for silence", self.page)
        # worked values from the demonstration's own check question
        self.assertAlmostEqual(float(F(9, 10) * F(1, 5) / (F(9, 10) * F(1, 5) + F(1, 2) * F(4, 5))), 0.310, places=3)

    def test_d03_retry_by_hand(self):
        cmiss = F(10)
        for (cdup, beta), state in self.states("C17-D03"):
            c, b = F(str(cdup)), F(str(beta))
            diff = (1 - b) * cmiss - b * c
            thr = cmiss / (cmiss + c)
            m = dict(state["metrics"])
            self.assertEqual(m["EU(retry) minus EU(decline)"], f"{float(diff):.2f}")
            self.assertEqual(m["Retry threshold"], f"{float(thr):.2f}")
            expected = "tie" if diff == 0 else ("retry" if diff > 0 else "decline")
            self.assertEqual(m["Better action"], expected, (cdup, beta))
            # the sign of the difference agrees with comparing beta to the threshold
            self.assertEqual(diff > 0, b < thr)
        for (cdup, beta), state in self.states("C17-D03"):
            text = state["interpretation"]
            self.assertIn("The threshold depends only on the two costs, not on the belief", text)
            self.assertNotIn("between the three thresholds", text)
            self.assertIn(f"Threshold = 10 / (10 + {cdup}) = {10 / (10 + cdup):.2f}", text)
        tie = next(s for v, s in self.states("C17-D03") if v == [10, 0.5])
        self.assertEqual(dict(tie["metrics"])["Better action"], "tie")
        self.assertIn("does not choose", tie["interpretation"])

    def test_d04_gate_truth_table(self):
        for (evidence, ready), state in self.states("C17-D04"):
            routes = [evidence == "idempotent", evidence == "absent", evidence == "restored"]
            member = (ready == "yes") and any(routes)
            m = dict(state["metrics"])
            self.assertEqual(m["Membership"], "in Rep(x)" if member else "not in Rep(x)", (evidence, ready))
            self.assertEqual(m["Routes that hold"], f"{sum(routes)} of 3")
            self.assertEqual(m["Ready"], "true" if ready == "yes" else "false")
            text = state["interpretation"]
            # necessity claims were softened to the chapter's wording
            self.assertNotIn("needs observation, recovery or a person first", text)
            self.assertNotIn("the next step is observation, recovery or a person", text)
        default = next(s for v, s in self.states("C17-D04") if v == ["none", "yes"])
        self.assertIn("no evidence supports a route", default["interpretation"])
        self.assertIn("may need observation, recovery, a deliberate risk decision or a person", default["interpretation"])
        self.assertIn("the next step may be a read, a recovery, a deliberate risk decision or a person", self.page)
        self.assertNotIn("the next step is a read, a recovery or a person", self.page)

    def test_displayed_equations_are_chapter_equations(self):
        chapter = next(c for c in json.loads((LAB / "chapter-map.json").read_text()) if c["chapter"] == 17)

        def norm(t):
            t = re.sub(r"\\tag\{[^}]*\}", "", t)
            t = re.sub(r"\\(?:[,;:!]|quad|qquad)", "", t)
            return re.sub(r"[\s{}]", "", t).rstrip(".,;")
        allowed = {norm(e["tex"]) for e in chapter["equations"]}
        alts = re.findall(r'data-tex="([^"]+)"', self.page)
        self.assertEqual(len(alts), 4)
        for tex in alts:
            self.assertIn(norm(html.unescape(tex)), allowed)

    def test_links_and_offline(self):
        self.assertIn('href="../../notebooks/17-effect-and-retry.ipynb"', self.page)
        self.assertIn('href="../../skills/maa-17-effect-and-retry/SKILL.md"', self.page)
        self.assertIsNone(re.search(r'(src|href)="(https?:)?//', self.page))

    def test_page_text_rules(self):
        text = re.sub(r"<script\b.*?</script>|<style\b.*?</style>", " ", self.page, flags=re.S)
        text = html.unescape(re.sub(r"<[^>]+>", " ", text))
        for state in (s for d in self.data["demos"] for s in d["states"].values()):
            text += " " + state["interpretation"] + " " + " ".join(" ".join(p) for p in state["metrics"])
        for bad in ("\u2014", "\u2013", "\u2212", "--"):
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
        self.assertEqual((report["states_checked"], report["resets_checked"], report["labelled_controls"]), (28, 4, 8))

    def test_build_is_reproducible(self):
        with tempfile.TemporaryDirectory() as out:
            again = build(out)
            self.assertEqual(hashlib.sha256(again.read_bytes()).hexdigest(), hashlib.sha256(self.reader.read_bytes()).hexdigest())


if __name__ == "__main__":
    unittest.main()
