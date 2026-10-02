"""Chapter 25 laboratory reader: independent hand checks of the built page.

The reader is built into a temporary directory (never the shared readers
folder). Every expected number is recomputed here from the chapter's own
arithmetic by a method different from the module's.
"""
from __future__ import annotations

import html
import itertools
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
SLUG = "25-development-guard-gate"


def venv_python():
    py = LAB / ".venv" / "bin" / "python"
    return str(py) if py.exists() else None


def as_number(text):
    try:
        return float(text)
    except ValueError:
        return text


class Chapter25ReaderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        python = venv_python()
        if python is None:
            raise unittest.SkipTest("laboratory .venv absent")
        cls.tmp = tempfile.mkdtemp()
        run = subprocess.run([python, str(WRAPPER), "--chapters", "25", "--out", cls.tmp], capture_output=True, text=True, timeout=600)
        if run.returncode != 0:
            raise AssertionError(run.stdout + run.stderr)
        cls.reader = Path(cls.tmp) / SLUG / "reader.html"
        cls.page = cls.reader.read_text(encoding="utf-8")
        cls.data = json.loads(re.search(r'<script id="reader-data" type="application/json">(.*?)</script>', cls.page, re.S).group(1))
        cls.demos = {d["id"]: d for d in cls.data["demos"]}

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def states(self, demo_id):
        demo = self.demos[demo_id]
        for key, state in demo["states"].items():
            idx = [int(i) for i in key.split(",")]
            yield [as_number(c["values"][i]) for c, i in zip(demo["controls"], idx)], dict(state["metrics"]), state

    def test_structure_and_budget(self):
        self.assertEqual(list(self.demos), ["C25-D01", "C25-D02", "C25-D03", "C25-D04"])
        self.assertEqual([len(d["states"]) for d in self.data["demos"]], [8, 8, 8, 8])
        self.assertLess(self.reader.stat().st_size, 2_500_000)

    def test_d01_family_counts(self):
        for (parts, variants), m, state in self.states("C25-D01"):
            parts, variants = int(parts), int(variants)
            # enumerate: each part left alone or set to one alternative; exclude the all-unchanged choice
            combos = sum(1 for c in itertools.product(range(variants + 1), repeat=parts) if any(c))
            single = sum(1 for c in itertools.product(range(variants + 1), repeat=parts) if sum(1 for x in c if x) == 1)
            self.assertEqual(m["Versions, any combination of edits"], str(combos))
            self.assertEqual(m["Versions, one edit at a time"], str(single))
            self.assertEqual(single, parts * variants)
        m = next(m for v, m, s in self.states("C25-D01") if v == [5, 3])
        self.assertEqual(m["Versions, any combination of edits"], "1023")
        # boundary: one part, the two descriptions coincide
        m = next(m for v, m, s in self.states("C25-D01") if v == [1, 2])
        self.assertEqual(m["Versions, one edit at a time"], m["Versions, any combination of edits"])
        self.assertIn("theta", m["Model parameters changed"])

    def test_d01_wording_follows_the_state(self):
        interp = {tuple(v): s["interpretation"] for v, m, s in self.states("C25-D01")}
        one = interp[(1, 2)]
        self.assertIn("1 part x 2 alternatives = 2", one)
        self.assertNotIn("1 parts", one)
        self.assertNotIn("grows too fast", one)
        self.assertIn("same number", one)
        self.assertNotIn("1.0 times", one)
        many = interp[(5, 3)]
        self.assertIn("5 parts x 3 alternatives = 15", many)
        self.assertIn("multiplicatively", many)
        for text in interp.values():
            self.assertNotIn("grows too fast", text)
        self.assertNotIn("nothing a reviewer can list", self.page)
        self.assertNotIn("Shaded rows may be changed", self.page)
        self.assertNotIn("the five parts are the chapter", self.page)

    def test_d02_names_and_defaults_are_defined(self):
        self.assertIn("named flashy and steady", self.page)
        self.assertNotIn("book's default case", self.page)
        self.assertNotIn("Book default", self.page)
        self.assertNotIn("mostly luck of the draw", self.page)
        self.assertIn("multiple of 0.25", self.page)

    def test_d03_d04_terms_are_defined(self):
        self.assertIn("The threshold tau is 0.25", self.page)
        self.assertIn("a canary is a small monitored release", self.page)
        self.assertNotIn("1 decisions", self.page)
        keys = {k for v, m, s in self.states("C25-D03") for k in m}
        self.assertIn("Bound, 1 decision", keys)
        self.assertNotIn("Bound, 1 decisions", keys)

    def test_d02_gate_by_hand(self):
        base = [1, 0, 1, 0]
        dev = {"flashy": [1, 1, 1, 1], "steady": [1, 1, 1, 0]}
        guard = {"default": {"flashy": [1, 0, 1, 0], "steady": [1, 1, 1, 0]},
                 "changed": {"flashy": [1, 1, 1, 0], "steady": [1, 1, 1, 0]}}
        demo = self.demos["C25-D02"]
        cases = ["default", "changed"]
        for k, state in demo["states"].items():
            i, j, t = (int(x) for x in k.split(","))
            case = cases[i]
            reused = j == 1
            thr = float(demo["controls"][2]["values"][t])
            rates = {n: sum(v) / 4 for n, v in dev.items()}
            winner = max(rates, key=rates.get)
            gain = sum(g - b for g, b in zip(guard[case][winner], base)) / 4
            m = dict(state["metrics"])
            self.assertEqual(m["Selected on development"], winner)
            self.assertEqual(m["Guard gain of the selected"], f"{gain:.2f}")
            expected = "rejected (guard reused)" if reused else ("accepted by this gate" if gain >= thr else "rejected (gain below threshold)")
            self.assertEqual(m["Release decision"], expected)
        # book numbers: default winner gain 0.00, changed winner gain 0.25
        self.assertEqual(dict(demo["states"]["0,0,0"]["metrics"])["Guard gain of the selected"], "0.00")
        self.assertEqual(dict(demo["states"]["1,0,0"]["metrics"])["Release decision"], "accepted by this gate")
        self.assertEqual(dict(demo["states"]["1,0,1"]["metrics"])["Release decision"], "rejected (gain below threshold)")
        self.assertEqual(dict(demo["states"]["1,1,0"]["metrics"])["Release decision"], "rejected (guard reused)")

    def test_d03_bound_and_exact_tail(self):
        def exact(m, tau=0.25):
            # dynamic program over the sum of m fair +1/-1 steps, independent of the module's binomial sum
            dist = {0: 1.0}
            for _ in range(m):
                nxt = {}
                for s, p in dist.items():
                    nxt[s + 1] = nxt.get(s + 1, 0) + p / 2
                    nxt[s - 1] = nxt.get(s - 1, 0) + p / 2
                dist = nxt
            return sum(p for s, p in dist.items() if s / m >= tau - 1e-12)
        def sig3(x):
            return f"{x:.{max(0, 2 - int(math.floor(math.log10(x))))}f}"
        for (m, q), met, state in self.states("C25-D03"):
            m, q = int(m), int(q)
            bound = math.exp(-m * 0.25 ** 2 / 2)
            self.assertEqual(met["Bound, one decision"], sig3(bound))
            self.assertEqual(met["Exact tail, fair plus or minus 1 case"], sig3(exact(m)))
            self.assertLess(exact(m), bound)
            union = met["Bound, 1 decision" if q == 1 else f"Bound, {q} decisions"]
            if q * bound > 1:
                self.assertIn("says nothing", union)
            else:
                self.assertTrue(union.startswith(sig3(q * bound)))
        m = next(m for v, m, s in self.states("C25-D03") if v == [200, 10])
        self.assertEqual(m["Bound, one decision"], "0.00193")
        self.assertTrue(m["Bound, 10 decisions"].startswith("0.0193"))
        m = next(m for v, m, s in self.states("C25-D03") if v == [50, 10])
        self.assertIn("above 1", m["Bound, 10 decisions"])
        # the check question: m = 300
        self.assertAlmostEqual(math.exp(-300 * 0.0625 / 2), 0.0000848, places=7)

    def test_d04_all_four_conditions(self):
        others = {"all": (0.80, 1, 1), "cost": (0.95, 1, 1), "authority": (0.80, 0, 1), "rollback": (0.80, 1, 0)}
        demo = self.demos["C25-D04"]
        keys = ["all", "cost", "authority", "rollback"]
        for k, state in demo["states"].items():
            i, j = (int(x) for x in k.split(","))
            uplift = float(demo["controls"][0]["values"][i])
            cost, auth, roll = others[keys[j]]
            flags = [uplift >= 0.25, cost <= 1.0 - 0.1 + 1e-12, bool(auth), bool(roll)]
            m = dict(state["metrics"])
            self.assertEqual(m["Accept"].startswith("yes"), all(flags), k)
            for name, flag in zip(["1. Uplift condition", "2. Cost condition", "3. Authorized in scope", "4. Rollback path tested"], flags):
                self.assertTrue(m[name].startswith("pass" if flag else "fail"), (k, name))
        # a cost of 0.95 is under c = 1.00 yet still fails the margin; high uplift does not rescue it
        m = dict(demo["states"]["1,1"]["metrics"])
        self.assertTrue(m["2. Cost condition"].startswith("fail"))
        self.assertEqual(m["Accept"], "no (0)")
        self.assertEqual(dict(demo["states"]["1,0"]["metrics"])["Accept"], "yes (1)")
        # check question: 0.92 > 0.90
        self.assertGreater(0.92, 1.00 - 0.10)

    def test_equations_are_chapter_equations(self):
        chapter = next(c for c in json.loads((LAB / "chapter-map.json").read_text()) if c["chapter"] == 25)
        def norm(t):
            t = re.sub(r"\\tag\{[^}]*\}", "", t)
            t = re.sub(r"\\[,;:!]", "", t)
            return re.sub(r"[\s{}]", "", t).rstrip(".")
        allowed = {norm(e["tex"]) for e in chapter["equations"]}
        alts = re.findall(r'data-tex="([^"]+)"', self.page)
        self.assertEqual(len(alts), 4)
        for tex in alts:
            self.assertIn(norm(html.unescape(tex)), allowed)

    def test_text_rules(self):
        text = re.sub(r"<script\b.*?</script>|<style\b.*?</style>", " ", self.page, flags=re.S)
        text = html.unescape(re.sub(r"<[^>]+>", " ", text))
        for state in (s for d in self.data["demos"] for s in d["states"].values()):
            text += " " + state["interpretation"] + " " + " ".join(" ".join(p) for p in state["metrics"])
        for bad in ("\u2014", "\u2013", "--"):
            self.assertNotIn(bad, text)
        for term in ("matplotlib", "numpy", "python", "jupyter"):
            self.assertNotIn(term, text.lower())
        self.assertIn("constructed", text.lower())

    def test_dom_harness(self):
        if shutil.which("node") is None:
            self.skipTest("Node is not installed")
        run = subprocess.run(["node", str(HARNESS), str(self.reader)], capture_output=True, text=True, timeout=120)
        self.assertEqual(run.returncode, 0, run.stderr)
        report = json.loads(run.stdout)["reports"][0]
        self.assertEqual((report["states_checked"], report["resets_checked"]), (32, 4))


if __name__ == "__main__":
    unittest.main()
